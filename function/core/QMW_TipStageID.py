from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QTableWidget, QVBoxLayout, QWidget


class QMWTipStageID(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("关卡代号一览 格式: 字母字母-数字-数字")
        # 设置窗口大小
        self.setMinimumSize(900, 610)
        self.setMaximumSize(900, 610)
        self.initUI()

    def initUI(self):

        table = QTableWidget()
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置为不可编辑
        table.verticalHeader().setVisible(False)  # 隐藏行号
        table.horizontalHeader().setVisible(False)  # 隐藏列号
        table.setSelectionMode(QTableWidget.NoSelection)  # 禁用选择功能

        # 定义表头和对应的数据
        data_dict = {
            "美味岛": [
                ["曲奇岛", "NO-1-1"],
                ["色拉岛-陆", "NO-1-2"],
                ["色拉岛-水", "NO-1-3"],
                ["慕斯岛", "NO-1-4"],
                ["香槟岛-陆", "NO-1-5"],
                ["香槟岛-水", "NO-1-6"],
                ["神殿", "NO-1-7"],
                ["布丁岛-日", "NO-1-8"],
                ["布丁岛-夜", "NO-1-9"],
                ["可可岛-日", "NO-1-10"],
                ["可可岛-夜", "NO-1-11"],
                ["咖喱岛-日", "NO-1-12"],
                ["咖喱岛-夜", "NO-1-13"],
                ["深渊", "NO-1-14"],
                ["美味漫游", "NO-1-15"]
            ],
            "火山岛": [
                ["芥末小屋-日", "NO-2-1"],
                ["芥末小屋-夜", "NO-2-2"],
                ["薄荷海滩-日", "NO-2-3"],
                ["薄荷海滩-夜", "NO-2-4"],
                ["芝士城堡", "NO-2-5"],
                ["炭烧雨林-日", "NO-2-6"],
                ["炭烧雨林-夜", "NO-2-7"],
                ["抹茶庄园-日", "NO-2-8"],
                ["抹茶庄园-夜", "NO-2-9"],
                ["玛奇朵港", "NO-2-10"],
                ["棉花糖天空-日", "NO-2-11"],
                ["棉花糖天空-夜", "NO-2-12"],
                ["果酱部落-日", "NO-2-13"],
                ["果酱部落-夜", "NO-2-14"],
                ["雪顶火山", "NO-2-15"],
                ["火山漫游", "NO-2-16"],
                ["勇士挑战-最高难", "NO-2-17"]
            ],
            "火山遗迹": [
                ["果仁瀑布", "NO-3-1"],
                ["榛子瀑布", "NO-3-2"],
                ["黑提丛林", "NO-3-3"],
                ["蓝莓丛林", "NO-3-4"],
                ["奶昔基地", "NO-3-5"],
                ["圣代基地", "NO-3-6"]
            ],
            "浮空岛": [
                ["茴香竹筏-日", "NO-4-1"],
                ["茴香竹筏-夜", "NO-4-2"],
                ["孜然断桥-日", "NO-4-3"],
                ["孜然断桥-夜", "NO-4-4"],
                ["卤料花园", "NO-4-5"],
                ["月桂天空-日", "NO-4-6"],
                ["月桂天空-夜", "NO-4-7"],
                ["香叶空港-日", "NO-4-8"],
                ["香叶空港-夜", "NO-4-9"],
                ["香料飞船", "NO-4-10"],
                ["花椒浮岛-日", "NO-4-11"],
                ["花椒浮岛-夜", "NO-4-12"],
                ["丁香彩虹-日", "NO-4-13"],
                ["丁香彩虹-夜", "NO-4-14"],
                ["十三香中心岛", "NO-4-15"],
                ["浮空漫游", "NO-4-16"],
            ],
            "海底旋涡": [
                ["金枪鱼洋流", "NO-5-1"],
                ["珊瑚洋流-日", "NO-5-2"],
                ["珊瑚洋流-夜", "NO-5-3"],
                ["北极贝湍流", "NO-5-4"],
                ["海葵洋流-日", "NO-5-5"],
                ["海葵洋流-夜", "NO-5-6"],
                ["天妇罗旋涡", "NO-5-7"]
            ],
            "星际穿越": [
                ["糖球空间站-日", "NO-6-1"],
                ["糖球空间站-夜", "NO-6-2"],
                ["苏打水星-日", "NO-6-3"],
                ["苏打水星-夜", "NO-6-4"],
                ["汉堡王星", "NO-6-5"],
                ["巴旦木星-日", "NO-6-6"],
                ["巴旦木星-夜", "NO-6-7"],
                ["冷萃星环-日", "NO-6-8"],
                ["冷萃星环-夜", "NO-6-9"],
                ["多拿滋星云", "NO-6-10"]
            ],
            "番外 / 跨服 ": [
                ["番外-营地", "EX-1-? (1-6)"],
                ["番外-沙漠", "EX-2-? (1-9)"],
                ["番外-雪山", "EX-3-? (1-5)"],
                ["番外-雷城", "EX-4-? (1-6)"],
                ["番外-奇境", "EX-5-? (1-8)"],
                ["跨服-城堡", "CS-1-? (1-8)"],
                ["跨服-天空", "CS-2-? (1-8)"],
                ["跨服-炼狱", "CS-3-? (1-8)"],
                ["跨服-水火", "CS-4-? (1-8)"],
                ["跨服-巫毒", "CS-5-? (1-8)"],
                ["跨服-冰跨", "CS-6-? (1-8)"],
            ],
            "魔塔 / 其他": [
                ["魔塔-单人", "MT-1-? (1-165)"],
                ["魔塔-双人", "MT-2-? (1-100)"],
                ["魔塔-密室", "MT-3-? (1-4)"],
                ["萌宠神殿", "PT-0-? (1-25)"],
                ["悬赏关卡", "OR-0-? (1-3)"],
                ["欢乐假期", "HH-0-0"],
                ["画龙点睛", "不支持"],
            ]
        }

        # 设置表头
        table_headers = list(data_dict.keys())

        # 表格初始化
        table.setRowCount(max([len(values) for values in data_dict.values()]) + 1)  # 表高
        table.setColumnCount(len(table_headers) * 2)  # 表宽

        # 列宽
        for column in range(table.columnCount()):
            if column % 2 == 0:  # 判断是否为偶数列
                table.setColumnWidth(column, 100)  # 设置偶数列的宽度
            else:  # 奇数列
                table.setColumnWidth(column, 85)  # 设置奇数列的宽度

        # 设置表头
        for index, header_text in enumerate(table_headers):
            span = 2  # 每个表头默认合并两列
            start_col = index * 2
            table.setSpan(0, start_col, 1, span)
            table.setItem(0, start_col, QTableWidgetItem(header_text))

        # 填充表格内容
        row = 1
        for col_index, header in enumerate(table_headers):
            for item1, item2 in data_dict[header]:
                table.setItem(row, col_index * 2, QTableWidgetItem(item1))
                table.setItem(row, col_index * 2 + 1, QTableWidgetItem(item2))
                row += 1
            row = 1  # 重置行号以填充下一个表头的内容


        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(table)

        # 设置主控件
        main_widget = QWidget()
        main_widget.setLayout(layout)

        # 将 控件注册 为 窗口主控件
        self.setCentralWidget(main_widget)
