from pygame import Surface, Rect

from typing import Optional, FrozenSet, Any, Callable, Iterable, Union
from weakref import ref
from math import ceil
from functools import partial


class Recurface:
    def __init__(
            self, surface: Optional[Surface] = None, position: Optional[tuple[float, float]] = None,
            parent: Optional["Recurface"] = None, priority: Any = None, do_render: bool = True
    ):
        self.__surface = surface
        self.__render_position = list(position) if position else None
        self.__render_priority = priority
        self.__do_render = do_render

        # Attributes which hold the object's render state

        # Used to store the rect representing the most recent render location
        self.__rect: Optional[Rect] = None
        # If True, ensures that the previous render location gets updated on the next frame
        self.__has_rect_changed: bool = False
        # Stores subsections of the most recent render location which have since changed, if the whole has not
        self.__changed_sub_rects: list[Rect] = []
        # Should only ever contain rects in a top-level recurface. Stores extra areas in the destination to be updated
        self.__top_level_changed_rects: list[Rect] = []

        # Child recurfaces are stored multiple ways for optimisation
        self.__child_recurfaces = set()
        self.__frozen_child_recurfaces = frozenset()
        self.__ordered_child_recurfaces = tuple()

        # Optimisation attributes

        # Stores the previously generated working surface, unless a change invalidates it
        self.__cached_surface = None
        # Tracks whether a reset has occurred since the previous render
        self.__is_reset: bool = True
        # Used when determining whether to reset cached surfaces
        self.__can_render_previous = self._can_render

        self.__parent_recurface = None
        self.parent_recurface = parent  # Done this way to deliberately invoke the code in .parent's setter

    @property
    def surface(self) -> Optional[Surface]:
        """
        If set to None when this recurface is rendered, any children will simply be rendered directly onto the
        destination using this object's render position as an offset, instead of being rendered onto
        this object's surface.

        If this stored surface is mutated externally between frames (rather than replaced with a different surface,
        for example) .flag_update() must be invoked, to flag the previous render location to be updated on the
        next render
        """

        return self.__surface

    @surface.setter
    def surface(self, value: Optional[Surface]):
        if self.__surface == value:
            return  # Already set to the correct value

        self.__surface = value

        self._flag_rects()
        self._flag_cached_surfaces(do_clear_self=True)

    @property
    def parent_recurface(self) -> Optional["Recurface"]:
        if self.__parent_recurface is None:
            return None

        return self.__parent_recurface()

    @parent_recurface.setter
    def parent_recurface(self, value: Optional["Recurface"]):
        old_parent = self.parent_recurface

        if old_parent is value:  # Already set to the correct value
            return

        if old_parent is not None:
            old_parent._frontload_update(self._reset_rects())
            self._flag_cached_surfaces(do_clear_self=False)

            self.__parent_recurface = None
            old_parent.remove_child_recurface(self)
            """
            Note: It is unnecessary to call `old_parent._flag_cached_surfaces(do_clear_self=False)` here to cover
            changes caused by the removal of this child recurface. The reason for this is that the previous call
            to `self._flag_cached_surfaces(do_clear_self=False)` would reset its cached surface if this object
            can_render, and if this object cannot render then its removal is irrelevant even if it would change
            the value of the parent's can_render
            """

        else:  # If this recurface was previously top-level
            # Assumes that the new parent will render to the same destination as this recurface did
            value._top_level_update((*self._reset_rects(), *self.__top_level_changed_rects))
            self.__top_level_changed_rects = []

        if value is not None:
            self.__parent_recurface = ref(value)
            value.add_child_recurface(self)

            self._flag_cached_surfaces(do_clear_self=False)

    @property
    def ancestry(self) -> tuple["Recurface", ...]:
        """
        Returns the direct sequence of recurfaces from this recurface object to the top-level recurface object
        of this particular chain. This does not include any 'branches' (other recurface objects that
        are elsewhere in the same chain, but are not direct parent objects to this one)
        """

        result = []
        current_obj = self
        while current_obj:
            result.append(current_obj)

            current_obj = current_obj.parent_recurface

        return tuple(result)

    @property
    def child_recurfaces(self) -> Union[tuple["Recurface", ...], FrozenSet["Recurface"]]:
        """
        Returns the child recurfaces stored by this object, as a tuple in (ascending) order of
        render priority (if possible). If the render priorities of these child recurfaces cannot be compared
        (this will be the case if any of the recurfaces have the default priority of None, for example),
        the child recurfaces will instead be returned as a frozenset (unordered)
        """

        if self.are_child_recurfaces_ordered:
            return self.__ordered_child_recurfaces
        else:
            return self.__frozen_child_recurfaces

    @property
    def are_child_recurfaces_ordered(self) -> bool:
        return not (type(self.__ordered_child_recurfaces) is TypeError)

    @property
    def render_position(self) -> Optional[tuple[float, float]]:
        """
        Represents the stored (x, y) values used to render to the destination,
        before rounding to the nearest pixel has been applied
        """

        return tuple(self.__render_position) if self.__render_position else None

    @render_position.setter
    def render_position(self, value: Optional[tuple[float, float]]):
        # Rule out all cases in which the new value is equivalent to the existing value
        if (self.__render_position is None) or (value is None):
            if self.__render_position == value:
                return  # Already set to the correct value
        else:
            if (self.__render_position[0] == value[0]) and (self.__render_position[1] == value[1]):
                return  # Already set to the correct value

        self.__render_position = [value[0], value[1]] if value else None

        self._flag_rects()
        self._flag_cached_surfaces(do_clear_self=False)

    @property
    def render_coords(self) -> Optional[tuple[int, int]]:
        """
        Represents the exact (x, y) coordinates that this recurface will render at on the destination.

        The values have been rounded using .to_nearest_pixel() before being returned.
        This rounding must be done before the values are used be pygame, as it instead floors float values, which
        leads to stuttery motion in some cases
        """

        return self.to_nearest_pixel(*self.render_position) if self.__render_position else None

    @property
    def absolute_render_coords(self) -> Optional[tuple[int, int]]:
        """
        Returns the summed render coords of all recurfaces in this object's ancestry. Assuming that the top-level
        recurface in this object's chain is rendered directly to a pygame window, the return value represents
        this object's absolute display location on that pygame window
        """

        result = [0, 0]

        current_obj = self
        while current_obj:
            if not current_obj.render_position:
                # Unable to calculate absolute render position due to missing position in the chain
                return None

            current_obj_coords = current_obj.render_coords

            result[0] += current_obj_coords[0]
            result[1] += current_obj_coords[1]

            current_obj = current_obj.parent_recurface

        return result[0], result[1]

    @property
    def x_render_coord(self) -> int:
        """
        Represents the exact x coordinate that this recurface will render at on the destination
        """

        if self.__render_position is None:
            raise ValueError(".render_position is not currently set")

        return self.to_nearest_pixel(self.__render_position[0])

    @property
    def y_render_coord(self) -> int:
        """
        Represents the exact y coordinate that this recurface will render at on the destination
        """

        if self.__render_position is None:
            raise ValueError(".render_position is not currently set")

        return self.to_nearest_pixel(self.__render_position[1])

    @property
    def render_priority(self) -> Any:
        """
        Determines the (ascending) order in which sibling recurfaces are rendered on-screen
        """

        return self.__render_priority

    @render_priority.setter
    def render_priority(self, value: Any):
        if self.__render_priority == value:
            return  # Already set to the correct value

        # Determining if this recurface has changed from ordered to unordered, or vice-versa
        is_ordered_old = (self.parent_recurface and self.parent_recurface.are_child_recurfaces_ordered)
        self.__render_priority = value
        if self.parent_recurface:
            self.parent_recurface._organise_child_recurfaces()
        is_ordered_new = (self.parent_recurface and self.parent_recurface.are_child_recurfaces_ordered)

        if is_ordered_old != is_ordered_new:  # Ordering of all siblings has been changed, they must all be updated
            for sibling in self.parent_recurface.child_recurfaces:
                sibling._flag_rects()
        else:  # Only this object has been reordered amongst its siblings
            self._flag_rects()

        self._flag_cached_surfaces(do_clear_self=False)

    @property
    def do_render(self) -> bool:
        """
        A flag property to be used as desired, which determines whether this recurface will be rendered to
        its destination or not each time .render() is called on the top-level recurface
        """

        return self.__do_render

    @do_render.setter
    def do_render(self, value: bool):
        if self.__do_render == value:
            return  # Already set to the correct value

        self.__do_render = value

        self._flag_rects()
        self._flag_cached_surfaces(do_clear_self=False)

    @property
    def is_rendered(self) -> bool:
        return bool(self.__rect)

    @property
    def _can_render(self) -> bool:
        """
        Used to quickly estimate if this recurface or its children are able to render anything onto its destination
        in the next render
        """

        if not (self.do_render and self.render_position):
            return False

        if (not self.surface) and (not self.child_recurfaces):
            return False

        return True

    def generate_surface_copy(self) -> Surface:
        """
        Can optionally be overridden.

        Generates a copy of this recurface object's stored surface. Raises an error if unable to do so.
        By default, this method uses the standard Surface.copy() method provided by pygame.

        For any subclasses which can implement a less resource-intensive process to generate a copy
        of their particular surface (for example, a subclass whose stored surface is simple to create from scratch and
        will remain static throughout execution), it is recommended to override this method to do so
        """

        if self.surface is None:
            raise ValueError(".surface does not contain a valid pygame Surface to copy")

        return self.surface.copy()

    def add_child_recurface(self, child: "Recurface") -> None:
        if child in self.__child_recurfaces:  # Child is already present
            return

        self.__child_recurfaces.add(child)
        self._organise_child_recurfaces()

        if child.parent_recurface is not self:
            child.parent_recurface = self

    def remove_child_recurface(self, child: "Recurface") -> None:
        if child in self.__child_recurfaces:
            self.__child_recurfaces.remove(child)
            self._organise_child_recurfaces()

            if child.parent_recurface is self:
                child.parent_recurface = None

    def move_render_position(self, x_offset: float = 0, y_offset: float = 0) -> tuple[float, float]:
        """
        Adds the provided offset values to the recurface's current position.
        Returns a tuple representing the updated position.

        Note: If .render_position is currently set to None, this will throw a ValueError
        """

        if self.__render_position is None:
            raise ValueError(".render_position is not currently set")

        old_position = self.render_position

        self.render_position = (
            old_position[0] + x_offset,
            old_position[1] + y_offset
        )

        return self.render_position

    def unlink(self) -> None:
        """
        Detaches the recurface from its parent and children.
        Children then have their positions updated to account for the removal of this recurface's offset,
        and are added directly to the erstwhile parent (if there is one).
        This effectively extracts the recurface from its chain, leaving everything else in place
        """

        parent = self.parent_recurface
        self.parent_recurface = None

        for child in self.child_recurfaces:
            child.parent_recurface = None

            child.move_render_position(*self.render_position)
            child.parent_recurface = parent

    def render(self, destination: Surface) -> list[Rect]:
        """
        Wrapper method for `._render()`.
        Returns an optimised list of pygame rects representing updated areas of the provided destination.

        This method should typically be called once per frame, on a single top-level recurface per external destination,
        and the returned rects used to update that destination
        """

        result = self.__top_level_changed_rects
        self.__top_level_changed_rects = []

        result += self._render(destination)

        return self.trimmed_rects(result)

    def _render(self, destination: Surface, coords_offset: tuple[int, int] = (0, 0)) -> list[Rect]:
        """
        Responsible for drawing copies of all stored surfaces in this recurface chain to the provided destination,
        at the appropriate locations and in the appropriate order.
        Returns a list of pygame rects representing updated areas on the provided destination
        """

        result = []

        # Helper variable used in rendering
        is_fully_updated = False
        if self.__has_rect_changed:
            is_fully_updated = True
        elif (not self.is_rendered) and self.surface:
            is_fully_updated = True

        # Adding rects for any areas which have changed since the last frame
        if self.is_rendered:
            if self.__has_rect_changed:
                result.append(self.__rect)
            elif self.__changed_sub_rects:
                result += self.__changed_sub_rects

        # Resetting attributes holding values from the previous render, now that they have been accounted for above
        self.__rect = None
        self.__has_rect_changed = False
        self.__changed_sub_rects = []

        # Checking if nothing new should be rendered to the screen
        if (not self.do_render) or (self.render_position is None):
            return result

        # Rendering
        if self.surface:  # This recurface must paste a surface onto the destination
            if self.__cached_surface:  # A previously made surface is still stored for re-use
                working_surface = self.__cached_surface

            else:  # A fresh surface must be made
                working_surface = self.generate_surface_copy()

                # Render all child recurfaces onto the working surface, in the correct order
                for child in self.child_recurfaces:
                    child_rects = child._render(working_surface)

                    # Child rects are only needed if the full area of this recurface will not be updated
                    if not is_fully_updated:
                        for child_rect in child_rects:
                            child_rect.x += self.x_render_coord
                            child_rect.y += self.y_render_coord
                            result.append(child_rect)

            # Set the cached surface afresh
            self.__cached_surface = working_surface

            # Apply the surface to its destination
            self.__rect = destination.blit(
                working_surface,
                (
                    self.x_render_coord + coords_offset[0],
                    self.y_render_coord + coords_offset[1]
                )
            )

            if is_fully_updated:
                # A copy of the rect is returned to prevent external modification
                result.append(self.__rect.copy())

        else:  # If this recurface has no surface, children are to be rendered directly onto the destination
            new_coords_offset = (
                coords_offset[0] + self.x_render_coord,
                coords_offset[1] + self.y_render_coord
            )

            # Render all child recurfaces onto the destination, in the correct order
            for child in self.child_recurfaces:
                rects = child._render(destination, coords_offset=new_coords_offset)
                for rect in rects:
                    result.append(rect)

        # This attribute is only reset if a fresh render was completed, so it is split from the reset attributes above
        self.__is_reset = False

        return result

    def _flag_rects(self) -> None:
        """
        This method manually flags the area covered by this recurface and its children to be updated on the next render
        """

        if self.is_rendered:
            self.__has_rect_changed = True
        else:
            for child in self.child_recurfaces:
                self._frontload_update(child._reset_rects())

    def _flag_cached_surfaces(self, do_clear_self: bool = False) -> None:
        """
        This method handles the clearing of cached surfaces which have been invalidated due to changes to the state of
        this recurface or one of its descendants
        """

        if do_clear_self:
            self.__cached_surface = None

        # Getting the previous value and a new one for can_render
        can_render_previous = self.__can_render_previous
        can_render = self._can_render
        # Storing the updated value
        self.__can_render_previous = can_render

        if not self.parent_recurface:
            return

        if can_render or (can_render != can_render_previous):
            return self.parent_recurface._flag_cached_surfaces(do_clear_self=True)

    def _reset_rects(self) -> list[Rect]:
        """
        Sets the variables which hold this object's rendering details back to their default values, and returns
        the last render location (if any). Recursively resets child recurfaces, and (if necessary) returns their
        render locations too.
        """

        # If this recurface has already been reset once since the last render, no further work needs doing
        if self.__is_reset:
            return []

        result = []

        if self.is_rendered:
            """
            If this recurface is rendered, it is only necessary to return `.__rect` from this method
            as that area will cover all child recurfaces
            """
            result.append(self.__rect)

        for child in self.child_recurfaces:
            child_rects = child._reset_rects()

            if not self.is_rendered:
                result += child_rects

        self.__rect = None
        self.__has_rect_changed = False
        self.__changed_sub_rects = []

        self.__is_reset = True

        return result

    def _frontload_update(self, rects: Iterable[Rect]) -> None:
        """
        Stores the provided rects inside the first recurface in this object's ancestry (starting from this one)
        which is rendered; these rects are assumed to represent subsections of that recurface's rendered surface
        to be updated next frame.

        If there are no rendered recurfaces in this object's ancestry, the top-level recurface stores these rects
        separately, to be returned as separate areas of the outer destination which must be updated next frame
        """

        if not rects:  # If there are no rects, nothing needs doing
            return

        if self.parent_recurface and (not self.is_rendered):
            return self.parent_recurface._frontload_update(rects)

        if self.is_rendered:
            # Add this object's render coords to the provided rects
            for rect in rects:
                rect.x += self.x_render_coord
                rect.y += self.y_render_coord

                self.__changed_sub_rects.append(rect)
        else:  # The top-level recurface is not rendered, meaning that these rects are for the destination
            # As this object is not part of the current render hierarchy, its offset need not be applied to the rects
            self.__top_level_changed_rects += list(rects)

    def _top_level_update(self, rects: Iterable[Rect]) -> None:
        """
        Stores the provided rects inside the top-level recurface in this chain, where they will be used
        next frame to update their respective areas on the outer destination.

        The provided rects are not assumed to be subsections of this chain's covered area, and therefore
        can represent areas on the destination which are entirely separate from this chain.
        """

        if not rects:  # If there are no rects, nothing needs doing
            return

        if self.parent_recurface:
            return self.parent_recurface._top_level_update(rects)

        self.__top_level_changed_rects += list(rects)

    def _organise_child_recurfaces(self) -> None:
        self.__frozen_child_recurfaces = frozenset(self.__child_recurfaces)

        try:
            self.__ordered_child_recurfaces = tuple(
                sorted(self.__child_recurfaces, key=lambda recurface: recurface.render_priority)
            )
        except TypeError as ex:  # Unable to sort recurfaces due to non-comparable priority values
            self.__ordered_child_recurfaces = ex

    @staticmethod
    def trimmed_rects(rects: Iterable[Rect]) -> list[Rect]:
        """
        Optimisation method, applied just before rects are returned from the top-level recurface.

        Returns a new list containing only those rects whose bounds are not entirely contained within the bounds of
        another rect present in the list
        (this includes removing additional identical copies of rects)
        """

        result = []

        # A rect can only be a direct subset of another rect if its surface area is equal or smaller
        rects_by_surface_area = sorted(rects, key=lambda rect: -(rect.width * rect.height))

        for rect_index, rect_to_check in enumerate(rects_by_surface_area):
            do_include = True
            for bigger_rect_index in range(0, rect_index):
                bigger_rect = rects_by_surface_area[bigger_rect_index]

                is_contained = not (
                        (rect_to_check.left < bigger_rect.left) or
                        (rect_to_check.right > bigger_rect.right) or
                        (rect_to_check.top < bigger_rect.top) or
                        (rect_to_check.bottom > bigger_rect.bottom)
                )  # This should require the minimum amount of comparisons on average

                if is_contained:
                    do_include = False
                    break

            if do_include:
                result.append(rect_to_check)

        return result

    @staticmethod
    def to_nearest_pixel(*coords: float) -> Union[None, int, tuple[int, ...]]:
        """
        For each provided coordinate, returns an integer pixel position to use for the purposes of rendering
        to that coordinate.

        Rounding is implemented half-up rather than the default banker's rounding, as consistency is considered
        more important than preventing the average of aggregated numbers from increasing,
        for the purposes of this project (object motion should be as smooth as possible)
        """

        result = []

        for coord in coords:
            if coord % 1 == 0.5:
                result.append(ceil(coord))
            else:
                result.append(round(coord))

        if (coords_len := len(result)) == 0:
            return None
        elif coords_len == 1:
            return result[0]
        else:
            return tuple(result)
