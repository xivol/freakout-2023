from pygame import *
import xlevel
import xgame
import xsound
import xutil


class Paddle(sprite.Sprite):
    MAX_VEL = 500

    def __init__(self, size, color):
        super().__init__()
        self.velocity = (0.0, 0.0)
        self.acceleration = (0.0, 0.0)
        self.rect = Rect(0, 0, size[0], size[1])
        self.image = xutil.transparent_image(self.rect.size)
        draw.rect(self.image, color, self.rect, 0, int(size[1] / 2))

    def update(self, game, delta):
        tx = self.velocity[0] * delta
        ty = self.velocity[1] * delta
        cx, cy = self.rect.center
        steps = 5
        for i in range(1, steps + 1):
            self.rect.center = (cx + i * tx / steps, cy + i * ty / steps)
            if sprite.spritecollideany(self, game.scene.border):
                self.rect.center = (cx, cy)
                self.velocity = (0, 0)
                return

        self.velocity = math.Vector2(math.clamp(self.velocity[0] +
                                                self.acceleration[0] * delta,
                                                -Paddle.MAX_VEL,
                                                Paddle.MAX_VEL),
                                     math.clamp(self.velocity[1] +
                                                self.acceleration[1] * delta,
                                                -Paddle.MAX_VEL,
                                                Paddle.MAX_VEL))


    def on_collide(self, collider, scene):
        xsound.SoundLibrary()['paddle'].play()


class Ball(sprite.Sprite):
    MAX_VEL = 300

    def __init__(self, radius, color, colider_func):
        super().__init__()
        self.velocity = math.Vector2(0.0, 0.0)
        self.acceleration = math.Vector2(0.0, 0.0)
        self.collider_func = colider_func
        self.rect = Rect(0, 0, radius * 2, radius * 2)
        self.image = xutil.transparent_image(self.rect.size)
        draw.circle(self.image, color, (radius, radius), radius)

    def update(self, game, delta):
        tx = self.velocity[0] * delta
        ty = self.velocity[1] * delta
        cx, cy = self.rect.center
        steps = 10
        for i in range(1, steps + 1):
            self.rect.center = (cx + i * tx / steps,
                                cy + i * ty / steps)
            if collider := sprite.spritecollideany(self, game.scene.colliders):
                self.rect.center = (cx + (i - 1) * tx / steps, cy + (i - 1) * ty / steps)
                self.collider_func(self, collider)
                break
        self.velocity = math.Vector2(self.velocity[0] + self.acceleration[0] * delta,
                                     self.velocity[1] + self.acceleration[1] * delta)


