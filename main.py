from pygame import *
import random
import xgame
import xinput
import xbreakout
import xfont
import xlevel
import xsound
import xutil


class BreakoutInput(xinput.InputManager):
    def on_keyup(self, event, game):
        super().on_keyup(event, game)
        if K_0 <= event.key <= K_9:
            xsound.SoundLibrary()['sound'+str(event.key - K_0 +1)].play()

        if event.key in {K_a, K_LEFT, K_d, K_RIGHT, K_w, K_UP, K_s, K_DOWN}:
            if isinstance(game.scene, xbreakout.Scene):
                dest = game.scene
            else:
                dest = game.scene.to_scene
            dest.paddle.velocity = (0, 0)
            if self.pressed_keys == set():
                dest.paddle.acceleration = (0, 0)


    def on_keydown(self, event, game):
        super().on_keydown(event, game)
        if not isinstance(game.scene, xbreakout.Scene):
            return
        if game.scene.orientation in {xutil.Orientation.UP, xutil.Orientation.DOWN}:
            if event.key == K_LEFT or event.key == K_a:
                game.scene.paddle.acceleration = (-1000, 0)
            if event.key == K_RIGHT or event.key == K_d:
                game.scene.paddle.acceleration = (1000, 0)
        else:
            if event.key == K_UP or event.key == K_w:
                game.scene.paddle.acceleration = (0, -1000)
            if event.key == K_DOWN or event.key == K_s:
                game.scene.paddle.acceleration = (0, 1000)
        if game.scene.paddle.acceleration != (0, 0) and game.scene.ball.velocity == (0, 0):
            game.scene.ball.velocity = math.Vector2(random.choice([-1, 1]),
                                                    random.choice([-1, 1])) * xbreakout.Ball.MAX_VEL


size = (800, 600)
colors = xlevel.LevelColors()

builder = xlevel.LevelBuilder()

breakout = xgame.Game("FREAKOUT", size,
                      BreakoutInput())

fonts = xfont.FontLibrary()
fonts['brick'] = ('data/PublicPixel.ttf', int(min(*size) * 0.025))

sounds = xsound.SoundLibrary()
sounds.set_ambient('data/sound/music.mp3')
sounds['loose'] = 'data/sound/Arkanoid SFX (10).wav'
sounds['enter'] = 'data/sound/Arkanoid SFX (7).wav'
sounds['leave'] = 'data/sound/Arkanoid SFX (8).wav'
sounds['exit'] = 'data/sound/Arkanoid SFX (9).wav'
sounds['spawn'] = 'data/sound/Arkanoid SFX (4).wav'
sounds['brick'] = 'data/sound/Arkanoid SFX (2).wav'
sounds['border'] = 'data/sound/Arkanoid SFX (1).wav'
sounds['paddle'] = 'data/sound/Arkanoid SFX (1).wav'


for i in range(12):
    sounds[f'sound{i+1}'] = f'data/sound/Arkanoid SFX ({i+1}).wav'

scene = xbreakout.Scene(size,
                        xlevel.LEVELS_TEMPLATE,
                        xutil.Orientation.UP,
                        builder, colors, fonts)

breakout.set_scene(scene)
breakout.run()
