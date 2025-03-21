#!/usr/bin/env python3
# -*- coding: utf-8 -*- #

"""
Avocados and stuff
"""

import os, random, sys
import pygame
import avocado, crystal, pingenerator, itext
from pygame.locals import *
from support.colors import *
from interface import hud


class TheGame:

    def __init__(self):
        """ Initialize the game """
        pygame.init()
        pygame.display.set_caption('Pin Avo, the Cado!')
        self.clock = pygame.time.Clock()
        self.initializeScreen()

        # initialize the game canvas
        self.timeout = 30
        self.level = 1
        self.psychomode = 2
        self.targetScore = 400
        ##############################
        # Never set below 4, else we have a high
        # probability of losing the game due to a missing color
        # Alternatively, you could edit chooseRandomColor()
        # to only work on the first multiplier colors
        self.desired_fps = 60
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.colors = [RED, GREEN, BLUE, YELLOW, PINK]
        self.multiplier = len(self.colors)
        self.bg = pygame.image.load(os.path.join('img', 'lawyerCrystalBall.png'))
        self.bg.set_colorkey((255,255,255))
        self.bg.set_alpha(75)
        self.last_colors = []

        # fonts
        self.bigFont = pygame.font.Font(None, 90)

        # Set splashscreen
        splashScreen = pygame.image.load(os.path.join('img', 'splashScreen.png'))
        self.screen.blit(
            pygame.transform.scale(
                splashScreen, (self.WIDTH, self.HEIGHT)
            ),
            (0, 0)
        )

        pygame.display.flip()
        pygame.time.wait(3000)

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(0.5)
            sound = True
        except:
            print("Y U NO sound? :(")
            sound = False


    def initializeScreen(self):
        # displayInfo = pygame.display.Info()
        # self.resize = 1.3

        # self.WIDTH = int(displayInfo.current_w / self.resize)
        # self.HEIGHT = int(displayInfo.current_h / self.resize)

        # Look at the cleverness ;)
        self.WIDTH, self.HEIGHT = 800, 600


    def mute(self,mute=False, sound=True):
        if not sound:
            return
        if mute:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(0.5)


    def playLevel(self,lvl=1,sound=True):
        if not sound:
            return
        if lvl == 1:
            pygame.mixer.music.load("""audio/level1.wav""")
        elif lvl == 2:
            pygame.mixer.music.load("""audio/level2.wav""")
        elif lvl >= 3:
            pygame.mixer.music.load("""audio/level3.wav""")
        pygame.mixer.music.play()

    def toggle_fullscreen(self):
        global fullS
        fullS = True
        self.screen = pygame.display.get_surface()
        self.tmp = self.screen.convert()
        self.caption = pygame.display.get_caption()
        self.cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007

        self.w,self.h = self.screen.get_width(),self.screen.get_height()
        self.flags = self.screen.get_flags()
        self.bits = self.screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        self.screen = pygame.display.set_mode((self.w,self.h),self.flags^FULLSCREEN,self.bits)
        self.screen.blit(self.tmp,(0,0))
        pygame.display.set_caption(*self.caption)

        pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??

        pygame.mouse.set_cursor( *self.cursor )  # Duoas 16-04-2007

        return self.screen


    def fadeSound(self, sound=True):
        if not sound:
            return
        pygame.mixer.music.fadeout(3000)


    def chooseRandomColor(self):
        selected = random.randint(0, len(self.colors) - 1)
        if len(self.last_colors) > 5:
            self.last_colors.pop(0)
        for i in range(0, 5):
            if selected in self.last_colors:
                selected = random.randint(0, 3)
            else:
                break
        self.last_colors.append(selected)
        return self.colors[selected]

    def gameOver(self):
        screen_width, screen_height = self.screen.get_size()
        gameOverImage = pygame.image.load(os.path.join('img', 'gameOver.png'))
        gameOverText = self.bigFont.render('GAME OVER', False, YELLOW)
        gameOverImage.blit(gameOverText, (screen_width/8, screen_height/7))
        self.screen.blit(pygame.transform.scale(gameOverImage,
                         self.screen.get_size()), (0, 0))
        pygame.display.flip()
        self.fadeSound()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()


    def keepPinned(self, avocado):
        self.pinned.append(avocado)


    def drawBackground(self):
        if type(self.bg) is tuple:
            self.screen.fill(self.bg)
        else:
            self.screen.blit(
                pygame.transform.scale(
                    self.bg, self.screen.get_size()
                ),
                (0, 0)
            )


    def resetLevel(self):
        self.pinnedAvocados = []
        self.movingAvocados = []
        self.thrownPins = []
        self.timeleft = self.timeout


    def main(self):
        score = 0
        boundaries = []

        # We could use this list for redrawing only this part
        # of the screen instead of all of it
        self.resetLevel()

        # initialize the HUD class and the lawyer
        the_hud = hud.Hud(self.screen)
        crystalBall = crystal.Crystal(self.screen, self.level, self.bigFont, self.psychomode)
        boundaries.append(crystalBall.getBoundaries())

        # Initial color indication
        color = self.chooseRandomColor()
        crystalBall.setColor(color)

        texts = []
        container = {'font': self.bigFont, 'screen': self.screen, 'clock': self.clock}

        running = True
        while running:
            time_passed = self.clock.tick(self.desired_fps)
            fps = self.clock.get_fps()
            screen_width, screen_height = self.screen.get_size()

            # Next level?
            if score >= (self.targetScore * self.level):
                self.level += 1
                levelText = itext.Text(
                    container,
                    'Level ' + str(self.level),
                    (screen_width / 3, screen_height /2),
                    2000
                )
                texts.append(levelText)
                self.playLevel(self.level)
                self.resetLevel()


            self.timeleft -= time_passed / 1000
            self.timeleft = round(self.timeleft, 2)
            if self.timeleft <= 0:
                self.gameOver()
            else:
                displaytime = self.timeleft


            # Redraw the background and put our lawyer back on top
            self.drawBackground()
            crystalBall.blitme()

            # Check if there's any text that wants to get displayed
            for text in texts:
                text.blitme()
                texts[:] = [text for text in texts if not text.hasExpired() ]

            # Redraw the HUD
            the_hud.draw_hud(score, displaytime, round(fps, 2))

            # Initialize a number of avocados, depending on the level
            avocadosInGame = len(self.movingAvocados)
            avocadosWanted = self.level * self.multiplier

            if avocadosInGame < avocadosWanted:
                probability = int(1.0/(avocadosWanted - avocadosInGame) * 100)
                if random.randint(0, probability) < 3:
                    properties = {'color': self.chooseRandomColor(), 'size': (50,50)}
                    # Spawn a new avocado
                    a = avocado.Avocado(
                        self.screen,
                        boundaries,
                        properties,
                        color,
                        self.level
                    )
                    self.movingAvocados.append(a)

            # Remove avocados from the list of moving avocados if they no longer move
            # Or add them to the list of pinned avocados if they're been hit
            self.pinnedAvocados += [avo for avo in self.movingAvocados if avo.isPinned() ]
            self.movingAvocados[:] = [ avo for avo in self.movingAvocados if avo.isFalling() ]

            ##############################
            #
            # Late-Night-Comments:
            #
            # Can we maybe handle the pinned avocados the same way I handle "stuck"
            # pins? It seems to be easier.. well, the pins don't fall out of the screen
            # though…
            #
            ##############################

            # Now redraw our avocados
            for a in self.movingAvocados:
                a.setTargetColor(color)
                a.move()
                a.blitme()

            for a in self.pinnedAvocados:
                a.blitme()

            # And finally check if we need to redraw any pins
            for activePin in self.thrownPins:
                activePin.blitme()
                if not activePin.isStuck():
                    activePin.moveTowardsTarget()

            # Catch events
            for event in pygame.event.get():
                # Collision detection
                if event.type == MOUSEBUTTONDOWN:
                    mousepos = pygame.mouse.get_pos()

                    # Throwing a new pin
                    newPin = pingenerator.Generate(self.screen)
                    newPin.throwAt(mousepos)
                    self.thrownPins.append(newPin)

                    # Check if any avocados have been hit
                    for avo in self.movingAvocados:
                        hit, center = avo.isHit(mousepos)
                        if hit is None:
                            continue
                        if hit:
                            score += 100
                            newPin.throwAt(center)
                            color = self.chooseRandomColor()
                            crystalBall.setColor(color)
                        else:
                            score -= 50


                # Had enough of this?
                if event.type == pygame.QUIT:
                    running = False
                    game.gameOver()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_f] != 0:
                        print("Toggling full screen, in the Future")
                        #game.toggle_fullscreen()
                elif (pygame.key.get_pressed()[pygame.K_q] != 0) or (pygame.key.get_pressed()[pygame.K_ESCAPE] != 0):
                    running = False
                    game.gameOver()
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()


if __name__ == '__main__':
    game = TheGame()
    game.playLevel()
    game.main()
