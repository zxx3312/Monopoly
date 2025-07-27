import pygame
from pygame.locals import *
from GameManager import GameManager
from Enums import GameStatus, PlayerTurn, Incidents
from LandManage import Landmasses
from ShootDice import ShootDice
from Player.NPC import NPC
from Player.PC import PC

if __name__ == "__main__":
    gameManager = GameManager()
    hero, enemy, landmasses, shootDice = None, None, None, None
    while gameManager.gameStatus != GameStatus.quit:
        gameManager.event_deal()

        if gameManager.gameStatus == GameStatus.start:
            gameManager.draw_beginning()
            gameManager.gameStatus = GameStatus.waitIn

        if gameManager.gameStatus == GameStatus.initial:
            if hero:
                del hero
            hero = PC("EcoWorker")
            if enemy:
                del enemy
            enemy = NPC("IndustryRep")
            if landmasses:
                del landmasses
            landmasses = Landmasses(hero, enemy)
            if shootDice:
                del shootDice
            shootDice = ShootDice()
            gameManager.get_character_name(hero.name, enemy.name)
            gameManager.gameStatus = GameStatus.playing
            gameManager.initialToPlaying = True

        if gameManager.gameStatus == GameStatus.playing:
            gameManager.clock.tick(10)
            gameManager.draw_map()
            gameManager.draw_lands(landmasses.lands)
            gameManager.draw_character(hero.position, enemy.position)
            gameManager.draw_active_status()
            gameManager.draw_messages((hero.messages(landmasses), enemy.messages(landmasses)))
            gameManager.draw_fix_dice(shootDice.finalPoints)
            gameManager.draw_music_button()
            gameManager.game_over_check(hero.carbon, enemy.carbon, hero.gold, enemy.gold)
            gameManager.draw_tips()

            if gameManager.playerTurn == PlayerTurn.PCMove:
                gameManager.diceSteps = hero.move()
                hero.position = (hero.position + gameManager.diceSteps[0]) % 44
                effect = hero.incidents(landmasses)
                if effect == "trade" and hero.chance:
                    hero.gold, enemy.gold = enemy.gold, hero.gold
                    hero.chance = False
                shootDice.set_dice(gameManager.diceSteps)

            elif gameManager.playerTurn == PlayerTurn.PCAct:
                land = landmasses.lands[hero.position]
                # print(gameManager.PCActKey[0], K_b)
                if gameManager.PCActKey[0] == K_b:
                    hero.buy(land, landmasses.is_full(hero.name))
                elif gameManager.PCActKey[1] == K_p:
                    hero.plant(land, 0)  # 默认种植海藻
                elif gameManager.PCActKey[2] == K_u:
                    hero.upgrade(land)
                elif gameManager.PCActKey[3] == K_f:
                    hero.build_factory(land)
                gameManager.PCActKey = [0, 0, 0, 0]

            elif gameManager.playerTurn == PlayerTurn.NPCMove:
                gameManager.diceSteps = enemy.move()
                enemy.position = (enemy.position + gameManager.diceSteps[0]) % 44
                effect = enemy.incidents(landmasses)
                if effect == "trade" and enemy.chance:
                    hero.gold, enemy.gold = enemy.gold, hero.gold
                    enemy.chance = False
                shootDice.set_dice(gameManager.diceSteps)

            elif gameManager.playerTurn == PlayerTurn.NPCAct:
                enemy.act(landmasses)
                gameManager.post_space_key_down()

            gameManager.draw_dice(shootDice.finalPoints, shootDice.randomSeries)
            gameManager.turn_change()
            gameManager.image_update()

        # if gameManager.gameStatus == GameStatus.playing:
        #     print(f"Current turn: {gameManager.playerTurn}")

        if gameManager.gameStatus == GameStatus.over:
            gameManager.draw_game_over(hero.carbon, enemy.carbon)

        
        # if gameManager.playerTurn == PlayerTurn.PCMove:
        #     print("PCmove")
        #     if hero.skip_turn:
        #         hero.skip_turn = False
        #         gameManager.turn_change()
        #         continue

        # if gameManager.playerTurn == PlayerTurn.NPCMove:
        #     print("NPCmove")
        #     if enemy.skip_turn:
        #         enemy.skip_turn = False
        #         gameManager.turn_change()
        #         continue
