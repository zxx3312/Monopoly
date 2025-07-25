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
        self.font = font.Font(self.source + "simhei.ttf", 20)
        self.screen = display.set_mode((800, 800))
        display.set_icon(self.__image_load("Dog.ico"))
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
        self.dice_animation_done = False  # 新增标志，控制骰子动画完成

        self.start = self.__image_load("Start.png")
        self.gameFail = self.__image_load("GameFail.png")
        self.gameWin = self.__image_load("GameWin.png")
        self.gameMap = self.__image_load("EcoMap.png")
        self.tips = self.__image_load("Tips.png")
        self.musicOn = self.__image_load("MusicOn.png")
        self.musicOff = self.__image_load("MusicOff.png")
        self.musicImage = self.musicOn
        self.musicBarrier = self.__image_load("MusicBarrier.png")
        self.musicButtonLocation = (41 * 25, 27 * 25)
        self.musicButtonRect = Rect(41 * 25, 27 * 25, 100, 75)
        self.activeOn = self.__image_load("ActiveOn.png")
        self.activeOff = self.__image_load("ActiveOff.png")

        self.PCName = ""
        self.PCImage = self.__image_load("PC.png")
        self.PCFixImage = self.__image_load("PCFix.png")
        self.PCBoard = [(5 * 25, 4 * 25 + 12), (5 * 25, 8 * 25)]
        self.NPCName = ""
        self.NPCImage = self.__image_load("NPC.png")
        self.NPCFixImage = self.__image_load("NPCFix.png")
        self.NPCBoard = [(27 * 25, 4 * 25 + 12), (27 * 25, 8 * 25)]

        self.diceImages = [self.__image_load(f"Dice{j+1}.png") for j in range(6)]
        self.diceBarrier = self.__image_load("DiceBarrier.png")
        self.diceBoard = [(22 * 25, 18 * 25 + 5), (19 * 25 + 12, 18 * 25 + 5), (24 * 25 + 13, 18 * 25 + 5)]
        self.diceLocation = [self.diceBoard[0]]
        self.diceSteps = (0, 0, True)

        self.plantImages = [[self.__image_load(f"any.png") for i in range(1, 5)] for plant in ["Seaweed", "WaterGrass", "Sunflower", "Tree", "Forest"]]
        self.factoryImages = [self.__image_load(f"any.png") for i in range(1, 5)]
        self.wasteland = self.__image_load("Wasteland.png")
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

    def __image_load(self, name):
        try:
            img = image.load(self.source + name).convert_alpha()
            if name == "EcoMap.png":
                img = pygame.transform.scale(img, (800, 800))
            return img
        except pygame.error:
            return image.load(self.source + "Wasteland.png").convert_alpha()

    def draw_beginning(self):
        for j in range(150):
            self.clock.tick(300)
            self.screen.blit(self.gameMap, (0, 0))
            self.screen.blit(self.PCFixImage, (6 * 25 + 13 + j * 1 - 10, 6 * 25 + 13 - 10))
            self.screen.blit(self.NPCFixImage, (38 * 25 + 13 - j * 1 - 10, 6 * 25 + 13 - 10))
            self.screen.blit(self.start, (175, 325))
            self.screen.blit(self.musicImage, self.musicButtonLocation)
            display.update()

    def draw_map(self):
        self.screen.blit(self.gameMap, (0, 0))

    def __location_convert(self, position):
        grid_size = 72
        if position < 11:
            return position * grid_size, 0
        elif position < 22:
            return 10 * grid_size, (position - 10) * grid_size
        elif position < 33:
            return (32 - position) * grid_size, 10 * grid_size
        elif position < 44:
            return 0, (43 - position) * grid_size
        else:
            return 0, 0

    def draw_character(self, PC_pos, NPC_pos):
        if self.playerTurn in [PlayerTurn.PCAct, PlayerTurn.NPCMove, PlayerTurn.start] or self.initialToPlaying:
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
        else:
            self.screen.blit(self.PCImage, self.__location_convert(PC_pos))
            self.screen.blit(self.NPCImage, self.__location_convert(NPC_pos))
        self.screen.blit(self.PCFixImage, (19 * 25 - 21, 4 * 25))
        self.screen.blit(self.NPCFixImage, (41 * 25 - 21, 4 * 25))

    def draw_active_status(self):
        if self.playerTurn in [PlayerTurn.PCMove, PlayerTurn.PCAct]:
            self.screen.blit(self.activeOn, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOn, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 8 * 25))
        elif self.playerTurn in [PlayerTurn.NPCMove, PlayerTurn.NPCAct]:
            self.screen.blit(self.activeOff, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOn, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOn, (26 * 25, 8 * 25))
        else:
            self.screen.blit(self.activeOff, (4 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (4 * 25, 8 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 4 * 25))
            self.screen.blit(self.activeOff, (26 * 25, 8 * 25))

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
            self.screen.blit(self.tips, (3 * 25, 27 * 25))
            tip = self.font.render(random.choice(self.tips_texts), True, (0, 255, 0))
            self.screen.blit(tip, (3 * 25, 27 * 25 + 50))

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
                # self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
                # self.screen.blit(self.diceImages[rand], self.diceLocation[0])
                display.update()
                await asyncio.sleep(0.1)  # 每帧延时0.1秒，模拟动画
            # self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
            # self.screen.blit(self.diceImages[final_points[0] - 1], self.diceLocation[0])
            display.update()
            await asyncio.sleep(0.1)  # 动画完成后延时0.1秒
            self.dice_animation_done = True  # 动画完成，允许移动

    def draw_fix_dice(self, final_points):
        self.screen.blit(self.diceImages[final_points[0] - 1], self.diceLocation[0])

    def draw_messages(self, messages):
        PC_messages = messages[0]
        for j in range(len(PC_messages[0])):
            for k in range(len(PC_messages[0][j])):
                self.screen.blit(self.font.render(PC_messages[0][j][k], True, [0, 0, 0]), (self.PCBoard[0][0] + k * 25 * 6, self.PCBoard[0][1] + j * 25))
        for j in range(len(PC_messages[1])):
            self.screen.blit(self.font.render(PC_messages[1][j], True, [0, 0, 255]), (self.PCBoard[1][0], self.PCBoard[1][1] + j * 25))

        NPC_messages = messages[1]
        if self.__developer_pattern_check():
            for j in range(len(NPC_messages[0])):
                for k in range(len(NPC_messages[0][j])):
                    self.screen.blit(self.font.render(NPC_messages[0][j][k], True, [0, 0, 0]), (self.NPCBoard[0][0] + k * 25 * 6, self.NPCBoard[0][1] + j * 25))
            for j in range(len(NPC_messages[1])):
                self.screen.blit(self.font.render(NPC_messages[1][j], True, [0, 0, 255]), (self.NPCBoard[1][0], self.NPCBoard[1][1] + j * 25))
        else:
            self.screen.blit(self.font.render("依次按下DWQ进入开发者模式", True, [0, 0, 255]), (27 * 25, 7 * 25))
            self.screen.blit(self.font.render("查看NPC的状态", True, [0, 0, 255]), (27 * 25, 8 * 25))

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
        self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))
        text = self.font.render(f"Winner: {self.winner}! Reduced {max(PC_carbon, NPC_carbon)} tons of CO2!", True, (0, 255, 0))
        self.screen.blit(text, (175, 325))
        self.screen.blit(self.gameWin if self.winner == self.PCName else self.gameFail, (175, 325))
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
        self.hero = PC("EcoWorker")
        self.enemy = NPC("IndustryRep")
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

    def draw_card_message(self, card_name):
        self.screen.blit(self.diceBarrier, (18 * 25, 17 * 25))  # 清空骰子区域
        card_text = self.font.render(f"卡片: {card_name}", True, (255, 0, 0))  # 红色文字显示卡片名称
        self.screen.blit(card_text, (18 * 25, 17 * 25 + 50))  # 显示在骰子区域下方
        display.update()
        time.delay(3000)  # 延时3秒

if platform.system() == "Emscripten":
    asyncio.ensure_future(GameManager().main_loop())
else:
    if __name__ == "__main__":
        asyncio.run(GameManager().main_loop())