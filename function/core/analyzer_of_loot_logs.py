import cProfile
import copy
import json
import os
import random
from collections import defaultdict, deque

import cv2

from function.common.one_time_match import one_item_match
from function.globals.get_paths import PATHS
from function.globals.init_resources import RESOURCE_P
from function.globals.log import CUS_LOGGER

"""
FAA战斗结果分析模块 - 战利品识别与自主学习的异元素融合:有向无环图驱动的高效算法.
基于拓扑排序的异元素战利品识别与自主学习系统, 通过多次迭代自学习战利品出现顺序的规律性,构建有向无环图模型.
利用图论中的拓扑排序算法, 获取最优识别任务序列, 避免重复遍历, 将时间复杂度降低至开双重根号量级.
该系统经过深度优化, 算法效率卓越, 识别准确高效.
致谢: 八重垣天知 
参考文献: "Topological sorting of large networks" (Communications of the ACM, 1962)
"""


def match_what_item_img_is_new(block, list_iter, last_name=None, may_locked=True):
    # 如果上次识图成功, 则再试一次, 看看是不是同一张图
    if last_name is not None:
        item_img = RESOURCE_P["item"]["战利品"][last_name + ".png"]

        # 对比 block 和 target_image 识图成功 返回识别的道具名称(不含扩展名)
        if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask"):
            return last_name, list_iter

        # 部分物品可能绑定
        if may_locked and last_name in ["4级四叶草", "5级四叶草", "威望币", "遗迹古卷", "金币", "小金币袋", "大金币袋"]:
            if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask_locked"):
                return "绑定 - " + last_name, list_iter

    # 先按照顺序表遍历, 极大减少耗时
    for item_name in list_iter:
        item_img = RESOURCE_P["item"]["战利品"][item_name + ".png"]

        # 对比 block 和 target_image 识图成功 返回识别的道具名称(不含扩展名)
        if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask_tradable"):
            return item_name, list_iter
        # 部分物品可能绑定
        if may_locked and item_name in ["4级四叶草", "5级四叶草", "威望币", "遗迹古卷", "金币", "小金币袋", "大金币袋"]:
            if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask_locked"):
                return "绑定 - " + item_name, list_iter

    # 如果在json中按顺序查找没有找到, 全部遍历
    for item_name, item_img in RESOURCE_P["item"]["战利品"].items():
        item_name = item_name.replace(".png", "")

        # 对比 block 和 target_image 识图成功 返回识别的道具名称(不含扩展名)
        if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask_tradable"):
            return item_name, list_iter

        # 部分物品可能绑定
        if may_locked and item_name in ["异次元空间袋", "法老王的黄金棺材盒", "4级四叶草", "5级四叶草", "威望币",
                                        "遗迹古卷", "金币", "小金币袋", "大金币袋"]:
            if one_item_match(img_block=block, img_tar=item_img, mode="match_template_with_mask_locked"):
                return "绑定 - " + item_name, list_iter

    # 还是找不到, 识图失败 把block保存到resource-picture-item-未编码索引中
    print(f'该道具未能识别, 已在 [ resource / picture /  item / 未编码索引中 ] 生成文件, 请检查')

    # 随便编码
    filename = "{}\\未编码索引\\{}.png".format(PATHS["picture"]["item"], random.randint(1, 100))

    # 保存图片
    cv2.imencode('.png', block)[1].tofile(filename)

    return "识别失败", list_iter


