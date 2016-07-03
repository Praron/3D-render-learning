from PIL import Image
from vector import *
import re
import random

filename = 'head.obj'

H = 1000
W = 1000
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def parseVertices(file):
    file.seek(0)

    vertices = []
    for str in file.readlines():
        if re.match('^v +', str):
            v = []
            for p in (re.split(' ', str)):
                if p != 'v':
                    v.append(float(p))
            vertices.append(tuple(v))
    return vertices


def parseFaces(file):
    file.seek(0)

    faces = []
    for str in file.readlines():
        if re.match('^f +', str):
            f = []
            for p in (re.split(' ', str)):
                if p != 'f':
                    f.append(int(re.split('/', p)[0]) - 1)
            faces.append(tuple(f))
    return faces


def frange(x=0, y=1, step=1.0):
    while x < y:
        yield x
        x += step


def _resize(p, w, h):  # From .obj to normal coordinate system
    return ((p[0] + 1) * W / 2, (-1 * p[1] + 1) * H / 2)


def dot(pixels, x, y, color):
    try:
        pixels[x, y] = tuple([int(c) for c in color])
    except IndexError:
        pass


def line(pixels, x0, y0, x1, y1, color):
        if abs(x0 - x1) < abs(y0 - y1):
            x0, y0, x1, y1 = y0, x0, y1, x1
            steep = True
        else:
            steep = False

        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0

        dx = x1 - x0
        y = y1 - y0
        derror = 2 * abs(y)
        error = 0
        y = y0
        for x in frange(x0, x1):
            if steep:
                dot(pixels, y, x, color)
            else:
                dot(pixels, x, y, color)

            error += derror
            if error > dx:
                y += 1 if y0 < y1 else -1
                error -= 2 * dx


def triangle(pixels, p0, p1, p2, color):
    # Sort and make Vectors from tuples
    p0, p1, p2 = map(lambda p: Vector(*p),
                     sorted([p0, p1, p2], key=lambda Vector: Vector[1]))

    total_h = p2.y - p0.y + 1
    first_h = p1.y - p0.y + 1
    second_h = p2.y - p1.y + 1
    total_w = p2.x - p0.x
    first_w = p1.x - p0.x
    second_w = p2.x - p1.x
    for y in frange(0, total_h):
        first_part = y < first_h and first_h != 0
        current_h = first_h if first_part else second_h

        a = y / total_h
        b = (y - ((0 if first_part else first_h))) / current_h
        ax = p0.x + total_w * a
        bx = p0.x + first_w * b if first_part else p1.x + second_w * b
        if ax > bx:
            ax, bx = bx, ax

        line(pixels, ax, p0.y + y, bx, p0.y + y, color)


def render_obj(pixels, verts, faces, color):
    for face in faces:
        screen_vec = Vector(*(_resize(verts[face[i]], W, H)
                            for i in range(3)))
        world_vec = [Vector(*verts[face[i]]) for i in range(3)]
        n = (world_vec[2] - world_vec[0]) % (world_vec[1] - world_vec[0])
        n = n.normalize()
        light = -1 * n * Vector(0, 0, 0.5)
        if light > 0:
            triangle(pixels, *screen_vec,
                     color=(tuple(light * c for c in color)))


# class Render():
#     def __init__(self, img):
#         self.img = img
#         self.pixels = img.load()

#     def _resize(self, p, w, h):  # From .obj to normal coordinate system
#         return ((p[0] + 1) * W / 2, (-1 * p[1] + 1) * H / 2)

#     def dot(self, x, y, color):
#         try:
#             self.pixels[x, y] = tuple([int(c) for c in color])
#         except IndexError:
#             pass

#     def line(self, x0, y0, x1, y1, color):

#         if abs(x0 - x1) < abs(y0 - y1):
#             x0, y0, x1, y1 = y0, x0, y1, x1
#             steep = True
#         else:
#             steep = False

#         if x0 > x1:
#             x0, y0, x1, y1 = x1, y1, x0, y0

#         dx = x1 - x0
#         y = y1 - y0
#         derror = 2 * abs(y)
#         error = 0
#         y = y0
#         for x in frange(x0, x1):
#             if steep:
#                 self.dot(y, x, color)
#             else:
#                 self.dot(x, y, color)

#             error += derror
#             if error > dx:
#                 y += 1 if y0 < y1 else -1
#                 error -= 2 * dx

#     def triangle(self, p0, p1, p2, color):

#         # Sort and make Vectors from tuples
#         p0, p1, p2 = map(lambda p: Vector(*p),
#                          sorted([p0, p1, p2], key=lambda Vector: Vector[1]))

#         total_h = p2.y - p0.y + 1
#         first_h = p1.y - p0.y + 1
#         second_h = p2.y - p1.y + 1
#         total_w = p2.x - p0.x
#         first_w = p1.x - p0.x
#         second_w = p2.x - p1.x
#         for y in frange(0, total_h):
#             first_part = y < first_h and first_h != 0
#             current_h = first_h if first_part else second_h

#             a = y / total_h
#             b = (y - ((0 if first_part else first_h))) / current_h
#             ax = p0.x + total_w * a
#             bx = p0.x + first_w * b if first_part else p1.x + second_w * b
#             if ax > bx:
#                 ax, bx = bx, ax

#             self.line(ax, p0.y + y, bx, p0.y + y, color)

#     def img_obj(self, verts, faces, color):
#         for face in faces:
#             screen_vec = Vector(*(self._resize(verts[face[i]], W, H)
#                                 for i in range(3)))
#             world_vec = [Vector(*verts[face[i]]) for i in range(3)]
#             n = (world_vec[2] - world_vec[0]) % (world_vec[1] - world_vec[0])
#             n = n.normalize()
#             light = -1 * n * Vector(0, 0, 0.5)
#             if light > 0:
#                 self.triangle(*screen_vec,
#                               color=(tuple(light * c for c in color)))


def main():
    img = Image.new('RGB', (W, H), 'black')
    # r = Render(img)

    file = open(filename, 'r')
    verts = parseVertices(file)
    faces = parseFaces(file)
    # r.img_obj(verts, faces, (255, 150, 100))

    pixels = img.load()
    render_obj(pixels, verts, faces, (255, 150, 100))

    img.show()
    # img.save('/home/escapsit/Programming/3D rendering/result.png')


if __name__ == '__main__':
    main()
