import pygame
import asyncio
import platform
from pygame import display, event, font, image, time, mixer
from pygame.locals import *
from MusicPlay import MusicPlay
from Enums import GameStatus, PlayerTurn
import random

class GameManager:
    def __init__(self):
        pygame.init()
        self.clock = time.Clock()
        self.source = "./source/"
        self.font = font.Font(self.source + "simhei.ttf", 15)
        # 调整窗口大小，保持棋盘比例 7562/7506 ≈ 1.0076
        self.screen = display.set_mode((756, 750))
        display.set_icon(self.__image_load("eco.png"))
        display.set_caption("环保作物种植")
        self.music = mixer.music.load(self.source + "BackgroundMusic.mp3")
        self.backgroundMusic = MusicPlay(self.music)

        self.initialToPlaying = False
        self.gameStatus = GameStatus.start
        self.playerTurn = PlayerTurn.start
        self.cheat = [0, 0, 0]
        self.spaceKeyDown = event.Event(KEYDOWN, key=K_SPACE)
        self.PCActKey = [0, 0, 0, 0]
        self.winner = ""
        self.turn_count = 0
        self.dice_animation_done = False

        self.start = self.__image_load("Start.png")
        self.gameFail = self.__image_load("GameFail.png")
        self.gameWin = self.__image_load("GameWin.png")
        self.initialMap = self.__image_load("EcoMap.png")
        self.gameMap = self.__image_load("gameMap.png")
        self.tips = self.__image_load("Tips.png")
        self.musicOn = self.__image_load("MusicOn.png")
        self.musicOff = self.__image_load("MusicOff.png")
        self.musicImage = self.musicOn
        self.musicBarrier = self.__image_load("MusicBarrier.png")
        self.musicButtonLocation = (41 * 25 * 756 / 800, 27 * 25 * 750 / 800)  # 缩放音乐按钮位置
        self.musicButtonRect = Rect(self.musicButtonLocation[0], self.musicButtonLocation[1], 100 * 756 / 800, 75 * 750 / 800)
        self.activeOn = self.__image_load("ActiveOn.png")
        self.activeOff = self.__image_load("ActiveOff.png")

        self.PCName = "PC"
        self.PCImage = self.__image_load("PC.png", scale_to=(74, 72))
        self.PCFixImage = self.__image_load("PCFix.png", scale_to=(74, 72))
        # 原始棋盘中 PC 区域
        self.PCBoard = [
            (1169 / 7562 * self.screen.get_width() + 10, 2753 / 7506 * self.screen.get_height() + 50),
            (1169 / 7562 * self.screen.get_width() + 10, 4407 / 7506 * self.screen.get_height() + 50)
        ]
        
        self.NPCName = "NPC"
        self.NPCImage = self.__image_load("NPC.png", scale_to=(74, 72))
        self.NPCFixImage = self.__image_load("NPCFix.png", scale_to=(74, 72))
        # NPC 是对称位置
        self.NPCBoard = [
            ((7562 - 3567) / 7562 * self.screen.get_width(), 2753 / 7506 * self.screen.get_height() + 50),
            ((7562 - 3567) / 7562 * self.screen.get_width(), 4407 / 7506 * self.screen.get_height() + 50)
        ]

        self.diceImages = [self.__image_load(f"Dice{j+1}.png") for j in range(6)]
        self.diceBarrier = self.__image_load("DiceBarrier.png")
        dice_x = self.screen.get_width() // 2 - 50  # 居中偏左约50像素
        dice_y = self.screen.get_height() - 220     # 离底部200像素

        self.diceBoard = [(dice_x, dice_y)]
        self.diceLocation = [self.diceBoard[0]]
        self.diceSteps = (0, 0, True)

        self.plantImages = [[self.__image_load(f"{plant}.png", scale_to=(74, 72)) for i in range(1, 5)] for plant in ["Seaweed", "WaterGrass", "Sunflower", "Tree", "Forest"]]
        self.factoryImages = [self.__image_load(f"factory{i}.png", scale_to=(74, 72)) for i in range(1, 5)]
        self.wasteland = self.__image_load("Wasteland.png", scale_to=(74, 72))
        self.tips_texts = [
            "海藻吸收二氧化碳，促进海洋碳汇！",
            "水草为海洋生态提供氧气和栖息地。",
            "向日葵通过光合作用减少碳排放。",
            "森林是地球的肺，每年吸收大量碳。"
        ]

    async def main_loop(self):
        while self.gameStatus != GameStatus.quit:
            self.event_deal()
            if self.gameStatus == GameStatus.start:
                self.draw_beginning()
                self.gameStatus = GameStatus.waitIn
            elif self.gameStatus == GameStatus.initial:
                self.__initialize_game()
                self.gameStatus = GameStatus.playing
                self.initialToPlaying = True
            elif self.gameStatus == GameStatus.playing:
                await self.__play_game()
                # 强制重绘屏幕
                self.draw_map()
                self.draw_lands(self.landmasses.lands)
                self.draw_character(self.hero.position, self.enemy.position)
                self.draw_active_status()
                self.draw_messages((self.hero.messages(self.landmasses), self.enemy.messages(self.landmasses)))
                self.draw_fix_dice(self.shootDice.finalPoints)
                self.draw_music_button()
                self.draw_tips()
                display.update()
            elif self.gameStatus == GameStatus.over:
                self.draw_game_over(self.hero.carbon, self.enemy.carbon)
            await asyncio.sleep(0.1)

    def event_deal(self):
        for even in event.get():
            if even.type == QUIT or (even.type == KEYDOWN and even.key == K_e):
                self.__quit()
            if even.type == KEYDOWN:
                if even.key == K_r:
                    self.__play_again()
                elif even.key == K_SPACE and self.gameStatus == GameStatus.waitIn:
                    self.gameStatus = GameStatus.initial
                    self.spaceKeyDown = even
                elif even.key == K_SPACE and self.gameStatus == GameStatus.playing:
                    self.turn_change_space()
                elif self.gameStatus == GameStatus.playing and not self.__developer_pattern_check():
                    self.__set_developer_pattern(even.key)
                self.__set_PC_act_key(even)
            if even.type == MOUSEBUTTONDOWN and even.button == BUTTON_LEFT:
                self.__music_pause(even.pos)

    def post_space_key_down(self):
        event.post(self.spaceKeyDown)

    def get_character_name(self, PC_name, NPC_name):
        self.PCName = PC_name
        self.NPCName = NPC_name

    @staticmethod
    def image_update():
        display.update()

    def __image_load(self, name, scale_to=None):
        try:
            img = image.load(self.source + name).convert_alpha()
            if name in ["EcoMap.png", "gameMap.png"]:
                img = pygame.transform.scale(img, (756, 750))
            elif scale_to:
                img = pygame.transform.scale(img, scale_to)
            return img
        except pygame.error:
            img = image.load(self.source + "Wasteland.png").convert_alpha()
            if scale_to:
                img = pygame.transform.scale(img, scale_to)
            return img

    def draw_beginning(self):
        for j in range(150):
            self.clock.tick(300)
            self.screen.blit(self.initialMap, (0, 0))
            # self.screen.blit(self.PCFixImage, (6 * 25 * 756 / 800 + 13 + j * 1 - 10, 6 * 25 * 750 / 800 + 13 - 10))
            # self.screen.blit(self.NPCFixImage, (38 * 25 * 756 / 800 + 13 - j * 1 - 10, 6 * 25 * 750 / 800 + 13 - 10))
            # self.screen.blit(self.start, (175 * 756 / 800, 325 * 750 / 800))
            self.screen.blit(self.musicImage, self.musicButtonLocation)
            display.update()

    def draw_map(self):
        self.screen.blit(self.gameMap, (0, 0))

    def __location_convert(self, position):
        # 棋盘尺寸从 (7562, 7506) 缩放到 (756, 750)
        scale_x, scale_y = 756 / 7562, 750 / 7506
        grid_width = (1028 - 102) * scale_x  # 约 92.6
        grid_height = (1013 - 109) * scale_y  # 约 90.4

        if position == 0:
            x = 102
            y = 109
            return x * scale_x, y * scale_y
        elif position < 11:
            # 顶部：0-11，x 从 102 到 6458，y 固定 109
            x = 1028 + (position - 1) * (6458 - 1028) / 10
            y = 109
            return x * scale_x, y * scale_y
        elif position == 11:
            x = 6458
            y = 109
            return x * scale_x, y * scale_y
        elif position < 22:
            # 右边：11-22，x 固定 6458，y 从 109 到 6451
            x = 6458
            y = 1013 + (position - 11 -1) * (6451 - 1013) / 10
            return x * scale_x, y * scale_y
        elif position == 22:
            x = 6458
            y = 6451
            return x * scale_x, y * scale_y
        elif position < 33:
            # 底部：22-33，x 从 6458 到 102（逆序），y 固定 6451
            x = 6458 - (position - 22 - 1) * (6458 - 1028) / 10
            y = 6451
            return x * scale_x, y * scale_y
        elif position == 33:
            x = 102
            y = 6451
            return x * scale_x, y * scale_y
        else:
            # 左边：33-44（回到0），x 固定 102，y 从 6451 到 109（逆序）
            x = 102
            y = 6451 - (position - 33 - 1) * (6451 - 1013) / 10
            return x * scale_x, y * scale_y

    def draw_character(self, PC_pos, NPC_pos):
        if self.playerTurn in [PlayerTurn.PCAct, PlayerTurn.NPCMove, PlayerTurn.start] or self.initialToPlaying:
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
        else:
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
        self.screen.blit(self.PCFixImage, (116.9, 235.3))
        self.screen.blit(self.NPCFixImage, (395.5, 235.3))

    def draw_active_status(self):
        # 不需要 scale 了，因为坐标都已经用 screen.get_width() 缩放过
        offset_x = -20  # active 图标左移 30 像素，紧贴信息框左边
        offset_y = -10    # 可调垂直微调

        if self.playerTurn in [PlayerTurn.PCMove, PlayerTurn.PCAct]:
            self.screen.blit(self.activeOn, (self.PCBoard[0][0] + offset_x, self.PCBoard[0][1] + offset_y))
            self.screen.blit(self.activeOff, (self.NPCBoard[0][0] + offset_x, self.NPCBoard[0][1] + offset_y))
        elif self.playerTurn in [PlayerTurn.NPCMove, PlayerTurn.NPCAct]:
            self.screen.blit(self.activeOff, (self.PCBoard[0][0] + offset_x, self.PCBoard[0][1] + offset_y))
            self.screen.blit(self.activeOn, (self.NPCBoard[0][0] + offset_x, self.NPCBoard[0][1] + offset_y))
        else:
            self.screen.blit(self.activeOff, (self.PCBoard[0][0] + offset_x, self.PCBoard[0][1] + offset_y))
            self.screen.blit(self.activeOff, (self.NPCBoard[0][0] + offset_x, self.NPCBoard[0][1] + offset_y))


    def draw_lands(self, all_lands):
        for land in all_lands:
            pos = self.__location_convert(land.position)
            if land.owner == self.PCName and land.plant_type is not None:
                self.screen.blit(self.plantImages[land.plant_type][land.plant_level - 1], pos)
            elif land.owner == self.PCName and land.factory_level > 0:
                self.screen.blit(self.factoryImages[land.factory_level - 1], pos)
            elif land.owner == self.NPCName and land.plant_type is not None:
                self.screen.blit(self.plantImages[land.plant_type][land.plant_level - 1], pos)
            elif land.owner == self.NPCName and land.factory_level > 0:
                self.screen.blit(self.factoryImages[land.factory_level - 1], pos)
            else:
                self.screen.blit(self.wasteland, pos)

    def draw_tips(self):
        if self.gameStatus != GameStatus.over:
            scale_x, scale_y = 756 / 7562, 750 / 7506
            self.screen.blit(self.tips, (3 * 25 * scale_x, 27 * 25 * scale_y))
            tip = self.font.render(random.choice(self.tips_texts), True, (0, 255, 0))
            self.screen.blit(tip, (3 * 25 * scale_x, 27 * 25 * scale_y + 50))

    def __developer_pattern_check(self):
        return self.cheat[0] * self.cheat[1] * self.cheat[2] == 1

    def __set_developer_pattern(self, event_key):
        if event_key == K_d:
            self.cheat[0] = 1
        if self.cheat[0] == 1 and event_key == K_w:
            self.cheat[1] = 1
        if self.cheat[1] == 1 and event_key == K_q:
            self.cheat[2] = 1

    def __set_PC_act_key(self, event):
        if event.key == K_b:
            self.PCActKey[0] = event.key
        if event.key == K_p:
            self.PCActKey[1] = event.key
        if event.key == K_u:
            self.PCActKey[2] = event.key
        if event.key == K_f:
            self.PCActKey[3] = event.key

    def __music_pause(self, mouse_pos):
        if self.backgroundMusic.pause(mouse_pos):
            self.__draw_music_button_change(self.backgroundMusic.isPlaying)

    def draw_music_button(self):
        self.screen.blit(self.musicImage, self.musicButtonLocation)

    def __draw_music_button_change(self, is_playing):
        self.musicImage = self.musicOn if is_playing else self.musicOff
        self.screen.blit(self.musicImage, self.musicButtonLocation)
        display.update(self.musicButtonRect)
        time.delay(100)
        self.screen.blit(self.musicBarrier, self.musicButtonLocation)
        self.screen.blit(self.musicImage, self.musicButtonLocation)
        display.update(self.musicButtonRect)

    def __set_dice_location(self):
        self.diceLocation = [self.diceBoard[0]]

    async def draw_dice(self, final_points, random_series):
        if self.diceSteps[2] is False and self.playerTurn in [PlayerTurn.PCMove, PlayerTurn.NPCMove]:
            self.__set_dice_location()
            self.clock.tick(5)
            for rand in random_series[:10]:
                self.draw_map()
                self.draw_lands(self.landmasses.lands)
                self.draw_character(self.hero.position, self.enemy.position)
                self.draw_active_status()
                self.draw_messages((self.hero.messages(self.landmasses), self.enemy.messages(self.landmasses)))
                self.draw_music_button()
                self.draw_tips()
                self.screen.blit(self.diceImages[rand], self.diceLocation[0])
                display.update()
                await asyncio.sleep(0.1)
            self.draw_map()
            self.draw_lands(self.landmasses.lands)
            self.draw_character(self.hero.position, self.enemy.position)
            self.draw_active_status()
            self.draw_messages((self.hero.messages(self.landmasses), self.enemy.messages(self.landmasses)))
            self.draw_music_button()
            self.draw_tips()
            self.screen.blit(self.diceImages[final_points[0] - 1], self.diceLocation[0])
            display.update()
            await asyncio.sleep(2.5)
            self.dice_animation_done = True

    def draw_fix_dice(self, final_points):
        self.screen.blit(self.diceImages[final_points[0] - 1], self.diceLocation[0])

    def draw_messages(self, messages):
        PC_messages = messages[0]
        for j in range(len(PC_messages[0])):
            for k in range(len(PC_messages[0][j])):
                self.screen.blit(self.font.render(PC_messages[0][j][k], True, [0, 0, 0]),
                                (self.PCBoard[0][0] + k * 25 * 6 * 756 / 800, self.PCBoard[0][1] + j * 25 * 750 / 800))
        for j in range(len(PC_messages[1])):
            self.screen.blit(self.font.render(PC_messages[1][j], True, [0, 0, 255]),
                            (self.PCBoard[1][0], self.PCBoard[1][1] + j * 25 * 750 / 800))

        NPC_messages = messages[1]
        for j in range(len(NPC_messages[0])):
            for k in range(len(NPC_messages[0][j])):
                self.screen.blit(self.font.render(NPC_messages[0][j][k], True, [0, 0, 0]),
                                (self.NPCBoard[0][0] + k * 25 * 6 * 756 / 800, self.NPCBoard[0][1] + j * 25 * 750 / 800))
        for j in range(len(NPC_messages[1])):
            self.screen.blit(self.font.render(NPC_messages[1][j], True, [0, 0, 255]),
                            (self.NPCBoard[1][0], self.NPCBoard[1][1] + j * 25 * 750 / 800))
        


    def turn_change(self):
        if self.playerTurn == PlayerTurn.PCMove:
            self.playerTurn = PlayerTurn.PCAct
        elif self.playerTurn == PlayerTurn.NPCMove:
            self.playerTurn = PlayerTurn.NPCAct

    def turn_change_space(self):
        if self.playerTurn == PlayerTurn.start:
            self.playerTurn = PlayerTurn.PCMove
        elif self.playerTurn == PlayerTurn.PCAct:
            time.delay(1500)
            self.playerTurn = PlayerTurn.NPCMove
        elif self.playerTurn == PlayerTurn.NPCAct:
            time.delay(1500)
            self.playerTurn = PlayerTurn.PCMove
            self.initialToPlaying = False
            self.turn_count += 1

    def game_over_check(self, PC_carbon, NPC_carbon, PC_gold, NPC_gold):
        if self.gameStatus != GameStatus.end:
            if PC_gold <= 0:
                self.winner = self.NPCName
                self.gameStatus = GameStatus.over
            elif NPC_gold <= 0:
                self.winner = self.PCName
                self.gameStatus = GameStatus.over
            elif PC_carbon <= 0 or NPC_carbon <= 0 or PC_carbon > 120 or NPC_carbon > 120 or self.turn_count >= 50:
                if PC_carbon < NPC_carbon:
                    self.winner = self.PCName
                elif NPC_carbon < PC_carbon:
                    self.winner = self.NPCName
                else:
                    self.winner = "平局"
                self.gameStatus = GameStatus.over

    def draw_game_over(self, PC_carbon, NPC_carbon):
        self.gameStatus = GameStatus.end
        self.screen.blit(self.diceBarrier, (18 * 25 * 756 / 800, 17 * 25 * 750 / 800))
        text = self.font.render(f"Winner: {self.winner}! Reduced {max(PC_carbon, NPC_carbon)} tons of CO2!", True, (0, 255, 0))
        self.screen.blit(text, (175 * 756 / 800, 325 * 750 / 800))
        self.screen.blit(self.gameWin if self.winner == self.PCName else self.gameFail, (175 * 756 / 800, 325 * 750 / 800))
        display.update()

    def __play_again(self):
        self.gameStatus = GameStatus.start
        self.playerTurn = PlayerTurn.start
        self.PCActKey = [0, 0, 0, 0]
        self.cheat = [0, 0, 0]
        self.diceLocation = [self.diceBoard[0]]
        self.diceSteps = (0, 0, True)
        self.turn_count = 0
        self.dice_animation_done = False

    def __quit(self):
        if self.backgroundMusic.isPlaying:
            mixer.music.fadeout(1500)
            time.delay(1500)
        pygame.quit()
        self.gameStatus = GameStatus.quit

    def __initialize_game(self):
        from Player.PC import PC
        from Player.NPC import NPC
        from LandManage import Landmasses
        from ShootDice import ShootDice
        self.hero = PC("Eco")
        self.hero.game_manager = self
        self.enemy = NPC("In")
        self.enemy.game_manager = self
        self.landmasses = Landmasses(self.hero.name, self.enemy.name)
        self.shootDice = ShootDice()
        self.get_character_name(self.hero.name, self.enemy.name)

    async def __play_game(self):
        self.clock.tick(10)
        self.hero.update(self.landmasses)
        self.enemy.update(self.landmasses)
        self.draw_map()
        self.draw_lands(self.landmasses.lands)
        self.draw_character(self.hero.position, self.enemy.position)
        self.draw_active_status()
        self.draw_messages((self.hero.messages(self.landmasses), self.enemy.messages(self.landmasses)))
        self.draw_fix_dice(self.shootDice.finalPoints)
        self.draw_music_button()
        self.game_over_check(self.hero.carbon, self.enemy.carbon, self.hero.gold, self.enemy.gold)
        self.draw_tips()

        if self.playerTurn == PlayerTurn.PCMove:
            if self.hero.skip_turn:
                self.hero.skip_turn = False
                self.dice_animation_done = False
                self.turn_change()
                return
            self.diceSteps = self.hero.move()
            self.shootDice.set_dice(self.diceSteps)
            await self.draw_dice(self.shootDice.finalPoints, self.shootDice.randomSeries)
            if self.dice_animation_done:
                self.hero.position = (self.hero.position + self.diceSteps[0]) % 44
                effect = self.hero.incidents(self.landmasses)
                if effect == "trade" and self.hero.chance:
                    self.hero.gold, self.enemy.gold = self.enemy.gold, self.hero.gold
                    self.hero.chance = False
                self.dice_animation_done = False

        elif self.playerTurn == PlayerTurn.PCAct:
            land = self.landmasses.lands[self.hero.position]
            if self.PCActKey[0] == K_b:
                self.hero.buy(land, self.landmasses.is_full(self.hero.name))
            elif self.PCActKey[1] == K_p:
                self.hero.plant(land, 0)
            elif self.PCActKey[2] == K_u:
                self.hero.upgrade(land)
            elif self.PCActKey[3] == K_f:
                self.hero.build_factory(land)
            self.PCActKey = [0, 0, 0, 0]

        elif self.playerTurn == PlayerTurn.NPCMove:
            if self.enemy.skip_turn:
                self.enemy.skip_turn = False
                self.dice_animation_done = False
                self.turn_change()
                return
            self.diceSteps = self.enemy.move()
            self.shootDice.set_dice(self.diceSteps)
            await self.draw_dice(self.shootDice.finalPoints, self.shootDice.randomSeries)
            if self.dice_animation_done:
                self.enemy.position = (self.enemy.position + self.diceSteps[0]) % 44
                effect = self.enemy.incidents(self.landmasses)
                if effect == "trade" and self.enemy.chance:
                    self.hero.gold, self.enemy.gold = self.enemy.gold, self.hero.gold
                    self.enemy.chance = False
                self.dice_animation_done = False

        elif self.playerTurn == PlayerTurn.NPCAct:
            self.enemy.act(self.landmasses)
            self.post_space_key_down()

        self.turn_change()
        self.image_update()

    async def draw_card_message(self, card_name):
        display_duration = 3000
        start_time = time.get_ticks()
        scale_x, scale_y = 756 / 7562, 750 / 7506
        while time.get_ticks() - start_time < display_duration:
            self.draw_map()
            self.draw_lands(self.landmasses.lands)
            self.draw_character(self.hero.position, self.enemy.position)
            self.draw_active_status()
            self.draw_messages((self.hero.messages(self.landmasses), self.enemy.messages(self.landmasses)))
            self.draw_fix_dice(self.shootDice.finalPoints)
            self.draw_music_button()
            self.draw_tips()
            background = pygame.Surface((200 * scale_x, 50 * scale_y), pygame.SRCALPHA)
            background.fill((0, 0, 0, 128))
            self.screen.blit(background, (18 * 25 * scale_x, 17 * 25 * scale_y + 30))
            card_text = self.font.render(f"卡片: {card_name}", True, (255, 50, 100))
            self.screen.blit(card_text, (18 * 25 * scale_x, 17 * 25 * scale_y + 50))
            display.update()
            self.clock.tick(60)
            await asyncio.sleep(0.016)

if platform.system() == "Emscripten":
    asyncio.ensure_future(GameManager().main_loop())
else:
    if __name__ == "__main__":
        asyncio.run(GameManager().main_loop())