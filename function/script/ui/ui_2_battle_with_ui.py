import json
import sys
from time import sleep

from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt5.QtWidgets import QApplication

from function.common.thread_with_exception import ThreadWithException
from function.script.scattered.get_channel_name import get_channel_name
from function.script.service.common import FAA
from function.script.service.common_multiplayer import invite
from function.script.ui.ui_1_load_opt import MyMainWindow1


class Todo(QThread):
    # 初始化向外发射信号
    sin_out = pyqtSignal(str)
    sin_out_completed = pyqtSignal()

    def __init__(self, faa, opt):
        super().__init__()
        # 用于暂停恢复
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.is_paused = False
        # 功能需要
        self.faa = faa
        self.opt = opt
        self.thread_1p = None
        self.thread_2p = None

    def reload_game(self):
        self.sin_out.emit("Refresh Game...")
        # 创建进程 -> 开始进程 -> 阻塞主进程
        self.thread_1p = ThreadWithException(target=self.faa[1].reload_game,
                                             name="1P Thread - Reload",
                                             kwargs={})

        self.thread_2p = ThreadWithException(target=self.faa[2].reload_game,
                                             name="2P Thread - Reload",
                                             kwargs={})
        # 涉及键盘抢夺, 容错低, 最好分开执行
        self.thread_1p.start()
        self.thread_1p.join()
        self.thread_2p.start()
        self.thread_2p.join()

    def compete_quest(self):
        self.sin_out.emit("Compete Quest...")
        # 创建进程 -> 开始进程 -> 阻塞主进程
        self.thread_1p = ThreadWithException(target=self.faa[1].quest,
                                             name="1P Thread - Quest",
                                             kwargs={})

        self.thread_2p = ThreadWithException(target=self.faa[2].quest,
                                             name="2P Thread - Quest",
                                             kwargs={})
        # 涉及键盘抢夺, 容错低, 最好分开执行
        self.thread_1p.start()
        sleep(0.333)
        self.thread_2p.start()
        self.thread_1p.join()
        self.thread_2p.join()

    def n_battle(self, is_group,
                 stage_id, max_times,
                 deck, battle_plan_1p, battle_plan_2p,
                 task_card, list_ban_card, dict_exit):
        """[单本轮战]1次 副本外 → 副本内n次战斗 → 副本外"""

        self.sin_out.emit("[单本轮战]目标副本:{}".format(stage_id))

        # 填入战斗方案和关卡信息
        self.faa[1].get_config_for_battle(is_group=is_group, battle_plan_index=battle_plan_1p, stage_id=stage_id)
        if is_group:
            self.faa[2].get_config_for_battle(is_group=is_group, battle_plan_index=battle_plan_2p, stage_id=stage_id)

        # 检查人物等级 不组队检查1P 组队还额外检查2P
        if not self.faa[1].check_level():
            self.sin_out.emit("[单本轮战]1P等级不足, 跳过")
            return False
        if is_group:
            if not self.faa[2].check_level():
                self.sin_out.emit("[单本轮战]2P等级不足, 跳过")
                return False

        if not is_group:
            # 单人前往副本
            self.faa[1].action_goto_stage(room_creator=True)
        else:
            # 多人前往副本
            while True:
                self.faa[1].action_goto_stage(room_creator=False)
                self.faa[2].action_goto_stage(room_creator=True)
                sleep(3)
                if invite(self.faa[2], self.faa[1]):
                    break
                else:
                    self.sin_out.emit("[单本轮战]服务器抽风,进入竞技岛,重新邀请...")
                    self.faa[1].action_exit(exit_mode=3)
                    self.faa[2].action_exit(exit_mode=3)

        # 轮次作战
        for i in range(max_times):
            self.sin_out.emit("[单本轮战]第{}次,开始".format(i + 1))

            # 创建战斗进程 -> 开始进程
            self.thread_1p = ThreadWithException(target=self.faa[1].action_round_of_game,
                                                 name="1P Thread",
                                                 kwargs={
                                                     "delay_start": False,
                                                     "battle_mode": 0,
                                                     "task_card": task_card,
                                                     "list_ban_card": list_ban_card,
                                                     "deck": deck
                                                 })
            if is_group:
                self.thread_2p = ThreadWithException(target=self.faa[2].action_round_of_game,
                                                     name="2P Thread",
                                                     kwargs={
                                                         "delay_start": True,
                                                         "battle_mode": 0,
                                                         "task_card": task_card,
                                                         "list_ban_card": list_ban_card,
                                                         "deck": deck
                                                     })
            print("=" * 50)

            self.thread_1p.start()
            if is_group:
                self.thread_2p.start()

            # 阻塞进程让进程执行完再继续本循环函数
            self.thread_1p.join()
            if is_group:
                self.thread_2p.join()

            print("=" * 50)

            # 最后一次的退出方式不同
            if i + 1 == max_times:
                for j in dict_exit["last_time"]:
                    self.faa[1].action_exit(exit_mode=j)
                    if is_group:
                        self.faa[2].action_exit(exit_mode=j)
            else:
                for j in dict_exit["other_time"]:
                    self.faa[1].action_exit(exit_mode=j)
                    if is_group:
                        self.faa[2].action_exit(exit_mode=j)

            print("[单本轮战] 第{}次, 结束\n".format(i + 1))
            self.sin_out.emit("[单本轮战] 第{}次, 结束\n".format(i + 1))

    def n_n_battle(self, task_list, list_type):
        """
        [多本战斗]n次 副本外→副本内n次战斗→副本外
        :param task_list: 任务清单
        :param list_type: 打哪些类型的副本 比如 ["NO","CS"]
        """
        # 遍历完成每一个任务
        for i in range(len(task_list)):
            task = task_list[i]
            # 判断不打的任务
            if task["stage_id"].split("-")[0] in list_type:
                self.sin_out.emit(
                    "[多本轮战]任务{},组队:{},目标地点:{},次数:{},额外带卡:{},Ban卡:{}".format(
                        i + 1,
                        "是" if task["battle_plan_2p"] else "否",
                        task["stage_id"],
                        task["max_times"],
                        task["task_card"],
                        task["list_ban_card"]))

                self.n_battle(
                    stage_id=task["stage_id"],
                    max_times=task["max_times"],
                    deck=task["deck"],
                    is_group=task["is_group"],
                    battle_plan_1p=task["battle_plan_1p"],
                    battle_plan_2p=task["battle_plan_2p"],
                    task_card=task["task_card"],
                    list_ban_card=task["list_ban_card"],
                    dict_exit=task["dict_exit"])
            else:
                self.sin_out.emit(
                    "[多本轮战]任务{},组队:{},目标地点:{},次数:{},额外带卡:{},Ban卡:{},不打的地图类型,skip\n".format(
                        i + 1,
                        "是" if task["battle_plan_2p"] else "否",
                        task["stage_id"],
                        task["max_times"],
                        task["task_card"],
                        task["list_ban_card"]))
                continue

    def double_task(self, text_, task_type, deck, battle_plan_1p, battle_plan_2p):
        """完成公会or情侣任务"""

        self.sin_out.emit("{}Link Start!\n".format(text_))

        self.sin_out.emit("{}检查领取奖励中...\n".format(text_))
        self.faa[1].action_task_receive_rewards(task_type=task_type)
        self.faa[2].action_task_receive_rewards(task_type=task_type)

        self.sin_out.emit("{}开始获取任务列表".format(text_))
        task_list = self.faa[1].action_get_task(target=task_type)

        for i in task_list:
            self.sin_out.emit("副本:{},额外带卡:{}".format(i["stage_id"], i["task_card"]))

        for i in range(len(task_list)):
            task_list[i]["deck"] = deck
            task_list[i]["battle_plan_1p"] = battle_plan_1p
            task_list[i]["battle_plan_2p"] = battle_plan_2p

        self.sin_out.emit("{}已取得任务,开始[多本轮战]...".format(text_))
        self.n_n_battle(task_list=task_list, list_type=["NO"])

        self.sin_out.emit("{}检查领取奖励中...\n".format(text_))
        self.faa[1].action_task_receive_rewards(task_type=task_type)
        self.faa[2].action_task_receive_rewards(task_type=task_type)

        self.sin_out.emit("{}Completed!\n".format(text_))

    def double_offer_reward(self, text_, deck, battle_plan_1p, battle_plan_2p):
        self.sin_out.emit("{}Link Start!\n".format(text_))
        # 战斗开始
        self.sin_out.emit("{}开始[多本轮战]...".format(text_))
        task_list = [
            {
                "deck": deck,
                "is_group": True,
                "battle_plan_1p": battle_plan_1p,
                "battle_plan_2p": battle_plan_2p,
                "stage_id": "OR-1-0",
                "max_times": 1,
                "task_card": "None",
                "list_ban_card": [],
                "dict_exit": {"other_time": [0], "last_time": [3]}
            }, {
                "deck": deck,
                "is_group": True,
                "battle_plan_1p": battle_plan_1p,
                "battle_plan_2p": battle_plan_2p,
                "stage_id": "OR-2-0",
                "max_times": 1,
                "task_card": "None",
                "list_ban_card": [],
                "dict_exit": {"other_time": [0], "last_time": [3]}
            }, {
                "deck": deck,
                "is_group": True,
                "battle_plan_1p": battle_plan_1p,
                "battle_plan_2p": battle_plan_2p,
                "stage_id": "OR-3-0",
                "max_times": 1,
                "task_card": "None",
                "list_ban_card": [],
                "dict_exit": {"other_time": [0], "last_time": [3]}
            }]
        self.n_n_battle(task_list=task_list, list_type=["OR"])
        # 领取奖励
        self.faa[1].action_task_receive_rewards(task_type="offer_reward")
        self.faa[2].action_task_receive_rewards(task_type="offer_reward")
        # 战斗结束
        self.sin_out.emit("{}Completed!\n".format(text_))

    def double_magic_tower(self, text_, floor, max_times, deck, battle_plan_1p, battle_plan_2p):
        self.sin_out.emit("{} Link Start!\n".format(text_))

        # 填入战斗方案和关卡信息
        stage_id = "MT-2-" + str(floor)
        self.faa[1].get_config_for_battle(is_group=True, battle_plan_index=battle_plan_1p, stage_id=stage_id)
        self.faa[2].get_config_for_battle(is_group=True, battle_plan_index=battle_plan_2p, stage_id=stage_id)

        # 轮次作战
        for i in range(max_times):
            self.sin_out.emit("{} 第{}次, 开始".format(text_, i + 1))
            flag_invite_failed = False

            # 前往副本
            while True:
                # 第一次 或 邀请失败后 进入方式不同
                if i == 0 or flag_invite_failed:
                    self.faa[1].action_goto_stage(room_creator=False, mt_first_time=True)
                    self.faa[2].action_goto_stage(room_creator=True, mt_first_time=True)
                else:
                    self.faa[2].action_goto_stage(room_creator=True)

                sleep(3)
                # 尝试要求 如果成功就结束循环 如果失败 退出到竞技岛尝试重新邀请
                if invite(self.faa[2], self.faa[1]):
                    break
                else:
                    flag_invite_failed = True
                    self.sin_out.emit("服务器抽风, 尝试进入竞技岛, 并重新进行邀请...")
                    self.faa[2].action_exit(exit_mode=3)
                    self.faa[1].action_exit(exit_mode=3)

            # 创建战斗进程 -> 开始进程 -> 阻塞进程让进程执行完再继续本循环函数
            self.thread_1p = ThreadWithException(target=self.faa[1].action_round_of_game,
                                                 name="1P Thread",
                                                 kwargs={
                                                     "delay_start": False,
                                                     "battle_mode": 0,
                                                     "task_card": "None",
                                                     "list_ban_card": [],
                                                     "deck": deck
                                                 })

            self.thread_2p = ThreadWithException(target=self.faa[2].action_round_of_game,
                                                 name="2P Thread",
                                                 kwargs={
                                                     "delay_start": True,
                                                     "battle_mode": 0,
                                                     "task_card": "None",
                                                     "list_ban_card": [],
                                                     "deck": deck
                                                 })
            self.thread_1p.start()
            self.thread_2p.start()
            self.thread_1p.join()
            self.thread_2p.join()

            # 打完出本
            if i + 1 == max_times:
                # 最后一把
                self.faa[1].action_exit(exit_mode=1)
                self.faa[2].action_exit(exit_mode=2)
            else:
                # 其他次数
                self.faa[1].action_exit(exit_mode=1)
                self.faa[2].action_exit(exit_mode=0)

            self.sin_out.emit("{} 第{}次, 结束\n".format(text_, i + 1))

        self.sin_out.emit("{} Completed!\n".format(text_))

    def alone_magic_tower(self, text_, player_id, floor, max_times, deck, battle_plan_1p):
        self.sin_out.emit("{} Link Start!\n".format(text_))

        stage_id = "MT-1-" + str(floor)
        self.faa[player_id].get_config_for_battle(is_group=False, battle_plan_index=battle_plan_1p, stage_id=stage_id)

        # 轮次作战
        for count_times in range(max_times):

            self.sin_out.emit("{} 第{}次, 开始".format(text_, count_times + 1))

            # 第一次的进入方式不同
            if count_times == 0:
                self.faa[player_id].action_goto_stage(room_creator=True, mt_first_time=True)
            else:
                self.faa[player_id].action_goto_stage(room_creator=True)

            # 创建战斗进程 -> 开始进程 -> 阻塞进程让进程执行完再继续本循环函数
            self.thread_1p = ThreadWithException(target=self.faa[player_id].action_round_of_game,
                                                 name="{}P Thread".format(player_id),
                                                 kwargs={
                                                     "deck": deck,
                                                     "delay_start": False,
                                                     "battle_mode": 0,
                                                     "task_card": "None",
                                                     "list_ban_card": []
                                                 })
            self.thread_1p.start()
            self.thread_1p.join()

            # 最后一次的退出方式不同
            if count_times + 1 == max_times:
                self.faa[player_id].action_exit(exit_mode=2)
            else:
                self.faa[player_id].action_exit(exit_mode=0)

            self.sin_out.emit("{} 第{}次, 结束\n".format(text_, count_times + 1))

        self.sin_out.emit("{} Completed!\n".format(text_))

    def alone_magic_tower_prison(self, text_, player_id, sutra_pavilion, deck, battle_plan_1p):

        self.sin_out.emit("{} Link Start!\n".format(text_))

        if sutra_pavilion:
            stage_list = ["MT-3-1", "MT-3-2", "MT-3-3", "MT-3-4"]
        else:
            stage_list = ["MT-3-1", "MT-3-3", "MT-3-4"]

        # 轮次作战
        for stage_id in stage_list:

            self.faa[player_id].get_config_for_battle(is_group=False, battle_plan_index=battle_plan_1p,
                                                      stage_id=stage_id)

            # 第一次的进入方式不同
            if stage_id == "MT-3-1":
                self.faa[player_id].action_goto_stage(room_creator=True, mt_first_time=True)
            else:
                self.faa[player_id].action_goto_stage(room_creator=True)

            self.sin_out.emit("{} 开始关卡:{}".format(text_, stage_id))

            # 创建战斗进程 -> 开始进程 -> 阻塞进程让进程执行完再继续本循环函数
            self.thread_1p = ThreadWithException(target=self.faa[player_id].action_round_of_game,
                                                 name="{}P Thread".format(player_id),
                                                 kwargs={
                                                     "deck": deck,
                                                     "delay_start": False,
                                                     "battle_mode": 0,
                                                     "task_card": "None",
                                                     "list_ban_card": []
                                                 })
            self.thread_1p.start()
            self.thread_1p.join()

            self.sin_out.emit("{}  战斗结束:{}".format(text_, stage_id))

            # 最后一次的退出方式不同
            if stage_id == "MT-3-4":
                self.faa[player_id].action_exit(exit_mode=2)
            else:
                self.faa[player_id].action_exit(exit_mode=0)

        self.sin_out.emit("{} Completed!\n".format(text_))

    def cross_server(self, text_, is_group, stage_id, max_times, deck, battle_plan_1p, battle_plan_2p):
        self.sin_out.emit("{} Link Start!\n".format(text_))

        # 填入战斗方案和关卡信息
        self.faa[1].get_config_for_battle(is_group=True, battle_plan_index=battle_plan_1p, stage_id=stage_id)
        if is_group:
            self.faa[2].get_config_for_battle(is_group=True, battle_plan_index=battle_plan_2p, stage_id=stage_id)

        self.faa[1].action_goto_stage(room_creator=True)
        if is_group:
            self.faa[2].action_goto_stage(room_creator=False)

        sleep(3)

        # 轮次作战
        for i in range(max_times):
            self.sin_out.emit("{} 第{}次, 开始".format(text_, i + 1))
            # 创建战斗进程 -> 开始进程 -> 阻塞进程让进程执行完再继续本循环函数
            self.thread_1p = ThreadWithException(target=self.faa[1].action_round_of_game,
                                                 name="1P Thread",
                                                 kwargs={"delay_start": True,
                                                         "battle_mode": 0,
                                                         "task_card": "None",
                                                         "list_ban_card": [],
                                                         "deck": deck
                                                         })
            if is_group:
                self.thread_2p = ThreadWithException(target=self.faa[2].action_round_of_game,
                                                     name="2P Thread",
                                                     kwargs={
                                                         "delay_start": False,
                                                         "battle_mode": 0,
                                                         "task_card": "None",
                                                         "list_ban_card": [],
                                                         "deck": deck
                                                     })
            self.thread_1p.start()
            if is_group:
                self.thread_2p.start()
            self.thread_1p.join()
            if is_group:
                self.thread_2p.join()

            # 打完出本
            if i + 1 == max_times:
                # 最后一把 打完回竞技岛
                self.faa[1].action_exit(exit_mode=3)
                if is_group:
                    self.faa[2].action_exit(exit_mode=3)
            else:
                # 其他次数 打完按兵不动
                self.faa[1].action_exit(exit_mode=0)
                if is_group:
                    self.faa[2].action_exit(exit_mode=0)

            self.sin_out.emit("{} 第{}次, 结束\n".format(text_, i + 1))

        self.sin_out.emit("{} Completed!\n".format(text_))

    def easy_battle(self, text_, stage_id, max_times, deck, is_group, battle_plan_1p, battle_plan_2p, dict_exit):
        """仅调用 n_battle"""
        # 战斗开始
        self.sin_out.emit("{} Link Start!\n".format(text_))
        # 战斗开始
        self.sin_out.emit("{}开始[多本轮战]...".format(text_))
        task_list = [
            {
                "stage_id": stage_id,
                "max_times": max_times,
                "deck": deck,
                "is_group": is_group,
                "battle_plan_1p": battle_plan_1p,
                "battle_plan_2p": battle_plan_2p,
                "task_card": "None",
                "list_ban_card": [],
                "dict_exit": dict_exit
            }]
        self.n_n_battle(task_list=task_list, list_type=["NO", "OR", "CS", "EX"])
        # 战斗结束
        self.sin_out.emit("{} Completed!\n".format(text_))

    def customize_battle(self, text_: str):
        # 开始链接
        self.sin_out.emit("{} Link Start!\n".format(text_))
        # 战斗开始
        self.sin_out.emit("{}开始[多本轮战]...".format(text_))

        with open(self.faa[1].paths["config"] + "//opt_customize_todo.json", "r", encoding="UTF-8") as file:
            task_list = json.load(file)

        self.n_n_battle(task_list=task_list, list_type=["NO"])

        # 战斗结束
        self.sin_out.emit("{} Completed!\n".format(text_))

    def run(self):
        """覆写主方法"""
        # 签到!
        self.sin_out.emit("每一个大类的任务开始前均会重启游戏以防止bug...")

        my_opt = self.opt["reload_and_daily_tasks"]
        if my_opt["active"]:
            self.reload_game()
            self.sin_out.emit("每日签到检查中...")
            self.faa[1].sign_in()
            self.faa[2].sign_in()

        my_opt = self.opt["normal_battle"]
        if my_opt["active"]:
            self.easy_battle(text_="[常规刷本]",
                             stage_id=my_opt["stage"],
                             max_times=int(my_opt["max_times"]),
                             deck=my_opt["deck"],
                             is_group=my_opt["is_group"],
                             battle_plan_1p=my_opt["battle_plan_1p"],
                             battle_plan_2p=my_opt["battle_plan_2p"],
                             dict_exit={"other_time": [0], "last_time": [3]})

        if (
                self.opt["guild_task"]["active"] or
                self.opt["spouse_task"]["active"] or
                self.opt["offer_reward"]["active"]
        ):
            self.reload_game()

        my_opt = self.opt["guild_task"]
        if my_opt["active"]:
            self.double_task(text_="[公会任务]",
                             task_type="guild",
                             deck=my_opt["deck"],
                             battle_plan_1p=my_opt["battle_plan_1p"],
                             battle_plan_2p=my_opt["battle_plan_2p"])

        my_opt = self.opt["spouse_task"]
        if my_opt["active"]:
            self.double_task(text_="[情侣任务]",
                             task_type="spouse",
                             deck=my_opt["deck"],
                             battle_plan_1p=my_opt["battle_plan_1p"],
                             battle_plan_2p=my_opt["battle_plan_2p"])

        my_opt = self.opt["offer_reward"]
        if my_opt["active"]:
            self.double_offer_reward(text_="[悬赏任务]",
                                     deck=my_opt["deck"],
                                     battle_plan_1p=my_opt["battle_plan_1p"],
                                     battle_plan_2p=my_opt["battle_plan_2p"])

        if (
                self.opt["relic"]["active"] or
                self.opt["cross_server"]["active"] or
                self.opt["warrior"]["active"]
        ):
            self.reload_game()

        my_opt = self.opt["relic"]
        if my_opt["active"]:
            self.easy_battle(text_="[火山遗迹]",
                             stage_id=my_opt["stage"],
                             max_times=int(my_opt["max_times"]),
                             deck=my_opt["deck"],
                             is_group=my_opt["is_group"],
                             battle_plan_1p=my_opt["battle_plan_1p"],
                             battle_plan_2p=my_opt["battle_plan_2p"],
                             dict_exit={"other_time": [0], "last_time": [3]})

        my_opt = self.opt["cross_server"]
        if my_opt["active"]:
            self.cross_server(text_="[跨服副本]",
                              is_group=my_opt["is_group"],
                              max_times=int(my_opt["max_times"]),
                              stage_id=my_opt["stage"],
                              deck=my_opt["deck"],
                              battle_plan_1p=my_opt["battle_plan_1p"],
                              battle_plan_2p=my_opt["battle_plan_2p"])

        my_opt = self.opt["warrior"]
        if my_opt["active"]:
            self.easy_battle(text_="[勇士挑战]",
                             stage_id="NO-2-17",
                             max_times=int(my_opt["max_times"]),
                             deck=my_opt["deck"],
                             is_group=my_opt["is_group"],
                             battle_plan_1p=my_opt["battle_plan_1p"],
                             battle_plan_2p=my_opt["battle_plan_2p"],
                             dict_exit={"other_time": [0], "last_time": [3, 2]})

        if (
                self.opt["magic_tower_alone_1"]["active"] or
                self.opt["magic_tower_alone_2"]["active"] or
                self.opt["magic_tower_prison_1"]["active"] or
                self.opt["magic_tower_prison_2"]["active"] or
                self.opt["magic_tower_double"]["active"]
        ):
            self.reload_game()

        for player_id in [1, 2]:
            my_opt = self.opt["magic_tower_alone_{}".format(player_id)]
            if my_opt["active"]:
                self.alone_magic_tower(text_="[魔塔单人_{}P]".format(player_id),
                                       player_id=player_id,
                                       floor=int(my_opt["stage"]),
                                       max_times=int(my_opt["max_times"]),
                                       deck=my_opt["deck"],
                                       battle_plan_1p=my_opt["battle_plan_1p"])

        for player_id in [1, 2]:
            my_opt = self.opt["magic_tower_prison_{}".format(player_id)]
            if my_opt["active"]:
                self.alone_magic_tower_prison(text_="[魔塔密室_{}P]".format(player_id),
                                              player_id=player_id,
                                              sutra_pavilion=my_opt["stage"],
                                              deck=my_opt["deck"],
                                              battle_plan_1p=my_opt["battle_plan_1p"])

        my_opt = self.opt["magic_tower_double"]
        if my_opt["active"]:
            self.double_magic_tower(text_="[魔塔双人]",
                                    floor=int(my_opt["stage"]),
                                    max_times=int(my_opt["max_times"]),
                                    deck=my_opt["deck"],
                                    battle_plan_1p=my_opt["battle_plan_1p"],
                                    battle_plan_2p=my_opt["battle_plan_2p"])

        my_opt = self.opt["customize"]
        if my_opt["active"]:
            self.reload_game()
            self.customize_battle(text_="[高级自定义]")

        # 全部完成前 先 领取一下任务
        self.sin_out.emit("检查所有任务完成情况")
        self.compete_quest()
        self.sin_out.emit("所有已领取奖励")

        # 全部完成了? 发个信号
        self.sin_out_completed.emit()

    def pause(self):
        """暂停"""
        self.mutex.lock()
        self.is_paused = True
        self.mutex.unlock()

    def resume(self):
        """恢复暂停"""
        self.mutex.lock()
        self.is_paused = False
        self.condition.wakeAll()
        self.mutex.unlock()


