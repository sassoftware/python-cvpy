class AnnotationLabel(object):

    def __init__(self, name: str = None, color: str = None):
        self._name = name
        self._color = color

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name) -> None:
        self._name = name

    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, color) -> None:
        self._color = color
