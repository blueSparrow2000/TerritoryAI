import pygame
import numpy as np
from tile import * # this contains Tile
import time
pygame.init()

class TileMapDrawer:
    def __init__(self, mapName = 'blank 10 12', show_start_location = True):
        self.mapName = mapName

        # UNCHANGED: initialize tile board and display setting
        tileMapData = read_tile_map(self.mapName)
        self.col, self.row = len(tileMapData[0]), len(tileMapData)
        WIDTH, HEIGHT = self.col * SIZE, self.row * SIZE
        self.w = WIDTH
        self.h = HEIGHT

        # UNCHANGED: init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption("TerritoryWar")
        self.clock = pygame.time.Clock()
        # UNCHANGED: set tilemap
        self.tiles,num_occupiable_tiles = Tile.generate_tile_map(tileMapData)
        self.total_num_tiles = num_occupiable_tiles
        self.all_tile_sprites_list = pygame.sprite.RenderPlain()
        self.flat_tile_sprites = [j for sub in self.tiles for j in sub]
        self.all_tile_sprites_list.add(*self.flat_tile_sprites)

        # if circle, start_locations = ((self.col-8, self.row-8), (self.col-8, 6), (6, self.row-8 ))
        wall_dist = 1
        if mapName.startswith('circle'):
            _, radius = mapName.split(' ')
            radius = int(radius)
            wall_dist = radius//2 - 1
        start_locations = ((wall_dist,wall_dist), (self.col - (wall_dist+1), self.row - (wall_dist+1)), (self.col - (wall_dist+1), wall_dist), (wall_dist, self.row - (wall_dist+1)))

        if show_start_location:
            # mark start locations in yellow
            for i in range(len(start_locations)):
                bot_start_location = start_locations[i]
                x,y = bot_start_location[0], bot_start_location[1]
                self.tiles[y][x].setColor('yellow')

        # some text setting
        self.font = pygame.font.SysFont('arial', 20)


    def reset(self):
        for tile in self.flat_tile_sprites:
            tile.reset()

    def draw_map(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

        self.all_tile_sprites_list.update()
        self.display.fill(WHITE)
        self.all_tile_sprites_list.draw(self.display)

        pygame.display.flip()
        self.clock.tick(1)
        return False

if __name__ == '__main__':
    simulate = TileMapDrawer('box 20 20',True)
    while True:
        quit = simulate.draw_map()
        if quit:
            break
    pygame.quit()
