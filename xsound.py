from pygame import *


class SoundLibrary:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundLibrary, cls).__new__(cls)
            cls._instance.library = dict()
            cls._instance.ambient = None
            mixer.init()
        return cls._instance

    def __setitem__(self, key, value):
        self.library[key] = mixer.Sound(value)

    def __getitem__(self, item):
        return self.library[item]

    def __contains__(self, item):
        return item in self.library

    def set_ambient(self, filename, **kwargs):
        mixer.music.load(filename)

    def play_ambient(self, loops, start, fadein):
        mixer.music.play(loops, start, fadein)
