class Recurface:
    def __init__(self, surface, position):
        self.__surface = surface
        self.__position = list(position)

        self.__parent = None
        self.__children = set()

        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []

    @property
    def surface(self):
        return self.__surface

    @surface.setter
    def surface(self, value):
        self.__rect__previous = self.__rect
        self.__surface = value

    @property
    def position(self):
        return tuple(self.__position)

    @position.setter
    def position(self, value):
        self.__rect__previous = self.__rect
        self.__position = list(value)

    @property
    def x(self):
        return self.__position[0]

    @x.setter
    def x(self, value):
        self.__rect__previous = self.__rect
        self.__position[0] = value

    @property
    def y(self):
        return self.__position[1]

    @y.setter
    def y(self, value):
        self.__rect__previous = self.__rect
        self.__position[1] = value

    @property
    def parent(self):
        return self.__parent

    @parent.setter
    def parent(self, value):
        if self.__parent:
            self.__parent.remove_child(self)

        self.__parent = value
        self.__parent.add_child(self)

    @property
    def children(self):
        return frozenset(self.__children)

    def add_child(self, recurface):
        if recurface.parent != self:
            recurface.parent = self

        recurface.reset()
        self.__children.add(recurface)

    def remove_child(self, recurface):
        recurface.parent = None
        self.__children.remove(recurface)

    def render(self, destination):
        result = []

        for recurface in self.__children:
            rects = recurface.render(self.__surface)

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

    def reset(self):
        self.__rect = None
        self.__rect__previous = None
        self.__rect__additional = []
