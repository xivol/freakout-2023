import pygame


class FontLibrary:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontLibrary, cls).__new__(cls)
            cls._instance.library = dict()
        return cls._instance

    def __setitem__(self, key, value):
        self.library[key] = pygame.font.FontType(*value)

    def __getitem__(self, item):
        return self.library[item]

    def __contains__(self, item):
        return item in self.library
