from enum import Enum

class GameStatus(Enum):
    start = 0       # 游戏开始界面
    waitIn = 1      # 等待进入游戏
    initial = 2     # 实例化角色、地皮、骰子
    playing = 3     # 游戏进行中
    over = 4        # 游戏结束界面
    end = 5         # 游戏结束界面绘制完毕
    quit = 6        # 退出游戏

class PlayerTurn(Enum):
    start = 0       # 游戏开始
    PCMove = 1      # 玩家移动
    PCAct = 2       # 玩家行动（购买、种植、升级、建造）
    NPCMove = 3     # NPC 移动
    NPCAct = 4      # NPC 行动

class Incidents(Enum):
    start = 0       # 起点
    explore = 1     # 探索，获得阳光
    pollution = 2   # 污染，损失阳光
    trade = 3       # 贸易，交换资源
    card = 4        # 抽取道具卡