import pygame
KEYHOLD = pygame.USEREVENT + 1
class InputManager:
    ALL_HANDLERS = {
        pygame.ACTIVEEVENT: 'on_activeevent',
        pygame.APP_DIDENTERBACKGROUND: 'on_app_didenterbackground',
        pygame.APP_DIDENTERFOREGROUND: 'on_app_didenterforeground',
        pygame.APP_LOWMEMORY: 'on_app_lowmemory',
        pygame.APP_TERMINATING: 'on_app_terminating',
        pygame.APP_WILLENTERBACKGROUND: 'on_app_willenterbackground',
        pygame.APP_WILLENTERFOREGROUND: 'on_app_willenterforeground',
        pygame.AUDIODEVICEADDED: 'on_audiodeviceadded',
        pygame.AUDIODEVICEREMOVED: 'on_audiodeviceremoved',
        pygame.CLIPBOARDUPDATE: 'on_clipboardupdate',
        pygame.CONTROLLERDEVICEADDED: 'on_controllerdeviceadded',
        pygame.CONTROLLERDEVICEREMAPPED: 'on_controllerdeviceremapped',
        pygame.CONTROLLERDEVICEREMOVED: 'on_controllerdeviceremoved',
        pygame.DROPBEGIN: 'on_dropbegin',
        pygame.DROPCOMPLETE: 'on_dropcomplete',
        pygame.DROPFILE: 'on_dropfile',
        pygame.DROPTEXT: 'on_droptext',
        pygame.FINGERDOWN: 'on_fingerdown',
        pygame.FINGERMOTION: 'on_fingermotion',
        pygame.FINGERUP: 'on_fingerup',
        pygame.JOYAXISMOTION: 'on_joyaxismotion',
        pygame.JOYBALLMOTION: 'on_joyballmotion',
        pygame.JOYBUTTONDOWN: 'on_joybuttondown',
        pygame.JOYBUTTONUP: 'on_joybuttonup',
        pygame.JOYDEVICEADDED: 'on_joydeviceadded',
        pygame.JOYDEVICEREMOVED: 'on_joydeviceremoved',
        pygame.JOYHATMOTION: 'on_joyhatmotion',
        pygame.KEYDOWN: 'on_keydown',
        pygame.KEYMAPCHANGED: 'on_keymapchanged',
        pygame.KEYUP: 'on_keyup',
        pygame.LOCALECHANGED: 'on_localechanged',
        pygame.MIDIIN: 'on_midiin',
        pygame.MIDIOUT: 'on_midiout',
        pygame.MOUSEBUTTONDOWN: 'on_mousebuttondown',
        pygame.MOUSEBUTTONUP: 'on_mousebuttonup',
        pygame.MOUSEMOTION: 'on_mousemotion',
        pygame.MOUSEWHEEL: 'on_mousewheel',
        pygame.MULTIGESTURE: 'on_multigesture',
        pygame.QUIT: 'on_quit',
        pygame.RENDER_DEVICE_RESET: 'on_render_device_reset',
        pygame.RENDER_TARGETS_RESET: 'on_render_targets_reset',
        pygame.TEXTEDITING: 'on_textediting',
        pygame.TEXTINPUT: 'on_textinput',
        pygame.VIDEOEXPOSE: 'on_videoexpose',
        pygame.VIDEORESIZE: 'on_videoresize',
        pygame.WINDOWCLOSE: 'on_windowclose',
        pygame.WINDOWDISPLAYCHANGED: 'on_windowdisplaychanged',
        pygame.WINDOWENTER: 'on_windowenter',
        pygame.WINDOWEXPOSED: 'on_windowexposed',
        pygame.WINDOWFOCUSGAINED: 'on_windowfocusgained',
        pygame.WINDOWFOCUSLOST: 'on_windowfocuslost',
        pygame.WINDOWHIDDEN: 'on_windowhidden',
        pygame.WINDOWHITTEST: 'on_windowhittest',
        pygame.WINDOWICCPROFCHANGED: 'on_windowiccprofchanged',
        pygame.WINDOWLEAVE: 'on_windowleave',
        pygame.WINDOWMAXIMIZED: 'on_windowmaximized',
        pygame.WINDOWMINIMIZED: 'on_windowminimized',
        pygame.WINDOWMOVED: 'on_windowmoved',
        pygame.WINDOWRESIZED: 'on_windowresized',
        pygame.WINDOWRESTORED: 'on_windowrestored',
        pygame.WINDOWSHOWN: 'on_windowshown',
        pygame.WINDOWSIZECHANGED: 'on_windowsizechanged',
        pygame.WINDOWTAKEFOCUS: 'on_windowtakefocus',
#       CUSTOM EVENTS
        KEYHOLD: 'on_keyhold',
    }

    def __init__(self):
        self.handlers = dict()
        self.pressed_keys = set()
        self.__init_handlers__()

    def __init_handlers__(self):
        for type, h in InputManager.ALL_HANDLERS.items():
            if hasattr(self, h):
                self.handlers[type] = getattr(self, h)

    def handle_input_event(self, event, game):
        if event.type in self.handlers:
            self.handlers[event.type](event, game)

    def on_quit(self, event, game):
        game.running = False

    def on_keydown(self, event, game):
        self.pressed_keys.add(event.key)

    def on_keyup(self, event, game):
        self.pressed_keys.remove(event.key)

    def handle_pressed_keys(self, game):
        for key in self.pressed_keys:
            pygame.event.post(pygame.Event(KEYHOLD, key=key))


