from pygame import Surface, Rect

from typing import List, Tuple, Optional, FrozenSet, Any
from weakref import ref


class Recurface:
    def __init__(
            self, surface: Optional[Surface] = None, position: Optional[Tuple[float, float]] = None,
            parent: Optional["Recurface"] = None, priority: Any = None
    ):
        self.__render_position = list(position) if position else None  # (x, y) to render at in the containing Surface
        self.__render_priority = priority  # Determines how recurfaces at the same nesting level are layered on screen

        self.__rect = None
        self.__rect_previous = None
        self.__additional_rects = []

        self.__child_recurfaces = set()
        self.__frozen_child_recurfaces = frozenset()
        self.__ordered_child_recurfaces = tuple()

        self.__surface = None
        self.surface = surface  # Deliberately invokes the code in .surface's setter

        self.__parent_recurface = None
        self.parent_recurface = parent  # Deliberately invokes the code in .parent's setter

    @property
    def surface(self) -> Optional[Surface]:
        return self.__surface

    @surface.setter
    def surface(self, value: Optional[Surface]):
        if self.__surface == value:
            return  # Surface is already correctly set

        self.__surface = value
        self.update_surface()

    @property
    def parent_recurface(self) -> Optional["Recurface"]:
        if self.__parent_recurface is None:
            return None

        return self.__parent_recurface()

    @parent_recurface.setter
    def parent_recurface(self, value: Optional["Recurface"]):
        curr_parent = self.parent_recurface

        if curr_parent is not None:
            if curr_parent is value:
                return  # Parent is already correctly set

            self._reset_rects(do_forward_rects=True)
            curr_parent.remove_child_recurface(self)  # Remove from any previous parent

        self.__parent_recurface = None if value is None else ref(value)

        new_parent = self.parent_recurface
        if new_parent is not None:
            new_parent.add_child_recurface(self)

    @property
    def lineage(self) -> Tuple["Recurface", ...]:
        """
        Returns the full sequence of recurfaces from this Recurface object to the top-level Recurface object
        in this particular rendering hierarchy. This does not include any 'branches' (other Recurface objects that
        are in the rendering hierarchy, but are not directly in the chain of parent objects to this one)
        """

        result = []
        current_obj = self
        while current_obj:
            result.append(current_obj)

            current_obj = current_obj.parent_recurface

        return tuple(result)

    @property
    def child_recurfaces(self) -> FrozenSet["Recurface"]:
        return self.__frozen_child_recurfaces

    @property
    def ordered_child_recurfaces(self) -> Tuple["Recurface", ...]:
        """
        Returns the child recurfaces linked to this Recurface object, sorted by their `.render_priority`.
        If the child recurfaces' priorities cannot be compared
        (this will be the case if any of the recurfaces have the default priority of None),
        the relevant TypeError will be raised
        """

        if type(self.__ordered_child_recurfaces) is TypeError:
            raise TypeError("unable to sort child recurfaces by priority")
        else:
            return self.__ordered_child_recurfaces

    @property
    def render_position(self) -> Optional[Tuple[float, float]]:
        """
        These render position values are rounded before being handed to pygame, as pygame floors float values by default
        which would cause the position of rendered objects to be a pixel off in some cases
        """

        return tuple(self.__render_position) if self.__render_position else None

    @render_position.setter
    def render_position(self, value: Optional[Tuple[float, float]]):
        if self.__render_position is None or value is None:
            if self.__render_position == value:
                return  # Position is already correctly set
        else:
            if self.__render_position[0] == value[0] and self.__render_position[1] == value[1]:
                return  # Position is already correctly set

        if self.__render_position:
            self.update_surface()

        self.__render_position = [value[0], value[1]] if value else None

    @property
    def absolute_render_position(self) -> Optional[Tuple[float, float]]:
        """
        Returns the summed render positions of all Recurface objects that are in the direct chain of objects from
        this one up to the top-level Recurface object. Assuming that the top-level Recurface object is rendered
        directly to a pygame window without any further offset, this return value represents
        this Recurface object's absolute display location on that pygame window
        """

        result = [0, 0]
        current_obj = self
        while current_obj:
            if current_obj.render_position is None:  # If any object in the hierarchy has a position of None
                return None

            result[0] += current_obj.x_render_position
            result[1] += current_obj.y_render_position

            current_obj = current_obj.parent_recurface

        return tuple(result)

    @property
    def x_render_position(self) -> float:
        if self.__render_position is None:
            raise ValueError("`.render_position` is not currently set")

        return self.__render_position[0]

    @x_render_position.setter
    def x_render_position(self, value: float):
        if self.__render_position is None:
            raise ValueError("`.render_position` is not currently set")

        if self.__render_position[0] == value:
            return  # Position is already correctly set

        self.__render_position[0] = value
        self.update_surface()

    @property
    def y_render_position(self) -> float:
        if self.__render_position is None:
            raise ValueError("`.render_position` is not currently set")

        return self.__render_position[1]

    @y_render_position.setter
    def y_render_position(self, value: float):
        if self.__render_position is None:
            raise ValueError("`.render_position` is not currently set")

        if self.__render_position[1] == value:
            return  # Position is already correctly set

        self.__render_position[1] = value
        self.update_surface()

    @property
    def render_priority(self) -> Any:
        return self.__render_priority

    @render_priority.setter
    def render_priority(self, value: Any):
        if self.__render_priority == value:
            return  # Priority is already correctly set

        self.__render_priority = value

        if self.parent_recurface:
            self.parent_recurface._organise_child_recurfaces()

    def add_child_recurface(self, child: "Recurface") -> None:
        if child in self.__child_recurfaces:
            return  # Child is already added

        self.__child_recurfaces.add(child)
        self._organise_child_recurfaces()

        child.parent_recurface = self

        child._reset_rects()  # Resetting child rects here for redundancy

    def remove_child_recurface(self, child: "Recurface") -> None:
        if child in self.__child_recurfaces:
            self.__child_recurfaces.remove(child)
            self._organise_child_recurfaces()

            child.parent_recurface = None

    def move_render_position(self, x_offset: float = 0, y_offset: float = 0) -> Tuple[float, float]:
        """
        Adds the provided offset values to the recurface's current position.
        Returns a tuple representing the updated .position.

        Note: If .position is currently set to None, this will throw a ValueError
        """

        self.x_render_position += x_offset
        self.y_render_position += y_offset

        return self.render_position

    def update_surface(self) -> None:
        """
        This method manually flags the stored surface's area to be updated on the next render.
        It should be invoked externally whenever the stored surface has been mutated in place
        (as opposed to replaced with a different Surface object)
        """

        self.__rect_previous = self.__rect

    def add_update_rects(self, *rects: Optional[Rect], do_update_position: bool = False) -> None:
        """
        Stores the provided pygame rects to be returned by this recurface on the next `.render()` call.
        Used internally to handle removing child objects.

        Any rects passed into this method should be bounded within the area of this recurface's stored surface,
        as they will only be used if not all of this recurface's surface area needs updating on the next render.

        If do_update_position is True, the provided rects will be offset by the position of .__rect before storing
        """

        is_rendered = bool(self.__rect)  # If area has been rendered previously
        if not is_rendered:
            return

        for rect in rects:
            if rect:
                if do_update_position:
                    """
                    Assumes that the area each provided rect represents is offset from the *last rendered* position
                    of this recurface's rect, not the *current* position - as the former would be the case if
                    the provided rects are from now-removed child recurfaces
                    """
                    rect.x += self.__rect.x
                    rect.y += self.__rect.y

                self.__additional_rects.append(rect)

    def render(self, destination: Surface) -> List[Rect]:
        """
        Wrapper method for `._render()`.
        Returns an optimised list of pygame rects representing updated areas of the provided destination.

        This method should typically be called on top-level (parent-less) recurfaces once per game tick,
        and `pygame.display.update()` should be passed the returned list of rects
        """

        return self.trimmed_rects(self._render(destination))

    def _render(self, destination: Surface) -> List[Optional[Rect]]:
        """
        Draws all child surfaces to a copy of .surface, then draws the copy to the provided destination.
        Returns a list of pygame rects representing updated areas of the provided destination
        """

        result = []
        is_rendered = bool(self.__rect)  # If area has been rendered previously
        is_updated = bool(self.__rect_previous)  # If area has been changed or moved

        # If either the stored surface or current position is None, nothing should display to the screen
        if (self.surface is None) or (self.render_position is None):
            if is_rendered:  # If something was previously rendered, that area of the screen needs updating to remove it
                result.append(self.__rect_previous)
                self._reset_rects()
            return result

        surface_working = self.generate_surface_copy()

        try:
            child_recurfaces = self.ordered_child_recurfaces
        except TypeError:
            child_recurfaces = self.child_recurfaces

        child_rects = []
        for child in child_recurfaces:  # Render all child objects in the correct order and collect returned Rects
            rects = child._render(surface_working)

            for rect in rects:
                if rect:  # Update rect position to account for nesting
                    rect.x += self.x_render_position
                    rect.y += self.y_render_position

                    child_rects.append(rect)

        self.__rect = destination.blit(
            surface_working,
            (
                round(self.x_render_position),
                round(self.y_render_position)
            )
        )

        # As .__rect persists between renders, only a working copy is returned so that it is not externally modified
        rect_working = self.__rect.copy()

        if not is_rendered:  # On the first render, update the full area
            result.append(rect_working)

        elif is_updated:  # If a change was made, update the full area and the previous area
            result += [self.__rect_previous, rect_working]

        else:  # Child and additional rects are only used if the full area was not updated
            result += child_rects

            if self.__additional_rects:  # If there are any extra areas that need updating
                result += self.__additional_rects

        # Only .__rect should retain its value post-render. Whether used or not, ._previous and ._additional are reset
        self.__rect_previous = None
        self.__additional_rects = []
        return result

    def unlink(self) -> None:
        """
        Detaches the recurface from its parent and children.
        If there is a parent recurface, all children are added to the parent.
        This effectively removes the recurface from its place in the chain without leaving the chain broken
        """

        parent = self.parent_recurface
        self.parent_recurface = None

        for child in self.child_recurfaces:
            child.move_render_position(*self.render_position)
            child.parent_recurface = parent

        self._reset_rects()  # Resetting rects here for redundancy

    def generate_surface_copy(self) -> Surface:
        """
        Can optionally be overridden.

        Generates a copy of this Recurface object's Surface, or raises an error if unable to do so.
        By default, this uses the standard `Surface.copy()` method provided by pygame.

        For any subclasses which can implement a less resource-intensive method to generate a copy
        of their Surface, it is recommended to override this method to do so
        """

        if self.surface is None:
            raise ValueError("`.surface` does not contain a valid pygame Surface to copy")

        return self.surface.copy()

    def _reset_rects(self, do_forward_rects: bool = False) -> None:
        """
        Sets variables which hold the object's rendering details back to their default values.
        This is automatically done whenever the parent object is changed
        """

        if do_forward_rects and self.parent_recurface:
            self.parent_recurface.add_update_rects(self.__rect, do_update_position=True)

        self.__rect = None
        self.__rect_previous = None
        self.__additional_rects = []

    def _organise_child_recurfaces(self) -> None:
        self.__frozen_child_recurfaces = frozenset(self.__child_recurfaces)

        try:
            self.__ordered_child_recurfaces = tuple(
                sorted(self.__child_recurfaces, key=lambda recurface: recurface.render_priority)
            )
        except TypeError as ex:  # Unable to sort recurfaces due to non-comparable priority values
            self.__ordered_child_recurfaces = ex

    @staticmethod
    def trimmed_rects(rects: List[Optional[Rect]]) -> List[Rect]:
        """
        Optimisation method applied in `.render_to_display()`.

        Returns a new list containing the same rects as the provided list, but with any None objects removed
        and any Rect objects whose bounds are entirely contained within another Rect object in the list also removed
        (this includes removing additional identical copies of rects)
        """

        result = []

        excluded_rect_indexes = set()
        for rect_index, rect in enumerate(rects):
            if rect is None:
                continue

            include_rect = True
            for other_rect_index, other_rect in enumerate(rects):
                if other_rect is None:
                    continue

                if other_rect_index == rect_index:
                    continue

                if other_rect_index in excluded_rect_indexes:
                    continue

                if is_rect_outside_other_rect := (
                    (rect.left < other_rect.left) or
                    (rect.right > other_rect.right) or
                    (rect.top < other_rect.top) or
                    (rect.bottom > other_rect.bottom)
                ):
                    continue

                else:  # If `rect` is equal to or inside `other_rect`
                    include_rect = False
                    break

            if include_rect:
                result.append(rect)
            else:
                excluded_rect_indexes.add(rect_index)

        return result