class MyMainWindow2(MyMainWindow1):

    def __init__(self):
        # 继承父类构造方法
        super().__init__()
        self.thread_todo = None
        self.reply = None
        self.faa = [None,None,None]
        # 线程激活即为True
        self.thread_states = False

    def todo_completed(self):
        # 设置按钮文本
        self.Button_Start.setText("开始\nLink Start")
        # 设置进程状态文本
        self.printf("\n>>> 全任务完成 线程关闭 <<<\n")
        # 设置flag
        self.thread_states = False

    def click_btn_start(self):
        """战斗开始函数"""
        # 线程没有激活
        if not self.thread_states:
            self.ui_to_opt()
            game_name = self.opt["game_name"]
            server_id = self.opt["server_id"]
            name_1p = self.opt["name_1p"]
            name_2p = self.opt["name_2p"]
            channel_1p, channel_2p = get_channel_name(game_name, name_1p, name_2p)

            # 把索引变值 需要注意的是 battle_plan均为索引 需要在FAA类中处理
            zoom_ratio = {0: 1.00, 1: 1.25, 2: 1.50, 3: 1.75, 4: 2.00, 5: 2.25, 6: 2.50}
            zoom_ratio = zoom_ratio[self.opt["zoom_ratio"]]

            faa = [None,None,None]
            faa[1] = FAA(channel=channel_1p,
                         zoom=zoom_ratio,
                         server_id=server_id,
                         player="1P",
                         character_level=self.opt["level_1p"],
                         is_use_key=True,  # boolean 是否使用钥匙 做任务必须选择 是
                         is_auto_battle=self.opt["auto_use_card"],  # boolean 是否使用自动战斗 做任务必须选择 是
                         is_auto_collect=False)

            faa[2] = FAA(channel=channel_2p,
                         zoom=zoom_ratio,
                         server_id=server_id,
                         player="2P",
                         character_level=self.opt["level_2p"],
                         is_use_key=True,
                         is_auto_battle=self.opt["auto_use_card"],
                         is_auto_collect=True)

            # 设置按钮文本
            self.Button_Start.setText("终止\nEnd")
            # 设置flag
            self.thread_states = True

            # Link Start!
            self.TextBrowser.clear()
            self.printf(">>> 链接开始 线程开启 <<<")
            self.printf(">>> 务必有二级密码, 且未输入以以兜底 <<<")
            self.printf("")

            self.thread_todo = Todo(faa=faa, opt=self.opt)
            # 绑定手动结束线程
            self.thread_todo.sin_out_completed.connect(self.todo_completed)
            # 绑定文本输出
            self.thread_todo.sin_out.connect(self.printf)
            # 开始线程
            self.thread_todo.start()

        else:
            """
            线程已经激活 则从外到内中断,再从内到外销毁
            thread_todo (QThread)
                |-- thread_1p (ThreadWithException)
                |-- thread_2p (ThreadWithException)
            """
            # 暂停外部线程
            self.thread_todo.pause()

            # 中断[内部战斗线程]
            for thread in [self.thread_todo.thread_1p, self.thread_todo.thread_2p]:
                if thread is not None:
                    thread.stop()
                    thread.join()  # 等待线程确实中断

            # 中断 销毁 [任务线程]
            self.thread_todo.terminate()
            self.thread_todo.wait()  # 等待线程确实中断
            self.thread_todo.deleteLater()

            # 结束线程后的ui处理
            self.todo_completed()


def main():
    # 实例化 PyQt后台管理
    app = QApplication(sys.argv)

    # 实例化 主窗口
    window = MyMainWindow2()

    # 建立槽连接 注意 多线程中 槽连接必须写在主函数
    # 注册函数：开始/结束按钮
    window.Button_Start.clicked.connect(lambda: window.click_btn_start())
    window.Button_Save.clicked.connect(lambda: window.click_btn_save())
    # 主窗口 实现
    window.show()

    # 运行主循环，必须调用此函数才可以开始事件处理
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
