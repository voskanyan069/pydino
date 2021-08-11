#!./venv/bin/python3

import json
import random
import _thread
import sys, getopt

import pygame
import pygame_widgets as pw
from pygame_widgets.button import Button

pygame.init() # init pygame

size = width, height = 640, 400 # screen size
screen = pygame.display.set_mode(size) # init screen
bg_color = (142,202,230) # background color
assets = './assets' # assets directory
data_path = f'{assets}/.data.json' # data file path

app_icon = pygame.image.load(f'{assets}/icon.png') # find icon image
pygame.display.set_caption('Dino') # set window title
pygame.display.set_icon(app_icon) # set app icon

menu = True # is menu showing
game = True # is game running
scores = 0 # game scores
high_score = 0 # all time high score
play_time = 0 # game play time seconds
health = 5 # game healths
data = 0 # temp start value for data

class Dino:
    def __init__(self, x, y):
        self.image = pygame.image.load(f'{assets}/dino.png') # dino asset
        self.speed = 0.2 # dino speed
        self.x = x # dino x
        self.y = y # dino y
        self.direction = {
            'left': -1 * self.speed,
            'right': self.speed
        }
        print(f'Created dino in [{x};{y}]') # info log

    def move(self, direction):
        if direction == 0 and self.x >= 5: # moved left
            self.x -= self.speed
        elif direction == 1 and self.x <= width-50: # moved right
            self.x += self.speed
        print(f'Dino moved to [{self.x};{self.y}]') # info log

    def add_speed(self, speed):
        self.speed += speed # add dino speed
        print(f'Dino speed added by {speed}') # info log

    def change_speed(self, new_speed):
        self.speed = new_speed # set new speed
        print(f'Dino speed changed - {new_speed}') # info log

    def show(self):
        screen.blit(self.image, (self.x,self.y)) # show dino in x, y position

    def get_params(self):
        return self.x-20, self.y-50, self.x+50, self.y+100 # x, y, w, h

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
        self.x += self.current_dir # move to current direction
        screen.blit(self.image, (self.x, self.y)) # show cloud in  x, y position

class Part:
    def __init__(self, dino, scores_text, health_text):
        self.dino = dino # dino
        self.scores_text = scores_text # scores text
        self.health_text = health_text # health text
        self.speed = 0.3 # part start speed
        self.part_w = 30 # part width
        self.x = random.randint(0, (width-self.part_w)) # start x point
        self.y = 0 # start y point
        self.dx, self.dy, self.dw, self.dh = 0, 0, 0, 0
        print(f'Part was created at {self.x}') # info log

    def reset(self):
        self.x = random.randint(0, (width-self.part_w)) # new random x position
        self.y = 0 # to window top

    def move(self):
        global scores
        global health
        self.dx, self.dy, self.dw, self.dh = \
                self.dino.get_params() # get geometry params of dino
        self.y += self.speed # move down the part
        
        # part is touching bottom border
        if self.y >= height:
            self.on_part_bottom()
        # x is between dino start and end
        if self.x > self.dx and self.x < self.dw:
            # y is between dino top and bottom
            if self.y > self.dy and self.y < self.dh:
                self.on_part_eat() # part touching dino

        screen.blit(self.image, (self.x,self.y)) # show part in x, y position

    def on_part_bottom(self):
        pass

    def on_part_eat(self):
        pass

class DinoPart(Part):
    def __init__(self, dino, scores_text, health_text):
        super(DinoPart, self).__init__ (dino, scores_text, health_text)
        self.image = pygame.image.load(f'{assets}/part.png') # cloud asset

    def on_part_bottom(self):
        global game
        global scores
        global health

        if scores <= 10: # if scores lower or equal 10
            scores = 0 # set scores to zero
        else: # if scores greather than 10
            scores -= 10 # minus scores
        health -= 1 # minus health by 1
        if health <= 0: # if no many healths
            end_game()
            show_menu() # show the menu
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.health_text.change_text(f'Health: {health}') # update scores text
        self.reset() # delete this and create new part

    def on_part_eat(self):
        global scores

        scores += 5 # append scores
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.reset() # delete this and create new part

class DamageFood(Part):
    def __init__(self, dino, scores_text, health_text):
        super(DamageFood, self).__init__ (dino, scores_text, health_text)
        self.image = pygame.image.load(f'{assets}/damage.png') # cloud asset

    def on_part_bottom(self):
        self.reset() # delete this and create new part

    def on_part_eat(self):
        global scores
        global health

        if scores <= 10: # if scores lower or equal 10
            scores = 0 # set scores to zero
        else: # if scores greather than 10
            scores -= 5 # minus scores
        health -= 1 # minus health
        if health <= 0: # if no many healths
            end_game()
            show_menu() # show the menu
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.health_text.change_text(f'Health: {health}') # update scores text
        self.reset() # delete this and create new part

class Text:
    def __init__(self, text, font_size, position):
        self.text = text # text to display
        self.font_family = f'{assets}/font.otf' # font path
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
        self.img = self.font.render(text, True, self.text_color) # rendered text

