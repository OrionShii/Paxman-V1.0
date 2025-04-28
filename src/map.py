import pygame
import json
import os
from sprites import SpriteLoader

class GameMap:
    def __init__(self, level_path='levels/level1.json'):
        with open(level_path) as f:
            self.data = json.load(f)
        self.grid = self.data['grid']
        self.cell_size = 32
        self._init_dots()
        self._init_powerups()
        self.sprites = SpriteLoader()
        self._load_sprites()

    def _load_sprites(self):
        self.wall_sprite = self.sprites.load('wall.png', (self.cell_size, self.cell_size))
        self.dot_sprite = self.sprites.load('dot.png', (self.cell_size//2, self.cell_size//2))
        self.powerup_sprites = {
            'T': self.sprites.load('powerup_teleport.png', (self.cell_size, self.cell_size)),
            'S': self.sprites.load('powerup_speed.png', (self.cell_size, self.cell_size)),
            'I': self.sprites.load('powerup_invincible.png', (self.cell_size, self.cell_size)),
        }

    def set_cell_size(self, w, h):
        rows = len(self.grid)
        cols = len(self.grid[0])
        self.cell_size = min(w // cols, h // rows)
        self._load_sprites()

    def _init_dots(self):
        self.dots = set()
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == '.':
                    self.dots.add((x, y))

    def _init_powerups(self):
        self.powerups = {}
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell in 'TSI':
                    self.powerups[(x, y)] = cell

    def is_walkable(self, x, y):
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            return self.grid[y][x] != '#'
        return False

    def eat_dot(self, x, y):
        if (x, y) in self.dots:
            self.dots.remove((x, y))
            return True
        return False

    def eat_powerup(self, x, y):
        if (x, y) in self.powerups:
            kind = self.powerups.pop((x, y))
            return kind
        return None

    def dots_left(self):
        return len(self.dots)

    def player_start(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 'P':
                    return x, y
        return 1, 1

    def ghost_start(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cell == 'G':
                    return x, y
        return 5, 5

    def draw(self, screen, offset=(0,0)):
        ox, oy = offset
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(ox + x*self.cell_size, oy + y*self.cell_size, self.cell_size, self.cell_size)
                if cell == '#':
                    if self.wall_sprite:
                        screen.blit(self.wall_sprite, (ox + x*self.cell_size, oy + y*self.cell_size))
                    else:
                        pygame.draw.rect(screen, (0, 255, 255), rect)
                elif (x, y) in self.dots:
                    if self.dot_sprite:
                        screen.blit(self.dot_sprite, (ox + x*self.cell_size + self.cell_size//4, oy + y*self.cell_size + self.cell_size//4))
                    else:
                        pygame.draw.circle(screen, (255,255,255), rect.center, 4)
                elif (x, y) in self.powerups:
                    kind = self.powerups[(x, y)]
                    sprite = self.powerup_sprites.get(kind)
                    if sprite:
                        screen.blit(sprite, (ox + x*self.cell_size, oy + y*self.cell_size))
                    else:
                        color = {'T': (0,255,255), 'S': (255,0,255), 'I': (255,255,0)}[kind]
                        pygame.draw.circle(screen, color, rect.center, self.cell_size//3) 