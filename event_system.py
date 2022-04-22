from meta_classes import Singleton
from collections import defaultdict
from typing import DefaultDict, Callable, List, Tuple
from enum import Enum


class EventNumber(Enum):
    SPACE_BAR_CLICK = 0
    A_KEY_HOLD = 1
    W_KEY_HOLD = 2
    D_KEY_HOLD = 3
    S_KEY_HOLD = 4

class Handler:
    def __init__(self, handler_function: Callable, *args: Tuple):
        self.__handler_function = handler_function
        self.__args = args

    def activate_handler(self):
        self.__handler_function(*self.__args)


class EventManager(metaclass=Singleton):
    def __init__(self):
        self.__handlers: defaultdict[EventNumber, List[Handler]] = defaultdict(lambda: [])

    def add_handler(self, event_number: EventNumber, handler: Callable, *args: Tuple):
        new_handler = Handler(handler, *args)
        self.__handlers[event_number].append(new_handler)

    def fire_event(self, event_number):
        #  activate all handlers that have the same event
        [handler.activate_handler() for handler in self.__handlers[event_number]]
