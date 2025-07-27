import random
from Enums import Incidents
from GameManager import GameManager

def trigger_event_card(player, landmasses):
    effects = [
        ("瑞雪兆丰年", lambda: gain_gold_per_land(player, 30), "瑞雪兆丰年，五谷登丰收。随机获得自己所有土地的一次收益（每块30金币）。"),
        ("好雨知时节", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10), "好雨知时节，当春乃发生。随机升级一块资产（植物或工厂），碳足迹减少10或15。"),
        ("植树节活动", lambda: plant_on_random_empty(player, landmasses), "植树节到了，一起为地球添绿吧！随机在一块空地种植基础植物，碳足迹减少10。"),
        ("环保补贴", lambda: setattr(player, "gold", player.gold + random.randint(20, 50)), "政府为鼓励环保行为，发放专项补贴。随机获得20-50金币。"),
        ("绿色能源发现", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10), "在这片土地上发现了可再生能源，有助于提升环保效益。"),
        ("环保志愿者", lambda: [setattr(player, "carbon", max(0, player.carbon - 10)), setattr(player, "gold", player.gold + 20)], "一群热心的志愿者来帮忙了，共同改善环境。碳足迹减少10，获得20金币。"),
        ("生态保护区", lambda: set_protected_land(player, landmasses, duration=2), "这片土地被划为生态保护区，受到特殊保护。未来两回合加倍收益。"),
        ("阳光充沛", lambda: double_plant_income(player, landmasses), "今天的阳光格外充足，植物生长旺盛！本回合植物收益双倍。"),
        ("环保技术创新", lambda: upgrade_random_asset(player, landmasses, reduce_carbon=10), "新技术的应用让环保变得更高效。"),
        ("绿色投资回报", lambda: setattr(player, "gold", player.gold + random.randint(50, 100)), "你的环保投资获得了回报！获得50-100金币。"),
        ("自然保护区成立", lambda: set_protected_land(player, landmasses, duration=3), "这片土地得到了自然的庇护，三回合免疫负面事件。"),
        ("生态奖励", lambda: [setattr(player, "carbon", max(0, player.carbon - 10)), setattr(player, "gold", player.gold + 20)], "环保努力获得认可！碳足迹减少10，获得20金币。"),
        ("酸雨来袭", lambda: degrade_random_plant(player, landmasses), "酸雨侵蚀植物，等级降低。"),
        ("工业污染", lambda: handle_industrial_pollution(player), "工厂污染，支付30金币或作物停止生长，碳足迹减少10。"),
        ("虫害爆发", lambda: handle_pest_outbreak(player, landmasses), "害虫入侵，植物受损或支付金币。"),
        ("干旱季节", lambda: set_no_income(player, duration=2), "干旱导致收益中断两回合。"),
        ("土地退化", lambda: handle_land_degradation(player, landmasses), "土地退化，无法升级或需修复。"),
        ("垃圾倾倒", lambda: handle_garbage_dump(player, landmasses), "随机植物等级-1 或支付清理费。"),
        ("土壤侵蚀", lambda: degrade_random_plant(player, landmasses), "植物等级下降。"),
        ("极端天气", lambda: set_no_income(player, duration=1), "极端天气阻断收益1回合。"),
        ("污染泄漏", lambda: handle_pollution_leak(player), "污染事件处理，金币不足则碳足迹上升。"),
        ("生物入侵", lambda: handle_pest_outbreak(player, landmasses), "外来物种入侵，植物受损或金币支付。"),
        ("生态交换卡", lambda: swap_random_asset(player, landmasses), "与对手交换一块地皮。"),
        ("土地规划卡", lambda: replan_random_land(player, landmasses), "重新规划一块土地。"),
        ("环保专家", lambda: assist_opponent(player, landmasses), "协助对手减少碳，需支付金币。"),
        ("市场波动卡", lambda: adjust_market_prices(player), "市场价格波动。"),
        ("土地置换卡", lambda: swap_random_land(player, landmasses), "交换土地布局。"),
        ("环保挑战卡", lambda: challenge_opponent(player, landmasses), "挑战对手，若碳高则支付金币。"),
        ("市场调控卡", lambda: adjust_market_prices(player), "调整价格影响经济策略。"),
        ("生态修复卡", lambda: restore_random_land(player, landmasses), "修复受损土地，减少碳足迹。"),
        ("资源交易卡", lambda: trade_resources(player, landmasses), "与对手交易资源（金币或土地）。"),
    ]
    name, func, description = random.choice(effects)
    print(f"\u89e6\u53d1\u4e8b\u4ef6\u5361: {name}")
    func()
    return name, description

def trigger_opportunity_card(player, landmasses):
    options = [
        ("前进之路", lambda: setattr(player, "position", (player.position + random.randint(3, 5)) % 44), 0.30, "快速前进3-5格。"),
        ("短暂停留", lambda: setattr(player, "skip_turn", True), 0.20, "停留1回合。"),
        ("财富惊喜", lambda: setattr(player, "gold", player.gold + random.randint(50, 100)), 0, "获得50-100金币。"),
        ("移动逆转", lambda: setattr(player, "position", (player.position - random.randint(2, 4)) % 44), 0, "后退2-4格。"),
        ("机会挑战", lambda: setattr(player, "gold", player.gold - 20) if player.gold >= 20 else setattr(player, "carbon", min(player.carbon + 10, 120)), 0, "支付20金币，否则碳足迹+10"),
        ("土地赠送", lambda: gift_random_land(player, landmasses), 0, "获得一块空地。"),
        ("碳足迹减免", lambda: setattr(player, "carbon", max(0, player.carbon - random.randint(5, 15))), 0, "减少5-15碳足迹。"),
        ("随机跳跃", lambda: setattr(player, "position", random.randint(1, 43)), 0, "跳至随机位置。"),
        ("进监狱", lambda: [setattr(player, "position", 22), setattr(player, "skip_turn", True)], 0, "进监狱并跳过1回合。"),
    ]
    total_prob = sum(prob for _, _, prob, _ in options if prob > 0)
    if random.random() < total_prob:
        weighted = [(name, func, desc) for name, func, prob, desc in options if prob > 0]
        weights = [prob for _, _, prob, _ in options if prob > 0]
        name, func, desc = random.choices(weighted, weights=weights, k=1)[0]
    else:
        name, func, desc = random.choice([(name, func, desc) for name, func, prob, desc in options if prob == 0])
    print(f"\u89e6\u53d1\u673a\u4f1a\u5361: {name}")
    func()
    return name, desc


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
    opponent = landmasses.PC if player.name == landmasses.NPC.name else landmasses.NPC
    for p in [landmasses.PC, landmasses.NPC]:
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
    opponent = landmasses.PC if player.name == landmasses.NPC.name else landmasses.NPC
    resource = random.choice(["gold", "land"])
    if resource == "gold":
        amount = random.randint(50, 100)
        if player.gold >= amount:
            player.gold -= amount
            for p in [landmasses.PC, landmasses.NPC]:
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