import pygame
from player import Player
from ghost import Ghost, GHOST_TYPES
from map import GameMap
from ui import GameUI
from sound import SoundManager
import json
import os
import random
import math

class Particle:
    def __init__(self, x, y, color, dx, dy, life):
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
        self.life = life
        self.max_life = life
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
    def draw(self, screen, ox, oy):
        alpha = max(0, int(255 * self.life / self.max_life))
        surf = pygame.Surface((8,8), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.color + (alpha,), (4,4), 4)
        screen.blit(surf, (ox + int(self.x), oy + int(self.y)))

class ComboPopup:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.life = 36
        self.max_life = 36
    def update(self):
        self.y -= 1.2
        self.life -= 1
    def draw(self, screen, ox, oy):
        alpha = max(0, int(255 * self.life / self.max_life))
        font = pygame.font.SysFont('Arial', 32)
        surf = font.render(f'+{self.value}', True, (255,255,0))
        surf.set_alpha(alpha)
        screen.blit(surf, (ox + int(self.x), oy + int(self.y)))

class Game:
    def __init__(self, screen, difficulty='Normal', skin='Yellow'):
        self.screen = screen
        self.difficulty = difficulty
        self.skin = skin
        self.game_over = False
        self.sounds = SoundManager()
        self.ghost_speed = {'Easy': 30, 'Normal': 15, 'Hard': 8}[difficulty]
        self.leaderboard_file = 'scores.json'
        self.leaderboard = self.load_leaderboard()
        self.saved_score = False
        self.reset()

    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file) as f:
                return json.load(f)
        return []

    def save_leaderboard(self):
        with open(self.leaderboard_file, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)

    def add_score(self, score):
        entry = {
            'score': score,
            'difficulty': self.difficulty,
            'skin': self.skin
        }
        self.leaderboard.append(entry)
        self.leaderboard = sorted(self.leaderboard, key=lambda x: x['score'], reverse=True)[:10]
        self.save_leaderboard()

    def reset(self):
        self.map = GameMap()
        self.player = Player(self.map, skin=self.skin)
        # Spawn ghosts: Blinky, Pinky, Inky, Clyde
        self.ghosts = []
        blinky = Ghost(self.map, GHOST_TYPES[0][1], speed=self.ghost_speed, ghost_type='blinky')
        self.ghosts.append(blinky)
        self.ghosts.append(Ghost(self.map, GHOST_TYPES[1][1], speed=self.ghost_speed, ghost_type='pinky'))
        self.ghosts.append(Ghost(self.map, GHOST_TYPES[2][1], speed=self.ghost_speed, ghost_type='inky', blinky_ref=blinky))
        self.ghosts.append(Ghost(self.map, GHOST_TYPES[3][1], speed=self.ghost_speed, ghost_type='clyde'))
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.ui = GameUI(self.screen)
        self.sounds.play_music('music.ogg')
        self.saved_score = False
        self.particles = []
        self.shake = 0
        self.combo_timer = 0
        self.combo_count = 0
        self.combo_popups = []
        self.start_timer = 120  # 2 seconds of READY!
        # Power-up abundance by difficulty
        if self.difficulty == 'Easy':
            for _ in range(2):
                self.player.teleport_uses += 1
        elif self.difficulty == 'Hard':
            self.player.teleport_uses = 0

    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self):
        if hasattr(self, 'start_timer') and self.start_timer > 0:
            self.start_timer -= 1
            return
        if self.lives <= 0:
            self.game_over = True
            self.sounds.stop_music()
            if not self.saved_score:
                self.add_score(self.score)
                self.saved_score = True
            return
        self.player.update()
        for ghost in self.ghosts:
            ghost.update(self.player)
        if self.map.eat_dot(self.player.x, self.player.y):
            self.score += 10
            self.sounds.play_sfx('dot.wav')
            self.spawn_particles(self.player.fx, self.player.fy, (0,255,255))
            # Combo logic
            if self.combo_timer > 0:
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.combo_timer = 30
            if self.combo_count > 1:
                self.combo_popups.append(ComboPopup(self.player.fx*self.map.cell_size, self.player.fy*self.map.cell_size, self.combo_count*10))
                self.score += (self.combo_count-1)*10
        # Power-up collection
        kind = self.map.eat_powerup(self.player.x, self.player.y)
        if kind:
            self.player.apply_powerup(kind)
            self.sounds.play_sfx('powerup.wav')
            self.spawn_particles(self.player.fx, self.player.fy, (255,0,255))
        if self.map.dots_left() == 0:
            self.game_over = True
            self.sounds.stop_music()
            if not self.saved_score:
                self.add_score(self.score)
                self.saved_score = True
        for ghost in self.ghosts:
            if ghost.x == self.player.x and ghost.y == self.player.y:
                if ghost.eaten:
                    continue
                if self.player.is_invincible() and ghost.mode == 'frightened':
                    ghost.eaten = True
                    ghost.mode = 'eyes'
                    continue
                if not self.player.is_invincible() and not ghost.eaten and ghost.mode != 'frightened':
                    self.lives -= 1
                    self.sounds.play_sfx('death.wav')
                    self.player.respawn()
                    self.spawn_particles(self.player.fx, self.player.fy, (255,0,0))
                    self.shake = 16
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()
        if self.shake > 0:
            self.shake -= 1
        # Update combo timer/popups
        if self.combo_timer > 0:
            self.combo_timer -= 1
        self.combo_popups = [c for c in self.combo_popups if c.life > 0]
        for c in self.combo_popups:
            c.update()

    def draw(self):
        self.screen.fill((20, 20, 40))
        map_w = len(self.map.grid[0]) * self.map.cell_size
        map_h = len(self.map.grid) * self.map.cell_size
        offset_x = (self.screen.get_width() - map_w) // 2
        offset_y = (self.screen.get_height() - map_h) // 2
        map_rect = pygame.Rect(offset_x, offset_y, map_w, map_h)
        # Screen shake
        sx = sy = 0
        if hasattr(self, 'shake') and self.shake > 0:
            sx = random.randint(-6,6)
            sy = random.randint(-6,6)
        self.map.draw(self.screen, (offset_x+sx, offset_y+sy))
        self.player.draw(self.screen, (offset_x+sx, offset_y+sy))
        for ghost in self.ghosts:
            ghost.draw(self.screen, (offset_x+sx, offset_y+sy), self.player)
        for p in self.particles:
            p.draw(self.screen, offset_x+sx, offset_y+sy)
        for c in self.combo_popups:
            c.draw(self.screen, offset_x+sx, offset_y+sy)
        # UI bar (arcade style)
        high_score = max(self.score, max([e['score'] for e in self.leaderboard], default=0))
        self.ui.draw(self.score, high_score, self.lives, map_rect)
        # READY/GAME OVER in center
        if hasattr(self, 'start_timer') and self.start_timer > 0:
            self.ui.draw_ready(map_rect)
        if self.game_over:
            self.ui.draw_game_over(map_rect)
        if self.game_over:
            self.draw_leaderboard()

    def draw_leaderboard(self):
        font = pygame.font.SysFont('Arial', 32)
        title = font.render('LEADERBOARD (Top 10)', True, (255,255,0))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 80))
        for i, entry in enumerate(self.leaderboard):
            s = f"{i+1}. {entry['score']}  ({entry['difficulty']}, {entry['skin']})"
            surf = font.render(s, True, (255,255,255))
            self.screen.blit(surf, (self.screen.get_width()//2 - surf.get_width()//2, 120 + i*36))

    def spawn_particles(self, fx, fy, color):
        cell = self.map.cell_size
        for _ in range(12):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            self.particles.append(Particle(fx*cell, fy*cell, color, dx, dy, 18)) 