from Player.Player import Player
from Enums import Incidents
from CardEffect import trigger_event_card, trigger_opportunity_card
import random

class NPC(Player):
    def buy(self, land, land_is_full):
        cost = int(200 * self.price_modifier)
        if land.owner == '系统' and self.gold >= cost and not land_is_full:
            self.gold -= cost
            land.owner = self.name
            land.type = random.choice(["land", "pool"])
            self.carbon = max(0, self.carbon - 5)
            return True
        return False

    def plant(self, land, plant_type):
        cost = int(50 * self.price_modifier)
        if land.owner == self.name and land.plant_type is None and self.gold >= cost and land.factory_level == 0 and self.can_plant:
            self.gold -= cost
            land.plant_type = plant_type
            land.plant_level = 1
            self.plants[plant_type] += 1
            self.carbon = max(0, self.carbon - 10)
            return True
        return False

    def upgrade(self, land):
        cost = int(100 * land.plant_level * self.price_modifier)
        if land.owner == self.name and land.plant_type is not None and land.plant_level < 4 and self.gold >= cost and self.can_upgrade:
            self.gold -= cost
            land.plant_level += 1
            self.carbon = max(0, self.carbon - 10)
            if land.plant_level == 4 and land.plant_type < 4:
                land.plant_type += 1
                land.plant_level = 1
                self.plants[land.plant_type - 1] -= 1
                self.plants[land.plant_type] += 1
            return True
        return False

    def build_factory(self, land):
        cost = int(150 * self.price_modifier)
        if land.owner == self.name and land.plant_type is None and land.factory_level == 0 and self.gold >= cost:
            self.gold -= cost
            land.factory_level = 1
            self.factories[0] += 1
            self.carbon = max(0, self.carbon - 15)
            return True
        return False

    def use_item(self, landmasses, target=None):
        if self.item in ["瑞雪兆丰年", "好雨知时节", "植树节活动", "环保补贴", "绿色能源发现", "环保志愿者", "生态保护区", "阳光充沛", "环保技术创新", "绿色投资回报", "自然保护区成立", "生态奖励"]:
            trigger_event_card(self, landmasses)
        elif self.item == "酸雨来袭":
            for land in landmasses.lands:
                if land.owner == self.name and land.plant_type is not None and land.protected_turns == 0:
                    land.plant_level = max(1, land.plant_level - 1)
        elif self.item == "工业污染":
            if self.gold >= 30:
                self.gold -= 30
                self.carbon = max(0, self.carbon - 10)
            else:
                self.can_plant = False
        elif self.item == "虫害爆发":
            if self.gold >= 20:
                self.gold -= 20
            else:
                candidates = [l for l in landmasses.lands if l.owner == self.name and l.plant_type is not None and l.protected_turns == 0]
                if candidates:
                    land = random.choice(candidates)
                    land.plant_level = max(1, land.plant_level - 1)
        elif self.item == "干旱季节":
            self.no_income_turns = 2
        elif self.item == "土地退化":
            if self.gold >= 30:
                self.gold -= 30
            else:
                self.can_upgrade = False
        elif self.item == "垃圾倾倒":
            if self.gold >= 30:
                self.gold -= 30
            else:
                candidates = [l for l in landmasses.lands if l.owner == self.name and l.plant_type is not None and l.protected_turns == 0]
                if candidates:
                    land = random.choice(candidates)
                    land.plant_level = max(1, land.plant_level - 1)
        elif self.item == "土壤侵蚀":
            candidates = [l for l in landmasses.lands if l.owner == self.name and l.plant_type is not None and l.protected_turns == 0]
            if candidates:
                land = random.choice(candidates)
                land.plant_level = max(1, land.plant_level - 1)
        elif self.item == "极端天气":
            self.no_income_turns = 1
        elif self.item == "污染泄漏":
            if self.gold >= 50:
                self.gold -= 50
            else:
                self.carbon = min(120, self.carbon + 15)
        elif self.item == "生物入侵":
            if self.gold >= 20:
                self.gold -= 20
            else:
                candidates = [l for l in landmasses.lands if l.owner == self.name and l.plant_type is not None and l.protected_turns == 0]
                if candidates:
                    land = random.choice(candidates)
                    land.plant_level = max(1, land.plant_level - 1)
        self.item = None

    def incidents(self, all_lands):
        land = all_lands.lands[self.position]
        if land.owner == "事件":
            self.item = trigger_event_card(self, all_lands)
            return f"事件卡: {self.item}"
        elif land.owner == "机会":
            self.item = trigger_opportunity_card(self, all_lands)
            return f"机会卡: {self.item}"
        elif land.owner == "监狱":
            self.skip_turn = True
            return "进监狱"
        elif land.owner != self.name and land.owner != "系统" and land.owner not in ["事件", "机会", "监狱"]:
            if land.factory_level > 0:
                rent = 30 * land.factory_level
                if self.gold >= rent:
                    self.gold -= rent
                    return f"支付{rent}金币过路费"
                else:
                    return "金币不足，游戏结束"
            elif land.plant_type is not None:
                carbon_increase = 5 * land.plant_level
                self.carbon = min(120, self.carbon + carbon_increase)
                return f"碳足迹增加{carbon_increase}"
        elif land.owner == "系统":
            return "无主地皮"
        elif land.owner == self.name:
            return "自己的地皮"
        return ""

    def incidents_messages(self, all_lands):
        land = all_lands.lands[self.position]
        messages = []
        if land.owner == "事件":
            if land.incident == Incidents.start:
                messages.append("事件：对手到达起点，获得100金币")
                self.gold += 100
            elif land.incident == Incidents.explore:
                messages.append("事件：对手探索自然，获得50阳光")
                self.carbon = max(0, self.carbon - 50)
            elif land.incident == Incidents.pollution:
                messages.append("事件：对手遭遇污染，损失30阳光")
                self.carbon = min(120, self.carbon + 30)
            elif land.incident == Incidents.trade:
                messages.append("事件：对手获得贸易机会")
                self.chance = True
            elif land.incident == Incidents.card:
                messages.append(f"事件：对手抽到道具卡 - {self.item}")
        elif land.owner == "机会":
            messages.append(f"机会卡：{self.item}")
        elif land.owner == "监狱":
            messages.append("事件：对手进入监狱，停留1回合")
        elif land.owner == "系统":
            messages.append("对手到达无主地皮")
        elif land.owner == self.name:
            messages.append("对手的地皮")
        else:
            messages.append("你的地皮")
            if land.factory_level > 0:
                messages.append(f"对手支付{30 * land.factory_level}金币过路费")
            elif land.plant_type is not None:
                messages.append(f"对手碳足迹增加{5 * land.plant_level}")
        return messages

    def act(self, landmasses):
        land = landmasses.lands[self.position]
        if land.owner == self.name:
            if land.plant_type is None and land.factory_level == 0 and self.gold >= int(50 * self.price_modifier) and self.can_plant:
                self.plant(land, random.randint(0, 4))
            elif land.plant_type is not None and self.gold >= int(100 * land.plant_level * self.price_modifier) and self.can_upgrade:
                self.upgrade(land)
            elif land.plant_type is None and land.factory_level == 0 and self.gold >= int(150 * self.price_modifier):
                self.build_factory(land)
        if self.item:
            self.use_item(landmasses, land)
        if land.incident == Incidents.trade and self.chance and self.gold < 1000:
            return "trade"
        return None