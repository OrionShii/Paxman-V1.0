import pygame
import os

class SoundManager:
    def __init__(self, sfx_path='assets/sounds', music_path='assets/music'):
        self.sfx_path = sfx_path
        self.music_path = music_path
        self.sfx_cache = {}
        pygame.mixer.init()

    def play_sfx(self, name):
        if name not in self.sfx_cache:
            path = os.path.join(self.sfx_path, name)
            if not os.path.exists(path):
                self.sfx_cache[name] = None
                return
            self.sfx_cache[name] = pygame.mixer.Sound(path)
        sfx = self.sfx_cache[name]
        if sfx:
            sfx.play()

    def play_music(self, name, loop=True):
        path = os.path.join(self.music_path, name)
        if not os.path.exists(path):
            return
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self):
        pygame.mixer.music.stop() 