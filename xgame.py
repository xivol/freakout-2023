import pygame


class Game:
    FPS = 60
    BG_COLOR = (0, 0, 0)

    def __init__(self, name, size, input):
        pygame.init()
        self.display = pygame.display.set_mode(size)
        pygame.display.set_caption(name)
        self.clock = pygame.time.Clock()
        self.input = input
        self.scene = None
        self.running = False
        self.pause = False

    def set_scene(self, scene):
        self.scene = scene

    def run(self):
        self.running = True
        while self.running:
           self.update()
        pygame.quit()

    def update(self):
        for event in pygame.event.get():
            self.input.handle_input_event(event, self)
        self.input.handle_pressed_keys(self)

        self.render(self.display)

        self.clock.tick(Game.FPS)
        if not self.pause:
            self.scene.update(self, 1 / Game.FPS)

    def render(self, surface):
        self.scene.draw(surface)
        pygame.display.flip()
