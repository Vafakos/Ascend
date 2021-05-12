import pygame
import random
import pickle

import sys
from os import path


# Game window resolution
display_width = 1280
display_height = 720

# game windows info
TITLE = "2D Platformer"
ICON = pygame.image.load('assets/images/logo.png')

# menu assets
play_m_over = pygame.image.load('assets/images/menu/PlayButtonP.png')
play_idle = pygame.image.load('assets/images/menu/PlayButtonNP.png')

quit_m_over = pygame.image.load('assets/images/menu/QuitButtonP.png')
quit_idle = pygame.image.load('assets/images/menu/QuitButtonNP.png')

title_img = pygame.image.load('assets/images/menu/Title.png')
menu_image = pygame.image.load('assets/images/menu/menuImage.png')
button_bg = pygame.image.load('assets/images/menu/button_bg.png')

# game over assets
game_over_template = pygame.image.load('assets/images/menu/goTemplate.png')

# player health bar
players_hp = 5
full_health = pygame.image.load('assets/images/health/full.png')
one_hit = pygame.image.load('assets/images/health/1Hit.png')
two_hits = pygame.image.load('assets/images/health/2Hit.png')
three_hits = pygame.image.load('assets/images/health/3Hit.png')
four_hits = pygame.image.load('assets/images/health/4Hit.png')
five_hits = pygame.image.load('assets/images/health/5Hit.png')

# frames per second
FPS = 60

# tiles
tile_size = 32

# Color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# pygame stuff
pygame.init()  # Initialize pygame
pygame.mixer.init()  # Initialize mixer
pygame.display.set_caption(TITLE)  # Setting window's title
pygame.display.set_icon(ICON)  # Setting up the icon of the window
screen = pygame.display.set_mode((display_width, display_height))  # Setting resolution
clock = pygame.time.Clock()  # Making an object for time tracking

running = True  # global boolean variable

# level variables
level = 1  # var to control the game level/tilemap
up = 0
max_level = 4

# background
background = pygame.image.load('assets/images/world/MYSTARS.png').convert()
background_rect = background.get_rect()

# game assets
bullet_img = pygame.image.load('assets/images/world/bullet.png').convert()

# load audio and sounds
menu_music = pygame.mixer.Sound('audio/menu.wav')
menu_music.set_volume(0.25)

game_music = pygame.mixer.Sound('audio/game01.wav')
game_music.set_volume(0.25)

jump_sound = pygame.mixer.Sound('audio/jump.wav')
jump_sound.set_volume(0.1)

take_damage_sound = pygame.mixer.Sound('audio/hurt.wav')
take_damage_sound.set_volume(0.1)

button_hover_sound = pygame.mixer.Sound('audio/button.wav')
button_hover_sound.set_volume(0.5)

# players asset
img = pygame.image.load('assets/images/chars/player.png')
img_flip = pygame.transform.flip(img, True, False)

class Player:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(img, (32, 32))  # scale the image
        self.image_flip = img_flip  # scale the image
        self.mask = pygame.mask.from_surface(self.image)  # Player mask for collisions

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        # for collision
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.vel_y = 0
        self.jumped = False

    def update(self):
        global up

        dx = 0
        dy = 0

        # get key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jumped:
            jump_sound.play()
            self.vel_y = -13
            self.jumped = True
        if key[pygame.K_LEFT]:
            self.image = img_flip
            dx -= 4
        if key[pygame.K_RIGHT]:
            self.image = img
            dx += 4
            # update player coordinates
        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
            self.rect.x += dx
            self.rect.y += dy

        if self.rect.bottom > display_height:
            self.rect.bottom = display_height
            dy = 0

        # draw player onto screen
        screen.blit(self.image, self.rect)

        # add gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # collision
        for tile in tile_map.tile_list:
            # check for collision x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            # check for collision y
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if not key[pygame.K_SPACE]:
                    self.jumped = False
                # check ground/jump
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # check ground/fall
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0

        if pygame.sprite.spritecollide(self, ascend_group, False):
            up = 1

        # update player coordinates
        self.rect.x += dx
        self.rect.y += dy

        # draw player onto screen
        screen.blit(self.image, self.rect)

    def reset(self, x, y):

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False


