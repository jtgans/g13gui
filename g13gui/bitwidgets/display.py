import PIL.ImageDraw
from PIL import Image

from g13gui.observer.subject import Subject


class Display(Subject):
    def __init__(self, displayDevice):
        self._displayDevice = displayDevice
        self.clear()

    def clear(self):
        size = self._displayDevice.dimensions
        self._bitmap = Image.new(mode='1', size=size)
        self._context = PIL.ImageDraw.Draw(self._bitmap)

    def getContext(self):
        return self._context

    def commit(self):
        self._displayDevice.update(self._bitmap)

    def debug(self):
        self._bitmap.show()
