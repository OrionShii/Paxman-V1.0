import pygame
import random
import math
from sprites import SpriteLoader
from collections import deque

GHOST_TYPES = [
    ('blinky', (255,0,0)),
    ('pinky', (255,128,255)),
    ('inky', (0,255,255)),
    ('clyde', (255,128,0)),
]

SCATTER_TARGETS = {
    'blinky': lambda grid: (len(grid[0])-2, 1),
    'pinky': lambda grid: (1, 1),
    'inky': lambda grid: (len(grid[0])-2, len(grid)-2),
    'clyde': lambda grid: (1, len(grid)-2),
}

class Ghost:
    def __init__(self, game_map, color, speed=15, ghost_type=None, blinky_ref=None):
        self.map = game_map
        self.x, self.y = self.map.ghost_start()
        self.fx, self.fy = float(self.x), float(self.y)
        self.color = color
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.sprites = SpriteLoader()
        self.ghost_type = ghost_type or self._type_from_color(color)
        self.blinky_ref = blinky_ref
        sprite_map = {
            'blinky': 'ghost_red.png',
            'pinky': 'ghost_pink.png',
            'inky': 'ghost_blue.png',
            'clyde': 'ghost_orange.png',
        }
        self.sprite = self.sprites.load(sprite_map.get(self.ghost_type, 'ghost_red.png'), (self.map.cell_size, self.map.cell_size))
        self.speed = speed
        self.frame = 0
        self.anim_frame = 0
        self.move_speed = 0.14
        self.mode = 'scatter'  # scatter, chase, frightened
        self.mode_timer = 420  # 7s at 60fps
        self.frightened_timer = 0
        self.scatter_target = SCATTER_TARGETS[self.ghost_type](self.map.grid)
        self.eaten = False
        self.home = self.map.ghost_start()

    def _type_from_color(self, color):
        if color == (255,0,0): return 'blinky'
        if color == (255,128,255): return 'pinky'
        if color == (0,255,255): return 'inky'
        if color == (255,128,0): return 'clyde'
        return 'blinky'

    def update(self, player):
        self.frame = (self.frame + 1) % self.speed
        if self.frame != 0:
            return
        # Eyes mode: go home
        if self.eaten:
            self.move_towards(self.home)
            if (self.x, self.y) == self.home:
                self.eaten = False
                self.mode = 'scatter'
                self.mode_timer = 420
            # No other logic while eyes
            dx = self.x - self.fx
            dy = self.y - self.fy
            dist = math.hypot(dx, dy)
            if dist > 0.01:
                self.fx += dx/dist * min(self.move_speed, dist)
                self.fy += dy/dist * min(self.move_speed, dist)
            else:
                self.fx, self.fy = float(self.x), float(self.y)
            self.anim_frame += 1
            return
        # Mode switching
        if self.mode == 'frightened':
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = 'scatter'
                self.mode_timer = 420
        else:
            self.mode_timer -= 1
            if self.mode_timer <= 0:
                if self.mode == 'scatter':
                    self.mode = 'chase'
                    self.mode_timer = 1740  # 29s
                else:
                    self.mode = 'scatter'
                    self.mode_timer = 420
        # Frightened mode trigger
        if player.is_invincible() and self.mode != 'frightened':
            self.mode = 'frightened'
            self.frightened_timer = 240
        # AI
        if self.mode == 'frightened':
            # Random move, blue/white
            dirs = [(1,0),(-1,0),(0,1),(0,-1)]
            random.shuffle(dirs)
            for d in dirs:
                nx, ny = self.x + d[0], self.y + d[1]
                if self.map.is_walkable(nx, ny):
                    self.x, self.y = nx, ny
                    break
        elif self.mode == 'scatter':
            self.move_towards(self.scatter_target)
        elif self.mode == 'chase':
            if self.ghost_type == 'blinky':
                target = (player.x, player.y)
            elif self.ghost_type == 'pinky':
                tx = player.x + player.dir[0]*4
                ty = player.y + player.dir[1]*4
                target = (max(0,min(tx,len(self.map.grid[0])-1)), max(0,min(ty,len(self.map.grid)-1)))
            elif self.ghost_type == 'inky' and self.blinky_ref:
                px, py = player.x + player.dir[0]*2, player.y + player.dir[1]*2
                bx, by = self.blinky_ref.x, self.blinky_ref.y
                vx, vy = px-bx, py-by
                tx, ty = bx + 2*vx, by + 2*vy
                target = (max(0,min(tx,len(self.map.grid[0])-1)), max(0,min(ty,len(self.map.grid)-1)))
            elif self.ghost_type == 'clyde':
                dist = (self.x-player.x)**2 + (self.y-player.y)**2
                if dist > 64:
                    target = (player.x, player.y)
                else:
                    target = self.scatter_target
            else:
                target = (player.x, player.y)
            self.move_towards(target)
        # Smooth movement toward (self.x, self.y)
        dx = self.x - self.fx
        dy = self.y - self.fy
        dist = math.hypot(dx, dy)
        if dist > 0.01:
            self.fx += dx/dist * min(self.move_speed, dist)
            self.fy += dy/dist * min(self.move_speed, dist)
        else:
            self.fx, self.fy = float(self.x), float(self.y)
        self.anim_frame += 1

    def move_towards(self, target):
        queue = deque()
        visited = set()
        queue.append(((self.x, self.y), []))
        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) == target and path:
                move = path[0]
                self.x, self.y = move
                return
            for d in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = cx + d[0], cy + d[1]
                if self.map.is_walkable(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path+[(nx, ny)]))
        # fallback: random
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(dirs)
        for d in dirs:
            nx, ny = self.x + d[0], self.y + d[1]
            if self.map.is_walkable(nx, ny):
                self.x, self.y = nx, ny
                return

    def draw(self, screen, offset=(0,0), player=None):
        ox, oy = offset
        cell = self.map.cell_size
        px = ox + int(self.fx*cell)
        py = oy + int(self.fy*cell)
        wobble = int(4*math.sin(self.anim_frame/6))
        if self.eaten:
            # Draw eyes: white with blue pupils
            pygame.draw.circle(screen, (255,255,255), (px+cell//2, py+cell//2 + wobble), cell//2-2)
            pygame.draw.circle(screen, (0,128,255), (px+cell//2-6, py+cell//2 + wobble), 4)
            pygame.draw.circle(screen, (0,128,255), (px+cell//2+6, py+cell//2 + wobble), 4)
        elif self.mode == 'frightened':
            color = (0,128,255) if (self.anim_frame//6)%2==0 else (255,255,255)
            pygame.draw.circle(screen, color, (px+cell//2, py+cell//2 + wobble), cell//2-2)
        elif self.sprite:
            screen.blit(self.sprite, (px, py + wobble))
        else:
            pygame.draw.circle(screen, self.color, (px+cell//2, py+cell//2 + wobble), cell//2-2) 