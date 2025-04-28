import pygame
import os
import math

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.start_game = False
        font_path = 'assets/fonts/PressStart2P.ttf'
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, 64)
            self.small_font = pygame.font.Font(font_path, 32)
        else:
            self.font = pygame.font.SysFont('Arial', 64)
            self.small_font = pygame.font.SysFont('Arial', 32)
        self.difficulties = ['Easy', 'Normal', 'Hard']
        self.skins = ['Yellow', 'Green', 'Pink']
        self.diff_idx = 1
        self.skin_idx = 0
        self.frame = 0
        self.reset()

    def reset(self):
        self.start_game = False
        self.diff_idx = 1
        self.skin_idx = 0
        self.frame = 0

    @property
    def selected_difficulty(self):
        return self.difficulties[self.diff_idx]

    @property
    def selected_skin(self):
        return self.skins[self.skin_idx]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.start_game = True
            elif event.key == pygame.K_LEFT:
                self.diff_idx = (self.diff_idx - 1) % len(self.difficulties)
            elif event.key == pygame.K_RIGHT:
                self.diff_idx = (self.diff_idx + 1) % len(self.difficulties)
            elif event.key == pygame.K_UP:
                self.skin_idx = (self.skin_idx - 1) % len(self.skins)
            elif event.key == pygame.K_DOWN:
                self.skin_idx = (self.skin_idx + 1) % len(self.skins)

    def update(self):
        self.frame += 1

    def draw(self):
        self.screen.fill((10, 10, 30))
        w, h = self.screen.get_size()
        t_slide = min(1, self.frame/30)
        o_slide = min(1, max(0, (self.frame-10)/30))
        # Title slides in from top
        title = self.font.render('PAXMAN', True, (0, 255, 255))
        title_y = int(40 + (80-40)*(1-t_slide))
        self.screen.blit(title, (w//2 - title.get_width()//2, title_y))
        # Prompt slides in
        prompt = self.small_font.render('Press ENTER to Start', True, (255, 255, 255))
        prompt_y = int(160 + (220-160)*(1-o_slide))
        self.screen.blit(prompt, (w//2 - prompt.get_width()//2, prompt_y))
        # Difficulty
        diff_y = int(260 + (320-260)*(1-o_slide))
        for i, d in enumerate(self.difficulties):
            color = (255,255,0) if i == self.diff_idx else (120,120,60)
            pulse = 1.0 + 0.08*math.sin(self.frame/8) if i == self.diff_idx else 1.0
            surf = self.small_font.render(f'Difficulty: {d}' if i == self.diff_idx else d, True, color)
            surf = pygame.transform.rotozoom(surf, 0, pulse)
            x = w//2 - surf.get_width()//2
            y = diff_y + i*44
            self.screen.blit(surf, (x, y))
            if i == self.diff_idx:
                # Neon border
                border = pygame.Surface((surf.get_width()+16, surf.get_height()+10), pygame.SRCALPHA)
                pygame.draw.rect(border, (0,255,255,120), border.get_rect(), border_radius=12, width=4)
                self.screen.blit(border, (x-8, y-5))
        # Skin
        skin_y = int(400 + (370-400)*(o_slide))
        for i, s in enumerate(self.skins):
            color = (255,128,255) if i == self.skin_idx else (120,60,120)
            pulse = 1.0 + 0.08*math.sin(self.frame/8+2) if i == self.skin_idx else 1.0
            surf = self.small_font.render(f'Skin: {s}' if i == self.skin_idx else s, True, color)
            surf = pygame.transform.rotozoom(surf, 0, pulse)
            x = w//2 - surf.get_width()//2
            y = skin_y + i*44
            self.screen.blit(surf, (x, y))
            if i == self.skin_idx:
                border = pygame.Surface((surf.get_width()+16, surf.get_height()+10), pygame.SRCALPHA)
                pygame.draw.rect(border, (255,0,255,120), border.get_rect(), border_radius=12, width=4)
                self.screen.blit(border, (x-8, y-5))
        # Help
        help1 = self.small_font.render('LEFT/RIGHT: Difficulty', True, (180,180,180))
        help2 = self.small_font.render('UP/DOWN: Skin', True, (180,180,180))
        self.screen.blit(help1, (w//2 - help1.get_width()//2, h-80))
        self.screen.blit(help2, (w//2 - help2.get_width()//2, h-50)) 