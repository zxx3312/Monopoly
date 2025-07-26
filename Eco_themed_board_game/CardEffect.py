import random
from Enums import Incidents
from GameManager import GameManager

def trigger_event_card(player, landmasses):
    effects = [
        ("瑞雪兆丰年", lambda: gain_gold_per_land(player, 30)),
        ("好雨知时节", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10)),
        ("植树节活动", lambda: plant_on_random_empty(player, landmasses)),
        ("环保补贴", lambda: player.gold.__add__(random.randint(20, 50))),
        ("绿色能源发现", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10)),
        ("环保志愿者", lambda: (setattr(player, "carbon", max(0, player.carbon - 10)), player.gold.__add__(20))),
        ("生态保护区", lambda: set_protected_land(player, landmasses, duration=2)),
        ("阳光充沛", lambda: double_plant_income(player, landmasses)),
        ("环保技术创新", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10)),
        ("绿色投资回报", lambda: player.gold.__add__(random.randint(50, 100))),
        ("自然保护区成立", lambda: set_protected_land(player, landmasses, duration=3)),
        ("生态奖励", lambda: (setattr(player, "carbon", max(0, player.carbon - 10)), player.gold.__add__(20))),
        ("酸雨来袭", lambda: degrade_random_plant(player, landmasses)),
        ("工业污染", lambda: handle_industrial_pollution(player)),
        ("虫害爆发", lambda: handle_pest_outbreak(player, landmasses)),
        ("干旱季节", lambda: set_no_income(player, duration=2)),
        ("土地退化", lambda: handle_land_degradation(player, landmasses)),
        ("垃圾倾倒", lambda: handle_garbage_dump(player, landmasses)),
        ("土壤侵蚀", lambda: degrade_random_plant(player, landmasses)),
        ("极端天气", lambda: set_no_income(player, duration=1)),
        ("污染泄漏", lambda: handle_pollution_leak(player)),
        ("生物入侵", lambda: handle_pest_outbreak(player, landmasses)),
        ("生态交换卡", lambda: swap_random_asset(player, landmasses)),
        ("土地规划卡", lambda: replan_random_land(player, landmasses)),
        ("环保专家", lambda: assist_opponent(player, landmasses)),
        ("市场波动卡", lambda: adjust_market_prices(player)),
        ("土地置换卡", lambda: swap_random_land(player, landmasses)),
        ("环保挑战卡", lambda: challenge_opponent(player, landmasses)),
        ("市场调控卡", lambda: adjust_market_prices(player)),
        ("生态修复卡", lambda: restore_random_land(player, landmasses)),
        ("资源交易卡", lambda: trade_resources(player, landmasses))
    ]
    name, func = random.choice(effects)
    print(f"触发事件卡：{name}")
    func()
    return name

def trigger_opportunity_card(player, landmasses):
    options = [
        # ("幸运起点", lambda: (setattr(player, "position", 0), player.gold.__add__(100)), 0.50),
        ("前进之路", lambda: setattr(player, "position", (player.position + random.randint(3, 5)) % 44), 0.30),
        ("短暂停留", lambda: setattr(player, "skip_turn", True), 0.20),
        ("财富惊喜", lambda: player.gold.__add__(random.randint(50, 100)), 0),
        ("移动逆转", lambda: setattr(player, "position", (player.position - random.randint(2, 4)) % 44), 0),
        ("机会挑战", lambda: player.gold.__sub__(20) if player.gold >= 20 else setattr(player, "carbon", min(player.carbon + 10, 120)), 0),
        ("土地赠送", lambda: gift_random_land(player, landmasses), 0),
        ("碳足迹减免", lambda: setattr(player, "carbon", max(0, player.carbon - random.randint(5, 15))), 0),
        # ("金币交换", lambda: swap_gold(player, landmasses, random.randint(50, 100)), 0),
        ("随机跳跃", lambda: setattr(player, "position", random.randint(1, 43)), 0),
        ("进监狱", lambda: (setattr(player, "position", 22), setattr(player, "skip_turn", True)), 0)
    ]
    total_prob = sum(prob for _, _, prob in options if prob > 0)
    if random.random() < total_prob:
        weighted_options = [(name, func) for name, func, prob in options if prob > 0]
        weights = [prob for _, _, prob in options if prob > 0]
        name, func = random.choices(weighted_options, weights=weights, k=1)[0]
    else:
        name, func = random.choice([(name, func) for name, func, prob in options if prob == 0])
    print(f"触发机会卡：{name}")
    func()
    return name

def gain_gold_per_land(player, per_land_gold):
    multiplier = 2 if player.double_income_turn > 0 else 1
    if player.no_income_turns == 0:
        count = sum(1 for land in player.owned_lands if land.plant_type is not None or land.factory_level > 0)
        player.gold += count * per_land_gold * multiplier

def upgrade_random_asset(player, landmasses, reduce_carbon=10):
    candidates = [l for l in landmasses.lands if l.owner == player.name and (l.plant_type is not None or l.factory_level > 0)]
    if candidates:
        land = random.choice(candidates)
        multiplier = 2 if player.double_income_turn > 0 else 1
        if land.plant_type is not None and land.plant_level < 4:
            land.plant_level += 1
            player.carbon = max(0, player.carbon - reduce_carbon * multiplier)
        elif land.factory_level > 0 and land.factory_level < 4:
            land.factory_level += 1
            player.carbon = max(0, player.carbon - reduce_carbon * 1.5 * multiplier)

