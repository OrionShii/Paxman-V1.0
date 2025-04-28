import pygame
import sys
import os
import math
from game import Game
from menu import MainMenu

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Paxman')
clock = pygame.time.Clock()

state = 'menu'
menu = MainMenu(screen)
game = None
paused = False
fade_alpha = 0
fade_dir = 0  # 0: no fade, 1: fade out, -1: fade in
next_state = None
frame = 0

FADE_SPEED = 20


def start_fade(to_state):
    global fade_alpha, fade_dir, next_state
    fade_alpha = 0
    fade_dir = 1
    next_state = to_state

def draw_fade(screen, alpha):
    fade = pygame.Surface((screen.get_width(), screen.get_height()))
    fade.fill((0,0,0))
    fade.set_alpha(alpha)
    screen.blit(fade, (0,0))

def get_font(size):
    font_path = 'assets/fonts/PressStart2P.ttf'
    if os.path.exists(font_path):
        return pygame.font.Font(font_path, size)
    return pygame.font.SysFont('Arial', size)

def draw_pause(screen, frame):
    w, h = screen.get_size()
    # Fade overlay
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((10,10,30,180))
    screen.blit(overlay, (0,0))
    # Pulsing neon text
    font = get_font(64)
    pulse = 1.0 + 0.08*math.sin(frame/8)
    surf = font.render('PAUSED', True, (0,255,255))
    surf = pygame.transform.rotozoom(surf, 0, pulse)
    x = w//2 - surf.get_width()//2
    y = h//2 - 80
    screen.blit(surf, (x, y))
    # Neon border
    border = pygame.Surface((surf.get_width()+24, surf.get_height()+16), pygame.SRCALPHA)
    pygame.draw.rect(border, (0,255,255,120), border.get_rect(), border_radius=18, width=6)
    screen.blit(border, (x-12, y-8))
    # Help
    small = get_font(28).render('Press ESC to Resume', True, (255,255,255))
    screen.blit(small, (w//2 - small.get_width()//2, h//2 + 20))

def draw_game_over(screen, frame):
    w, h = screen.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((30,0,0,180))
    screen.blit(overlay, (0,0))
    font = get_font(64)
    pulse = 1.0 + 0.08*math.sin(frame/8)
    surf = font.render('GAME OVER', True, (255,0,128))
    surf = pygame.transform.rotozoom(surf, 0, pulse)
    x = w//2 - surf.get_width()//2
    y = h//2 - 80
    screen.blit(surf, (x, y))
    border = pygame.Surface((surf.get_width()+24, surf.get_height()+16), pygame.SRCALPHA)
    pygame.draw.rect(border, (255,0,255,120), border.get_rect(), border_radius=18, width=6)
    screen.blit(border, (x-12, y-8))
    small = get_font(28).render('Press ENTER for Menu', True, (255,255,255))
    screen.blit(small, (w//2 - small.get_width()//2, h//2 + 20))

while True:
    frame += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if state == 'game' and game:
                game.map.set_cell_size(event.w, event.h)
        if fade_dir == 0:
            if state == 'menu':
                menu.handle_event(event)
            elif state == 'game':
                if not paused and not game.game_over:
                    game.handle_event(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not paused and not game.game_over:
                            paused = True
                        elif paused:
                            paused = False
                    if game.game_over and event.key == pygame.K_RETURN:
                        start_fade('menu')
    if fade_dir == 0:
        if state == 'menu':
            menu.update()
            menu.draw()
            if game:
                game.draw(show_leaderboard=True)
            if menu.start_game:
                start_fade('game')
        elif state == 'game':
            if not paused and not game.game_over:
                game.update()
            game.draw()
            if paused:
                draw_pause(screen, frame)
            if game.game_over:
                draw_game_over(screen, frame)
    else:
        if fade_dir == 1:
            fade_alpha += FADE_SPEED
            if fade_alpha >= 255:
                fade_alpha = 255
                fade_dir = -1
                if next_state == 'game':
                    paused = False
                    game = Game(screen, menu.selected_difficulty, menu.selected_skin)
                    game.map.set_cell_size(screen.get_width(), screen.get_height())
                    game.reset()
                    state = 'game'
                elif next_state == 'menu':
                    state = 'menu'
                    menu.reset()
        elif fade_dir == -1:
            fade_alpha -= FADE_SPEED
            if fade_alpha <= 0:
                fade_alpha = 0
                fade_dir = 0
        if state == 'menu':
            menu.update()
            menu.draw()
            if game:
                game.draw(show_leaderboard=True)
        elif state == 'game':
            if not paused and not game.game_over:
                game.update()
            game.draw()
            if paused:
                draw_pause(screen, frame)
            if game.game_over:
                draw_game_over(screen, frame)
        draw_fade(screen, fade_alpha)
    pygame.display.flip()
    clock.tick(60) 