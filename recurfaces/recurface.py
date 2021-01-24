import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from pygame import Surface, Rect

from typing import Sequence, List, Tuple, Optional, FrozenSet


class Recurface:
    def __init__(self, surface: Surface, position: Optional[Sequence[int]] = None):
        self.__surface = surface  # Should hold a pygame Surface
        self.__position = list(position) if position else None  # (x, y) position to blit to in the containing Surface

        self.__parent = None
        self.__children = set()

        self.__rect = None
        self.__rect_previous = None
        self.__rect_additional = []

    @property
    def surface(self) -> Surface:
        return self.__surface

    @surface.setter
    def surface(self, value: Surface):
        if self.__surface is value:
            return  # Surface is already correctly set

        self.__rect_previous = self.__rect
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
            self.__rect_previous = self.__rect

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

        self.__rect_previous = self.__rect
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

        self.__rect_previous = self.__rect
        self.__position[1] = value

    @property
    def parent(self) -> Optional["Recurface"]:
        return self.__parent

    @parent.setter
    def parent(self, value: Optional["Recurface"]):
        if self.__parent:
            if self.__parent is value:
                return  # Parent is already correctly set

            self._reset(forward_rects=True)
            self.__parent.remove_child(self)  # Remove from any previous parent

        self.__parent = value
        if self.__parent:
            self.__parent.add_child(self)

    @property
    def children(self) -> FrozenSet["Recurface"]:
        return frozenset(self.__children)

    def add_child(self, child: "Recurface") -> None:
        if child in self.__children:
            return  # Child is already added

        self.__children.add(child)
        child.parent = self

        child._reset()  # Extra call to reset() for redundancy

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
        If update_position is True, the provided rects will be offset by the position of .__rect before storing.
        """

        is_rendered = bool(self.__rect)  # If area has been rendered previously
        if not is_rendered:
            return

        for rect in rects:
            if rect:
                if update_position:
                    rect.x += self.__rect.x
                    rect.y += self.__rect.y

                self.__rect_additional.append(rect)

    def render(self, destination: Surface) -> List[Optional[Rect]]:
        """
        Draws all child surfaces to a copy of .surface, then draws the copy to the provided destination.
        Returns a list of pygame rects representing updated areas of the provided destination.

        Note: This function should be called on top-level (parent-less) recurfaces once per game tick, and
        pygame.display.update() should be passed all returned rects
        """

        result = []
        is_rendered = bool(self.__rect)  # If area has been rendered previously
        is_updated = bool(self.__rect_previous)  # If area has been changed or moved

        if not self.position:  # If position is None, nothing should display to the screen
            if is_rendered:  # If something was previously rendered, that area of the screen needs updating to remove it
                result.append(self.__rect_previous)
                self._reset()
            return result

        surface_working = self.surface.copy()

        child_rects = []
        for child in self.children:  # Render all child objects and collect returned Rects
            rects = child.render(surface_working)

            for rect in rects:
                if rect:  # Update rect position to account for nesting
                    rect.x += self.x
                    rect.y += self.y

                    child_rects.append(rect)

        self.__rect = destination.blit(surface_working, self.position)

        # As .__rect persists between renders, only a working copy is returned so that it is not externally modified
        rect_working = self.__rect.copy()

        if not is_rendered:  # On the first render, update the full area
            result.append(rect_working)

        elif is_updated:  # If a change was made, update the full area and the previous area
            result += [self.__rect_previous, rect_working]

        else:  # Child and additional rects are only used if the full area was not updated
            result += child_rects

            if self.__rect_additional:  # If there are any extra areas that need updating
                result += self.__rect_additional

        # Only .__rect should retain its value post-render. Whether used or not, _previous and _additional are reset
        self.__rect_previous = None
        self.__rect_additional = []
        return result

    def unlink(self) -> None:
        """
        Detaches the recurface from its parent and children.
        If there is a parent recurface, all children are added to the parent.
        This effectively removes the recurface from its place in the chain without leaving the chain broken
        """

        parent = self.parent
        self.parent = None

        for child in self.children:
            child.move(*self.position)
            child.parent = parent

        self._reset()

    def _reset(self, forward_rects: bool = False) -> None:
        """
        Sets variables which hold the object's rendering details back to their default values.
        This should only be done if the parent object is being changed
        """

        if forward_rects and self.parent:
            if self.parent:
                self.parent.add_update_rects([self.__rect], update_position=True)

        self.__rect = None
        self.__rect_previous = None
        self.__rect_additional = []
