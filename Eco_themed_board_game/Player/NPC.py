from Player.Player import Player
from Enums import Incidents
import random

class NPC(Player):
    def buy(self, land, land_is_full):
        if land.owner == '系统' and self.gold >= 500 and not land_is_full:
            self.gold -= 500
            land.owner = self.name
            land.type = random.choice(["land", "pool"])
            return True
        return False

    def plant(self, land, plant_type):
        if land.owner == self.name and land.plant_type is None and self.gold >= 200:
            self.gold -= 200
            land.plant_type = plant_type
            land.plant_level = 1
            self.plants[plant_type] += 1
            return True
        return False

    def upgrade(self, land):
        if land.owner == self.name and land.plant_type is not None and land.plant_level < 3 and self.fertilizer >= 20 * land.plant_level:
            self.fertilizer -= 20 * land.plant_level
            land.plant_level += 1
            if land.plant_level == 3 and land.plant_type < 4:
                land.plant_type += 1
                land.plant_level = 1
                self.plants[land.plant_type - 1] -= 1
                self.plants[land.plant_type] += 1
            return True
        return False

    def build_factory(self, land):
        if land.owner == self.name and land.plant_type is None and land.factory_level == 0 and self.gold >= 1000:
            self.gold -= 1000
            land.factory_level = 1
            self.factories[0] += 1
            return True
        return False

    def use_item(self, landmasses, target=None):
        if self.item == "瑞雪兆丰年":
            total_sunlight = 0
            for land in landmasses.lands:
                if land.owner == self.name and land.plant_type is not None:
                    total_sunlight += 10 * land.plant_level
            self.sunlight += total_sunlight
            self.item = None
        elif self.item == "好雨知时节" and target is not None:
            self.upgrade(target)
            self.item = None
        elif self.item == "酸雨来袭":
            for land in landmasses.lands:
                if land.owner == self.name and land.plant_type is not None:
                    land.plant_level = max(1, land.plant_level - 1)
            self.item = None
        elif self.item == "工业污染":
            self.fertilizer -= 20
            self.item = None

    def incidents(self, all_lands):
        land = all_lands.lands[self.position]
        if land.owner == "事件":
            if land.incident == Incidents.explore:
                self.sunlight += 50
                return 50
            elif land.incident == Incidents.pollution:
                self.sunlight -= 30
                return -30
            elif land.incident == Incidents.trade:
                self.chance = True
                return "trade"
            elif land.incident == Incidents.card:
                self.item = random.choice(["瑞雪兆丰年", "好雨知时节", "酸雨来袭", "工业污染"])
                return 0
        elif land.owner != self.name and land.owner != "事件" and land.factory_level > 0:
            rent = 5 * land.factory_level
            self.fertilizer -= rent
            return rent
        return 0

    def incidents_messages(self, all_lands):
        land = all_lands.lands[self.position]
        messages = []
        if land.owner == "事件":
            if land.incident == Incidents.start:
                messages.append("事件：对手到达起点")
            elif land.incident == Incidents.explore:
                messages.append("事件：对手探索自然，获得50阳光")
            elif land.incident == Incidents.pollution:
                messages.append("事件：对手遭遇污染，损失30阳光")
            elif land.incident == Incidents.trade:
                messages.append("事件：对手获得贸易机会")
            elif land.incident == Incidents.card:
                messages.append(f"事件：对手抽到道具卡 - {self.item}")
        elif land.owner == "系统":
            messages.append("对手到达无主地皮")
        elif land.owner == self.name:
            messages.append("对手的地皮")
        else:
            messages.append("你的地皮")
            if land.factory_level > 0:
                messages.append(f"对手支付{5 * land.factory_level}肥料过路费")
        return messages

    def act(self, landmasses):
        land = landmasses.lands[self.position]
        if land.owner == self.name:
            if land.plant_type is None and land.factory_level == 0 and self.gold >= 200:
                self.plant(land, random.randint(0, 4))
            elif land.plant_type is not None and self.fertilizer >= 20 * land.plant_level:
                self.upgrade(land)
            elif land.plant_type is None and land.factory_level == 0 and self.gold >= 1000:
                self.build_factory(land)
        if self.item:
            self.use_item(landmasses, land)
        if land.incident == Incidents.trade and self.chance and self.gold < 1000:
            return "trade"
        return None