from pygame import *
import math

import xsound
import xutil

LEVELS_TEMPLATE = \
    """
     #3# *** #6# *** #7# #8# *** #6# *** #3#
       #2# #4# *** #8# #0# #9# *** #4# #2#    
     #1# *** #5# *** #9# #7# *** #5# *** #1#
       *** *** *** *** #1# *** *** *** ***
    """

WALL_TEMPLATES = [
    """
      *** ___ *** ___ ___ *** ___ ***
    *** ___ *** ___ #$# ___ *** ___ *** 
      *** ___ *** ___ ___ *** ___ ***  
    """,
    """
      *** ___ *** ___ ___ *** ___ ***
    *** *** *** *** #$# *** *** *** *** 
      *** ___ *** ___ ___ *** ___ ***  
    """,
    """
      *** *** *** ___ ___ *** *** ***
    *** ___ *** ___ #$# ___ *** ___ *** 
      *** *** *** ___ ___ *** *** ***  
    """,
    """
      *** ___ *** *** *** *** ___ ***
    *** ___ *** *** #$# *** *** ___ *** 
      *** ___ *** *** *** *** ___ ***  
    """,
    """
      *** *** *** ___ ___ *** *** ***
    *** *** *** *** #$# *** *** *** *** 
      *** *** *** ___ ___ *** *** ***  
    """,
    """"
    *** *** *** *** ___ ___ *** *** *** ***
      *** ___ *** ___ #$# ___ *** ___ *** 
    *** *** *** *** ___ ___ *** *** *** ***
    """,
    """
    *** ___ *** *** ___ ___ *** *** ___ ***
      *** *** #2# *** #$# *** #2# *** *** 
    *** ___ *** *** ___ ___ *** *** ___ ***
      *** *** ___ *** ___ *** ___ *** *** 
    """,
    """
    *** ___ ___ *** ___ ___ *** ___ ___ ***
      *** #3# *** *** #$# *** *** #3# *** 
    ___ *** *** ___ ___ ___ ___ *** *** ___
      ___ *** ___ ___ ___ ___ ___ *** ___
    """,
    """
    *** ___ *** *** ___ ___ *** *** ___ ***
      *** *** #4# *** #$# *** #4# *** *** 
    ___ ___ *** *** ___ ___ *** ***
      *** *** ___ ___ ___ ___ ___ *** ***
    """,
    """
    *** *** ___ ___ *** *** ___ ___ *** ***
      *** *** *** *** #$# *** *** *** ***
        *** *** ___ *** *** ___ *** ***
      *** *** ___ ___ *** ___ ___  *** *** 
    """,
]

BONUSES = {
    "***": 5,
    "#$#": 100,
    "#0#": "inf",
    "#1#": WALL_TEMPLATES[1],
    "#2#": WALL_TEMPLATES[2],
    "#3#": WALL_TEMPLATES[3],
    "#4#": WALL_TEMPLATES[4],
    "#5#": WALL_TEMPLATES[5],
    "#6#": WALL_TEMPLATES[6],
    "#7#": WALL_TEMPLATES[7],
    "#8#": WALL_TEMPLATES[6],
    "#9#": WALL_TEMPLATES[7],
}


class Border(sprite.Sprite):
    def __init__(self, size, color):
        super().__init__()
        self.rect = Rect(0, 0, size[0], size[1])
        self.image = xutil.transparent_image(self.rect.size)
        self.image.fill(color)

    def on_collide(self, collider, scene):
        xsound.SoundLibrary()['border'].play()


class Brick(sprite.Sprite):
    def __draw_brick__(self, colors):
        w, h = self.rect.size
        pad = 4
        self.image.fill(colors.fill)
        border = self.rect.copy()
        border.topleft = (pad, pad)
        border.size = (w - 3 * pad, h - 3 * pad)
        for b in [border.topleft, border.topright, border.midtop,
                  border.bottomleft, border.bottomright, border.midbottom]:
            draw.rect(self.image, colors.border, Rect(b, (pad, pad)))

    def __init__(self, value, size, colors):
        super().__init__()
        self.value = value
        self.rect = Rect(0, 0, size[0], size[1])
        self.colors = colors
        self.image = xutil.transparent_image(self.rect.size)
        self.__draw_brick__(colors)

    def on_collide(self, collider, scene):
        xsound.SoundLibrary()['brick'].play()