def match_items_from_image(img_save_path, img, mode='loots', test_print=False, method="new"):
    """
    保存图片, 分析图片，获取战利品字典，尽可能不要输出None
    :param img_save_path: 图片保存路径
    :param img: 图片文件  numpy.ndarray
    :param mode: 识别模式
    :param test_print: 是否输出调试信息
    :param method: str 匹配方法 old已被删除 目前请不要填写保持默认的"new"
    :return:
    """

    # 判断mode和method正确:
    if mode not in ["loots", "chests"]:
        raise ValueError("mode参数错误")
    if method not in ["new"]:
        raise ValueError("method参数错误")

    # 奇技淫巧之二,保留上一次的识别图片名
    last_name = None

    # 保存图片
    cv2.imencode('.png', img)[1].tofile(img_save_path)

    # 单个图片的列表
    block_list = []
    # 按模式分割图片
    if mode == 'loots':
        # 战利品模式 把每张图片分割成35 * 35像素的块，间隔的x与y都是49
        rows = 5
        column = 10
        for i in range(rows):
            for j in range(column):
                # 切分为 49x49 block = img[i * 49:(i + 1) * 49, j * 49:(j + 1) * 49, :]
                # 切分为 44x44 block = block[1:-4, 1:-4, :]
                block_list.append(img[i * 49 + 1: (i + 1) * 49 - 4, j * 49 + 1: (j + 1) * 49 - 4, :])

    if mode == 'chests':
        # 开宝箱模式 先切分为 44x44
        for i in range(0, img.shape[1], 44):
            block_list.append(img[:, i:i + 44, :])

    # 保存最佳匹配道具的识图数据
    best_match_items = {}

    # 读取现 JSON 文件
    json_path = PATHS["logs"] + "\\item_ranking.json"
    ranking_list = ranking_read_data(json_path=json_path)["ranking_easy"]
    print(ranking_list)

    # 获取列表的迭代器 从上一个检测的目标开始, 迭代已记录的json顺序中后面的部分
    list_iter = iter(copy.deepcopy(ranking_list))

    # 按照分割规则，遍历分割每一块，然后依次识图
    for block in block_list:

        # 执行模板匹配并获取最佳匹配的文件名
        if mode == 'loots':
            # loots
            best_match_item, list_iter = match_what_item_img_is_new(
                block=block, list_iter=list_iter, last_name=last_name, may_locked=False)
        else:
            # chests
            best_match_item, list_iter = match_what_item_img_is_new(
                block=block, list_iter=list_iter, last_name=last_name, may_locked=True)

        if best_match_item in ['None-0', 'None-1', 'None-2']:
            # 识别为无 后面的就不用识别了
            break

        if best_match_item:
            # 如果道具ID已存在，则增加数量，否则初始化数量为1
            if best_match_item in best_match_items:
                best_match_items[best_match_item] += 1
            else:
                best_match_items[best_match_item] = 1

        # 如果不是识别失败,就暂时保存上一次的图片名,下次识图开始时额外识别一次上一次图片
        if best_match_item != "识别失败":
            last_name = best_match_item
        if best_match_item == "识别失败":
            list_iter = iter(copy.deepcopy(ranking_list))  # 重新获取迭代器

    # 把识别结果显示到界面上
    if test_print:
        CUS_LOGGER.debug(f"match_items_from_image方法 战利品识别结果：{best_match_items}")

    if mode == 'loots':
        # loots
        # 去掉result里面的识别失败给去掉
        best_match_items_no_failed = list(best_match_items.keys())
        if "识别失败" in best_match_items_no_failed:
            best_match_items_no_failed.remove("识别失败")
        ranking_new = update_ranking(best_match_items_no_failed)
        if test_print:
            CUS_LOGGER.debug(f"获取 loots 后, 更新 ranking.json 方法, 更新后结果：{ranking_new}")
    else:
        # chests
        if test_print:
            CUS_LOGGER.debug(f"获取 chests, 不更新 ranking.json")

    # 返回识别结果
    return best_match_items