class Scene:

    def __init__(self, size, layout, orientation, builder, colors, fonts, parent=None):
        self.parent = parent
        self.nested = None
        self.state = 'init'

        self.size = size
        self.layout = layout
        self.orientation = orientation
        self.builder = builder
        self.colors = colors
        self.fonts = fonts

        self.sprites = sprite.Group()
        self.colliders = sprite.Group()

        self.__init_scene__()

        if parent is None:
            self.spawn_ball()
            self.transition = TransitionStart(self)
            self.state = 'transition'
        else:
            self.state = 'playing'
        xsound.SoundLibrary().play_ambient(-1, 0, 8000)

    def __init_scene__(self):
        w, h = self.size
        pad = min(w, h) * 0.025
        bricks, border, pit = self.builder.build(self.layout, xlevel.BONUSES,
                                                 self.size,
                                                 self.orientation,
                                                 pad,
                                                 self.colors,
                                                 self.fonts['brick'])
        self.bricks = bricks
        self.sprites.add(bricks)
        self.border = border
        self.sprites.add(border)
        self.pit = pit
        self.sprites.add(pit)

        self.paddle = self.__make_paddle__()
        self.sprites.add(self.paddle)

        self.colliders.add(self.sprites)

    def __make_paddle__(self):
        w, h = self.size
        pad_h = min(w, h) * 0.025
        pad_w = w * 0.125
        if self.orientation in {xutil.Orientation.LEFT, xutil.Orientation.RIGHT}:
            pad_w, pad_h = pad_h, pad_w

        s = Paddle((pad_w, pad_h), self.colors.paddle)
        if self.orientation == xutil.Orientation.UP:
            s.rect.topleft = ((w - pad_w) / 2, h - 2 * pad_h)
        elif self.orientation == xutil.Orientation.DOWN:
            s.rect.topleft = ((w - pad_w) / 2, pad_h)
        elif self.orientation == xutil.Orientation.LEFT:
            s.rect.topleft = (w - 2 * pad_w, (h - pad_h) / 2)
        else:
            s.rect.topleft = (pad_w, (h - pad_h) / 2)
        return s

    def spawn_ball(self, offset=(0,0)):
        if hasattr(self, 'ball'):
            self.sprites.remove(self.ball)
        w, h = self.size
        radius = min(w, h) * 0.0125
        paddle = self.paddle.rect
        self.ball = Ball(radius, self.colors.ball, self.collider_func)
        if self.orientation == xutil.Orientation.UP:
            self.ball.rect.center = (paddle.left + paddle.size[0] / 2 + offset[0],
                                     paddle.top - radius + offset[1])
        elif self.orientation == xutil.Orientation.DOWN:
            self.ball.rect.center = (paddle.left + paddle.size[0] / 2+ offset[0],
                                     paddle.top + paddle.size[1] + radius+ offset[1])
        elif self.orientation == xutil.Orientation.LEFT:
            self.ball.rect.center = (paddle.left - radius+ offset[0],
                                     paddle.top + paddle.size[1] / 2+ offset[1])
        else:
            self.ball.rect.center = (paddle.left + paddle.size[0] + radius+ offset[0],
                                     paddle.top + paddle.size[1] / 2+ offset[1])
        self.sprites.add(self.ball)

    def draw(self, surface):
        surface.fill(self.colors.background)
        self.sprites.draw(surface)

    def update(self, game, delta):
        if self.state == 'transition':
            game.set_scene(self.transition)
            self.state = 'background'
        else:
            self.sprites.update(game, delta)

    def collider_func(self, ball, collider):
        v = ball.velocity
        r = collider.rect

        reflect_vel = Scene.bounce_from_rect(math.Vector2(*ball.rect.center),
                                             ball.velocity, collider.rect)
        if collider == self.pit:
            self.exit_from_pit(collider, ball)
        elif collider in self.bricks:
            self.sprites.remove(collider)
            self.colliders.remove(collider)
            if isinstance(collider, xlevel.EnterBrick):
                self.enter_the_brick(collider, ball)
        elif collider in self.border:
            xsound.SoundLibrary()['border'].play()

        collider.on_collide(ball, self)

        ball.velocity = reflect_vel

    def exit_from_pit(self, pit, ball):
        if self.parent is not None:
            self.parent.ball.velocity = self.ball.velocity
            self.transition = TransitionOut(self, self.parent, self.parent.portal)
            self.state = 'transition'
            xsound.SoundLibrary()['leave'].play()
        else:
            self.spawn_ball()
            self.transition = TransitionStart(self)
            self.state = 'transition'
            xsound.SoundLibrary()['loose'].play()

    def enter_the_brick(self, brick, ball):
        dir = Vector2(ball.rect.center) - Vector2(brick.rect.center)
        norm_pos = Vector2(dir.x / brick.rect.size[0], dir.y / brick.rect.size[1])
        i = xutil.argmax(list(map(lambda x: dir.normalize().dot(x.vector()),
                                  xutil.Orientation.all())))
        orient = xutil.Orientation(i)
        self.nested = Scene(self.size, brick.value, orient, self.builder,
                            xlevel.LevelColors(brick.colors), self.fonts, parent=self)
        pad = min(list(self.border)[0].rect.bottomright)
        if orient in {xutil.Orientation.UP, xutil.Orientation.DOWN}:
            self.nested.paddle.rect.center = (math.clamp(norm_pos[0] * (self.nested.size[0] - 2 * pad),
                                                         self.nested.paddle.rect.size[0] / 2 + pad,
                                                         self.nested.size[0] -
                                                         self.nested.paddle.rect.size[0] / 2 - pad),
                                              self.nested.paddle.rect.center[1])
            self.nested.spawn_ball(offset=(0, -pad if orient == xutil.Orientation.UP else pad))
        if orient in {xutil.Orientation.LEFT, xutil.Orientation.RIGHT}:
            self.nested.paddle.rect.center = (self.nested.paddle.rect.center[0],
                                              math.clamp(norm_pos[1] * (self.nested.size[1] - 2 * pad),
                                                         self.nested.paddle.rect.size[1] / 2 + pad,
                                                         self.nested.size[1] -
                                                         self.nested.paddle.rect.size[1] / 2 - pad))
            self.nested.spawn_ball(offset=(pad if orient == xutil.Orientation.RIGHT else -pad, 0))
        self.nested.ball.velocity = ball.velocity

        self.transition = TransitionIn(self, self.nested, brick.rect)
        self.portal = brick.rect.copy()
        self.state = 'transition'

    @staticmethod
    def bounce_from_rect(ball, vel, rect):
        # TODO: corner bounce sticks! need investigation
        # TODO: passthrough some corners! need investigation
        a = Vector2(rect.left, rect.top)
        b = Vector2(rect.right, rect.top)
        c = Vector2(rect.right, rect.bottom)
        d = Vector2(rect.left, rect.bottom)
        min_intersect = 1E20
        min_line = tuple()
        for line in [(a, b), (b, c), (c, d), (d, a)]:
            t1, t2 = xutil.intersect_params(ball, ball + vel, line[0], line[1])
            if t1 is not None and 0 <= t2 <= 1:
                if t1 < min_intersect:
                    min_intersect = t1
                    min_line = line
        if min_intersect == 1E20:
            return vel
        contact = min_intersect * vel + ball
        normal = xutil.normal_to_line(min_line[0], min_line[1])
        reflect = xutil.reflect_point_over(ball, contact, contact + normal)
        orig = xutil.reflect_point_over(ball + vel, contact, contact + normal)
        return reflect - orig


