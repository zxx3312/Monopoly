from Enums import Incidents
import random

class OneLand:
    def __init__(self, position, owner="系统", incident=Incidents.start):
        self.owner = owner
        self.position = position
        self.type = None  # "land" 或 "pool"
        self.plant_type = None  # 0:海藻, 1:水草, 2:向日葵, 3:树木, 4:森林
        self.plant_level = 0
        self.factory_level = 0
        self.incident = incident

    def price(self, who):
        if self.owner == "系统":
            return 500
        if self.owner == who and self.plant_type is None and self.factory_level == 0:
            return 200  # 种植作物
        if self.owner == who and self.plant_type is None and self.factory_level == 0:
            return 1000  # 建造工厂
        return 0

class Landmasses:
    def __init__(self, PCName, NPCName):
        self.lands = []
        self.PCName = PCName
        self.NPCName = NPCName
        for j in range(44):
            if j in [0, 11, 22, 33]:  # 事件格（角）
                self.lands.append(OneLand(j, owner="事件", incident=Incidents(j // 11)))
            else:
                self.lands.append(OneLand(j))
        self.PCAward = False
        self.NPCAward = False
        self.PCAwardMessage = 0
        self.NPCAwardMessage = 0

    def is_full(self, name):
        if name == self.PCName and self.PCAward:
            return False
        if name == self.NPCName and self.NPCAward:
            return False
        counter = sum(1 for land in self.lands if land.owner != "系统" and land.owner != "事件")
        if counter >= 32:
            if name == self.PCName:
                self.PCAward = True
            else:
                self.NPCAward = True
            return True
        return False