class MyButton:
    def __init__(self, btn_y, text, on_click):
        btn_w = 150 # button width
        btn_h = 50  # button height
        btn_x = (width // 2) - (btn_w // 2) # center button by x
        btn_radius = 10 # button radius
        color_1 = (33,158,188) # button default color
        color_2 = (4,107,159)  # button hover color
        color_3 = (3,81,119)   # button click color

        self.button = Button( # create button
            screen, btn_x, btn_y, btn_w, btn_h, text=text, fontSize=40,
            inactiveColour=color_1, hoverColour=color_2,
            pressedColour=color_3, radius=btn_radius,
            onClick=on_click
        )

class File:
    def __init__(self, filename):
        self.filename = filename

    def read_data(self, key):
        with open(self.filename, mode='r') as file: # read file content
            data = json.load(file) # save file data to variable
            return data['data'][key] # get data value by key
    
    def write_data(self, key, value):
        new = {key: value} # create new object
        with open(self.filename, mode='r') as file: # read file content
            data = json.load(file) # save file data to variable
        with open(self.filename, mode='w') as file: # open file for write
            data['data'][key] = value # append data in datafile
            json.dump(data, file, indent=4) # rewrite json file
            file.close() # close data file
        print(f'Data was writen [{new}]') # info log

def main(argv):
    global data
    global high_score

    try:
        opts, args = getopt.getopt(argv,"hc",["help","clear"]) # get args
    except getopt.GetoptError: # if error on args getting
        print('\n\nUsage: dino.py -h/--help | to show help message')
        sys.exit(2) # exit app with error code 2
    for opt, arg in opts:
        if opt == '-h' or opt == '--help': # -h/--help
            print('\n\n') # two lines
            print('Dino'.center(80)) # print app name in terminal center
            print('\t-h/--help  - Show this help message') # show help usage
            print('\t-c/--clear - Clear data file') # show clear usage
            sys.exit(0) # exit without errors
        elif opt == "-c" or opt == "--clear": # -c/--clear
            datafile = open(f'{assets}/.data.json', 'w') # open file for write
            datafile.write('{\n\t"data": {\n\t}\n}') # write this to file
            datafile.close() # close file
            sys.exit(0) # exit without errors

    data = File(data_path) # file of data
    try:
        high_score = data.read_data('high_score') # read from data file
    except:
        high_score = 0 # if not find from data file
    show_menu() # open menu

def show_menu():
    global menu
    menu = True

    start_btn = MyButton(120, 'Play', on_start_click).button # play button init
    exit_btn = MyButton(180, 'Exit', on_exit_click).button # exit button init
    high_score_text = Text(f'High-Score: {high_score}', 30, ((width//2)-70,240))

    while menu:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: # exit on window close
                menu = False

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            menu = False

        screen.fill(bg_color) # update background color
        high_score_text.update()
        pw.update(events) # update pygame_widgetes

        update_frame() # update frame

def on_start_click():
    global menu
    menu = False # stop menu
    play() # start game

def on_exit_click():
    # close the window
    pygame.quit()
    quit()

def play():
    # game
    global game
    global health
    global play_time
    # reset game options
    game = True
    scores = 0
    health = 5
    play_time = 0

    # dino
    dino_h = 100 # dino image height (px)
    dino_x = (width // 2) - (dino_h // 2) # screen center
    dino_y = height - dino_h # screen bottom
    dino = Dino(dino_x, dino_y) # creating dino

    # clouds
    clouds = [] # clouds list
    cloud_size = 100 # cloud image size (px)
    for i in range(random.randint(5, 8)): # create random count of clouds
        clouds.append(Cloud(
            random.randint(0, (width-cloud_size)),     # x
            random.randint(20, (height-cloud_size-50)) # y
        ))

    # texts
    scores_text = Text('Score: 0', 22, (10, 10)) # scores text
    time_text = Text('Time: 0', 22, (10, 40)) # time text
    health_text = Text('Health: 5', 22, (10, 70)) # health text

    # parts
    parts = []
    for i in range(random.randint(2, 4)):
        parts.append(DinoPart(dino, scores_text, health_text))
    for i in range(random.randint(1, 2)):
        parts.append(DamageFood(dino, scores_text, health_text))

    # launch new threads
    _thread.start_new_thread(update_time, ()) # play time thread
    _thread.start_new_thread(update_dino_speed, (dino,)) # dino speed thread

    # start game
    while game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # exit on window close
                game = False

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            game = False
        # movement
        if keys[pygame.K_LEFT]: # <-
            dino.move(0)
        elif keys[pygame.K_RIGHT]: # ->
            dino.move(1)
        # update frame
        screen.fill(bg_color) # update background color
        dino.show() # move dino
        for cloud in clouds: # loop all clouds
            cloud.move() # move cloud to current possible direction
        for part in parts: # loop all parts
            part.move() # start part movement
        
        scores_text.update() # refresh scores
        time_text.update() # refresh time
        health_text.update() # refresh time
        time_text.change_text(f'Time: {play_time}s') # update time text

        update_frame() # new frame

def end_game():
    global game
    global high_score
    global scores
    global data

    game = False # stop game window
    if high_score < scores: # if last game scores greather than high score
        data.write_data('high_score', scores) # rewrite high score
        high_score = scores # update high score
    scores = 0

def update_frame():
    pygame.display.update() # update frame

def update_time():
    global game
    global play_time

    while game:
        play_time += 1 # add seconds by 1
        print(f'Time updated - {play_time}') # info log
        pygame.time.wait(1000) # sleep for 1 sec

def update_dino_speed(dino):
    global game
    count = 0

    while game and count <= 10: # repeat 10 times
        pygame.time.wait(10000) # sleep for 10 sec
        dino.add_speed(0.1) # add dino speed by 0.1
        count += 1 # add count by 1

if __name__ == '__main__':
    main(sys.argv[1:]) # send command-line arguments as parameter