class Bullets(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (23, 23))
        self.rect = self.image.get_rect()
        self.rect.x = 900
        self.rect.y = 40
        self.speed_y = random.randrange(1, 4)
        self.speed_x = random.randrange(-5, 0)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > display_height + 10 or self.rect.left < -25 or self.rect.right > display_width + 20:
            self.rect.x = 900
            self.rect.y = 40
            self.speed_y = random.randrange(1, 8)


class Ascend(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('assets/images/world/next_level.png')
        self.image = pygame.transform.scale(img, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.sprites = []
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemy.png')), (550, 690)))
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemyserious.png')), (550, 690)))
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemyserious2.png')), (550, 690)))
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemy2.png')), (550, 690)))
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemyserious.png')), (550, 690)))
        self.sprites.append(pygame.transform.scale((pygame.image.load('assets/images/chars/enemyserious2.png')), (550, 690)))
        self.current_sprite = 0
        self.image = self.sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.topright = [x, y]

    def update(self):
        screen.blit(self.image, self.rect)
        self.current_sprite += 0.1
        if self.current_sprite >= len(self.sprites):
            self.current_sprite = 0
        self.image = self.sprites[int(self.current_sprite)]


# Function to check for events
def events():
    global running
    for event in pygame.event.get():  # loops throw the events
        # quit
        if event.type == pygame.QUIT:
            pygame.quit()  # unload the pygame library
            try:
                sys.exit()  # close the game window
            finally:
                running = False  # break the while statement in update


def draw_display():
    screen.fill(BLACK)  # fills the screen with a color
    screen.blit(background, background_rect)
    player.update()
    update_health()
    tile_map.draw()

    # enemy
    enemy.update()
    # draw
    all_sprites.draw(screen)
    # exit
    ascend_group.draw(screen)
    pygame.display.flip()

# reset function


def reset_level(level):
    global tile_map
    player.reset(100, display_height - 180)
    ascend_group.empty()
    # load and create world
    if path.exists(f'level{level}'):
        pickle_on = open(f'level{level}', 'rb')
        world_data = pickle.load(pickle_on)
    tile_map = World(world_data)
    return tile_map

# menu screen/ runing before main loop


def start_menu():
    # start and stop audio
    pygame.mixer.stop()
    menu_music.play()

    sound_bt_one = False
    sound_bt_two = False
    while True:
        for ev in pygame.event.get():
            # if you close the window
            if ev.type == pygame.QUIT:
                pygame.quit()
            # if you press on the 'PLAY' button
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if display_width/2-70 <= mouse[0] <= display_width/2+40 and display_height/2+20 <= mouse[1] <= display_height/2+80:
                    main()
                if display_width/2-70 <= mouse[0] <= display_width/2+40 and display_height/2+130 <= mouse[1] <= display_height/2+190:
                    pygame.quit()

        screen.blit(menu_image, (0, 0))  # background image
        screen.blit(title_img, (0, 0))  # background for buttons
        # background for buttons
        screen.blit(button_bg, (display_width/2-140, display_height/2-30))
        mouse = pygame.mouse.get_pos()  # get mouse position

        # if the mouse is over the 'PLAY' or not (changes the state/image)
        if display_width/2-60 <= mouse[0] <= display_width/2+40 and display_height/2+20 <= mouse[1] <= display_height/2+80:
            screen.blit(play_m_over, (display_width/2-75, display_height/2-10))
            if not sound_bt_one:
                button_hover_sound.play()
                sound_bt_one = True
        else:
            screen.blit(play_idle, (display_width/2-75, display_height/2-10))
            sound_bt_one = False

        # if the mouse is over the 'QUIT' or not (changes the state/image)
        if display_width/2-60 <= mouse[0] <= display_width/2+40 and display_height/2+130 <= mouse[1] <= display_height/2+190:
            screen.blit(quit_m_over, (display_width /2-75, display_height/2+100))
            if not sound_bt_two:
                button_hover_sound.play()
                sound_bt_two = True
        else:
            screen.blit(quit_idle, (display_width/2-75, display_height/2+100))
            sound_bt_two = False

        pygame.display.update()


# same logic as start_menu but for the end game
def game_over():
    # start and stop audio
    pygame.mixer.stop()
    menu_music.play()

    sound_bt_one = False
    sound_bt_two = False
    while True:
        for ev in pygame.event.get():
            # if you close the window
            if ev.type == pygame.QUIT:
                pygame.quit()
            # if you press on the 'PLAY' button
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if display_width/2-70 <= mouse[0] <= display_width/2+40 and display_height/2+20 <= mouse[1] <= display_height/2+80:
                    # reset what is needed for replayability
                    global players_hp, level
                    player.reset(100, display_height - 130)
                    players_hp = 5
                    level = 1
                    up = 0
                    reset_level(level)
                    # calling main to start again the game
                    main()
                if display_width/2-70 <= mouse[0] <= display_width/2+40 and display_height/2+130 <= mouse[1] <= display_height/2+190:
                    pygame.quit()

        screen.blit(game_over_template, (0, 0))  # background image
        mouse = pygame.mouse.get_pos()  # get mouse position

        # if the mouse is over the 'PLAY' or not (changes the state/image)
        if display_width/2-60 <= mouse[0] <= display_width/2+40 and display_height/2+20 <= mouse[1] <= display_height/2+80:
            screen.blit(play_m_over, (display_width/2-75, display_height/2-10))
            if not sound_bt_one:
                button_hover_sound.play()
                sound_bt_one = True
        else:
            screen.blit(play_idle, (display_width/2-75, display_height/2-10))
            sound_bt_one = False

        # if the mouse is over the 'QUIT' or not (changes the state/image)
        if display_width/2-60 <= mouse[0] <= display_width/2+40 and display_height/2+130 <= mouse[1] <= display_height/2+190:
            screen.blit(quit_m_over, (display_width /2-75, display_height/2+100))
            if not sound_bt_two:
                button_hover_sound.play()
                sound_bt_two = True
        else:
            screen.blit(quit_idle, (display_width/2-75, display_height/2+100))
            sound_bt_two = False

        pygame.display.update()


class World:
    def __init__(self, data):
        self.tile_list = []

        # load images
        ground1 = pygame.image.load('assets/images/world/0.png')
        ground2 = pygame.image.load('assets/images/world/left.png')
        ground3 = pygame.image.load('assets/images/world/right.png')
        ground4 = pygame.image.load('assets/images/world/downright.png')
        ground5 = pygame.image.load('assets/images/world/topright.png')
        ground6 = pygame.image.load('assets/images/world/topleft.png')
        ground7 = pygame.image.load('assets/images/world/down left.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(ground1, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(ground2, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(ground3, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = pygame.transform.scale(ground4, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    img = pygame.transform.scale(ground5, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 6:
                    img = pygame.transform.scale(ground6, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 7:
                    img = pygame.transform.scale(ground7, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 8:
                    ascend = Ascend(col_count * tile_size,row_count * tile_size)
                    ascend_group.add(ascend)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])


def update_health():
    if players_hp == 5:
        screen.blit(full_health, (650, -100))
    elif players_hp == 4:
        screen.blit(one_hit, (650, -100))
    elif players_hp == 3:
        screen.blit(two_hits, (650, -100))
    elif players_hp == 2:
        screen.blit(three_hits, (650, -100))
    elif players_hp == 1:
        screen.blit(four_hits, (650, -100))
    elif players_hp == 0:
        screen.blit(five_hits, (650, -100))
        game_over()


def check_collision(player, bullets):
    # check if bullet hit
    global players_hp
    hits = pygame.sprite.spritecollide(player, bullets, True)
    for hit in hits:
        bullet = Bullets()
        all_sprites.add(bullet)
        bullets.add(bullet)

    if hits:
        players_hp -= 1
        take_damage_sound.play()


def level_load():
    global up, level, tile_map
    if up == 0:
        draw_display()
    if up == 1:
        level += 1
        if level <= max_level:
            tile_map = []
            tile_map = reset_level(level)
            up = 0
    if level > max_level:
        game_over()

# groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
ascend_group = pygame.sprite.Group()
for i in range(8):
    bullet = Bullets()
    all_sprites.add(bullet)
    bullets.add(bullet)


def main():
    # sounds/music
    pygame.mixer.stop()  # clear the sound channel
    game_music.play(-1)

    while running:
        clock.tick(FPS)  # updates only with the specified FPS
        events()
        level_load()

        draw_display()

        all_sprites.update()
        check_collision(player, bullets)

    pygame.quit()


# load and create world
if path.exists(f'level{level}'):
    pickle_in = open(f'level{level}', 'rb')
    world_data = pickle.load(pickle_in)
tile_map = World(world_data)

# player
player = Player(100, display_height - 130)
# enemy
enemy = Enemy(1450, display_height - 700)
# call menu function
start_menu()
