import pygame as pg
from game_time import GlobalTime
from game_settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, RED, BLACK, GREEN, MAZE_SIZE, SPACE_BETWEEN_ROOM, \
    ROOM_SIZE, START_ROOM_POSITION, DOOR_WIDTH, DOOR_HEIGHT, SPACE_BETWEEN_ROOM_MINI_MAP, ROOM_MINI_MAP_SIZE, \
    START_MINI_MAP_ROOM_POSITION
from game_objects import Object, Sprite, Player,ObjectMetaClass
from typing import List, Dict
from maze import Maze
from renderer import RenderMode, RenderLayer
from camera import Camera
from collections import defaultdict
from collision import CollisionMasks
from event_system import EventManager,EventNumber
import game_debug


class Game:
    def __init__(self):
        pg.init()
        pg.font.init()

        self.__font = pg.font.Font(None,30)

        pg.display.set_caption("My Game")
        self.__screen = pg.display.set_mode() #  same as pg.display.get_surface()

        self.__camera = Camera()
        self.__maze = Maze(MAZE_SIZE)
        self.__event_manager = EventManager()

        self.__game_clock = GlobalTime()
        self.__is_playing = True

        for room_position in self.__maze.generate_visual_rooms(SPACE_BETWEEN_ROOM,START_ROOM_POSITION):
            #  create all the rooms in the game
            Object(room_position[0], room_position[1], ROOM_SIZE, ROOM_SIZE, WHITE, RenderLayer.ROOM, RenderMode.NORMAL)

        for mini_map_room_position in self.__maze.generate_visual_rooms(SPACE_BETWEEN_ROOM_MINI_MAP,START_MINI_MAP_ROOM_POSITION):
            #  create all the rooms in the mini map
            Object(mini_map_room_position[0], mini_map_room_position[1], ROOM_MINI_MAP_SIZE, ROOM_MINI_MAP_SIZE,RED,RenderLayer.MINI_MAP,RenderMode.UI)

        p = Player(WINDOW_WIDTH/2,WINDOW_HEIGHT/2)


    def start(self):
        self.__game_loop()


    def __update(self):

        #collision
        for sprite in ObjectMetaClass.sprites:
            sprite.collider.get_collision(ObjectMetaClass.sprites)


    def __late_update(self):

        self.__game_clock.update()

        for objects_in_layer in ObjectMetaClass.objects.values():
            for obj in objects_in_layer:
                obj.update()

        for sprite in ObjectMetaClass.sprites:
            sprite.collider.late_update()

    def __render(self):
        self.__screen.fill(BLACK)
        for render_layer in RenderLayer:
            for object in ObjectMetaClass.objects[render_layer]:
                object.render(self.__screen,self.__camera)

        self.__debug()

        pg.display.flip()

    def __debug(self):
        game_debug.debugging("fps: " + str(self.__game_clock.get_fps_rate()),self.__font)
        game_debug.debugging("avg fps: " + str(self.__game_clock.get_avg_fps_rate()),self.__font, y = 40)

    def __events(self):
        self.__keys_to_events()
        pg.event.pump()

    def __keys_to_events(self):
        keys_pressed = pg.event.get()
        for event in keys_pressed:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.__event_manager.fire_event(EventNumber.SPACE_BAR_CLICK)

        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.__event_manager.fire_event(EventNumber.A_KEY_HOLD)
        if keys[pg.K_w]:
            self.__event_manager.fire_event(EventNumber.W_KEY_HOLD)
        if keys[pg.K_d]:
            self.__event_manager.fire_event(EventNumber.D_KEY_HOLD)
        if keys[pg.K_s]:
            self.__event_manager.fire_event(EventNumber.S_KEY_HOLD)

    def __game_loop(self):
        while self.__is_playing:
            self.__events()
            self.__update()
            self.__render()
            self.__late_update()

if __name__ == "__main__":
    Game().start()
