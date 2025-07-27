from random import randint
from abc import ABCMeta, abstractmethod
from Enums import Incidents

class Player:
    __metaclass__ = ABCMeta

    def __init__(self, name):
        self.name = name
        self.position = 0
        self.gold = 500
        self.fertilizer = 50
        self.carbon = 80
        self.plants = [0] * 5
        self.factories = [0] * 4
        self.item = None
        self.item_description = None
        self.chance = False
        self.skip_turn = False
        self.double_income_turn = 0
        self.no_income_turns = 0
        self.can_plant = True
        self.can_upgrade = True
        self.price_modifier = 1.0
        self.owned_lands = []

    def move(self):
        roll = randint(1, 6)
        return roll, 0, False

    def update(self, landmasses):
        self.owned_lands = [l for l in landmasses.lands if l.owner == self.name]
        for land in self.owned_lands:
            if land.factory_level > 0:
                self.carbon = min(120, self.carbon + 5)
            if land.protected_turns > 0:
                land.protected_turns -= 1
        if self.double_income_turn > 0:
            self.double_income_turn -= 1
        if self.no_income_turns > 0:
            self.no_income_turns -= 1
        if self.gold < 0:
            self.gold = 0

    @abstractmethod
    def incidents(self, all_lands):
        pass

    def messages(self, all_lands):
        base_messages = self.__base_messages()
        incidents_messages = self.incidents_messages(all_lands)
        # incidents_messages = self.item_description
        return base_messages, incidents_messages

    def __base_messages(self):
        messages = []
        for j in range(4):
            messages.append([])
        messages[0].append(f"昵称: {self.name}")
        messages[0].append(f"坐标: {self.position}")
        messages[1].append(f"碳足迹: {self.carbon}")
        messages[1].append(f"金币: {self.gold}")
        messages[2].append(f"肥料: {self.fertilizer}")
        messages[3].append(f"道具: {self.item or '无'}")
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