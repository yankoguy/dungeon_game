import pygame as pg
from meta_classes import Singleton
from game_settings import FPS


class GlobalTime(metaclass=Singleton):
    """
    GlobalTime stores important time varibles
    """
    def __init__(self):
        self.__delta_time = 0  # Fixed time that doesn't affected by the FPS rate
        self.__running_time = 0  # How much time does the game run
        self.__clock = pg.time.Clock()
        self.__sum_fps = 0
        self.__frames_passed = 1
        self._running_time = self.__delta_time

    def update(self):
        self.__delta_time = self.__clock.tick(FPS) / 1000
        self.__running_time += self.delta_time
        self.__frames_passed += 1
        self.__sum_fps += self.get_fps_rate()

    @property
    def delta_time(self):
        return self.__delta_time

    @property
    def running_time(self):
        return self.__running_time

    def reset_delta_time(self):
        self.__clock.tick(FPS)

    def get_fps_rate(self):
        return int(self.__clock.get_fps())

    def get_avg_fps_rate(self):
        return int(self.__sum_fps/self.__frames_passed)

class Timer:
    """
    The Timer used to determain time of actions in game, like the time between gun shoot for example
    Attributes:
        function_to_activate - which function to call when the timer reaches to zero
    """

    def __init__(self, start_time, function_to_activate=None):
        self.__time = start_time
        self.__function_to_activate = function_to_activate
        self.__pause = False  # Timer can be paused
        self.__finish = False

    @property
    def finish(self):
        return self.__finish

    def update_timer(self):
        if not self.__pause:
            if self.__time <= 0:
                self.__finish = True
                if self.__function_to_activate is not None:
                    self.__function_to_activate()
            else:
                self.__time -= GlobalTime.delta_time()

    def pause_timer(self):
        self.__pause = True

    def resume_timer(self):
        self.__pause = False
