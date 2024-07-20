import base64
import datetime

import cv2
import numpy
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from function.core.QMW_1_load_settings import QMainWindowLoadSettings
from function.globals.get_paths import PATHS
from function.globals.log import CUS_LOGGER


class QMainWindowLog(QMainWindowLoadSettings):
    signal_dialog = pyqtSignal(str, str)  # 标题, 正文
    signal_print_to_ui_1 = pyqtSignal(str, str, bool)
    signal_image_to_ui_1 = pyqtSignal(numpy.ndarray)

    def __init__(self):
        # 继承父类构造方法
        super().__init__()

        # 链接防呆弹窗
        self.signal_dialog.connect(self.show_dialog)

        # 是模仿信号类写法 的 类, 并不是直接输出, 其emit方法是 一个可以输入 缺省的颜色 或 时间参数 来生成文本 调用 signal_print_to_ui_1
        self.signal_print_to_ui = self.MidSignalPrint(signal_1=self.signal_print_to_ui_1)
        # 真正的 发送信息激活 print 的函数, 被链接到直接发送信息到ui的函数
        self.signal_print_to_ui_1.connect(self.print_to_ui)

        # 类似上面, 但图片, 用于支持 输入 路径 或 numpy.ndarray
        self.signal_image_to_ui = self.MidSignalImage(signal_1=self.signal_image_to_ui_1)
        self.signal_image_to_ui_1.connect(self.image_to_ui)

        # 储存所有信号
        self.signal_dict = {
            "print_to_ui": self.signal_print_to_ui,
            "image_to_ui": self.signal_image_to_ui,
            "dialog": self.signal_dialog,
            "end": self.signal_todo_end
        }

        # 打印默认输出提示
        self.start_print()

    class MidSignalPrint:
        """
        模仿信号的类, 但其实本身完全不是信号, 是为了可以接受缺省参数而模仿的中间类,
        该类的emit方法是 一个可以输入 缺省的颜色 或 时间参数 来生成文本的方法
        并调用信号发送真正的信息
        """

        def __init__(self, signal_1):
            super().__init__()
            self.signal_1 = signal_1
            self.color_scheme = {
                1: "C80000",  # 深红色
                2: "E67800",  # 深橙色暗调
                3: "006400",  # 深绿色
                4: "009688",  # 深宝石绿
                5: "0056A6",  # 深海蓝
                6: "003153",  # 普鲁士蓝
                7: "5E2D79",  # 深兰花紫
                8: "4B0082",  # 靛蓝
                9: "333333",  # 煤黑色
            }

        def emit(self, text, color="333333", color_level=None, time=True):
            if color_level in self.color_scheme:
                color = self.color_scheme[color_level]

            # 处理缺省参数
            self.signal_1.emit(text, color, time)

    class MidSignalImage:
        """
        模仿信号的类, 但其实本身完全不是信号, 是为了可以接受缺省参数而模仿的中间类,
        该类的emit方法是 一个可以输入 numpy.ndarray 或 图片路径 并判断是否读取的方法
        并调用信号发送真正的图片
        """

        def __init__(self, signal_1):
            super().__init__()
            self.signal_1 = signal_1

        def emit(self, image):
            # 根据 路径 或者 numpy.ndarray 选择是否读取
            if type(image) is not np.ndarray:
                # 读取目标图像,中文路径兼容方案
                image_ndarray = cv2.imdecode(buf=np.fromfile(file=image, dtype=np.uint8), flags=-1)
            else:
                image_ndarray = image
            # 处理缺省参数
            self.signal_1.emit(image_ndarray)

    def start_print(self):
        """打印默认输出提示"""

        self.signal_image_to_ui.emit(image=PATHS["logo"] + "\\圆角-FetTuo-192x.png")
        self.signal_print_to_ui.emit(text="嗷呜, 欢迎使用FAA-美食大战老鼠自动放卡作战小助手~", time=False)

        self.signal_print_to_ui.emit(text="本软件 [开源][免费][绿色] 当前版本: 1.4.0", time=False)
        self.signal_print_to_ui.emit(text="", time=False)
        self.signal_print_to_ui.emit(text="使用安全说明", color_level=1, time=False)
        self.signal_print_to_ui.emit(text="[1] 务必有二级密码", time=False)
        self.signal_print_to_ui.emit(text="[2] 有一定的礼卷防翻牌异常", time=False)
        self.signal_print_to_ui.emit(text="[3] 高星或珍贵不绑卡挂拍卖/提前转移", time=False)
        self.signal_print_to_ui.emit(text="", time=False)
        self.signal_print_to_ui.emit(text="使用疑难解决", color_level=1, time=False)
        self.signal_print_to_ui.emit(text="用户请认真阅读[FAA从入门到神殿.pdf], 解决[闪退/没反应/UI缩放]等问题",
                                     color_level=2,
                                     time=False)
        self.signal_print_to_ui.emit(text="开发者和深入使用, 请参考[README.md]", time=False)
        self.signal_print_to_ui.emit(text="鼠标悬停在文字或按钮上会显示部分提示信息~", time=False)
        self.signal_print_to_ui.emit(text="任务或定时器开始运行后, 将锁定点击按钮时的配置文件, 不应用实时更改",
                                     time=False)
        self.signal_print_to_ui.emit(text="该版本的FAA会向服务器发送战利品掉落Log以做掉落统计, 不传输<任何>其他内容",
                                     time=False)
        self.signal_print_to_ui.emit(text="", time=False)
        self.signal_print_to_ui.emit(text="相关链接", color_level=1, time=False)
        self.signal_print_to_ui.emit(text="[爱发电]  https://afdian.net/a/zssy_faa ", time=False)
        self.signal_print_to_ui.emit(text="[爱发电]你们的支持是FAA持(不)续(跑)开(路)发的最大动力",
                                     time=False)
        self.signal_print_to_ui.emit(text="[Github]  https://github.com/StareAbyss/FoodsVsMiceAutoAssistant",
                                     time=False)
        self.signal_print_to_ui.emit(text="[Github]  开源不易, 为我点个Star吧! 发送Issues是最有效的问题反馈渠道",
                                     time=False)
        self.signal_print_to_ui.emit(text="[B站][UP直视深淵][宣传]  https://www.bilibili.com/video/BV1fS421N7zf",
                                     time=False)
        self.signal_print_to_ui.emit(text="[B站]  速速一键三连辣!", time=False)
        self.signal_print_to_ui.emit(text="[交流QQ群]  1群: 786921130  2群: 142272678 ", time=False)
        self.signal_print_to_ui.emit(text="[交流QQ群]  欢迎加入交流讨论游戏相关和自动化相关问题 & 获取使用帮助",
                                     time=False)

    # 用于展示弹窗信息的方法
    @QtCore.pyqtSlot(str, str)
    def show_dialog(self, title, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.exec_()

    def print_to_ui(self, text, color, time):
        """打印文本到输出框 """
        # 时间文本
        text_time = "[{}] ".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if time else ""
        # 颜色文本
        text_all = f'<span style="color:#{color};">{text_time}{text}</span>'
        # 输出到输出框
        self.TextBrowser.append(text_all)
        # 实时输出
        self.TextBrowser.moveCursor(self.TextBrowser.textCursor().End)
        QtWidgets.QApplication.processEvents()
        # 输出到日志和运行框
        CUS_LOGGER.info(text)

    def image_to_ui(self, image_ndarray: numpy.ndarray):
        """
        :param image_ndarray: 必须是 numpy.ndarray 对象
        :return:
        """

        # 編碼字節流
        _, img_encoded = cv2.imencode('.png', image_ndarray)

        # base64
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        image_html = f"<img src='data:image/png;base64,{img_base64}'>"

        # self.TextBrowser.insertHtml(image_html)

        # 输出到输出框
        self.TextBrowser.append(image_html)
        # 实时输出
        self.TextBrowser.moveCursor(self.TextBrowser.textCursor().End)
        QtWidgets.QApplication.processEvents()
