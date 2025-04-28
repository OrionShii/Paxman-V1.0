import pygame
import os

class GameUI:
    def __init__(self, screen):
        self.screen = screen
        font_path = 'assets/fonts/PressStart2P.ttf'
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 28)
            self.big_font = pygame.font.Font(font_path, 48)
        else:
            self.font = pygame.font.SysFont('Arial', 32)
            self.big_font = pygame.font.SysFont('Arial', 48)
        self.icon_life = self.load_icon('icon_life.png')

    def load_icon(self, name):
        path = os.path.join('assets/sprites', name)
        if os.path.exists(path):
            return pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (32, 32))
        return None

    def draw(self, score, high_score, lives, map_rect):
        w = self.screen.get_width()
        # Top UI bar
        label_score = self.font.render('SCORE', True, (255,255,255))
        label_high = self.font.render('HIGH SCORE', True, (255,0,0))
        score_surf = self.font.render(f'{score:05d}', True, (255,255,0))
        high_surf = self.font.render(f'{high_score:05d}', True, (255,255,0))
        # Draw labels
        y = map_rect.top - 60
        self.screen.blit(label_score, (map_rect.left, y))
        self.screen.blit(label_high, (map_rect.centerx - label_high.get_width()//2, y))
        self.screen.blit(label_score, (map_rect.right - label_score.get_width(), y))
        # Draw scores
        y2 = y + 32
        self.screen.blit(score_surf, (map_rect.left, y2))
        self.screen.blit(high_surf, (map_rect.centerx - high_surf.get_width()//2, y2))
        self.screen.blit(score_surf, (map_rect.right - score_surf.get_width(), y2))
        # Draw lives (Pac-Man icons) below map
        if self.icon_life:
            for i in range(lives):
                self.screen.blit(self.icon_life, (map_rect.left + i*36, map_rect.bottom + 12))
        else:
            lives_surf = self.font.render(f'Lives: {lives}', True, (255,255,0))
            self.screen.blit(lives_surf, (map_rect.left, map_rect.bottom + 12))

    def draw_ready(self, map_rect):
        surf = self.big_font.render('READY!', True, (255,255,0))
        self.screen.blit(surf, (map_rect.centerx - surf.get_width()//2, map_rect.centery - surf.get_height()//2))

    def draw_game_over(self, map_rect):
        surf = self.big_font.render('GAME OVER', True, (255,0,0))
        self.screen.blit(surf, (map_rect.centerx - surf.get_width()//2, map_rect.centery - surf.get_height()//2)) 