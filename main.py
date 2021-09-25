#!./venv/bin/python3

import os
import re
import json
import glob
import random
import _thread
import sys, getopt
from colorama import Fore, Style

import pygame
import pygame_widgets as pw
from mymodules.button import Button

pygame.init() # init pygame

size = width, height = 640, 400 # screen size
screen = pygame.display.set_mode(size) # init screen
bg_color = (142,202,230) # background color
fullpath = os.path.realpath(__file__) # get this script static path
fullpath = re.sub(r'\/(?!.*\/).*py', '', fullpath) # remove filename from path
assets = f'{fullpath}/assets' # assets directory
data_path = f'{assets}/.data.json' # data file path

app_icon = pygame.image.load(f'{assets}/icon.png') # find icon image
pygame.display.set_caption('Dino') # set window title
pygame.display.set_icon(app_icon) # set app icon

menu = True # is menu showing
game = True # is game running
mouse_play = True # is game runned in mouse mode
is_dino_die = True # is dino die in game
log_enabled = True # is logs output enabled
scores = 0 # game scores
high_score = 0 # all time high score
play_time = 0 # game play time seconds
health = 5 # game healths
data = 0 # temp start value for data
skin_index = 0 # default index of dino skins
temp_skin_index = 0 # temp index for changing dino skin in menu but not saving
part_skin_index = 0 # default index of part skins
temp_part_skin_index = 0 # temp index for part skin in menu but not saving
font_family = f'{assets}/font.otf' # font path
mouse_control_btn = 0 # define the button for global use
is_dino_die_control_btn = 0 # define the button for global use
select_skin = 'dino' # which skin currently selected [default: dino]
start_btn = 0 # menu start button
skins_btn = 0 # menu skins button
exit_btn = 0 # menu exit button
skin_save_btn = 0 # skin menu save button
skin_cancel_btn = 0 # skin menu cancel button
dino_skin_menu = 0 # dino skin in skin menu
select_skin_part = 0 # skin menu part skin select button
skin_select_larrow = 0 # skin select left arrow image
skin_select_rarrow = 0 # skin select right arrow image
dino_skins = {} # dino skins dict {name: path}
part_skins = {} # part skins dict {name: path}
dino_skins_path = glob.glob(f'{assets}/dino*') # all dino skins path
part_skins_path = glob.glob(f'{assets}/part*') # all part skins path

# fill dino skins dict
for i in range(len(dino_skins_path)):
    skin_name = dino_skins_path[i]
    dino_skins_path[i] = os.path.relpath(dino_skins_path[i], assets)
    dino_skins_path[i] = dino_skins_path[i].split('.')[0]
    dino_skins_path[i] = dino_skins_path[i].replace('_', ' ')
    dino_skins_path[i] = dino_skins_path[i].title()
    dino_skins[dino_skins_path[i]] = skin_name

# fill part skins dict
for i in range(len(part_skins_path)):
    skin_name = part_skins_path[i]
    part_skins_path[i] = os.path.relpath(part_skins_path[i], assets)
    part_skins_path[i] = part_skins_path[i].split('.')[0]
    part_skins_path[i] = part_skins_path[i].replace('_', ' ')
    part_skins_path[i] = part_skins_path[i].title()
    part_skins[part_skins_path[i]] = skin_name

class Dino:
    def __init__(self, x, y):
        path = list(dino_skins.values())[skin_index]
        info_log(path)
        self.image = pygame.image.load(path)
        self.speed = 0.2 # dino speed
        self.x = x # dino x
        self.y = y # dino y
        self.direction = {
            'left': -1 * self.speed,
            'right': self.speed
        }
        info_log(f'Created dino in [{x};{y}]') # info log

    def move(self, direction):
        if direction == 0 and self.x >= 5: # moved left
            self.x -= self.speed
        elif direction == 1 and self.x <= width-50: # moved right
            self.x += self.speed
        info_log(f'Dino moved to [{self.x};{self.y}]') # info log

    def move_to_position(self, x):
        self.x = x
        info_log(f'Dino moved to [{self.x};{self.y}]') # info log

    def add_speed(self, speed):
        self.speed += speed # add dino speed
        info_log(f'Dino speed added by {speed}') # info log

    def change_speed(self, new_speed):
        self.speed = new_speed # set new speed
        info_log(f'Dino speed changed - {new_speed}') # info log

    def show(self):
        screen.blit(self.image, (self.x,self.y)) # show dino in x, y position

    def get_params(self):
        return self.x-20, self.y-50, self.x+50, self.y+100 # x, y, w, h

    def change_skin(self, skin_path):
        # change dino skin [color]
        self.image = pygame.image.load(skin_path)

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
        info_log(f'Created cloud with speed {self.speed} in [{x};{y}]') # info log

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
        info_log(f'Part was created at {self.x}') # info log

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
        path = list(part_skins.values())[part_skin_index]
        self.image = pygame.image.load(path) # part asset

    def on_part_bottom(self):
        global game
        global scores
        global is_dino_die

        if scores <= 10: # if scores lower or equal 10
            scores = 0 # set scores to zero
        else: # if scores greather than 10
            scores -= 10 # minus scores
        if is_dino_die: # if is_dino_die option turned on
            global health
            health -= 1 # minus health by 1
            if health <= 0: # if no many healths
                end_game() # end game
                show_menu() # show the menu
            self.health_text.change_text(f'Health: {health}') # update health
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.reset() # delete this and create new part

    def on_part_eat(self):
        global scores

        scores += 5 # append scores
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.reset() # delete this and create new part

