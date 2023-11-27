import enum
from pygame.math import *
import pygame


class Orientation(enum.Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

    @classmethod
    def all(cls):
        return [Orientation.UP, Orientation.LEFT,
                Orientation.DOWN, Orientation.RIGHT]

    def vector(self):
        if self == Orientation.UP:
            return Vector2(0, 1)
        elif self == Orientation.LEFT:
            return Vector2(1, 0)
        elif self == Orientation.DOWN:
            return Vector2(0, -1)
        elif self == Orientation.RIGHT:
            return Vector2(-1, 0)


def argmax(array):
    return array.index(max(array))


def transparent_image(size, depth=32):
    image = pygame.Surface(size, pygame.SRCALPHA, depth)
    image = image.convert_alpha()
    return image


def make_border(width, height, border):
    top = pygame.Rect(0, 0, width, border)
    bottom = pygame.Rect(0, height, width, border)
    left = pygame.Rect(0, 0, border, height)
    right = pygame.Rect(width, 0, border, height)
    return top, left, bottom, right


def intersect_params(start1, end1, start2, end2):
    v1 = (end1 - start1)
    v2 = (end2 - start2)
    if v2.x * v1.y != v1.x * v2.y:
        t1 = ((start2.y - start1.y) * v2.x - (start2.x - start1.x) * v2.y) / (v2.x * v1.y - v1.x * v2.y)
        t2 = ((start2.y - start1.y) * v1.x - (start2.x - start1.x) * v1.y) / (v2.x * v1.y - v1.x * v2.y)
        return t1, t2
    else:
        return None, None


def normal_to_line(start1, end1):
    v1 = end1 - start1
    return Vector2(-v1.y, v1.x)


def reflect_point_over(point, start1, end1):
    n = normal_to_line(start1, end1)
    t1, t2 = intersect_params(point, point + n, start1, end1)
    intersect = t1 * n + point
    return 2 * intersect - point
