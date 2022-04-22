from meta_classes import Singleton
from game_settings import WINDOW_WIDTH,WINDOW_HEIGHT,CAMERA_SPEED
import pygame as pg
from typing import Tuple

class Camera(metaclass=Singleton):
    def __init__(self):
        self.__camera_view = pg.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)  # The part of the map that shown in screen
        self.__camera_move_speed = CAMERA_SPEED
        self.__current_x_pos = int(WINDOW_WIDTH/2)
        self.__current_y_pos = int(WINDOW_HEIGHT/2)

    @property
    def x(self):
        return self.__current_x_pos

    @property
    def y(self):
        return self.__current_y_pos

    def screen_offset(self) -> Tuple: #  return the world position of an object in the screen
        #  for example the screen have range bentween (0,0) to (width, height) the world can position adds offset to this
        return self.x -int(WINDOW_WIDTH/2) , self.y-int(WINDOW_HEIGHT/2)

    def update(self,target_x,target_y) -> None:

        x = -target_x + int(WINDOW_WIDTH/2)
        y = -target_y + int(WINDOW_HEIGHT/2)
        self.__current_x_pos = target_x
        self.__current_y_pos = target_y
        self.__camera_view = pg.Rect(x,y,WINDOW_WIDTH,WINDOW_HEIGHT)

    def apply_pos(self, entity: pg.rect) -> pg.rect:
        """
        In order to "move" the camera we should move all the objects on the screen because we there is not real camera :)
        So we change the camera position and when we render an object we render it with the offset of the _camera
        attributes:
            entity - the object we are about to show
        """
        return entity.move(self.__camera_view.topleft)


