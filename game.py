import pygame
from collections import deque
import random
import numpy as np



global animation_frames
animation_frames = {}

def load_animation(path,frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc)
        animation_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data
def collision_test(rect,tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list
def move(rect,movement,tiles):
    collision_types = {'top':False,'bottom':False,'right':False,'left':False}
    rect.x += movement[0]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect,tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types
def change_action(action_var,frame,new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var,frame
class enemy_obj():
    def __init__(self, loc,image):
        self.loc = loc
        self.rect = pygame.Rect(self.loc[0], self.loc[1], 13, 13)
        self.image = image

    def render(self, surf):
        surf.blit(self.image, (self.rect.x, self.rect.y))


class Temp(pygame.sprite.Sprite):
    def __init__(self,color,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([7,1])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

class invinsible_obj(pygame.sprite.Sprite):
    def __init__(self,position):   
        pygame.sprite.Sprite.__init__(self)
        self.color = (255,215,0)
        self.image = pygame.Surface([5,5])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

class slow_obj(pygame.sprite.Sprite):
    def __init__(self,position):   
        pygame.sprite.Sprite.__init__(self)
        self.color = (0,255,127)
        self.image = pygame.Surface([5,5])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = position


class jumper_obj():
    def __init__(self, loc,jumper_img):
        self.loc = loc
        self.jumper_img = jumper_img

    def render(self, surf):
        surf.blit(self.jumper_img, (self.loc[0], self.loc[1]))

    def get_rect(self):
        return pygame.Rect(self.loc[0], self.loc[1], 8, 9)

    def collision_test(self, rect):
        jumper_rect = self.get_rect()
        return jumper_rect.colliderect(rect)









class Player():
     
    def __init__(self,x,y,sizex,sizey):
        self.x = x
        self.y = y
        self.sizex = sizex
        self.sizey = sizey
        self.rect = pygame.Rect(x,y,sizex,sizey)
        self.moving_right = False
        self.moving_left = False
        self.vertical_momentum = 0
        self.air_timer = 0
        self.player_movement = [0,0]
        self.player_action = 'idle'
        self.player_frame = 0
        self.player_flip = False
        
        self.animation_database = {}
        self.animation_database['run'] = load_animation('player_animations/run',[7,7])
        self.animation_database['idle'] = load_animation('player_animations/idle',[7,7,40]) 
        self.gold_img = pygame.image.load('player_animations/gold_player.png').convert()
        self.gold_img.set_colorkey((255,255,255))
        self.green_img = pygame.image.load('player_animations/posion.png').convert()
        self.green_img.set_colorkey((255,255,255))
        self.red_img = pygame.image.load('player_animations/red.png').convert()
        self.red_img.set_colorkey((255,255,255))
    def player_move(self,tile_rects,slow):
        self.player_movement = [0,0]
        if slow is True:
            if self.moving_right == True:
                self.player_movement[0] += 1
            if self.moving_left == True:
                self.player_movement[0] -= 1
            self.player_movement[1] += self.vertical_momentum
            self.vertical_momentum += 1
            if self.vertical_momentum > 3:
                self.vertical_momentum = 3
        else:
            if self.moving_right == True:
                self.player_movement[0] += 2
            if self.moving_left == True:
                self.player_movement[0] -= 2
            self.player_movement[1] += self.vertical_momentum
            self.vertical_momentum += 0.2
            if self.vertical_momentum > 3:
                self.vertical_momentum = 3
        self.rect,collisions = move(self.rect,self.player_movement,tile_rects)
        if collisions['bottom'] == True:
            self.air_timer = 0
            self.vertical_momentum = 0
        else:
            self.air_timer +=1
    

    def display(self,display,invinsible,slow,enemies_list):

        if self.player_movement[0] == 0:
            self.player_action,self.player_frame = change_action(self.player_action,self.player_frame,'idle')
        if self.player_movement[0] > 0:
            self.player_flip = False
            self.player_action,self.player_frame = change_action(self.player_action,self.player_frame,'run')
        if self.player_movement[0] < 0:
            self.player_flip = True
            self.player_action,self.player_frame = change_action(self.player_action,self.player_frame,'run')
        self.player_frame+=1

        if self.player_frame >= len(self.animation_database[self.player_action]):
            self.player_frame = 0
        player_img_id = self.animation_database[self.player_action][self.player_frame]
        new_rect = pygame.Rect(self.rect.x-2,self.rect.y,8,8)
        if invinsible:
            player_img = self.gold_img
            slow = False
        elif slow:
            player_img = self.green_img
        elif  new_rect.collidelist(enemies_list) <= -1:
            player_img = animation_frames[player_img_id]

        else:
            player_img = self.red_img



        display.blit(pygame.transform.flip(player_img,self.player_flip,False),(self.rect.x,self.rect.y))


class GAME:
    def __init__(self):


        pygame.init() # initiates pygame
        self.clock = pygame.time.Clock()
        self.WINDOW_SIZE = (600,400)
        self.done = False
        self.reward = 0
        self.prev_actions = None
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE,0,32)
        #images
        self.grass_img = pygame.image.load('data/images/grass.png')
        self.dirt_img = pygame.image.load('data/images/dirt.png')
        self.enemy_img = pygame.image.load('data/images/enemy.png').convert()
        self.enemy_img.set_colorkey((255,255,255))
        self.jumper_img = pygame.image.load('data/images/jumper.png').convert()
        self.jumper_img.set_colorkey((255,255,255))
        self.red = False

        self.max_enemy = 4
        self.done = False
        self.display = pygame.Surface((300,200))
        self.player = Player(random.randint(20,260),100,8,10)
        self.start = pygame.time.get_ticks()
        self.new_rect = pygame.Rect(self.player.rect.x-2,self.player.rect.y,8,8)
        self.enemies = []
        self.enemies_list = []
        self.gold_obj = invinsible_obj([random.randint(60,250),25])
        self.black_obj = slow_obj([random.randint(60,250),25])
        self.invinsible = False
        self.done = False   
        self.slow = False
        for i in range(3):
            self.enemies.append([0,enemy_obj((random.randint(35,240),80),self.enemy_img),random.randint(-1,1),False,random.randint(-1,1)])
        for enemy in self.enemies:
            self.enemies_list.append(enemy[1])
        self.tile_rects = []

        self.jumper_objects = []
        for i in range(3):
            self.jumper_objects.append(jumper_obj((70+i*70,55),self.jumper_img))
        self.game_map = [['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','0','0','0','0','0','0','0','0','0','0','0','0','0','0','0','1','1'],
                    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
                    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
                    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
                    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1'],
                    ['1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1','1']]
        self.compute_tile_rects()   
        # self.goldEvent = pygame.USEREVENT
        # self.blackEvent = pygame.USEREVENT
        # self.respawn_time_gold = pygame.USEREVENT
        # self.respawn_time_black = pygame.USEREVENT
        self.red_time = pygame.USEREVENT
        
    def obj_operation(self):
        
        try:
            if self.new_rect.colliderect(self.gold_obj):
                # self.goldStartTime = pygame.time.get_ticks()
                del self.gold_obj
                self.invinsible = True
                self.reward += 3500
                self.goldEvent = pygame.USEREVENT + 1
                self.respawn_time_gold = pygame.USEREVENT + 1
                pygame.time.set_timer(self.goldEvent, 5000)
                pygame.time.set_timer(self.respawn_time_gold, 5000)
            else:
                self.display.blit(self.gold_obj.image,self.gold_obj.rect)
                self.respawn_time_gold = pygame.USEREVENT 
                self.reward = self.reward
        except:
            pass
        try:
            if self.new_rect.colliderect(self.black_obj):
                # self.blackStartTime = pygame.time.get_ticks()
                del self.black_obj
                self.slow = True
                self.reward -= 2000
                self.blackEvent = pygame.USEREVENT + 1
                self.respawn_time_black = pygame.USEREVENT + 1
                pygame.time.set_timer(self.blackEvent, 5000)
                pygame.time.set_timer(self.respawn_time_black, 5000)
            else:
                self.display.blit(self.black_obj.image,self.black_obj.rect)
                self.respawn_time_black = pygame.USEREVENT 
                self.reward = self.reward
        except:
            pass
    def compute_tile_rects(self):
        y = 0
        for layer in self.game_map:
            x = 0
            for tile in layer:
   
                if tile != '0':
                    self.tile_rects.append(pygame.Rect(x*16,y*16,16,16))
                x += 1
            y += 1     
    def action(self,action):
        # self.player.movement = [0,0]
        if action==0:
            self.player.moving_right = True
            self.player.moving_left = False
        if action==1:
            self.player.moving_left = True
            self.player.moving_right = False
        if action==2:
            self.player.moving_left = False
            self.player.moving_right = False
            if self.slow is not True:
                if self.player.air_timer <6:
                    self.player.vertical_momentum = -4.8
            else:
                self.player.vertical_momentum = 0
        if action==3:
            # self.player.movement[0] = 0 
            self.player.moving_left = False
            self.player.moving_right = False
        return action
    def enemy_movement(self):

        for index,enemy in enumerate(self.enemies):
            if enemy[3] is False:
                i = 1
            else:
                i = -1
            enemy[0] += i * 0.3
            if enemy[0] > i*3:
                enemy[0] = i*3
            enemy_movement = [0,enemy[0]]

            # if self.player.rect.x > enemy[1].rect.x +5:
            #     enemy_movement[0] = 1
            # if self.player.rect.x < enemy[1].rect.x -5:
            #     enemy_movement[0] = -1
            enemy_movement[0] = enemy[2]*enemy[4]
            enemy[1].rect,collision_types = move(enemy[1].rect,enemy_movement,self.tile_rects)
            if enemy[1].rect.y == 115:
                enemy[3] = True
                # if enemy[1].rect.x == 16:
                #     enemy[2] = 1
                #     enemy[4] = 1
                # elif enemy[1].rect.x == 275:

                #     enemy[2] = -1
                #     enemy[4] =  1
                # else:
                if enemy[2] == 0:
                    enemy[2] += random.randint(-1,1)
                else:
                    enemy[4] = random.randint(-1,1)
            elif enemy[1].rect.y <= 90:
                enemy[3] = False
            self.enemies_list[index] = enemy[1]
            # if collision_types['bottom'] == True:
            #     enemy[0] = 0
            enemy_top = Temp([255,0,0],[enemy[1].rect.x+3.9,enemy[1].rect.y-1.3])
            self.new_rect = pygame.Rect(self.player.rect.x-2,self.player.rect.y,8,8)

            self.display.blit(enemy_top.image,enemy_top.rect)
            enemy[1].render(self.display)
            # if self.invinsible:
                
            #     if self.new_rect.colliderect(enemy[1].rect):
            #         self.reward += 700
            #         self.enemies.remove(enemy)
            #         self.enemies_list.pop(index)
            if self.new_rect.colliderect(enemy_top) and self.player.vertical_momentum>0 :
                self.reward += 5
                self.player.vertical_momentum = -4
                self.enemies.remove(enemy)
                self.enemies_list.pop(index)
            # elif self.new_rect.colliderect(enemy_top) and self.player.vertical_momentum>0 and self.position_cod() is True:
            #     self.reward += 0
            #     self.player.vertical_momentum = -4
                # self.enemies.remove(enemy)
                # self.enemies_list.pop(index)
            # elif self.new_rect.colliderect(enemy[1].rect) and self.red is False and self.position_cod():
            #     self.red = True
            #     self.reward -= 500
            #     self.red_time = pygame.USEREVENT + 1
            #     pygame.time.set_timer(self.red_time, 600)
            elif self.new_rect.colliderect(enemy[1].rect) and self.red is False :
                self.red = True
                self.reward -= 5
                self.red_time = pygame.USEREVENT + 1
                pygame.time.set_timer(self.red_time, 600)
                # self.done = True
    def jumper(self):
        for jumper in self.jumper_objects:
            jumper.render(self.display)
            if jumper.collision_test(self.new_rect):
                self.player.vertical_momentum = -3
    def draw_tile(self):
        self.display.fill((146,244,255)) # clear screen by filling it with blue
        y = 0
        for layer in self.game_map:
            x = 0
            for tile in layer:
                if tile == '1':
                    self.display.blit(self.dirt_img,(x*16,y*16))
                if tile == '2':
                    self.display.blit(self.grass_img,(x*16,y*16))

                x += 1
            y += 1 
    def position_cod(self):
        if (self.player.rect.x<=280 and self.player.rect.x>=255) or (self.player.rect.x>=16 and self.player.rect.x<=40):
            return True
        else:
            return False
    def update_and_show(self):
        # self.playtime = pygame.USEREVENT + 1
        # pygame.time.set_timer(self.playtime, 6000)
        # print(self.red)
        self.draw_tile()
        self.jumper()
        
        self.enemy_movement()
        self.player.player_move(self.tile_rects,self.slow)
        
        self.generate_enemy()
        # self.obj_operation()
        self.respawn_obj()
        # self.reward += 1
        self.player.display(self.display,self.invinsible,self.slow,self.enemies_list)
        self.screen.blit(pygame.transform.scale(self.display,self.WINDOW_SIZE),(0,0))
        # self.done_()
        pygame.display.update()
        self.clock.tick(60)

    def surf_to_array(self,surf):
        return pygame.surfarray.pixels3d(surf)
    def observe(self):
        # enemies_location = []
        # jumper_location = []
        # agent_location_x =  self.player.rect.x
        # agent_location_y =  self.player.rect.y
        # try:
        #     gold_location_x = self.gold_obj.rect.x
        #     gold_location_y = self.gold_obj.rect.y
        # except:
        #     gold_location_x = 0
        #     gold_location_y = 0

        # try:
        #     black_location_x = self.black_obj.rect.x
        #     black_location_y = self.black_obj.rect.y
        # except:
        #     black_location_x = 0
        #     black_location_y = 0
        # for i in range(7):
        #     try:
        #         enemies_location.append(self.enemies[i][1].rect.x)
        #         enemies_location.append(self.enemies[i][1].rect.y)
        #     except:
        #         enemies_location.append(0)
        #         enemies_location.append(0)





        # # for enemy in range(5):
        # #     enemies_location.append(enemy[1].rect.x)
        # #     enemies_location.append(enemy[1].rect.y)

        # # self.prev_actions = deque(maxlen = 12) 

        # # for i in range(12-len(enemies_location)):
        # #     self.prev_actions.append(-1)

        # for jumper in self.jumper_objects:
        #     jumper_location.append(jumper.loc[0])
        #     jumper_location.append(jumper.loc[1])



    
        # observation = [agent_location_x,agent_location_y] + [gold_location_x,gold_location_y]+[black_location_x,black_location_y]+enemies_location+jumper_location
        observation = pygame.surfarray.pixels3d(self.display)
        observation = np.array(observation)

    


        return observation
    def generate_enemy(self):
        now = pygame.time.get_ticks()
 
        if now - self.start > 2000 and len(self.enemies)<=self.max_enemy:
            self.start  = now
            enemy = enemy_obj((random.randint(35,240),80),self.enemy_img)

            self.enemies.append([0,enemy,random.randint(-1,1),False,random.randint(-1,1)])
            self.enemies_list.append(enemy)
    def respawn_obj(self):
        for event in pygame.event.get(): # event loop
            # if event.type == self.goldEvent:
            #     self.invinsible = False
            # if event.type == self.blackEvent:
            #     self.slow = False
            # if event.type == self.respawn_time_gold:
            #     self.gold_obj = invinsible_obj([random.randint(60,250),25])
            # if event.type == self.respawn_time_black:
            #     self.black_obj = slow_obj([random.randint(60,250),25])
            if event.type == self.red_time:
                self.red = False
    def done_(self):
        # Fail = False
        # Pass = Fla
        # if self.reward > 7000 or self.reward < -10000:
        #     # self.reward += 100000
        #     # fail = False
        #     return True
        # elif self.reward < -6000:
        #     # self.reward -= 6000
        #     # fail = True
        #     return True


        # if self.position_cod():
        #     self.reward -= 5
            # fail = False
            # return False
        # else:
            self.reward += 5


            # return False
