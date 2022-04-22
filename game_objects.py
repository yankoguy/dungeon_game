import pygame as pg
from renderer import RenderMode, RenderLayer
from game_settings import PLAYER_SPEED, GREEN, GUN_COLOR, START_MINI_MAP_ROOM_POSITION, PLAYER_ICON_SIZE, \
    ROOM_MINI_MAP_SIZE, \
    WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, RED, BLACK, GREEN, MAZE_SIZE, SPACE_BETWEEN_ROOM, \
    ROOM_SIZE, START_ROOM_POSITION, DOOR_WIDTH, DOOR_HEIGHT, SPACE_BETWEEN_ROOM_MINI_MAP, ROOM_MINI_MAP_SIZE, \
    START_MINI_MAP_ROOM_POSITION, PLAYER_WIDTH, PLAYER_HEIGHT
from collision import Collider, CollisionMasks
from typing import Tuple, List, DefaultDict
from camera import Camera
from event_system import EventManager, EventNumber
from renderer import RenderLayer
from collections import defaultdict
import numpy as np

from enums import DoorPlacement


class ObjectMetaClass(type):
    """
    An metaclass for all objects in game
    """
    objects: DefaultDict[RenderLayer, List] = defaultdict(lambda: [])
    sprites: List = []

    def __call__(cls, *args, **kwargs):
        new_obj = super(ObjectMetaClass, cls).__call__(*args, **kwargs)
        cls.objects[new_obj.layer].append(new_obj)
        if isinstance(new_obj, Sprite):
            cls.sprites.append(new_obj)
        return new_obj


class Object(metaclass=ObjectMetaClass):
    def __init__(self, x, y, width, height, color, render_layer: RenderLayer, render_mode: RenderMode):
        self._rect = pg.Rect((x, y), (width, height))
        self._color = color
        self._render_layer = render_layer
        self._render_mode = render_mode

    @property
    def rect(self):
        return self._rect

    def destroy(self):
        ObjectMetaClass.objects[self.layer].remove(self)

    def set_position(self, new_x, new_y):
        self._rect.x = new_x
        self._rect.y = new_y

    def update(self):
        pass

    def late_update(self):
        pass

    def render(self, screen, camera):
        if self._render_mode == RenderMode.NORMAL:
            # The object is Sprite
            pg.draw.rect(screen, self._color, camera.apply_pos(self._rect))

        elif self._render_mode == RenderMode.UI:
            # The object is UI
            pg.draw.rect(screen, self._color, self._rect)

    @property
    def layer(self):
        return self._render_layer


class Sprite(Object):
    def __init__(self, x, y, width, height, color, render_layer: RenderLayer, render_mode: RenderMode,
                 mask: CollisionMasks,
                 masks_to_collide_with: Tuple[CollisionMasks]):
        super().__init__(x, y, width, height, color, render_layer, render_mode)
        self._collider = Collider(x, y, width, height, mask,
                                  masks_to_collide_with)  # The collider is an
        # object that gives you the information about the sprite collision

    @property
    def collider(self):
        return self._collider

    def destroy(self):
        super().destroy()
        ObjectMetaClass.sprites.remove(self)


class Door(Sprite):
    def __init__(self, x, y, width, height, color, door_placement: DoorPlacement):
        self.__placement = door_placement

        # object that gives you the information about the sprite collision

        #  Add the door offset to the position (in pixels)
        x += self.get_door_room_offset()[0] * ROOM_SIZE
        y += self.get_door_room_offset()[1] * ROOM_SIZE

        if door_placement == DoorPlacement.RIGHT or door_placement == DoorPlacement.LEFT:
            width, height = height, width  # if the door is on the left or right
            y -= DOOR_HEIGHT / 2
        else:
            x -= DOOR_WIDTH / 2

        super().__init__(x, y, width, height, color, RenderLayer.DOOR, RenderMode.NORMAL, CollisionMasks.DOOR,
                         (CollisionMasks.PLAYER,))

    @property
    def placement(self):
        return self.__placement

    def get_door_room_offset(self) -> Tuple[float, float]:
        #  returns the offset position of the door in the room (not in pixels), for example in the door is TOP it will be (0.5,0)
        if self.__placement == DoorPlacement.TOP:
            return 0.5, 0
        if self.__placement == DoorPlacement.RIGHT:
            return 1 - np.round(DOOR_HEIGHT / WINDOW_HEIGHT,
                                2), 0.5  # some calculation to adjust the door to be in a good position
        if self.__placement == DoorPlacement.BOTTOM:
            return 0.5, 1 - np.round(DOOR_HEIGHT / WINDOW_HEIGHT,
                                     2)  # some calculation to adjust the door to be in a good position
        if self.__placement == DoorPlacement.LEFT:
            return 0, 0.5

    def update(self):
        CAMERA_OFFSET_ADJUSMENT = DOOR_WIDTH  # some adjusments to the camera y position
        if self.collider.collision:
            player_offset = SPACE_BETWEEN_ROOM - ROOM_SIZE + DOOR_WIDTH
            camera_offset = player_offset + ROOM_SIZE
            player = self.collider.collision  # only the player can pass thorguht doors
            icon = player.icon
            if self.__placement == DoorPlacement.TOP:
                player.pass_trought_door(self._rect.x, self._rect.y - player_offset, 0,
                                         -camera_offset + CAMERA_OFFSET_ADJUSMENT)
                icon.set_position(icon.rect.x, icon.rect.y - SPACE_BETWEEN_ROOM_MINI_MAP)
            elif self.__placement == DoorPlacement.RIGHT:
                player.pass_trought_door(self._rect.x + player_offset, self._rect.y,
                                         camera_offset - CAMERA_OFFSET_ADJUSMENT, 0)
                icon.set_position(icon.rect.x + SPACE_BETWEEN_ROOM_MINI_MAP, icon.rect.y)
            elif self.__placement == DoorPlacement.BOTTOM:
                player.pass_trought_door(self._rect.x, self._rect.y + player_offset, 0,
                                         camera_offset - CAMERA_OFFSET_ADJUSMENT)
                icon.set_position(icon.rect.x, icon.rect.y + SPACE_BETWEEN_ROOM_MINI_MAP)
            elif self.__placement == DoorPlacement.LEFT:
                player.pass_trought_door(self._rect.x - player_offset, self._rect.y,
                                         -camera_offset + CAMERA_OFFSET_ADJUSMENT, 0)
                icon.set_position(icon.rect.x - SPACE_BETWEEN_ROOM_MINI_MAP, icon.rect.y)


