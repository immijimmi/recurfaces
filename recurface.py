import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import Surface, Rect
from typing import Iterable, Tuple, Optional


class Recurface:
    """A pygame framework used to organise Surfaces into a chain structure"""

    def __init__(self, surface: Surface, position: Iterable[int]):
        self.__surface = surface  # Should hold a pygame Surface
        self.__position = list(position)  # (x, y) position to blit to in the containing Surface

        self.__parent = None
        self.__children = set()

        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []

    @property
    def surface(self) -> Surface:
        return self.__surface

    @surface.setter
    def surface(self, value: Surface):
        self.__rect__previous = self.__rect
        self.__surface = value

    @property
    def position(self) -> Tuple[int]:
        return tuple(self.__position)

    @position.setter
    def position(self, value: Iterable[int]):
        self.__rect__previous = self.__rect
        self.__position = list(value)

    @property
    def x(self) -> int:
        return self.__position[0]

    @x.setter
    def x(self, value: int):
        self.__rect__previous = self.__rect
        self.__position[0] = value

    @property
    def y(self) -> int:
        return self.__position[1]

    @y.setter
    def y(self, value: int):
        self.__rect__previous = self.__rect
        self.__position[1] = value

    @property
    def parent(self) -> Optional["Recurface"]:
        return self.__parent

    @parent.setter
    def parent(self, value: "Recurface"):
        if self.__parent:
            if self.__parent is value:
                return  # Parent is already correctly set

            self.__parent.remove_child(self)  # Remove from any previous parent

        self.__parent = value
        if self.__parent:
            self.__parent.add_child(self)

    @property
    def children(self) -> frozenset:
        return frozenset(self.__children)

    def add_child(self, child: "Recurface") -> None:
        if child in self.__children:
            return  # Child is already added

        self.__children.add(child)
        child.parent = self
        child.reset()

    def remove_child(self, child: "Recurface") -> None:
        self.__children.remove(child)
        child.parent = None

    def render(self, destination: Surface) -> Iterable[Rect]:
        result = []

        for child in self.__children:
            rects = child.render(self.__surface)

            for rect in rects:
                if rect:
                    rect.x += self.__position[0]
                    rect.y += self.__position[1]

                    result.append(rect)

        is_rendered = bool(self.__rect)
        self.__rect = destination.blit(self.__surface, self.__position)
        if not is_rendered:
            result.append(self.__rect)  # On the first render, return the full surface
            return result

        if self.__rect__previous:
            result += [self.__rect__previous, self.__rect]
            self.__rect__previous = None

        if self.__rect__additional:
            result += self.__rect__additional
            self.__rect__additional = []

        return result

    def reset(self) -> None:
        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []

    def __del__(self):
        for child in self.__children:
            self.remove_child(child)

        self.parent = None
