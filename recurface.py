import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import Surface, Rect
from typing import Iterable, Tuple, Optional


class Recurface:
    """A pygame framework used to organise Surfaces into a chain structure"""

    def __init__(self, surface: Surface, position: Optional[Iterable[int]] = None):
        self.__surface = surface  # Should hold a pygame Surface
        self.__position = list(position) if position else None  # (x, y) position to blit to in the containing Surface

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
    def position(self) -> Optional[Tuple[int]]:
        return tuple(self.__position) if self.__position else None

    @position.setter
    def position(self, value: Optional[Iterable[int]]):
        if self.__position:
            self.__rect__previous = self.__rect

        self.__position = list(value) if value else None

    @property
    def x(self) -> int:
        if not self.__position:
            raise ValueError("position is not currently set")

        return self.__position[0]

    @x.setter
    def x(self, value: int):
        if not self.__position:
            raise ValueError("position is not currently set")

        self.__rect__previous = self.__rect
        self.__position[0] = value

    @property
    def y(self) -> int:
        if not self.__position:
            raise ValueError("position is not currently set")

        return self.__position[1]

    @y.setter
    def y(self, value: int):
        if not self.__position:
            raise ValueError("position is not currently set")

        self.__rect__previous = self.__rect
        self.__position[1] = value

    @property
    def parent(self) -> Optional["Recurface"]:
        return self.__parent

    @parent.setter
    def parent(self, value: Optional["Recurface"]):
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
        child._reset()

    def remove_child(self, child: "Recurface") -> None:
        self.__children.remove(child)
        child.parent = None

    def add_update_rects(self, rects: Iterable[Optional[Rect]], update_position: bool = False) -> None:
        """
        Stores provided rects to be updated on the next render.
        If update_position is True, the rects are offset by self.position before storing
        """

        if update_position:
            if not self.__position:
                raise ValueError("position is not currently set")

            for rect in rects:
                rect.x += self.__position[0]
                rect.y += self.__position[1]

        self.__rect__additional += rects

    def render(self, destination: Surface) -> Iterable[Optional[Rect]]:
        """
        Blits surfaces to the provided destination for this object and any of its children.
        This function should be called on top-level (parent-less) recurfaces once per game tick, and
        pygame.display.update() should be passed all returned rects
        """

        result = []
        is_rendered = bool(self.__rect)  # Surface has been rendered previously

        if not self.__position:  # If position is None, nothing should display to the screen
            if is_rendered:  # If something was previously rendered, that area of the screen needs updating to remove it
                result.append(self.__rect)
                self.__rect = None  # is_rendered will now be False on the next .render call

            return result

        for child in self.__children:  # Render all child objects and collect returned Rects
            rects = child.render(self.__surface)

            for rect in rects:
                if rect:
                    rect.x += self.__position[0]
                    rect.y += self.__position[1]

                    result.append(rect)

        self.__rect = destination.blit(self.__surface, self.__position)

        if not is_rendered:  # On the first render, return the full surface
            return [self.__rect]

        if self.__rect__previous:  # If the surface was changed or moved
            result += [self.__rect__previous, self.__rect]
            self.__rect__previous = None

        if self.__rect__additional:  # If there are any extra areas that need updating
            result += self.__rect__additional
            self.__rect__additional = []

        return result

    def unlink(self) -> None:
        """
        Removes this object from its place in the chain,
        attaching any child objects to this object's parent if there is one
        """

        for child in self.children:
            child.parent = self.__parent

        self.parent = None

    def _reset(self) -> None:
        """
        Sets variables which hold the object's rendering details back to their default values.
        This should only be done if the parent object is being changed
        """

        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []

    def __del__(self):
        """
        Note that deleting this object will leave any child objects with no parent object.
        Calling .unlink() before deleting will attach child objects to this object's parent if there is one
        """

        for child in self.__children:
            self.remove_child(child)

        if self.__parent:
            self.__parent.add_update_rects([self.__rect, self.__rect__previous, *self.__rect__additional])
            self._reset()

            self.parent = None
