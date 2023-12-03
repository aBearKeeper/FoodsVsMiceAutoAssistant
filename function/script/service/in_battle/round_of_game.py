from time import sleep

from function.common.bg_mouse import mouse_left_click
from function.common.bg_p_compare import loop_find_p_in_w, loop_find_ps_in_w, find_ps_in_w
from function.tools.screen_loot_logs import screen_loot_logs


# 从FAA类中直接获取
def round_of_game(handle, zoom, paths, player, stage_info_id, action_battle_normal,
                  deck: int, delay_start: bool, battle_mode: int, task_card: str, list_ban_card: list):
    """
    一轮战斗
    Args:
        :param handle: 来自FAA类 variable
        :param zoom: 来自FAA类 variable
        :param paths: 来自FAA类 variable
        :param player: 来自FAA类 variable
        :param stage_info_id: 来自FAA类 variable
        :param action_battle_normal: 来自FAA类 function
        :param delay_start: 是房主 房主要晚一点点开始
        :param battle_mode: 战斗模式 0 cd模式 或 1遍历模式
        :param task_card: 任务要求卡片的序号。默认0即为没有。
        :param list_ban_card: ban卡列表
        :param deck: 卡组序号(1-6)
    """

    # 对齐线程
    sleep(0.3)

    # 刷新ui: 状态文本
    print("[{}] 寻找开始或准备按钮".format(player))

    # 循环查找开始按键
    my_path = paths["picture"]["common"] + "\\battle\\before_ready_check_start.png"
    if not loop_find_p_in_w(raw_w_handle=handle,
                            raw_range=[0, 0, 950, 600],
                            target_path=my_path,
                            click_zoom=zoom,
                            target_interval=1,
                            target_sleep=0.3,
                            click=False,
                            target_failed_check=10):
        print("[{}] 找不到开始游戏! 创建房间可能失败!".format(player))

    # 房主延时
    if delay_start:
        sleep(0.5)
    # 选择卡组
    print("[{}] 选择卡组".format(player))
    mouse_left_click(handle=handle,
                     x=int({1: 425, 2: 523, 3: 588, 4: 666, 5: 756, 6: 837}[deck] * zoom),
                     y=int(121 * zoom),
                     sleep_time=0.5)

    """开始寻找并添加任务所需卡片"""
    # 由于公会任务的卡组特性, 当任务卡为[气泡]时, 不需要额外选择带卡.
    if task_card == "None" or task_card == "气泡-0":
        print("[{}] 不需要额外带卡,跳过".format(player))
    else:
        # 房主晚点开始
        if delay_start:
            sleep(6)
        print("[{}] 开始寻找任务卡".format(player))
        # 复位滑块
        mouse_left_click(handle=handle, x=int(931 * zoom), y=int(209 * zoom), sleep_time=0.25)
        flag_find_task_card = False
        for i in range(7):
            # 找到就点一下
            if not flag_find_task_card:
                find = loop_find_p_in_w(
                    raw_w_handle=handle,
                    raw_range=[0, 0, 950, 600],
                    target_path=paths["picture"]["card"] + "\\" + task_card + ".png",
                    target_tolerance=0.95,
                    click_zoom=zoom,
                    click=True,
                    target_failed_check=1)
                if find:
                    flag_find_task_card = True
            # 滑块向下移动3次
            for j in range(3):
                mouse_left_click(handle=handle, x=int(931 * zoom), y=int(400 * zoom), sleep_time=0.05)
        # 双方都完成循环 以保证同步
        print("[{}] 完成任务卡查找 大概.?".format(player))

    # 房主延时
    if delay_start:
        sleep(0.5)
    # 点击开始
    find = loop_find_p_in_w(
        raw_w_handle=handle,
        raw_range=[0, 0, 950, 600],
        target_path=paths["picture"]["common"] + "\\battle\\before_ready_check_start.png",
        click_zoom=zoom,
        target_interval=1,
        target_sleep=0.3,
        click=True,
        target_failed_check=10)
    if not find:
        print("[{}] 10s找不到[开始/准备]字样! 创建房间可能失败!".format(player))

    # 防止被没有带xx卡卡住
    # my_path = paths["picture"]["common"] + "\\battle\\before_no_mat_card_enter.png"
    # if find_p_in_w(handle=handle, target_path=my_path):
    #     mouse_left_click(handle, int(427 * zoom), int(353 * zoom))

    # 刷新ui: 状态文本
    print("[{}] 查找火苗标识物, 等待进入战斗".format(player))

    # 循环查找火苗图标 找到战斗开始
    loop_find_p_in_w(
        raw_w_handle=handle,
        raw_range=[0, 0, 950, 600],
        target_path=paths["picture"]["common"] + "\\battle\\fire_element.png",
        click_zoom=zoom,
        target_interval=1,
        target_sleep=1,
        click=False,
        target_failed_check=86400)

    # 刷新ui: 状态文本
    print("[{}] 找到火苗标识物, 战斗进行中...".format(player))
    sleep(1)

    # 房主晚点放下人物
    if delay_start:
        sleep(0.5)

    # 战斗循环
    action_battle_normal(battle_mode=battle_mode, task_card=task_card, list_ban_card=list_ban_card)

    print("[{}] 识别到五种战斗结束标志之一, 进行收尾工作".format(player))
    """战斗结束后, 一般流程为 (潜在的任务完成黑屏) -> 战利品 -> 战斗结算 -> 翻宝箱, 之后会回到房间, 魔塔会回到其他界面"""

    """战利品部分"""
    find = find_ps_in_w(
        raw_w_handle=handle,
        raw_range=[0, 0, 950, 600],
        target_opts=[{"target_path": paths["picture"]["common"] + "\\battle\\end_1_loot.png",
                      "target_tolerance": 0.999},
                     {"target_path": paths["picture"]["common"] + "\\battle\\end_2_loot.png",
                      "target_tolerance": 0.999}],
        return_mode="or")
    if find:
        print("[{}] [Safe] [战利品UI] 正常结束, 尝试捕获战利品截图".format(player))
        screen_loot_logs(handle=handle, zoom=zoom, save_log_path=paths["logs"], stage_id=stage_info_id, player=player)
    else:
        print("[{}] [Safe] [非战利品UI] 正常结束, 可能由于延迟未能捕获战利品, 继续流程".format(player))

    """战斗结算部分, 等待跳过就好了"""

    """翻宝箱部分, 循环查找, 确认是否可以安全翻牌"""
    find = loop_find_p_in_w(
        raw_w_handle=handle,
        raw_range=[0, 0, 950, 600],
        target_path=paths["picture"]["common"] + "\\battle\\end_4_chest.png",
        target_failed_check=15,
        target_sleep=2,
        click=False,
        click_zoom=zoom
    )
    if find:
        # 刷新ui: 状态文本
        print("[{}] [Safe] [翻宝箱UI] 捕获到正确标志, 翻牌中...".format(player))
        # 开始翻牌
        sleep(1.5)
        mouse_left_click(handle=handle, x=int(708 * zoom), y=int(502 * zoom), interval_time=0.05, sleep_time=6)
        # 翻牌 1+2
        mouse_left_click(handle=handle, x=int(550 * zoom), y=int(170 * zoom), interval_time=0.05, sleep_time=0.5)
        mouse_left_click(handle=handle, x=int(708 * zoom), y=int(170 * zoom), interval_time=0.05, sleep_time=0.5)
        # 结束翻牌
        mouse_left_click(handle=handle, x=int(708 * zoom), y=int(502 * zoom), interval_time=0.05, sleep_time=0.5)
    else:
        print("=" * 50)
        print("[{}] [Warning] [翻宝箱UI] 15s未能捕获正确标志, 出问题了!".format(player))
        print("=" * 50)

    # 查找战斗结束 来兜底正确完成了战斗
    print("[{}] [Safe] [开始/准备/魔塔蛋糕UI] 尝试捕获正确标志, 以完成战斗流程.".format(player))

    find = loop_find_ps_in_w(raw_w_handle=handle,
                             raw_range=[0, 0, 950, 600],
                             target_opts=[
                                 {"target_path": paths["picture"]["common"] + "\\battle\\before_ready_check_start.png",
                                  "target_tolerance": 0.99},
                                 {"target_path": paths["picture"]["common"] + "\\mage_tower_ui.png",
                                  "target_tolerance": 0.99}],
                             target_return_mode="or",
                             target_failed_check=10,
                             target_interval=0.2)

    if find:
        print("[{}] [Safe] 成功捕获[开始/准备/魔塔蛋糕UI], 完成战斗流程.".format(player))
        sleep(3)
    else:
        print("=" * 50)
        print("[{}] [Error] 10s没能捕获[开始/准备/魔塔蛋糕UI], 超长时间sleep, 请关闭脚本!!!".format(player))
        print("=" * 50)
        sleep(999999)

    # 休息7s 来让线程对齐 防止未知bug
    sleep(7)