class Transition:
    STEPS = xgame.Game.FPS / 3

    def __init__(self, from_scene, to_scene):
        self.from_scene = from_scene
        self.to_scene = to_scene
        self.back_surface = self.__init_backsurface__()

    def __init_backsurface__(self):
        return Surface((1, 1))


class TransitionIn(Transition):
    def __init__(self, from_scene, to_scene, start_rect):
        super().__init__(from_scene, to_scene)
        self.current_rect = start_rect
        self.rect_inc = Vector2(from_scene.size[0] - start_rect.size[0],
                                from_scene.size[1] - start_rect.size[1]) / self.STEPS
        self.rect_off = - Vector2(from_scene.size[0] - start_rect.size[0],
                                  from_scene.size[1] - start_rect.size[1]) / self.STEPS / 2
        self.current_radius = min(*to_scene.size) / 4
        self.radius_inc = (self.current_radius - to_scene.ball.rect.width / 2) / \
                          (self.to_scene.size[0] / 2 / self.rect_inc[0])

    def __init_backsurface__(self):
        s = Surface(self.to_scene.size)
        self.to_scene.draw(s)
        return s

    def draw(self, surface):
        self.from_scene.draw(surface)
        draw.rect(surface, self.to_scene.colors.background, self.current_rect, width=int(min(*self.rect_inc)))
        surface.blit(self.back_surface, self.current_rect, self.current_rect)
        if self.current_rect.collidepoint(self.to_scene.ball.rect.center):
            draw.circle(surface, self.to_scene.colors.ball,
                        self.to_scene.ball.rect.center,
                        int(self.current_radius) // 2,
                        width=1)
            draw.circle(surface, self.to_scene.colors.ball,
                        self.to_scene.ball.rect.center,
                        int(self.current_radius),
                        width=3)

    def update(self, game, delta):
        if self.current_radius <= self.to_scene.ball.rect.size[0] / 2:
            game.set_scene(self.to_scene)
        else:
            if self.current_rect.collidepoint(self.to_scene.ball.rect.center):
                self.current_radius -= self.radius_inc
            self.current_rect.size = Vector2(self.current_rect.size) + self.rect_inc
            self.current_rect.topleft = Vector2(self.current_rect.topleft) + self.rect_off


