from pygame import Surface

from classes import Recurface
from .constants import Constants


class Config:
    """
    Example config object - would be passed to Game upon instantiation
    """

    class ExampleView(Recurface):  # Dummy Recurface which will simply display a white screen
        def _update(self, elapsed, events):
            pass

        def _render(self):
            surface = Surface((800, 600))
            surface.fill(Constants.COLOURS["white"])

            return surface, (0, 0)

    SETTINGS = {
        "fps": 60,
        "resolution": (800, 600),
        "title": "Recurfaces"
    }

    STARTING_VIEW = ExampleView
