import math
import random
import enum
from typing import List, Dict, Tuple
import logging
from game_objects import Sprite
from renderer import RenderMode, RenderLayer
from game_settings import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, RED, BLACK, GREEN, MAZE_SIZE, SPACE_BETWEEN_ROOM, \
    ROOM_SIZE, START_ROOM_POSITION, DOOR_WIDTH, DOOR_HEIGHT, SPACE_BETWEEN_ROOM_MINI_MAP, ROOM_MINI_MAP_SIZE, \
    START_MINI_MAP_ROOM_POSITION

from game_objects import Door
from collision import Collider, CollisionMasks

from enums import DoorPlacement


def get_opposite_door_placement(
        placement: DoorPlacement):  # The opposite placement of the door (TOP -> BOTTOM, RIGHT -> LEFT...)
    if placement == DoorPlacement.TOP:
        return DoorPlacement.BOTTOM
    if placement == DoorPlacement.BOTTOM:
        return DoorPlacement.TOP
    if placement == DoorPlacement.RIGHT:
        return DoorPlacement.LEFT
    if placement == DoorPlacement.LEFT:
        return DoorPlacement.RIGHT


class Room:
    def __init__(self,room_placement):
        self.__doors: List[Door] = []
        self.__room_placement = room_placement

    @property
    def doors(self):
        return self.__doors

    def get_doors_position(self) -> List[Tuple[float, float]]:
        #  returns the offset position of the doors in the room (not in pixels), for example in the door is TOP it will be (0.5,0)
        return [door.get_door_room_offset() for door in self.__doors]

    def is_available(self):
        #  if the room has already 4 doors you can't add any more to it
        return len(self.__doors) != 4

    def remove_door(self, door_placement_to_remove: DoorPlacement):
        for door in self.__doors:
            if door.placement == door_placement_to_remove:
                self.__doors.remove(door)
                return
        logging.warning("no such door placement was found")

    def add_door(self, placement: DoorPlacement = DoorPlacement.NO_PLACEMENT) -> DoorPlacement:
        if placement == DoorPlacement.NO_PLACEMENT:
            placement = self.__get_free_door_placement()

        #  Calcultate the door position (in pixels)
        x = self.__room_placement[0] * SPACE_BETWEEN_ROOM + START_ROOM_POSITION[0]
        y = self.__room_placement[1] * SPACE_BETWEEN_ROOM + START_ROOM_POSITION[1]

        self.__doors.append(Door(x,y, DOOR_WIDTH, DOOR_HEIGHT, GREEN,placement))
        return placement

    def __get_free_door_placement(self) -> DoorPlacement:  # returns a place where you can place door
        possible_placements = [placement.value for placement in DoorPlacement if
                               placement.value != DoorPlacement.NO_PLACEMENT.value]
        for door in self.__doors:
            possible_placements.remove(door.placement.value)
        return DoorPlacement(possible_placements[random.randint(0, len(possible_placements) - 1)])


class Maze:
    FIRST_ROOM_POSITION = (0, 0)

    def __init__(self, maze_size: int):
        if maze_size < 1:
            logging.warning(f"maze size must be larger than 0 got {maze_size}")

        first_room_in_maze = Room(Maze.FIRST_ROOM_POSITION)

        self.__rooms: List[Room] = [first_room_in_maze]
        self.__visual_rooms: Dict[Room, Tuple[int, int]] = {
            first_room_in_maze: Maze.FIRST_ROOM_POSITION}  # maps the room to his place in the array
        self.__maze_size = maze_size  # The size of the maze is how many rooms does it have
        self.__current_size = 1

        while self.__current_size < maze_size:
            self.__add_room_to_maze()

    @property
    def rooms(self):
        return self.__rooms

    def get_all_doors_in_maze(self) -> List[Door]:
        return [door for room in self.__rooms for door in room.doors]

    @staticmethod
    def __get_new_room_index(current_place: Tuple[int, int], door_placement: DoorPlacement) -> (
            int, int):  # returns the new index of the room which will be created in the maze array

        if door_placement == DoorPlacement.TOP:
            return current_place[0], current_place[1] - 1
        if door_placement == DoorPlacement.RIGHT:
            return current_place[0] + 1, current_place[1]
        if door_placement == DoorPlacement.BOTTOM:
            return current_place[0], current_place[1] + 1
        if door_placement == DoorPlacement.LEFT:
            return current_place[0] - 1, current_place[1]

    @property
    def rooms_position(self):
        return self.__visual_rooms.values()

    def __add_room_to_maze(self):
        # first lets choose a room to add door to
        room_placement = random.randint(0, self.__current_size - 1)
        while not self.__rooms[room_placement].is_available():
            room_placement = random.randint(0, self.__current_size - 1)
        #  now we have a room to add a door to

        door_placement = self.__rooms[room_placement].add_door()
        new_room_index = Maze.__get_new_room_index(self.__visual_rooms[self.__rooms[room_placement]],
                                                   door_placement)  # get the index in the array of the new room that was created

        if new_room_index in self.__visual_rooms.values():
            #  if there is already room in this place we will start all the process of finding new room
            #  the place of the room can already be occupied by another room that was built there before
            self.__rooms[room_placement].remove_door(door_placement)  # we need to remove the door we just added
            self.__add_room_to_maze()
            return

        #  now we create a new room
        new_room = Room(new_room_index)
        self.__rooms.append(new_room)

        self.__visual_rooms[new_room] = new_room_index  # map the room to his position in the array

        #  and lets add a door to this room (on the opposite side of the door in our old room)
        new_room.add_door(get_opposite_door_placement(DoorPlacement(door_placement)))

        self.__current_size += 1

    def generate_visual_rooms(self, space_between_rooms: int, start_position: Tuple[int, int]) -> List[
        Tuple[int, int]]:
        #  returns the position of the position in pixels of all the rooms according to the size and the space provided
        rooms_position = []
        for room_position in self.rooms_position:
            rooms_position.append((
                room_position[0] * space_between_rooms + start_position[0],
                room_position[1] * space_between_rooms + start_position[1]))

        return rooms_position

    def generate_visual_doors(self, space_between_rooms: int, start_position: Tuple[int, int]) -> List[
        Tuple[int, int]]:
        #  returns the position of the position in pixels of all the rooms according to the size and the space provided
        doors_position = []
        for room in self.__rooms:
            for door_position_offset in room.get_doors_position():
                doors_position.append((
                    self.__visual_rooms[room][0] * space_between_rooms + start_position[0] + door_position_offset[
                        0] * ROOM_SIZE,
                    self.__visual_rooms[room][1] * space_between_rooms + start_position[1] + door_position_offset[
                        1] * ROOM_SIZE))

        return doors_position
