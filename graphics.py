'''
Created on 2012-12-02

@author: Sebastien Ouellet sebouel@gmail.com
'''

import pygame

####### Parameters #######

framerate = 20

white = (255,255,255)
black = (0,0,0)
light_blue = (0,191,255)
green1 = (60,179,113)
orange1 = (255,0,0)
grey = (220,220,220)
blue = (30,144,255)
green = (39,162,20)
red = (192,39,22)
orange = (255,139,40)

screen_width = 768
screen_height = 768

block_size = 12

##########################

class Unit(pygame.sprite.Sprite):
    """ Generic class for block sprites """
    def __init__(self,pos,type):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((block_size,block_size))
        if type == "circle":
            self.image.fill(blue)
            #pygame.draw.circle(self.image,blue,(block_size+2,block_size+2),3,2)
        elif type == "square":
            self.image.fill(green)
        elif type == "flag":
            self.image.fill(red)
        elif type == "base":
            self.image.fill(orange)
        self.rect = self.image.get_rect()
        self.position = self.calculate_position(pos)
        self.rect.center = self.position

    def calculate_position(self,pos):
        """ Returns the position on the screen """
        x = shift(pos[0])
        y = shift(pos[1])
        return (x,y)

def shift(coordinate):
    """ Projects a coordinate into a pixel location """
    return (coordinate+1)*(block_size+1)

def generate_unit(position, type, group):
    """ Creates a sprite and adds it to a group of sprites """
    group.add(Unit(position,type))

def update_sprites(group, everything):
    """ Empty a group and recreates all sprites """
    group.empty()
    generate_unit(everything[1], "base", group)
    for square in everything[2]:
        generate_unit(square.position, "square", group)
    for circle in everything[3]:
        generate_unit(circle.position, "circle", group)
    generate_unit(everything[0], "flag", group)
    
def input():
    """ Allows the user to exit the game and adjust the framerate """
    global framerate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
            framerate += 10
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            framerate += -8
        return False
    
