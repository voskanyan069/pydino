#!./venv/bin/python3

import pygame
import random

pygame.init() # init pygame

size = width, height = 640, 400 # screen size
screen = pygame.display.set_mode(size) # init screen
bg_color = (74,236,239) # background color
assets = './assets' # assets directory

class Dino:
    def __init__(self):
        self.image = pygame.image.load(f'{assets}/dino.png') # dino asset
        print('Created dino') # info log

    def move(self, x, y):
        screen.blit(self.image, (x,y)) # show dino in x, y position

class Cloud:
    def __init__(self, x, y):
        self.image = pygame.image.load(f'{assets}/cloud.png') # cloud asset
        self.speed = random.uniform(0.05, 0.1) # cloud speed
        self.direction = {
            'left': -1 * self.speed,
            'right': self.speed
        }
        self.current_dir = self.direction['left'] # default start direction
        self.x = x # define x position
        self.y = y # define y position
        print(f'Created cloud with speed {self.speed} in [{x};{y}]') # info log

    def move(self):
        if self.x <= 5: # if touch left border
            self.current_dir = self.direction['right']
        elif self.x >= (width - 105): # if touch right border
            self.current_dir = self.direction['left']
        self.x += self.current_dir
        screen.blit(self.image, (self.x, self.y)) # show cloud in  x, y position

class Text:
    def __init__(self, text, font_size, position):
        self.text = text # text to display
        self.font_family = f'{assets}/font.ttf' # font path
        self.font_size = font_size # font size
        self.text_color = (56,61,61) # text color
        self.font = pygame.font.Font(self.font_family, self.font_size) # font
        self.img = self.font.render(text, True, self.text_color) # rendered text
        self.position = position # text position
        print(f'Created text - {text}') # info log

    def update(self):
        screen.blit(self.img, self.position) # update text to show

    def change_text(self, text):
        self.text = text # rewrite displayed text

def main():
    game = True

    dino = Dino() # creating dino
    dino_size = 100 # dino image size (px)
    dino_x = (width // 2) - (dino_size // 2) # screen center
    dino_y = height - dino_size # screen bottom

    clouds = [] # clouds list
    cloud_size = 100 # cloud image size (px)

    score = Text('Score: 0', 20, (10, 10)) # scores text

    for i in range(random.randint(5, 8)): # create random count of clouds
        clouds.append(Cloud(
            random.randint(0, (width-cloud_size)),     # x
            random.randint(20, (height-cloud_size-50)) # y
        ))

    while game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # exit on window close
                game = False
        
        screen.fill(bg_color) # background color
        dino.move(dino_x, dino_y) # move dino
        for cloud in clouds: # loop all clouds
            cloud.move() # move cloud to current possible direction
        score.update() # refresh scores

        update_frame()

def update_frame():
    pygame.display.update() # update frame

if __name__ == '__main__':
    main()
