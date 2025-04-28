import pygame
import math
from sprites import SpriteLoader

class Player:
    def __init__(self, game_map, skin='Yellow'):
        self.map = game_map
        self.x, self.y = self.map.player_start()
        self.fx, self.fy = float(self.x), float(self.y)
        self.dir = (0, 0)
        self.next_dir = (0, 0)
        self.sprites = SpriteLoader()
        skin_map = {
            'Yellow': 'pacman_yellow.png',
            'Green': 'pacman_green.png',
            'Pink': 'pacman_pink.png',
        }
        sprite_name = skin_map.get(skin, 'pacman_yellow.png')
        self.sprite = self.sprites.load(sprite_name, (self.map.cell_size, self.map.cell_size))
        self.teleport_uses = 0
        self.speed_timer = 0
        self.invincible_timer = 0
        self.anim_frame = 0
        self.speed = 0.18  # tiles per frame

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.next_dir = (0, -1)
            elif event.key == pygame.K_DOWN:
                self.next_dir = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.next_dir = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.next_dir = (1, 0)
            elif event.key == pygame.K_SPACE and self.teleport_uses > 0:
                # Teleport to opposite side
                self.x = len(self.map.grid[0]) - 1 - self.x
                self.fx = float(self.x)
                self.teleport_uses -= 1

    def update(self):
        if self.speed_timer > 0:
            self.speed_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        moves = 2 if self.is_speed_boosted() else 1
        for _ in range(moves):
            # Try to turn if possible
            nx, ny = self.x + self.next_dir[0], self.y + self.next_dir[1]
            if self.map.is_walkable(nx, ny):
                self.dir = self.next_dir
            # Move smoothly toward next tile
            tx, ty = self.x + self.dir[0], self.y + self.dir[1]
            if self.map.is_walkable(tx, ty):
                dx = tx - self.fx
                dy = ty - self.fy
                dist = math.hypot(dx, dy)
                step = self.speed * (1.5 if self.is_speed_boosted() else 1)
                if dist > 0.01:
                    self.fx += dx/dist * min(step, dist)
                    self.fy += dy/dist * min(step, dist)
                if abs(self.fx - tx) < 0.05 and abs(self.fy - ty) < 0.05:
                    self.x, self.y = tx, ty
                    self.fx, self.fy = float(self.x), float(self.y)
            self.anim_frame += 1

    def draw(self, screen, offset=(0,0)):
        ox, oy = offset
        cell = self.map.cell_size
        px = ox + int(self.fx*cell)
        py = oy + int(self.fy*cell)
        if self.sprite:
            screen.blit(self.sprite, (px, py))
        else:
            # Animated mouth
            angle = 30 + 20*math.sin(self.anim_frame/3)
            direction = self.dir
            if direction == (0, -1):  # up
                rot = 90
            elif direction == (0, 1):  # down
                rot = 270
            elif direction == (-1, 0):  # left
                rot = 180
            else:  # right or idle
                rot = 0
            pygame.draw.arc(screen, (255,255,0), (px, py, cell, cell),
                math.radians(angle+rot), math.radians(360-angle+rot), cell//2)
            pygame.draw.circle(screen, (255,255,0), (px+cell//2, py+cell//2), cell//2-2)

    def respawn(self):
        self.x, self.y = self.map.player_start()
        self.fx, self.fy = float(self.x), float(self.y)
        self.dir = (0, 0)
        self.next_dir = (0, 0)

    def apply_powerup(self, kind):
        if kind == 'T':
            self.teleport_uses += 1
        elif kind == 'S':
            self.speed_timer = 180  # 3 seconds at 60 FPS
        elif kind == 'I':
            self.invincible_timer = 180

    def is_invincible(self):
        return self.invincible_timer > 0

    def is_speed_boosted(self):
        return self.speed_timer > 0 