class ExitBrick(Brick):
    def __draw_brick__(self, colors):
        w, h = self.rect.size
        pad = 2
        self.image.fill(colors.fill)
        border = self.rect
        border.topleft = (pad, pad)
        border.size = (w - 2 * pad, h - 2 * pad)
        draw.rect(self.image, colors.border, border, width=pad)
        draw.rect(self.image, colors.border, border, width=pad, border_radius=pad * 4)
        self.image.fill(colors.fill, Rect((pad * 6, 0), (w - 12 * pad, h)))
        self.image.fill(colors.fill, Rect((0, pad * 6), (w, h - 12 * pad)))

    def __draw_symbol__(self, colors, font):
        w, h = self.rect.size
        text = font.render(str(self.value), False, colors.accent)
        self.image.blit(text, (w // 2 - text.get_rect().width // 2,
                               h // 2 - text.get_rect().height // 2))

    def __init__(self, value, size, colors, font):
        super(ExitBrick, self).__init__(value, size, colors)
        self.__draw_symbol__(colors, font)

    def on_collide(self, collider, scene):
        xsound.SoundLibrary()['exit'].play()


class OmegaBrick(ExitBrick):
    def __draw_symbol__(self, colors, font):
        points = []
        for i in range(-10, 11):
            x = i / 10.0
            y = abs(x) * math.sqrt(1 - abs(x))
            points.append((x, y))
        for i in range(10, -11, -1):
            x = i / 10.0
            y = -abs(x) * math.sqrt(1 - abs(x))
            points.append((x, y))

        for i in range(len(points)):
            points[i] = (points[i][0] * self.rect.width / 3 + self.rect.center[0],
                         points[i][1] * self.rect.height / 3 + self.rect.center[1])

        draw.polygon(self.image, colors.accent, points, width=4)


class EnterBrick(Brick):
    def __draw_brick__(self, colors):
        w, h = self.rect.size
        pad = 2
        self.image.fill(colors.fill)
        border = self.rect.copy()
        border.topleft = (pad, pad)
        border.size = (w - 2 * pad, h - 2 * pad)
        draw.rect(self.image, colors.border, border, width=pad)
        core = border.copy()
        core.topleft = (pad + 5 * border.width / 12, pad + 5 * border.height / 12)
        core.size = (border.width / 6, border.height / 6)
        draw.rect(self.image, colors.accent, core)

    def __init__(self, value, size, colors, font):
        super().__init__(value, size, colors)

    def on_collide(self, collider, scene):
        xsound.SoundLibrary()['enter'].play()


class BrickColors:
    def __init__(self, fill, border, accent=None):
        self.fill = fill
        self.border = border
        self.accent = accent


class LevelColors:
    def __init__(self, brick=None):
        if not brick:
            self.background = (8, 0, 32)
            self.border = (128, 0, 128)
            self.paddle = (200, 128, 255)
            self.ball = (200, 128, 255)
            self.brick = (200, 64, 64)
            self.core = (255, 255, 128)
            self.brick_border = (0, 0, 24)
        else:
            self.background = brick.fill
            self.border = brick.border
            self.core = brick.accent
            self.paddle = brick.border
            self.ball = brick.border
            self.brick = brick.border
            self.brick_border = self.background

    def brick_color(self, i, j=0):
        hsva = Color(self.brick).hsva
        new_hue = hsva[0] - (360 / 20) * i if hsva[0] - (360 / 20) * i > 0 else hsva[0] - (360 / 20) * i + 360
        color = Color('black')
        color.hsva = (new_hue, hsva[1], hsva[2], hsva[3])
        return color


class LevelBuilder:
    _instance = None

    def __new__(cls, bricks_line=10):
        if cls._instance is None:
            cls._instance = super(LevelBuilder, cls).__new__(cls)
            cls._instance.elements = cls.__init_elements__()
            cls._instance.bricks_line = bricks_line
        return cls._instance

    @classmethod
    def __init_elements__(cls):
        elements = dict()
        elements['***'] = lambda **kwargs: Brick(kwargs['bonus'], kwargs['size'],
                                                 BrickColors(kwargs['colors'].brick,
                                                             kwargs['colors'].brick_border,
                                                             kwargs['colors'].brick_border))
        elements['#$#'] = lambda **kwargs: ExitBrick(kwargs['bonus'], kwargs['size'],
                                                     BrickColors(kwargs['colors'].core,
                                                                 kwargs['colors'].brick_border,
                                                                 kwargs['colors'].brick_border),
                                                     kwargs['font'])
        elements['#0#'] = lambda **kwargs: OmegaBrick(kwargs['bonus'], kwargs['size'],
                                                      BrickColors(kwargs['colors'].core,
                                                                  kwargs['colors'].brick_border,
                                                                  kwargs['colors'].brick_border),
                                                      kwargs['font'])
        for i in range(1, 10):
            elements[f'#{i}#'] = lambda **kwargs: EnterBrick(kwargs['bonus'], kwargs['size'],
                                                             BrickColors(kwargs['colors'].brick_color(
                                                                 int(kwargs['brick'].strip('#'))),
                                                                 kwargs['colors'].brick_border,
                                                                 kwargs['colors'].core), kwargs['font'])
        return elements

    def build(self, layout, bonuses, size, orientation, pad, colors, font):
        w, h = size
        offset_x = 4 * pad
        offset_y = 6 * pad

        box = list(xutil.make_border(w - 2 * pad, h - 2 * pad, pad))
        pit_rect = box.pop((orientation.value + 2) % 4)
        borders = sprite.Group()
        for rect in box:
            b = Border(rect.size, colors.border)
            if rect.top == 0:
                rect.top = pad
            if rect.left == 0:
                rect.left = pad
            b.rect = rect
            borders.add(b)

        if pit_rect.width > pit_rect.height:
            pit_rect.width = w
            if pit_rect.top == 0:
                pit_rect.top = pad
        else:
            pit_rect.height = h
            if pit_rect.left == 0:
                pit_rect.left = pad

        pit = Border(pit_rect.size, colors.border)
        pit.rect = pit_rect
        pit.rect.center = Vector2(pit.rect.center) + \
                          2 * orientation.vector() * pad

        wall = self.brick_wall(layout, bonuses, size,
                               orientation, (offset_x, offset_y),
                               colors, font)
        return wall, borders, pit

    def brick_wall(self, layout, bonuses, size,
                   orientation, offset, colors, font):
        w, h = size
        layout = layout.strip('\n')
        brick_w = (w - 2 * offset[0]) / (self.bricks_line + 1)
        brick_h = brick_w / w * h
        blank = brick_w // self.bricks_line

        x, y = offset
        if orientation == xutil.Orientation.DOWN:
            y = h - offset[1] - \
                (len(layout.split('\n')) - 1) * (brick_h + blank)

        wall = sprite.Group()
        for i, line in enumerate(layout.split('\n')):
            bricks = self.bricks_line - len(line.split())
            x = offset[0] + \
                (bricks % 2) * brick_w // 2 + \
                (bricks // 2) * (brick_w + blank)
            for j in line.split():
                if j in self.elements:
                    brick = self.elements[j](bonus=bonuses.get(j, None),
                                             size=(brick_w, brick_h),
                                             colors=colors,
                                             font=font,
                                             brick=j)
                    brick.rect.topleft = (x, y)
                    wall.add(brick)
                x += brick_w + blank
            y += brick_h + blank
            x = offset[0] + ((i + 1) % 2) * brick_w / 2
        return wall
