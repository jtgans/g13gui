import PIL
import struct
from io import BytesIO

from g13gui.bitwidgets.displaydevice import DisplayDevice


class DisplayMetrics(object):
    WIDTH_PIXELS = 160
    HEIGHT_PIXELS = 48


def ImageToLPBM(image):
    """Simple function to convert a PIL Image into LPBM format."""

    i = image.getdata()
    bio = BytesIO()

    maxBytes = (DisplayMetrics.WIDTH_PIXELS *
                DisplayMetrics.HEIGHT_PIXELS // 8)
    row = 0
    col = 0

    for byteNum in range(0, maxBytes):
        b = int()

        if row == 40:
            maxSubrow = 3
        else:
            maxSubrow = 8

        for subrow in range(0, maxSubrow):
            offset = col + (row + subrow) * DisplayMetrics.WIDTH_PIXELS
            b |= i[offset] << subrow

        bio.write(struct.pack('<B', b))

        col += 1
        if (col % 160) == 0:
            col = 0
            row += 8

    return bio.getvalue()


class G13DisplayDevice(DisplayDevice):
    """A bitwidget display device for the G13 LCD"""

    def __init__(self, manager):
        self._manager = manager

    @property
    def dimensions(self):
        return (DisplayMetrics.WIDTH_PIXELS, DisplayMetrics.HEIGHT_PIXELS)

    def update(self, image):
        lpbm = ImageToLPBM(image)
        self._pushFrame(lpbm)

    def _pushFrame(self, lpbm):
        self._manager.setLCDBuffer(lpbm)
