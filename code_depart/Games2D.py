from pygame.locals import *
import pygame
import matplotlib.pyplot as plt
from Player import *
from Player_AI import *
from Maze import *
from Constants import *
from Path_Finder import *
from UnlockDoor import UnlockDoor
from KillMonster import *
import math

class App:
    windowWidth = WIDTH
    windowHeight = HEIGHT
    player = 0

    def __init__(self, mazefile):
        self.map = mazefile
        self._running = True
        self._win = False
        self._dead = False
        self._display_surf = None
        self._clock = None
        self._image_surf = None
        self.level = 0
        self.score = 0
        self.timer = 0.0
        self.ready_to_fight = False
        self.KillMonster = KillMonster(1000,0.02,50,0.9,0.2) #best config a date
        self.player = Player()
        self.maze = Maze(mazefile)
        self.perception = None
        self.pathfind = Path_Finder(mazefile)               # Initialise Path_Finder
        self.chemin = Path_Finder.find_path(self.pathfind)  # Retourne les nodes à atteindre
        if self.chemin == None:
            exit()
        self.ai_player = Player_AI(self.chemin[0],self.chemin, self.perception, self.player, self.map)
        

    def on_init(self):
        pygame.init()
        pygame.event.pump()
        self._display_surf = pygame.display.set_mode((self.windowWidth, self.windowHeight), pygame.HWSURFACE)
        self._clock = pygame.time.Clock()
        pygame.display.set_caption("Dungeon Crawler")
        pygame.time.set_timer(pygame.USEREVENT, 10)
        self._running = True
        self.maze.make_maze_wall_list()
        self.maze.make_maze_item_lists()
        self._image_surf = pygame.image.load("assets/Images/knight.png")
        self.player.set_position(self.maze.start[0], self.maze.start[1])
        self.player.set_size(PLAYER_SIZE*self.maze.tile_size_x, PLAYER_SIZE*self.maze.tile_size_x)
        self._image_surf = pygame.transform.scale(self._image_surf, self.player.get_size())

    def on_keyboard_input(self, keys):
        if keys[K_RIGHT] or keys[K_d]:
            self.move_player_right()

        if keys[K_LEFT] or keys[K_a]:
            self.move_player_left()

        if keys[K_UP] or keys[K_w]:
            self.move_player_up()

        if keys[K_DOWN] or keys[K_s]:
            self.move_player_down()

        # Utility functions for AI
        if keys[K_p]:
            perception = self.maze.make_perception_list(self.player, self._display_surf)
            if perception[3] != []:
                print("Monster detected!")
                self.KillMonster.setMonster(perception[3][0])
                best = self.KillMonster.genetic_algorithm()
                self.player.set_attributes(best["player"])
                
            # returns a list of 5 lists of pygame.rect inside the perception radius
            # the 4 lists are [wall_list, obstacle_list, item_list, monster_list, door_list]
            # item_list includes coins and treasure

        if keys[K_m]:
            for monster in self.maze.monsterList:
                print(monster.mock_fight(self.player))
            # returns the number of rounds you win against the monster
            # you need to win all four rounds to beat it

        if keys[K_SPACE]:
            if(len(self.maze.look_at_door(self.player, self._display_surf)) > 0):
                key = UnlockDoor.unlockDoor(self.maze.look_at_door(self.player, self._display_surf)[0])
                self.maze.unlock_door(key)
            # returns the state of the doors you can currently see
            # you need to unlock it by providing the correct key

        if keys[K_u]:
            self.maze.unlock_door('first')
            # returns true if the door is unlocked, false if the answer is incorrect and the door remains locked
            # if the door is unlocked you can pass through it (no visible change... yet)            
        if (keys[K_ESCAPE]):
            self._running = False

    # FONCTION À Ajuster selon votre format d'instruction
    def on_AI_input(self, instruction):
        if instruction == 'RIGHT':
            self.move_player_right()

        if instruction == 'LEFT':
            self.move_player_left()

        if instruction == 'UP':
            self.move_player_up()

        if instruction == 'DOWN':
            self.move_player_down()

    def on_collision(self):
        return self.on_wall_collision() or self.on_obstacle_collision() or self.on_door_collision()

    def move_player_right(self):
        self.player.moveRight()
        if self.on_collision():
            self.player.moveLeft()

    def move_player_left(self):
        self.player.moveLeft()
        if self.on_collision():
            self.player.moveRight()

    def move_player_up(self):
        self.player.moveUp()
        if self.on_collision():
            self.player.moveDown()

    def move_player_down(self):
        self.player.moveDown()
        if self.on_collision():
            self.player.moveUp()

    def on_wall_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.wallList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_obstacle_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.obstacleList)
        if not collide_index == -1:
            # print("Collision Detected!")
            return True
        return False

    def on_coin_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.coinList)
        if not collide_index == -1:
            self.maze.coinList.pop(collide_index)
            return True
        else:
            return False

    def on_treasure_collision(self):
        collide_index = self.player.get_rect().collidelist(self.maze.treasureList)
        if not collide_index == -1:
            self.maze.treasureList.pop(collide_index)
            return True
        else:
            return False

    def on_monster_collision(self):
        for monster in self.maze.monsterList:
            if self.player.get_rect().colliderect(monster.rect):
                return monster
        return False

    def on_door_collision(self):
        for door in self.maze.doorList:
            if self.player.get_rect().colliderect(door.rect):
                return True
        return False

    def on_exit(self):
        return self.player.get_rect().colliderect(self.maze.exit)

    def maze_render(self):
        self._display_surf.fill((0, 0, 0))
        self.maze.draw(self._display_surf)
        font = pygame.font.SysFont(None, 32)
        text = font.render("Coins: " + str(self.score), True, WHITE)
        self._display_surf.blit(text, (WIDTH - 120, 10))
        text = font.render("Time: " + format(self.timer, ".2f"), True, WHITE)
        self._display_surf.blit(text, (WIDTH - 300, 10))

    def on_render(self):
        self.maze_render()
        self._display_surf.blit(self._image_surf, (self.player.x, self.player.y))
        pygame.display.flip()

    def on_win_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("CONGRATULATIONS!", True, GREEN)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_death_render(self):
        self.maze_render()
        font = pygame.font.SysFont(None, 120)
        text = font.render("YOU DIED!", True, RED)
        self._display_surf.blit(text, (0.1 * self.windowWidth, 0.4 * self.windowHeight))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.on_init()

        while self._running:
            self._clock.tick(GAME_CLOCK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                if event.type == pygame.USEREVENT:
                    self.timer += 0.01
            pygame.event.pump()

            keys = pygame.key.get_pressed()
            self.on_keyboard_input(keys)
            self.ai_player.maze = self.map
            self.ai_player.player_size = self.player.get_size()
            self.ai_player.current_node = (math.floor((self.player.x)/self.maze.tile_size_x), math.floor(self.player.y/self.maze.tile_size_y))
            self.ai_player.perception = self.maze.make_perception_list(self.player, self._display_surf)
            instruction = Player_AI.get_instruction(self.ai_player)
            # Check for doors
            if(len(self.maze.look_at_door(self.player, self._display_surf)) > 0):
                key = UnlockDoor.unlockDoor(self.maze.look_at_door(self.player, self._display_surf)[0])
                self.maze.unlock_door(key)
            #print(str(current_node))
            
            if self.ready_to_fight == False:
                perception = self.maze.make_perception_list(self.player, self._display_surf)
                if perception[3] != []:
                    print("Monster detected!")
                    self.KillMonster.setMonster(perception[3][0])
                    best = self.KillMonster.genetic_algorithm()
                    self.player.set_attributes(best["player"])
                    self.ready_to_fight = True

            self.on_AI_input(instruction)

            if self.on_coin_collision():
                self.score += 1
            if self.on_treasure_collision():
                self.score += 10
            monster = self.on_monster_collision()
            if monster:
                self.ready_to_fight = False
                if monster.fight(self.player):
                    self.maze.monsterList.remove(monster)
                    self.score += 50
                else:
                    self._running = False
                    self._dead = True
            if self.on_exit():
                self._running = False
                self._win = True
            self.on_render()

        while self._win:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._win = False
            self.on_win_render()

        while self._dead:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._dead = False
            self.on_death_render()

        self.on_cleanup()