class TransitionOut(Transition):
    def __init__(self, from_scene, to_scene, end_rect):
        super().__init__(from_scene, to_scene)
        self.current_rect = Rect((0, 0), from_scene.size)
        self.rect_off = (Vector2(self.current_rect.topleft) -
                         Vector2(end_rect.topleft)) / self.STEPS
        self.rect_inc = Vector2(from_scene.size[0] - end_rect.size[0],
                                from_scene.size[1] - end_rect.size[1]) / self.STEPS
        self.current_radius = min(*to_scene.size) / 4
        self.radius_inc = (self.current_radius - to_scene.ball.rect.width / 2) / \
                          (self.to_scene.size[0] / 2 / self.rect_inc[0])
        self.end_rect = end_rect

    def __init_backsurface__(self):
        s = Surface(self.from_scene.size)
        self.from_scene.draw(s)
        return s

    def update(self, game, delta):
        if self.current_radius <= self.to_scene.ball.rect.size[0] / 2:
            game.set_scene(self.to_scene)
        else:
            if not self.current_rect.collidepoint(self.to_scene.ball.rect.center):
                self.current_radius -= self.radius_inc
            self.current_rect.size = Vector2(self.current_rect.size) - self.rect_inc
            self.current_rect.topleft = Vector2(self.current_rect.topleft) - self.rect_off

    def draw(self, surface):
        self.to_scene.draw(surface)
        draw.rect(surface, self.to_scene.colors.background, self.current_rect, width=int(min(*self.rect_inc)))
        surface.blit(self.back_surface, self.current_rect, self.current_rect)
        if not self.current_rect.collidepoint(self.to_scene.ball.rect.center):
            draw.circle(surface, self.from_scene.colors.ball,
                        self.to_scene.ball.rect.center,
                        int(self.current_radius) // 2,
                        width=1)
            draw.circle(surface, self.to_scene.colors.ball,
                        self.to_scene.ball.rect.center,
                        int(self.current_radius),
                        width=3)


class TransitionStart(Transition):
    def __init__(self, scene):
        super().__init__(scene, scene)
        scene.sprites.remove(scene.ball)
        self.current_radius = min(*scene.size) / 4
        self.radius_inc = (self.current_radius - scene.ball.rect.size[0] / 2) / Transition.STEPS / 2
        xsound.SoundLibrary()['spawn'].play(fade_ms=200)

    def __init_backsurface__(self):
        s = Surface(self.to_scene.size)
        self.to_scene.draw(s)
        return s

    def draw(self, surface):
        surface.blit(self.back_surface, surface.get_rect())
        draw.circle(surface, self.to_scene.colors.ball,
                    self.to_scene.ball.rect.center,
                    int(self.current_radius) // 2,
                    width=1)
        draw.circle(surface, self.to_scene.colors.ball,
                    self.to_scene.ball.rect.center,
                    int(self.current_radius),
                    width=3)

    def update(self, game, delta):
        if self.current_radius <= self.to_scene.ball.rect.size[0] / 2:
            game.set_scene(self.to_scene)
            self.to_scene.sprites.add(self.to_scene.ball)

        self.current_radius -= self.radius_inc
