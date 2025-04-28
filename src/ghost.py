import pygame
import random
import math
from sprites import SpriteLoader
from collections import deque

class Ghost:
    def __init__(self, game_map, color, speed=15):
        self.map = game_map
        self.x, self.y = self.map.ghost_start()
        self.fx, self.fy = float(self.x), float(self.y)
        self.color = color
        self.dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        self.sprites = SpriteLoader()
        color_map = {
            (255,0,0): ('ghost_red.png', 'chaser'),
            (0,255,0): ('ghost_green.png', 'patrol'),
            (0,0,255): ('ghost_blue.png', 'ambusher'),
            (255,128,0): ('ghost_orange.png', 'random'),
        }
        sprite_name, self.ai_type = color_map.get(color, ('ghost_red.png', 'chaser'))
        self.sprite = self.sprites.load(sprite_name, (self.map.cell_size, self.map.cell_size))
        self.patrol_points = [(1,1), (1,len(self.map.grid)-2), (len(self.map.grid[0])-2,1), (len(self.map.grid[0])-2,len(self.map.grid)-2)]
        self.patrol_idx = 0
        self.speed = speed
        self.frame = 0
        self.anim_frame = 0
        self.move_speed = 0.14  # tiles per frame

    def update(self, player):
        self.frame = (self.frame + 1) % self.speed
        if self.frame != 0:
            return
        frightened = player.is_invincible()
        if frightened:
            # Run away from Pac-Man
            px, py = player.x, player.y
            best = None
            max_dist = -1
            for d in [(1,0),(-1,0),(0,1),(0,-1)]:
                nx, ny = self.x + d[0], self.y + d[1]
                if self.map.is_walkable(nx, ny):
                    dist = (nx-px)**2 + (ny-py)**2
                    if dist > max_dist:
                        max_dist = dist
                        best = (nx, ny)
            if best:
                self.x, self.y = best
        else:
            if self.ai_type == 'chaser':
                target = (player.x, player.y)
                self.move_towards(target)
            elif self.ai_type == 'ambusher':
                tx = player.x + player.dir[0]*3
                ty = player.y + player.dir[1]*3
                target = (max(0,min(tx,len(self.map.grid[0])-1)), max(0,min(ty,len(self.map.grid)-1)))
                self.move_towards(target)
            elif self.ai_type == 'patrol':
                target = self.patrol_points[self.patrol_idx]
                if (self.x, self.y) == target:
                    self.patrol_idx = (self.patrol_idx + 1) % len(self.patrol_points)
                    target = self.patrol_points[self.patrol_idx]
                self.move_towards(target)
            else:  # random
                dirs = [(1,0),(-1,0),(0,1),(0,-1)]
                random.shuffle(dirs)
                for d in dirs:
                    nx, ny = self.x + d[0], self.y + d[1]
                    if self.map.is_walkable(nx, ny):
                        self.dir = d
                        break
                tx, ty = self.x + self.dir[0], self.y + self.dir[1]
                if self.map.is_walkable(tx, ty):
                    self.x, self.y = tx, ty
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
        # BFS for shortest path
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
        # Wobble animation
        wobble = int(4*math.sin(self.anim_frame/6))
        frightened = player.is_invincible() if player else False
        if frightened:
            # Flash blue/white
            color = (0,128,255) if (self.anim_frame//6)%2==0 else (255,255,255)
            pygame.draw.circle(screen, color, (px+cell//2, py+cell//2 + wobble), cell//2-2)
        elif self.sprite:
            screen.blit(self.sprite, (px, py + wobble))
        else:
            pygame.draw.circle(screen, self.color, (px+cell//2, py+cell//2 + wobble), cell//2-2) 