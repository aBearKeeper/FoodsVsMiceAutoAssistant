# FAA_FoodsVsMouses_AutoAssistant
一款名叫中国页游《美食大战老鼠》的自动助手。  
An automatic assistant for a Chinese webpage game called Foods Vs Mouses. 

本软件不支持任何作弊功能(秒杀或更多)。  
This software does not support any cheating function (flash killing and more).

本软件尚处于开发阶段, 已实现功能见下。  
This software is still in the development stage and its functions have been implemented as shown below.

该工具开发初衷是圆梦十年前的童年愿望 (悲)    
The original intention of developing this tool is to fulfill a childhood wish ten years ago (XP)

联系我: QQ - 815204388  
Contact : Tencent QQ - 815204388  


## 主要功能 Main

    主要功能
    │
    ├─ 自动流水线刷本
    │   ├─ 公会任务
    │   ├─ 情侣任务
    │   ├─ 单人魔塔(默认5连)
    │   ├─ 双人魔塔(默认5连)
    │   ├─ 单人魔塔密室(默认4连)
    │   ├─ 单人跨服(默认10连)
    │   ├─ 单人勇士本(默认10连)
    │   ├─ 单人火山遗迹(默认5连)
    │   ├─ 双人悬赏(默认3连,不稳定)
    │   └─ 双人单本连刷
    │
    ├─ 自动日常(开发中...)
    │   ├─ 每日签到
    │   ├─ 美食活动免费许愿
    │   ├─ 每日vip签到&礼卷领取
    │   └─ 每日免费塔罗抽取
    │
    └─ 未来计划
        ├─ 部分高难关卡自定义战斗支持
        ├─ GUI界面
        ├─ 自动登录和自动启动
        └─ 双人跨服

## 使用要求
#### 1.浏览器
目前仅支持 [360游戏大厅] 的 [多窗口模式]。

#### 2.卡组
大号(P1)至少有 [16] 个卡牌格子 并将第 [6] 个卡组按如下顺序放好。  
`木盘子 麦芽糖 小火 布丁 海星 糖葫芦 狮子座 瓜皮 双层小笼包 酒瓶炸弹 油灯 香肠 热狗 肥牛火锅 气泡 咖啡粉`  

小号(P2)至少有 [10]个卡牌格子 并将第 [6] 个卡组按如下顺序放好。  
`木盘子 麦芽糖 双层小笼包 酒瓶炸弹 油灯 香肠 热狗 肥牛火锅 气泡 咖啡粉`

#### 3.练度
没说明则可以任意配置, 可采取上位替代

    木盘子: 必须一转, p1|p2均是
    小火: 12星+技能7+2转, 否则可能产火不足, 很多关卡打不过
    海星: 12星+技能7+2转, 否则很多关卡打不过
    糖葫芦: 9星+技能5
    狮子座: 9星
    瓜皮: 9星+1转+技能7, 没有问题也不是很大, 但容错更高

#### 4.其他
脚本所在目录前的所有目录内 [不能有任何中文路径]!

启动脚本前 请更改todo.josn 有少量的配置文件需要更改。这是在GUI做出来之前的代餐。

每次启动脚本 必须在界面相对干净的区域! 且 [右上能看到地球]  

P2必须加P1为好友, 且为 [唯一] 好友(P1不受限)  

最好保证P1和P2 [等级] 足够进入大多数副本, 否则部分功能在顺序执行时会卡死  

刷本需要输入的 [地图代号] 见下文, 目前 [不支持探险营地和番外副本], 注意大小写空格等问题

## 关于&免责声明
1. 本软件采用通用 [全自动] 进图组队+战斗。执行期间 [务必不要把鼠标移入游戏区域] 内将干扰功能。  
2. 本软件战斗以 [1P为战斗力], 2P仅使用承载用垫子卡。为增加便捷性通用性, 本脚本将公会任务可能用到的卡片已添加到卡组中。  
3. 本软件组队以 [2P为队长], 进行双人模式的组队操作。  
4. 本软件不对背包爆满的问题做预设, 请自行 [保证背包格子充足]。  
5. 本软件处于 [开发测试阶段] , 执行过程中建议 [关注执行情况] , 若执行中因bug导致任何问题, 请立刻关闭窗口, 本人不负任何法律责任。为防止潜在的问题发生, 建议为您的角色 [设定二级密码] 且在本次登录中 [不输入它] 做兜底。  

## 地图代号说明

地图代号包含: 地图类型-地图序号-关卡序号

常用案例:  
神殿:`NO-1-7`    
深渊:`NO-1-14`   
城堡:`NO-2-5`  
港口:`NO-2-10`   
火山:`NO-2-15`   
花园:`NO-4-5`  

    NO: Normal 普通关卡 包括三岛+海岛+遗迹 总选择2区
        1: 美味岛
        2: 火山岛
        3: 火山遗迹
        4: 浮空岛
        5: 旋涡
        6: 探险营地
            从1开始, 根据地图顺序递增
            外论：
                漫游关卡为 NO-1-15 NO-2-16 NO-4-16
                勇士挑战为 NO-2-17 仅支持钢铁侠
    MT: Magic Tower 魔塔蛋糕 通过地图进入
        1: 单人
            直接填入层数(1-155)
        2: 双人
            直接填入层数(1-100)
        3: 密室
            1为炼金房(1-4)
    CS: Cross Server 跨服副本(不支持组队)
        1: 古堡
        2: 天空
        3: 地狱
        4: 水火
        5: 巫毒
        6: 冰封
            1-8：所有地图
    OR: Offer a Reward 悬赏副本
        1: 美味
        2: 火山
        3: 浮空
            0: 保证每一个关卡都有三个参数 占位
            
## 项目路径
如要拿到本地使用, 请解压 resource.zip 放到项目根目录级. 

    root
     │
     ├─ function
     │   ├─ common 包含各种工具类, 后台进行 截图/找图/按键/点击等
     │   ├─ script 主要功能函数 以common.py和farm_no_ui.py为主 其他未实现
     │   ├─ get_root_path.py 根据exe和pycharm运行环境 获取root路径
     │   └─ main.py 主函数
     ├─ resource
     │   ├─ logs 战利品记录
     │   ├─ common
     │   ├─ common
     │   ├─ common

封装为exe后, 需要把 todo.json 和 resource解压后的文件夹 放到main.exe的上一级的目录即可开始运行.  
Link Start!
