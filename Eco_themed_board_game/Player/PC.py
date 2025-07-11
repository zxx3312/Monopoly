from Player.Player import Player
from Enums import Incidents
import random

class PC(Player):
    def buy(self, land, land_is_full):
        if land.owner == '系统' and self.gold >= 500 and not land_is_full:
            self.gold -= 500
            land.owner = self.name
            land.type = random.choice(["land", "pool"])
            print(f"{self.name} purchased land at position {land.position}")
            return True
        else:
            print(f"Cannot buy: owner={land.owner}, gold={self.gold}, land_full={land_is_full}")
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
                messages.append("事件：你到达了起点")
            elif land.incident == Incidents.explore:
                messages.append("事件：探索自然，获得50阳光")
                messages.append("海藻吸收二氧化碳，促进海洋碳汇！")
            elif land.incident == Incidents.pollution:
                messages.append("事件：遭遇污染，损失30阳光")
                messages.append("工业污染威胁生态平衡！")
            elif land.incident == Incidents.trade:
                messages.append("事件：获得贸易机会")
                messages.append("按B键与对手交换金币")
            elif land.incident == Incidents.card:
                messages.append(f"事件：抽到道具卡 - {self.item}")
        elif land.owner == "系统":
            messages.append("这里是一片无主的地皮")
            messages.append("按B键花费500金币购买")
        elif land.owner == self.name:
            if land.plant_type is None and land.factory_level == 0:
                messages.append("你的地皮，尚未开发")
                messages.append("按P键花费200金币种植作物")
                messages.append("按F键花费1000金币建造工厂")
            elif land.plant_type is not None:
                messages.append(f"你的{['海藻', '水草', '向日葵', '树木', '森林'][land.plant_type]}，等级{land.plant_level}")
                if land.plant_level < 3:
                    messages.append(f"按U键花费{20 * land.plant_level}肥料升级")
            elif land.factory_level > 0:
                messages.append(f"你的工厂，等级{land.factory_level}")
        else:
            messages.append("对手的地皮")
            if land.factory_level > 0:
                messages.append(f"支付{5 * land.factory_level}肥料过路费")
        return messages