from random import randint
from abc import ABCMeta, abstractmethod
from Enums import Incidents

class Player:
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.position = 0
        self.gold = 10000  # 初始金币
        self.fertilizer = 50  # 初始肥料
        self.sunlight = 100  # 初始环境指标（阳光）
        self.plants = [0] * 5  # 作物计数（海藻、水草、向日葵、树木、森林）
        self.factories = [0] * 3  # 工厂等级计数
        self.item = None  # 道具卡
        self.chance = False  # 贸易机会

    def move(self):
        roll = randint(1, 6)
        self.position = (self.position + roll) % 40
        return roll, 0, False  # 兼容原骰子格式

    @abstractmethod
    def incidents(self, all_lands):
        pass

    def messages(self, all_lands):
        base_messages = self.__base_messages()
        incidents_messages = self.incidents_messages(all_lands)
        return base_messages, incidents_messages

    def __base_messages(self):
        messages = []
        for j in range(3):
            messages.append([])
        messages[0].append(f"昵称: {self.name}")
        messages[0].append(f"坐标: {self.position}")
        messages[1].append(f"阳光: {self.sunlight}")
        messages[1].append(f"金币: {self.gold}")
        messages[2].append(f"肥料: {self.fertilizer}")
        messages[2].append(f"道具: {self.item or '无'}")
        return messages

    @abstractmethod
    def incidents_messages(self, all_lands):
        pass

    @abstractmethod
    def buy(self, land, land_is_full):
        pass

    @abstractmethod
    def plant(self, land, plant_type):
        pass

    @abstractmethod
    def upgrade(self, land):
        pass

    @abstractmethod
    def build_factory(self, land):
        pass

    @abstractmethod
    def use_item(self, landmasses, target=None):
        pass