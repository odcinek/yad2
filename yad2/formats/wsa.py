import struct
import os
import sys
import Image
import random
import logging
from yad2.utils import Sprite
from yad2.encoders import Format40, Format80


class Wsa:

    def __init__(self, filename):
        self.logger = logging.getLogger('root')
        self.filename = filename
        self.filesize = os.path.getsize(self.filename)

    def extract(self):
        f = open(self.filename, "rb")
        numframes = struct.unpack('H', f.read(2))[0]
        width = struct.unpack('H', f.read(2))[0]
        height = struct.unpack('H', f.read(2))[0]
        delta = struct.unpack('H', f.read(2))[0]
        flags = struct.unpack('H', f.read(2))[0]

        self.logger.debug("numframes " + str(numframes) + ", width " + str(width) + ", height " + str(height) + ", delta " + str(delta) + ", flags " + str(flags) + ", fs " + str(self.filesize))
        offsets = []

        for i in range(0, numframes + 2):
            offsets.append(struct.unpack('I', f.read(4))[0])

        base = "".join(chr(x) for x in [0] * (width * height))

        images = []
        for i in range(0, len(offsets) - 2):
            length = int(offsets[i + 1] - offsets[i])
            f.seek(offsets[i])

            data = f.read(offsets[i + 1] - offsets[i])
            stage1 = Format80(data).decode()
            points = Format40(base, stage1).decode()

            image = Sprite(width, height)
            for index, pixel in enumerate(points):
                if index > width * height - 1:
                    break
                color = struct.unpack('B', pixel)[0]
                image.putpixel(index % width, int(index / width), color)

            images.append((str(i), image))
            base = points

        self.logger.debug("offsets " + str(offsets))

        f.close()
        return images
