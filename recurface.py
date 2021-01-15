import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import Surface, Rect
from typing import Sequence, List, Tuple, Optional


class Recurface:
    """A pygame framework used to organise Surfaces into a chain structure"""

    def __init__(self, surface: Surface, position: Optional[Sequence[int]] = None):
        self.__surface = surface  # Should hold a pygame Surface
        self.__position = list(position) if position else None  # (x, y) position to blit to in the containing Surface

        self.__parent = None
        self.__children = set()

        self.__surface__working = None
        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []

    @property
    def surface(self) -> Surface:
        return self.__surface

    @surface.setter
    def surface(self, value: Surface):
        if self.__surface is value:
            return  # Surface is already correctly set

        self.__rect__previous = self.__rect
        self.__surface = value

    @property
    def position(self) -> Optional[Tuple[int]]:
        return tuple(self.__position) if self.__position else None

    @position.setter
    def position(self, value: Optional[Sequence[int]]):
        if self.__position is None or value is None:
            if self.__position == value:
                return  # Position is already correctly set
        else:
            if self.__position[0] == value[0] and self.__position[1] == value[1]:
                return  # Position is already correctly set

        if self.__position:
            self.__rect__previous = self.__rect

        self.__position = [value[0], value[1]] if value else None

    @property
    def x(self) -> int:
        if not self.__position:
            raise ValueError("position is not currently set")

        return self.__position[0]

    @x.setter
    def x(self, value: int):
        if not self.__position:
            raise ValueError("position is not currently set")

        if self.__position[0] == value:
            return  # Position is already correctly set

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

        if self.__position[1] == value:
            return  # Position is already correctly set

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
        if child in self.__children:
            self.__children.remove(child)
            child.parent = None

    def move(self, x_offset: int = 0, y_offset: int = 0) -> Tuple[int]:
        """
        Adds the provided offset values to the recurface's current position.
        Returns a tuple representing the updated .position.

        Note: If .position is currently set to None, this will throw a ValueError
        """

        self.x += x_offset
        self.y += y_offset

        return self.position

    def add_update_rects(self, rects: Sequence[Optional[Rect]], update_position: bool = False) -> None:
        """
        Stores the provided pygame rects to be returned by this recurface on the next render() call.
        Used internally to handle removing child objects.
        If update_position is True, the provided rects will be offset by .position before storing.

        Note: If .position is currently set to None and update_position is True, this will throw a ValueError
        """

        if update_position:
            if not self.__position:
                raise ValueError("position is not currently set")

        for rect in rects:
            if rect:
                if update_position:
                    rect.x += self.__position[0]
                    rect.y += self.__position[1]

                self.__rect__additional.append(rect)

    def render(self, destination: Surface) -> List[Optional[Rect]]:
        """
        Draws all child surfaces to a copy of .surface, then draws the copy to the provided destination.
        Returns a list of pygame rects representing updated areas of the provided destination.

        Note: This function should be called on top-level (parent-less) recurfaces once per game tick, and
        pygame.display.update() should be passed all returned rects
        """

        result = []
        is_rendered = bool(self.__rect)  # If surface has been rendered previously
        is_updated = bool(self.__rect__previous)  # If surface has been changed or moved

        if self.__rect__additional:  # If there are any extra areas that need updating
            result += self.__rect__additional
            self.__rect__additional = []

        if not self.__position:  # If position is None, nothing should display to the screen
            if is_rendered:  # If something was previously rendered, that area of the screen needs updating to remove it
                result.append(self.__rect__previous)
                self.__rect__previous = None
                self.__rect = None  # is_rendered will now be False on the next .render call
            return result

        self.__surface__working = self.__surface.copy()
        for child in self.__children:  # Render all child objects and collect returned Rects
            rects = child.render(self.__surface__working)

            for rect in rects:
                if rect:
                    rect.x += self.__position[0]
                    rect.y += self.__position[1]

                    result.append(rect)

        self.__rect = destination.blit(self.__surface__working, self.__position)

        if not is_rendered:  # On the first render, update the full surface
            result.append(self.__rect)

        elif is_updated:
            result += [self.__rect__previous, self.__rect]
            self.__rect__previous = None

        return result

    def unlink(self) -> None:
        """
        Detaches the recurface from its parent and children.
        If there is a parent recurface, all children are added to the parent.
        This effectively removes the recurface from its place in the chain without leaving the chain broken
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
        Deleting the recurface will detach it from its parent and children, without linking the children to the parent.
        """

        for child in self.__children:
            self.remove_child(child)

        if self.__parent:
            self.__parent.add_update_rects([self.__rect, self.__rect__previous, *self.__rect__additional])
            self._reset()

            self.parent = None