def plant_on_random_empty(player, landmasses):
    candidates = [l for l in landmasses.lands if l.owner == player.name and l.plant_type is None and l.factory_level == 0]
    if candidates:
        land = random.choice(candidates)
        land.plant_type = random.randint(0, 4)
        land.plant_level = 1
        player.plants[land.plant_type] += 1
        multiplier = 2 if player.double_income_turn > 0 else 1
        player.carbon = max(0, player.carbon - 10 * multiplier)

def set_protected_land(player, landmasses, duration):
    candidates = [l for l in landmasses.lands if l.owner == player.name]
    if candidates:
        land = random.choice(candidates)
        land.protected_turns = duration

def double_plant_income(player, landmasses):
    player.double_income_turn = 1

def degrade_random_plant(player, landmasses):
    candidates = [l for l in landmasses.lands if l.owner == player.name and l.plant_type is not None and l.protected_turns == 0]
    if candidates:
        land = random.choice(candidates)
        land.plant_level = max(1, land.plant_level - 1)

def handle_industrial_pollution(player):
    if player.gold >= 30:
        player.gold -= 30
        player.carbon = max(0, player.carbon - 10)
    else:
        player.can_plant = False

def handle_pest_outbreak(player, landmasses):
    if player.gold >= 20:
        player.gold -= 20
    else:
        candidates = [l for l in landmasses.lands if l.owner == player.name and l.plant_type is not None and l.protected_turns == 0]
        if candidates:
            land = random.choice(candidates)
            land.plant_level = max(1, land.plant_level - 1)

def set_no_income(player, duration):
    player.no_income_turns = duration

def handle_land_degradation(player, landmasses):
    if player.gold >= 30:
        player.gold -= 30
    else:
        player.can_upgrade = False

def handle_garbage_dump(player, landmasses):
    if player.gold >= 30:
        player.gold -= 30
    else:
        candidates = [l for l in landmasses.lands if l.owner == player.name and l.plant_type is not None and l.protected_turns == 0]
        if candidates:
            land = random.choice(candidates)
            land.plant_level = max(1, land.plant_level - 1)

def handle_pollution_leak(player):
    if player.gold >= 50:
        player.gold -= 50
    else:
        player.carbon = min(120, player.carbon + 15)

def swap_random_asset(player, landmasses):
    opponent = landmasses.PC.name if player.name == landmasses.NPC.name else landmasses.NPC.name
    player_lands = [l for l in landmasses.lands if l.owner == player.name]
    opponent_lands = [l for l in landmasses.lands if l.owner == opponent]
    if player_lands and opponent_lands:
        land1 = random.choice(player_lands)
        land2 = random.choice(opponent_lands)
        land1.owner, land2.owner = land2.owner, land1.owner

def replan_random_land(player, landmasses):
    candidates = [l for l in landmasses.lands if l.owner == player.name]
    if candidates:
        land = random.choice(candidates)
        if land.plant_type is not None:
            land.plant_type = None
            land.plant_level = 0
        else:
            land.plant_type = random.randint(0, 4)
            land.plant_level = 1
            player.carbon = max(0, player.carbon - 10)

def assist_opponent(player, landmasses):
    if player.gold >= 20:
        player.gold -= 20
        opponent = landmasses.PC if player.name == landmasses.NPC.name else landmasses.NPC
        opponent.carbon = max(0, opponent.carbon - 10)

def adjust_market_prices(player):
    player.price_modifier = random.uniform(0.8, 1.2)

def swap_random_land(player, landmasses):
    opponent = landmasses.PC.name if player.name == landmasses.NPC.name else landmasses.NPC.name
    player_lands = [l for l in landmasses.lands if l.owner == player.name]
    opponent_lands = [l for l in landmasses.lands if l.owner == opponent]
    if player_lands and opponent_lands:
        land1 = random.choice(player_lands)
        land2 = random.choice(opponent_lands)
        land1.owner, land2.owner = land2.owner, land1.owner

def challenge_opponent(player, landmasses):
    opponent = landmasses.PC.name if player.name == landmasses.NPC.name else landmasses.NPC.name
    for p in [landmasses.PC.name, landmasses.NPC.name]:
        if p == opponent:
            other_player = p
    if player.carbon > other_player.carbon and player.gold >= 30:
        player.gold -= 30

def restore_random_land(player, landmasses):
    candidates = [l for l in landmasses.lands if l.owner == player.name and l.plant_type is not None]
    if candidates:
        land = random.choice(candidates)
        land.plant_level = min(4, land.plant_level + 1)
        player.carbon = max(0, player.carbon - 10)

def trade_resources(player, landmasses):
    opponent = landmasses.PC.name if player.name == landmasses.NPC.name else landmasses.NPC.name
    resource = random.choice(["gold", "land"])
    if resource == "gold":
        amount = random.randint(50, 100)
        if player.gold >= amount:
            player.gold -= amount
            for p in [landmasses.PC.name, landmasses.NPC.name]:
                if p == opponent:
                    other_player = p
                    other_player.gold += amount
    else:
        swap_random_land(player, landmasses)

def gift_random_land(player, landmasses):
    candidates = [l for l in landmasses.lands if l.owner == "系统"]
    if candidates:
        land = random.choice(candidates)
        land.owner = player.name
        land.type = random.choice(["land", "pool"])
        player.carbon = max(0, player.carbon - 5)