class DamageFood(Part):
    def __init__(self, dino, scores_text, health_text):
        super(DamageFood, self).__init__ (dino, scores_text, health_text)
        self.image = pygame.image.load(f'{assets}/damage.png') # damage asset

    def on_part_bottom(self):
        self.reset() # delete this and create new part

    def on_part_eat(self):
        global scores
        global is_dino_die

        if scores <= 25: # if scores lower or equal 10
            scores = 0 # set scores to zero
        else: # if scores greather than 10
            scores -= 25 # minus scores
        if is_dino_die: # if is_dino_die option turned on
            global health

            health -= 1 # minus health
            if health <= 0: # if no many healths
                end_game() # end game
                show_menu() # show the menu
            self.health_text.change_text(f'Health: {health}') # update health
        self.scores_text.change_text(f'Score: {scores}') # update scores text
        self.reset() # delete this and create new part

class Text:
    def __init__(self, text, font_size, position, is_center=False):
        global font_family
        
        self.text = text # text to display
        self.font_size = font_size # font size
        self.text_color = (56,61,61) # text color
        self.font = pygame.font.Font(font_family, self.font_size) # font
        self.img = self.font.render(text, True, self.text_color) # render text
        if is_center:
            self.align_center(position) # align to x center
        else:
            self.position = position # text position
        info_log(f'Created text - {text} [{self.position}]') # info log

    def update(self):
        screen.blit(self.img, self.position) # update text to show

    def change_text(self, text):
        self.text = text # rewrite displayed text
        self.img = self.font.render(text, True, self.text_color) # rendered text

    def align_center(self, y_pos):
        # center text in the screen width
        self.position = self.img.get_rect(center=(width//2, y_pos))

class MyButton:
    def __init__(self, params, text, on_click, font_size=30,
            radius=10, is_center=True, image=False):
        global font_family
        
        self.btn_x = params[0] # button x position
        self.btn_y = params[1] # button y position
        self.btn_w = params[2] # button width
        self.btn_h = params[3] # button height
        self.radius = radius   # button corner radius
        self.text = text # button text
        self.font = pygame.font.Font(font_family, font_size) # font family
        self.on_click = on_click # on click method
        if is_center: # if button placed on center
            self.btn_x = (width // 2) - (self.btn_w // 2) # center button by x
        self.color_1 = (33,158,188) # button default color
        self.color_2 = (4,107,159)  # button hover color
        self.color_3 = (3,81,119)   # button click color

        self.button = Button( # create button
            screen, self.btn_x, self.btn_y, self.btn_w, self.btn_h,
            text=self.text, font=self.font,
            inactiveColour=self.color_1, hoverColour=self.color_2,
            pressedColour=self.color_3, radius=self.radius,
            onClick=self.on_click
        )
        if image:
            self.image = pygame.image.load(f'{assets}/{image}')
            self.button.setImage(self.image)
        info_log(f'{text} button cerated with {params} parameters') # info log

    def set_text(self, new_text):
        self.button.set_text(new_text)
        info_log(f'{self.text} button text changed {new_text}') # info log

class SkinMenuDino:
    def __init__(self):
        dino_h = 100 # dino image height (px)
        self.x = (width // 2) - (dino_h // 4) # screen center
        self.y = (height // 2) - (dino_h // 1.2) # screen center

    def show(self):
        global skin_index
        global dino_skins

        title = list(dino_skins.keys()) \
                [temp_skin_index] # title of the current skin
        path = dino_skins[title] # asset path of dino skin
        img = pygame.image.load(path)
        screen.blit(img, (self.x,self.y))

class SkinMenuPart:
    def __init__(self):
        part_h = 50 # dino image height (px)
        self.x = (width // 2) - (part_h // 4) # screen center
        self.y = (height // 2) - (part_h // 1.2) # screen center

    def show(self):
        global part_skin_index
        global part_skins

        title = list(part_skins.keys()) \
                [temp_part_skin_index] # title of the current skin
        path = part_skins[title] # asset path of dino skin
        img = pygame.image.load(path)
        screen.blit(img, (self.x,self.y))

class SkinMenuArrow:
    def __init__(self, direction, on_click):
        path = f'{assets}/arrow_{direction}.png'
        self.dir = direction
        self.img = pygame.image.load(path)
        self.btn_size = 75
        if self.dir == 'left':
            self.x = self.btn_size
        else:
            self.x = width - (self.btn_size * 2)
        self.y = (height // 2) - (self.btn_size // 1.2)
        self.button = Button( # create button
            screen, self.x, self.y, self.btn_size, self.btn_size,
            radius = 100, onClick=on_click, image=self.img
        )

class File:
    def __init__(self, filename):
        self.filename = filename # set filename

    def read_data(self, key):
        try:
            with open(self.filename, mode='r') as file: # read file content
                data = json.load(file) # save file data to variable
                return data['data'][key] # get data value by key
        except FileNotFoundError as e: # if file not exist
            info_log(f'{Fore.RED} [ERROR] {self.filename} file not found \
                    {Style.RESET_ALL}') # error
    
    def write_data(self, key, value):
        new = {key: value} # create new object
        try:
            with open(self.filename, mode='r') as file: # read file content
                data = json.load(file) # save file data to variable
            with open(self.filename, mode='w') as file: # open file for write
                data['data'][key] = value # append data in datafile
                json.dump(data, file, indent=4) # rewrite json file
                file.close() # close data file
            info_log(f'Data was writen [{new}]') # info log
        except FileNotFoundError as e: # if file not exist
            info_log(f'{Fore.RED} [ERROR] {self.filename} file not found \
                    {Style.RESET_ALL}') # error

def main(argv):
    global data
    global high_score

    try:
        opts, args = \
                getopt.getopt(argv,"hcl",["help","clear","log"]) # get args
    except getopt.GetoptError: # if error on args getting
        print('\n\nUsage: dino.py -h/--help | to show help message') # help
        sys.exit(2) # exit app with error code 2
    for opt, arg in opts: # loop in arguments
        if opt == '-h' or opt == '--help': # -h/--help
            print('\n\n') # two lines
            print('Dino'.center(80)) # print app name in terminal center
            print('\t-h/--help  - Show this help message') # show help usage
            print('\t-c/--clear - Clear data file') # show clear usage
            print('\t-l/--log   - Log outputs to terminal') # show logs usage
            sys.exit(0) # exit without errors
        elif opt == '-c' or opt == '--clear': # -c/--clear
            datafile = open(f'{assets}/.data.json', 'w') # open file for write
            datafile.write('{\n\t"data": {\n\t}\n}') # write this to file
            datafile.close() # close file
            sys.exit(0) # exit without errors
        elif opt == '-l' or opt == '--log': # -l/--log
            global log_enabled
            log_enabled = True # set logs to terminal true

    data = File(data_path) # file of data
    try:
        high_score = data.read_data('high_score') # read from data file
    except:
        high_score = 0 # if not find from data file
    show_menu() # open menu

def show_menu():
    global menu
    global start_btn
    global skins_btn
    global exit_btn
    global mouse_play
    global mouse_control_btn
    global is_dino_die
    global is_dino_die_control_btn
    menu = True

    # menu buttons initialization
    if start_btn == 0:
        start_btn = MyButton((0,100,150,50), 'Play', on_start_click).button
        skins_btn = MyButton((0,155,150,50), 'Skins', on_skins_click).button
        exit_btn = MyButton((0,210,150,50), 'Exit', on_exit_click).button
        mouse_control_btn = MyButton((width-150,10,140,30),
            f'Mouse control: {mouse_play}', on_mouse_control_click,
            font_size=18, radius=5, is_center=False)
        is_dino_die_control_btn = MyButton((width-150,50,140,30),
            f'Dino death: {is_dino_die}', on_death_control_click,
            font_size=18, radius=5, is_center=False)
    else:
        start_btn.show()
        skins_btn.show()
        exit_btn.show()
        mouse_control_btn.button.show()
        is_dino_die_control_btn.button.show()

    high_score_text = Text(f'High-Score: {high_score}', 24,
        ((width//2)-65,260))

    while menu:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: # exit on window close
                menu = False

        screen.fill(bg_color) # update background color
        high_score_text.update() # update high score text
        pw.update(events) # update pygame_widgetes

        update_frame() # update frame

def on_start_click():
    global menu

    info_log('Game started') # info log
    menu = False # stop menu
    play() # start game

def on_skins_click():
    global menu
    global select_skin
    global skin_index
    global temp_skin_index
    global skin_select_larrow
    global skin_select_rarrow
    global skin_save_btn
    global skin_cancel_btn
    global select_skin_dino
    global select_skin_part
    global start_btn
    global skins_btn
    global exit_btn
    global mouse_control_btn
    global is_dino_die_control_btn
    temp_skin_index = skin_index
    select_skin = 'dino'

    # Delete menu buttons
    start_btn.hide()
    skins_btn.hide()
    exit_btn.hide()
    mouse_control_btn.button.hide()
    is_dino_die_control_btn.button.hide()

    # initialize skin menu buttons if window openning first time
    if skin_save_btn == 0:
        skin_save_btn = MyButton((0,280,150,50), 'Save',
            on_skin_save).button
        skin_cancel_btn = MyButton((0,340,150,50), 'Cancel',
            on_skin_cancel).button
        skin_select_larrow = SkinMenuArrow('left', on_larrow_click)
        skin_select_rarrow = SkinMenuArrow('right', on_rarrow_click)
        select_skin_dino = MyButton(
                (width-120,10,50,50), None,
                on_select_dino_skin_click, is_center=False,
                image='skin_dino.png'
            )
        select_skin_part = MyButton(
                (width-60,10,50,50), None,
                on_select_part_skin_click, is_center=False,
                image='skin_part.png'
            )
    else: # show buttons if its already initialized
        skin_save_btn.show()
        skin_cancel_btn.show()
        skin_select_larrow.button.show()
        skin_select_rarrow.button.show()
        select_skin_dino.button.show()
        select_skin_part.button.show()

    dino_skin_menu = SkinMenuDino()
    dino_skin_name = Text(
            list(dino_skins.keys())[temp_skin_index], # skin name
            25, # font size
            80, # y position
            is_center=True # is centered text
        )

    while menu:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: # exit on window close
                menu = False

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            on_skin_cancel()

        screen.fill(bg_color) # update background color
        pw.update(events) # update pygame_widgetes
        
        # update skin title
        dino_skin_name.change_text(list(dino_skins.keys())[temp_skin_index])
        dino_skin_name.align_center(80)

        dino_skin_menu.show() # update dino skin image
        dino_skin_name.update() # update dino skin name

        update_frame() # update frame

def on_select_part_skin_click():
    global menu
    global temp_part_skin_index
    global skin_select_larrow
    global skin_select_rarrow
    global skin_save_btn
    global skin_cancel_btn
    global select_skin

    select_skin = 'part'
    part_skin_menu = SkinMenuPart()
    part_skin_name = Text(
            list(part_skins.keys())[temp_part_skin_index], # skin name
            25, # font size
            80, # y position
            is_center=True # is centered text
        )

    while menu:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: # exit on window close
                menu = False

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            on_skin_cancel()

        screen.fill(bg_color) # update background color
        pw.update(events) # update pygame_widgetes
        
        # update skin title
        part_skin_name.change_text(list(part_skins.keys()) \
                [temp_part_skin_index])
        part_skin_name.align_center(80)

        part_skin_menu.show() # update part skin image
        part_skin_name.update() # update part skin name

        update_frame() # update frame

def on_select_dino_skin_click():
    global menu
    global temp_skin_index
    global skin_select_larrow
    global skin_select_rarrow
    global skin_save_btn
    global skin_cancel_btn
    global select_skin
    global select_skin_dino

    select_skin = 'dino'
    skin_menu = SkinMenuDino()
    skin_name = Text(
            list(dino_skins.keys())[temp_skin_index], # skin name
            25, # font size
            80, # y position
            is_center=True # is centered text
        )

    while menu:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT: # exit on window close
                menu = False

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            on_skin_cancel()

        screen.fill(bg_color) # update background color
        pw.update(events) # update pygame_widgetes
        
        # update skin title
        skin_name.change_text(list(dino_skins.keys())[temp_skin_index])
        skin_name.align_center(80)

        skin_menu.show() # update dino skin image
        skin_name.update() # update dino skin name

        update_frame() # update frame

def on_rarrow_click():
    global select_skin
    global temp_skin_index
    global temp_part_skin_index
    global dino_skins
    global part_skins

    # check which skin was changing
    if select_skin == 'dino':
        # change dino skin to next
        if temp_skin_index < len(dino_skins) - 1:
            temp_skin_index += 1
    elif select_skin == 'part':
        # change part skin to prvious
        if temp_part_skin_index < len(part_skins) - 1:
            temp_part_skin_index += 1

def on_larrow_click():
    global select_skin
    global temp_skin_index
    global temp_part_skin_index

    # check which skin was changing
    if select_skin == 'dino':
        # change dino skin to previous
        if temp_skin_index > 0:
            temp_skin_index -= 1
    elif select_skin == 'part':
        # change part skin to prvious
        if temp_part_skin_index > 0:
            temp_part_skin_index -= 1

def on_skin_save():
    global skin_index
    global temp_skin_index
    global part_skin_index
    global temp_part_skin_index

    # forward temp index to index
    skin_index = temp_skin_index 
    part_skin_index = temp_part_skin_index
    info_log(f'D skin has been changed [{skin_index}]') # info log
    info_log(f'P skin has been changed [{part_skin_index}]') # info log
    hide_skin_buttons() # hide skin menu buttons
    show_menu() # show main menu

def on_skin_cancel():
    hide_skin_buttons() # hide skin menu buttons
    show_menu() # show main menu

def hide_skin_buttons():
    global skin_save_btn
    global skin_cancel_btn
    global skin_select_larrow
    global skin_select_rarrow
    global select_skin_dino
    global select_skin_part

    # hide skin menu buttons
    skin_save_btn.hide()
    skin_cancel_btn.hide()
    skin_select_larrow.button.hide()
    skin_select_rarrow.button.hide()
    select_skin_dino.button.hide()
    select_skin_part.button.hide()

def on_exit_click():
    info_log('Game closed') # info log
    # close the window
    pygame.quit() # close pygame
    quit() # close python

def on_mouse_control_click():
    global mouse_play
    global mouse_control_btn

    mouse_play = not mouse_play # reverse mouse control option
    mouse_control_btn.set_text(f'Mouse control: {mouse_play}') # change text
    info_log(f'Mouse control switched to {mouse_play}') # info log

def on_death_control_click():
    global is_dino_die
    global is_dino_die_control_btn

    is_dino_die = not is_dino_die # reverse death option
    is_dino_die_control_btn.set_text(f'Dino death: {is_dino_die}') # change text
    info_log(f'Dino death switched to {is_dino_die}') # info log

def play():
    # game
    global game
    global health
    global scores
    global high_score
    global play_time
    global mouse_play
    global is_dino_die

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
    if is_dino_die:
        health_text = Text('Health: 5', 22, (10, 70)) # health text
    else:
        health_text = None # health text temp value for parts

    # parts
    parts = [] # list of parts
    for i in range(random.randint(2, 4)): # create 3-5 parts
        parts.append(DinoPart(dino, scores_text, health_text)) # add new part
    for i in range(random.randint(1, 2)): # create 2-3 mines
        parts.append(DamageFood(dino, scores_text, health_text)) # add new mine

    # launch new threads
    _thread.start_new_thread(update_time, ()) # play time thread
    _thread.start_new_thread(update_dino_speed, (dino,)) # dino speed thread

    # start game
    while game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: # exit on window close
                end_game()

        keys = pygame.key.get_pressed() # pressed keys
        # close on esc
        if keys[pygame.K_ESCAPE]:
            end_game()
            show_menu()
        # movement
        if mouse_play:
            mx, _ = pygame.mouse.get_pos() # get current mouse position
            dino.move_to_position(mx) # move dino to current mouse x in window
        else:
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

        # refresh texts
        scores_text.update() # refresh scores
        time_text.update() # refresh time
        if is_dino_die:
            health_text.update() # refresh health
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
    scores = 0 # reset scores

def update_frame():
    pygame.display.update() # update frame

def update_time():
    global game
    global play_time

    while game:
        play_time += 1 # add seconds by 1
        info_log(f'Time updated - {play_time}') # info log
        pygame.time.wait(1000) # sleep for 1 sec

def update_dino_speed(dino):
    global game
    count = 0 # how many times speed added

    while game and count <= 10: # repeat 10 times
        pygame.time.wait(10000) # sleep for 10 sec
        dino.add_speed(0.1) # add dino speed by 0.1
        count += 1 # add count by 1

def info_log(msg):
    global log_enabled

    if log_enabled:
        print(f' [INFO] {msg}')

if __name__ == '__main__':
    main(sys.argv[1:]) # send command-line arguments as parameter
