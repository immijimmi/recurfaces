from pygame import Surface

from typing import Callable
from enum import Enum


class PipelineFlag(str, Enum):
    APPLY_CHILDREN = "apply_children"
    CACHE_SURFACE = "cache_surface"


class PipelineFilter:
    def __init__(
            self,
            filter_func: Callable[[Surface], Surface],
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
        process its input identically each time it is called;
        If, when given an input equivalent to a previous input, it always produces a corresponding output
        equivalent to the outputs produced the previous times it received that input, it is considered deterministic
        for the purposes of this class.

        This distinction is necessary to determine whether the filter's output can be cached or not
        """

        return self.__is_deterministic

    @property
    def filter(self) -> Callable[[Surface], Surface]:
        """
        The filter function stored under this property will receive a pygame Surface, and should return a
        corresponding surface modified as desired
        """
        return self.__filter
