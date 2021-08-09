#!./venv/bin/python3

import pygame

pygame.init()

size = width, height = 640, 400 # screen size
screen = pygame.display.set_mode(size) # init screen
bg_color = (74,236,239) # background color
assets = './assets' # assets directory


class Dino:
    def __init__(self):
        self.dino_img = pygame.image.load(f'{assets}/dino.png') # dino asset

    def move(self, x, y):
        screen.blit(self.dino_img, (x,y)) # show dino asset in x, y position

def main():
    dino = Dino() # creating dino
    dino_size = 100 # dino image size (px)
    dino_x = (width // 2) - (dino_size // 2) # screen center
    dino_y = height - dino_size # screen bottom

    while 1:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # exit on window close
                pygame.quit()
                quit()
        
        screen.fill(bg_color) # background color
        dino.move(dino_x, dino_y) # move dino
        update_frame()

def update_frame():
    pygame.display.update()

if __name__ == '__main__':
    main()