class Player(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, GREEN, RenderLayer.PLAYER, RenderMode.NORMAL,
                         CollisionMasks.PLAYER, (CollisionMasks.DOOR,))
        self.__vx, self.__vy = 0, 0  # The velocity of the object
        self.__player_icon = Object(START_MINI_MAP_ROOM_POSITION[0] + (ROOM_MINI_MAP_SIZE - PLAYER_ICON_SIZE) / 2,
                                    START_MINI_MAP_ROOM_POSITION[1] + (ROOM_MINI_MAP_SIZE - PLAYER_ICON_SIZE) / 2
                                    , PLAYER_ICON_SIZE, PLAYER_ICON_SIZE, GREEN, RenderLayer.MINI_MAP, RenderMode.UI)
        self.__gun = Gun(x + PLAYER_WIDTH / 4, y + PLAYER_HEIGHT / 4, PLAYER_WIDTH / 2, PLAYER_HEIGHT / 2, GUN_COLOR,
                         RenderLayer.GUN,
                         RenderMode.NORMAL, self)

        EventManager().add_handler(EventNumber.A_KEY_HOLD, self.__change_velocity_x, -PLAYER_SPEED)
        EventManager().add_handler(EventNumber.W_KEY_HOLD, self.__change_velocity_y, -PLAYER_SPEED)
        EventManager().add_handler(EventNumber.D_KEY_HOLD, self.__change_velocity_x, PLAYER_SPEED)
        EventManager().add_handler(EventNumber.S_KEY_HOLD, self.__change_velocity_y, PLAYER_SPEED)

    def __change_velocity_x(self, amount: int):
        self.__vx += amount

    def __change_velocity_y(self, amount: int):
        self.__vy += amount

    @property
    def icon(self):
        return self.__player_icon

    @property
    def gun(self):
        return self.__gun

    def update(self):
        self.collider.update(self._rect.x - self.__vx,
                             self._rect.y - self.__vy)  # Update the collider to the position the player wants to move to
        self.__move()
        self.__movement()
        self.__gun.stick_to_holder()

    def __movement(self):
        self._rect.x += int(self.__vx)  # Move the bullet
        self._rect.y += int(self.__vy)  # Move the bullet
        self.__vx -= int(self.__vx)  # Subtract from velocity
        self.__vy -= int(self.__vy)  # Subtract from velocity

    def __move(self):
        if self.__vx != 0 and self.__vy != 0:
            #  diagonal movement
            self.__vx *= 0.707
            self.__vy *= 0.707

    def pass_trought_door(self, new_x, new_y, camera_x_offset, camera_y_offset):
        self._rect.x = new_x
        self._rect.y = new_y

        self.collider.update(new_x, new_y)  # Place the camera in the middle of the room
        camera = Camera()
        camera.update(camera.x + camera_x_offset, camera.y + camera_y_offset)


class Gun(Object):
    def __init__(self, x, y, width, height, color, render_layer: RenderLayer, render_mode: RenderMode, holder: Sprite):
        super().__init__(x, y, width, height, color, render_layer, render_mode)
        self.__holder = holder
        self.__x_offset_from_holder = x - holder.rect.x
        self.__y_offset_from_holder = y - holder.rect.y
        EventManager().add_handler(EventNumber.SPACE_BAR_CLICK, self.__fire, )

    def stick_to_holder(self):
        self._rect.x = self.__x_offset_from_holder + self.__holder.rect.x
        self._rect.y = self.__y_offset_from_holder + self.__holder.rect.y

    def __fire(self):
        Bullet(self.rect.x, self.rect.y, 10, 10, BLACK, CollisionMasks.BULLET, (),
               pg.mouse.get_pos()[0] + Camera().screen_offset()[0],
               pg.mouse.get_pos()[1] + + Camera().screen_offset()[1], 10)


class Bullet(Sprite):
    def __init__(self, x, y, width, height, color, mask: CollisionMasks, masks_to_collide_with: Tuple[CollisionMasks],
                 target_x, target_y, speed):
        super().__init__(x, y, width, height, color, RenderLayer.BULLET, RenderMode.NORMAL, mask, masks_to_collide_with)
        self.__vx, self.__vy = 0, 0  # The velocity of the object
        self.__speed = speed
        self.__movement_direction_x = (target_x - x) / (abs(target_x - x) + abs(target_y - y))
        self.__movement_direction_y = (target_y - y) / (abs(target_x - x) + abs(target_y - y))

    def update(self):
        self.__vx += self.__movement_direction_x * self.__speed
        self.__vy += self.__movement_direction_y * self.__speed
        self.__movement()

    def __movement(self):
        self._rect.x += int(self.__vx)  # Move the bullet
        self._rect.y += int(self.__vy)  # Move the bullet
        self.__vx -= int(self.__vx)  # Subtract from velocity
        self.__vy -= int(self.__vy)  # Subtract from velocity

    def __del__(self):
        print("I'm being automatically destroyed. Goodbye!")
