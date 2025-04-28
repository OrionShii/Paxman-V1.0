import pygame
import os

class SpriteLoader:
    def __init__(self, base_path='assets/sprites'):
        self.base_path = base_path
        self.cache = {}

    def load(self, name, size=None):
        key = (name, size)
        if key in self.cache:
            return self.cache[key]
        path = os.path.join(self.base_path, name)
        if not os.path.exists(path):
            self.cache[key] = None
            return None
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        self.cache[key] = img
        return img 