def update_dag_graph(item_list_new):
    """
    根据list中各个物品(str格式)的排序 来保存成一个json文件
    会根据本次输入, 和保存的之前的图比较, 以排序, 最终获得几乎所有物品的物品的结果表
    使用有向无环图, 保留无法区分前后的数据
    :param item_list_new 物品顺序 list 仅一维
    :return: 也就是json的格式
    {
        "ranking": ["物品1", "物品2","物品4", "物品5",...] // 去括号方便直接被调用
    }
    """

    CUS_LOGGER.debug("[有向无环图] [更新] 正在进行...")

    # 读取现 JSON Ranking 文件
    json_path = PATHS["logs"] + "\\item_ranking_dag_graph.json"
    data = ranking_read_data(json_path=json_path)

    """根据输入列表, 构造有向无环图"""
    # 继承老数据 图表 用 { x : [a,b,c] , ... } 代表多个有向边 也就是 出度
    graph = data.get('graph') if not data.get('graph') else dict()

    # seq 一组数据 例如: ["物品1", "物品2","物品4", "物品5",...]
    for i in range(len(item_list_new)):
        # 例如: "物品1"
        item_1 = item_list_new[i]
        # 首次添加 入度0
        if item_1 not in graph.keys():
            graph[item_1] = []
        # 仅两两一组进行创建边
        if i < len(item_list_new) - 1:
            item_2 = item_list_new[i + 1]
            # 首次添加 入度0
            if item_2 not in graph[item_1]:
                # 图中 item 1 -> item 2
                graph[item_1].append(item_2)
    data['graph'] = graph

    # 保存更新后的 JSON 文件
    ranking_save_data(json_path=json_path, data=data)

    return data['graph']


def ranking_read_data(json_path):
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if "ranking" in data and "ranking_easy" in data:
                return data
    return {'ranking': [], "ranking_easy": []}


def ranking_save_data(json_path, data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def build_graph(sequences):
    """根据输入列表, 构造有向无环图"""
    graph = defaultdict(list)  # 图标
    indegree = defaultdict(int)  # 入度
    nodes = set()  # 节点

    # 防止添加重复的边
    seen_relations = set()
    # seq 一组数据 例如: [["物品1"], ["物品2","物品4"], ["物品5"],...]
    for seq in sequences:
        for i in range(len(seq)):
            # 例如:  seq[i] => ["物品1"]
            for item_1 in seq[i]:
                # 首次添加 入度0
                if item_1 not in indegree:
                    indegree[item_1] = 0
                nodes.add(item_1)
                # 仅两两一组进行创建边
                if i < len(seq) - 1:
                    # 例如:  seq[i] => ["物品2","物品4"]
                    for item_2 in seq[i + 1]:
                        relation = (item_1, item_2)
                        # 防止添加重复的边
                        if relation not in seen_relations:
                            seen_relations.add(relation)
                            graph[item_1].append(item_2)
                            indegree[item_2] += 1
    return graph, indegree, nodes


def topological_sort(graph, indegree, nodes):
    # 找出所有没有传入的边的节点
    zero_indegree_queue = deque([node for node in nodes if indegree[node] == 0])
    sorted_order = []

    while zero_indegree_queue:
        # 收集所有当前零度节点
        current_level = list(zero_indegree_queue)
        zero_indegree_queue.clear()
        sorted_order.append(list(current_level))

        for node in current_level:
            # 减少每个节点的度
            for neighbor in graph[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    zero_indegree_queue.append(neighbor)

    if sum(len(level) for level in sorted_order) != len(nodes):
        CUS_LOGGER.error(
            "战利品截图发现序列中存在循环，没有有效的拓扑排序?! 看来锑食的排序过于随机了! 本次不做物品ranking更新")
        return False
    return sorted_order


def find_total_order(sequences_old, sequences_new):
    """
    构造有向无环图, 并计算新顺序
    :param sequences_old:  example: [["物品1"], ["物品3","物品4"]]
    :param sequences_new:  同上
    :return: example: [["物品1"], ["物品2"],["物品3","物品4"], ["物品5","物品7"]]
    """
    # 拼合新老数据
    sequences = [sequences_old, sequences_new]
    # 构造有向无环图
    graph, indegree, nodes = build_graph(sequences)
    # 计算新顺序
    result = topological_sort(graph, indegree, nodes)
    if result:
        return result
    else:
        # 没有有效的拓扑排序 直接返回输入旧记录...
        return sequences_old


if __name__ == '__main__':
    # Example usage:
    def main():
        sequences = [
            ['a', 'b', 'd', 'f'],
            ['a', 'c', 'e', 'f']
        ]
        for item_list in sequences:
            print(update_ranking(item_list))


    cProfile.run("main()")
