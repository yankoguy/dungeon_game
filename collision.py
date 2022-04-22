from enum import Enum
from utilitiez import on_object

class CollisionMasks(Enum):
    WALLS = 1
    BUILDINGS = 2
    ENEMY = 3
    PLAYER = 4
    BULLET=5
    COLLECTABLE = 6
    DOOR = 7

class CollisionPositions(Enum):
    NO_CLLOISTION = 0
    TOP = 1
    BOTTOM = 2
    LEFT = 3
    RIGHT = 4

class Collider:
    """
    An object that responsible for checking collision between objects
    """

    def __init__(self, x, y, width, height, mask: CollisionMasks, masks_to_collide_with: tuple):
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__mask = mask
        self.__masks_to_collide_with = masks_to_collide_with
        self.__collision = None # Will be equal to the sprite this object collided with in current frame
        self.__collistion_positions = []# In which border of the collider did the collide occurred

    def update(self, x, y):
        """
        Update the collider position
        """
        self.__x = x
        self.__y = y

    @property
    def collision(self):
        return self.__collision

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def mask(self):
        return self.__mask

    @property
    def collistion_positions(self):
        return self.__collistion_positions

    def late_update(self):
        self._reset_collision()

    def _reset_collision(self):
        self.__collision = None
        self.__collistion_positions = []

    def _get_collision_pos(self) -> list:
        collistions = []
        if self.__y > self.collision.collider.y:
            collistions.append(CollisionPositions.TOP)
        else:
            collistions.append(CollisionPositions.BOTTOM)
        if self.__x > self.collision.collider.x:
            collistions.append(CollisionPositions.LEFT)
        else:
            collistions.append(CollisionPositions.RIGHT)

        return collistions

    def get_collision(self, sprites: list) -> None:
        """
        Returns The object that collide with, if collide with nothing returns None
        Attributes:
            sprites - A list of sprites that the player may collide with
        """
        for sprite in sprites:
            collider = sprite.collider
            if collider is not self and collider.mask in self.__masks_to_collide_with:
                if on_object(self.__x, self.__y, self.__width, self.__height, collider.x, collider.y, collider.width, collider.height):
                    self.__collision = sprite
                    self.__collistion_positions = self._get_collision_pos()