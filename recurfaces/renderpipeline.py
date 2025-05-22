from pygame import Surface

from typing import Callable
from enum import Enum


class PipelineFlag(str, Enum):
    APPLY_CHILDREN = "apply_children"
    CACHE_SURFACE = "cache_surface"


class PipelineFilter:
    def __init__(
            self,
            filter_func: Callable[[Surface, tuple[int, int]], tuple[Surface, tuple[int, int]]],
            is_deterministic: bool
    ):
        self.__filter = filter_func
        self.__is_deterministic = is_deterministic

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented

        return (self.filter is other.filter) and (self.is_deterministic == other.is_deterministic)

    @property
    def is_deterministic(self) -> bool:
        """
        This attribute should be set to a value which indicates whether the stored filter function will
        modify its inputs predictably each time it is called; If, when given the same arguments, it always returns
        the same output values, it is considered deterministic for the purposes of this class.

        This distinction is necessary to determine whether the filter's outputs can be cached or not
        """

        return self.__is_deterministic

    @property
    def filter(self) -> Callable[[Surface, tuple[int, int]], tuple[Surface, tuple[int, int]]]:
        """
        The filter function stored under this property will receive 2 arguments - a pygame Surface, and
        a tuple of two int coordinates representing the current on-screen render location of that surface.

        It should also return a surface and a tuple of two int coordinates (both placed in an outer tuple),
        modified as desired
        """
        return self.__filter
