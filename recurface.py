from abc import ABC


class Recurface(ABC):
    def __init__(self):
        self._children = []

    def update(self, elapsed, events):
        updated_rectangles = self._update(elapsed, events) or []

        for recurface in self._children:
            updated_rectangles += recurface.update(elapsed, events) or []

        return updated_rectangles

    def render(self):
        render_args = (surface, position) = self._render()

        for recurface in self._children:
            surface.blit(*recurface.render())

        return render_args

    def _update(self, elapsed, events):
        """
        Should return a list of pygame rectangles which indicate changed parts of the display
        """
        raise NotImplementedError

    def _render(self):
        """
        Should return a pygame surface, and the position to render it at in the parent surface
        """
        raise NotImplementedError
