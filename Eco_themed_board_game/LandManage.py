from Enums import Incidents
import random

class OneLand:
    def __init__(self, position, owner="系统", incident=Incidents.start):
        self.owner = owner
        self.position = position
        self.type = None
        self.plant_type = None
        self.plant_level = 0
        self.factory_level = 0
        self.incident = incident
        self.protected_turns = 0

    def price(self, who):
        if self.owner == "系统":
            return int(200 * who.price_modifier)
        if self.owner == who.name and self.plant_type is None and self.factory_level == 0:
            return int(50 * who.price_modifier)
        if self.owner == who.name and self.plant_type is None and self.factory_level == 0:
            return int(150 * who.price_modifier)
        if self.owner == who.name and self.plant_type is not None and self.plant_level < 4:
            return int(100 * self.plant_level * who.price_modifier)
        return 0

class Landmasses:
    def __init__(self, PCName, NPCName):
        self.lands = []
        self.PC = PCName
        self.NPC = NPCName
        event_positions = [1, 5, 8, 13, 19, 25, 29, 35, 40]
        opportunity_positions = [3, 6, 10, 15, 17, 21, 27, 31, 37, 42]
        jail_position = 22

        for j in range(44):
            if j in event_positions:
                self.lands.append(OneLand(j, owner="事件", incident=Incidents.card))
            elif j in opportunity_positions:
                self.lands.append(OneLand(j, owner="机会", incident=Incidents.trade))
            elif j == jail_position:
                self.lands.append(OneLand(j, owner="监狱", incident=Incidents.pollution))
            else:
                self.lands.append(OneLand(j))

        self.PCAward = False
        self.NPCAward = False
        self.PCAwardMessage = 0
        self.NPCAwardMessage = 0

    def is_full(self, name):
        if name == self.PC.name and self.PCAward:
            return False
        if name == self.NPC.name and self.NPCAward:
            return False
        counter = sum(1 for land in self.lands if land.owner != "系统" and land.owner != "事件" and land.owner != "机会" and land.owner != "监狱")
        if counter >= 32:
            if name == self.PC.name:
                self.PCAward = True
            else:
                self.NPCAward = True
            return True
        return False