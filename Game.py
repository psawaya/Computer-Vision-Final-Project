#!/usr/bin/env python

import pygame
import pygame.font

from pygame.locals import *

from random import randint

from PointTracker import PointTracker

class CVGame:
    def __init__(self):
        self.point_tracker = PointTracker()
        
        pygame.init()
        
        self.font = pygame.font.Font (pygame.font.get_default_font(),20)
        
        self.screen = pygame.display.set_mode((640, 480))
        pygame.display.set_caption('Paul Tracker Game')
        pygame.mouse.set_visible(0)

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.background.fill((0, 0, 0))
        
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()
        self.clock = pygame.time.Clock()
        
        self.playerX = 50
        self.playerY = 50
        
        self.vX = 0
        self.vY = 0
        
        self.enemyX = 400
        self.enemyY = 450
        
        self.targetX = 200
        self.targetY = 250
        
        self.score = 0
        
        self.loop()
    
    def loop(self):
        #Main Loop
        while 1:
            self.point_tracker.loop()
            self.clock.tick(60)
            
            ignoreInput = False

            #Handle Input Events
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    pass
                elif event.type is MOUSEBUTTONUP:
                    pass

            self.background.fill((0,0,0))

            movement = self.point_tracker.pollAbsoluteMovement()

            self.vX = min(10,self.vX + movement[0]*2)
            self.vY = min(10,self.vY + movement[1]*2)
                        
            if not(pygame.key.get_pressed()[K_a]):
                self.playerX = min (max (0, self.playerX + self.vX), 640)
                self.playerY = min (max (0, self.playerY + self.vY), 480)
            
            self.vX = max(0, self.vX - 0.5)
            self.vY = max(0, self.vY - 0.5)
            
            self.playerX = movement[0]
            self.playerY = movement[1]

            pygame.draw.circle(self.background, (0,0,255), (self.playerX,self.playerY), 30, 2)
            pygame.draw.circle(self.background, (0,255,0), (self.targetX,self.targetY), 20, 10)
            pygame.draw.circle(self.background, (255,0,0), (self.enemyX,self.enemyY), 20, 10)
            
            if self.playerCollideRect(pygame.Rect(self.targetX,self.targetY,20,20)):
                self.targetX = randint(0,640-20)
                self.targetY = randint(0,480-20)
                
                self.enemyX = randint(0,640-20)
                self.enemyY = randint(0,480-20)
                
                self.score += 1
            
            if self.playerCollideRect(pygame.Rect(self.enemyX,self.enemyY,20,20)):
                self.score -= 1

            self.writeToScreen("score: %s" % self.score)

            #Draw Everything
            self.screen.blit(self.background, (0, 0))
#            allsprites.draw(screen)
            pygame.display.flip()

    
    def writeToScreen(self,text):
        font_surf = pygame.Surface((150,50))
        self.background.blit(self.font.render(text,False,(0,255,0)), (0,0))
        
    def playerCollideRect(self,rect):
        player_rect = pygame.Rect(self.playerX,self.playerY,30,30)
        return player_rect.colliderect(rect)

def thresh(x,y):
    if x > y:
        return x
    else:
        return 0

if __name__ == "__main__":
    CVGame()