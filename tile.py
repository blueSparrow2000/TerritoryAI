'''
Tile class
color means occupied to some agent or a team

*** IMPORTANT ***
'white' tiles are considered unoccupied tiles!
we cannot use them

ATTRIBUTES
Color: Unique Identifier - determines which agent owns this tile
x,y: Position - only agent's position may change
highlight: For debugging purpose, blink (in red) one frame


* 한 이미지를 복사해서 붙여넣기 하니까.. 그 이미지의 투명도를 조정하면 전부 다 조정되네... 허허... 특정 타일 부분이 아니라..
그러면 각 픽셀마다 가림막 만들어놔야하나?
'''
from variables import *
from tileDataIO import *
from container import *
from collections import deque

class Tile(pygame.sprite.Sprite):
    # get image of tiles
    available_colors = read_all_file_names('images/tiles')
    tile_image_dict = {}
    # save only the first letter of available colors (this is a table for converting one letter text map)
    available_color_initials = {s[0]: s for s in available_colors}
    # WALL INITIAL IS +
    available_color_initials['+'] = 'wall'
    tile_image_initialized = False

    # get image of tile heads
    head_available_colors = read_all_file_names('images/tile_heads')
    head_tile_image_dict = {}
    # save only the first letter of available colors (this is a table for converting one letter text map)
    head_available_color_initials = {s[0]: s for s in head_available_colors}

    highlight_image = None

    def __init__(self,x,y,color = None):
        super().__init__()
        # initialize images once in a run tile
        if not Tile.tile_image_initialized:
            Tile.tile_image_initialized = True
            for img_color in Tile.available_colors:
                Tile.tile_image_dict[img_color] = Image(img_color, folder="/images/tiles/", size=[SIZE, SIZE])
            for img_color in Tile.head_available_colors:
                Tile.head_tile_image_dict[img_color] = Image(img_color, folder="/images/tile_heads/", size=[SIZE, SIZE])
            Tile.highlight_image = Image('highlight', folder="/images/misc/", size=[SIZE, SIZE])
        self.x = x
        self.y = y
        self.drawX = self.x*SIZE
        self.drawY = self.y*SIZE
        self.color = color
        self.isWall = False
        if self.color is None: # None
            self.color = 'white'
        elif Tile.is_wall_color(self.color): # wall
            self.isWall = True
        self.image = Tile.tile_image_dict[self.color].image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.drawX,self.drawY

        self.highlight = False
        self.remove_highlight = False
        self.enclosed = False
        self.alpha = 255 # opaque

    def is_wall(self):
        return self.isWall

    def reset(self):
        if self.isWall:
            return

        self.enclosed = False
        self.alpha = 255
        self.image.set_alpha(self.alpha)

        # reset color - tile does not move (Except for dumbAI tile which is children)
        self.color = 'white'
        self.image = Tile.tile_image_dict[self.color].image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.drawX,self.drawY

        self.highlight = False
        self.remove_highlight = False


    def getPos(self):
        return self.x,self.y

    def getColor(self):
        return self.color

    def setColor(self,set_color): # 이걸 호출하면 해당 타일의 색을 변화시킬 수 있다!
        past_color = self.color
        self.color = set_color
        if self.color is None: # None
            self.color = 'white'
        self.image = Tile.tile_image_dict[self.color].image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.drawX,self.drawY
        # return True if color is changed = someone occupied this cell!
        return past_color != set_color

    def setEnclosed(self):
        self.enclosed = True
        self.alpha = 60 # transparent

    # def draw(self,board): # draw sprite
    #     pygame.draw.rect(self.image, self.color, self.rect) #pygame.Rect(self.drawX, self.drawY, SIZE, SIZE)

    def turn_highlight_red(self):
        self.highlight = True
        # print('highlight position', self.x,self.y)

    def update(self): # if update position, color etc.
        if self.isWall:
            return

        if self.enclosed:
            self.alpha += 20
            if self.alpha > 255:
                self.alpha = 255
                self.enclosed = False
            # change image property w.r.t alpha values here
            self.image.set_alpha(self.alpha)

        if self.remove_highlight:
            self.remove_highlight = False
            self.image = Tile.tile_image_dict[self.color].image
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = self.drawX, self.drawY

        if self.highlight:
            self.highlight = False
            self.remove_highlight = True
            self.image = Tile.highlight_image.image
            self.image.set_alpha(255) # highlight should not be affected by alpha
            self.rect = self.image.get_rect()
            self.rect.x, self.rect.y = self.drawX, self.drawY

    def moveTile(self, dx, dy): # in coordinates
        self.x+= dx
        self.y+= dy
        self.drawX,self.drawY = self.x*SIZE , self.y*SIZE
        self.rect.x, self.rect.y = self.drawX, self.drawY

    '''
    # Factory method
    Read tilemap text data and make it into 2D array
    
    tileData: 2D array 
    [ ['w', 'w', ... ] ['w', 'w', ... ] ... ]
    '''
    @classmethod
    def generate_tile_map(cls, tileData):
        col, row = len(tileData[0]), len(tileData) # (x,y) = tiles[y][x] # x is col y is row
        num_wall = 0

        # tiles = [[cls(c, r,cls.available_color_initials[tileData[r][c].lower()]) for c in range(col)] for r in range(row)]
        tiles = [[] for r in range(row)]
        for r in range(row):
            for c in range(col):
                this_entity_color = cls.available_color_initials[tileData[r][c].lower()]
                entity = cls(c, r, this_entity_color)
                tiles[r].append(entity)
                if Tile.is_wall_color(this_entity_color):
                    num_wall += 1

        num_occupiable_tiles = col*row - num_wall
        return tiles, num_occupiable_tiles

    '''
    # Utility method
    Given tile list, change(set) color according to given list
    '''
    @staticmethod
    def set_colors(tiles, target_coords_and_colors):
        for celem in target_coords_and_colors:
            x,y,color = celem
            tiles[y][x].setColor(color)
            # print(tiles[y][x].display_color)

    @staticmethod
    def set_enclosed(tiles, target_coords_and_colors):
        for celem in target_coords_and_colors:
            x,y,_ = celem # discard color (no need)
            tiles[y][x].setEnclosed()

    @staticmethod
    def is_wall_color(color):
        return color == 'wall'


class ScoreEntry():
    color_lookup_table = {'dark':(10,10,10), 'green':(162,217,138), 'blue':(73,126,255), 'orange':(255,188,151), 'purple':(139,104,153), 'red':(255,130,132), 'skyblue':(112,224,255), 'white':(247,247,247),'yellow':(242,230,132)}

    def __init__(self, x, y,total_num_tiles):
        self.total_num_tiles = total_num_tiles
        self.x = x
        self.y = y
        self.width = 400
        self.height = 44
        self.rectX = self.x - self.width//4
        self.rectY = self.y - self.height//4

        self.name = ''
        self.color = 'white'
        self.textColor = 'white'
        self.scorePercentage = 0

        self.image = Tile.head_tile_image_dict[self.color].image
        self.font_for_winner_message = pygame.font.SysFont('arial', 20, True)

    def draw(self,screen):
        pygame.draw.rect(screen, LIGHTER_BACKGROUND, pygame.Rect(self.rectX, self.rectY, self.width, self.height), 0, 10)

        screen.blit(self.image, (self.x , self.y))
        text_name = self.font_for_winner_message.render("{:10}".format(self.name), True, self.textColor)
        text_score = self.font_for_winner_message.render("{:2d} %".format(self.scorePercentage),True, self.textColor)
        screen.blit(text_name, [self.x + 60, self.y])
        screen.blit(text_score, [self.x + 160, self.y])


    def update(self, record):
        self.color = record[0]
        self.textColor = self.color
        if self.textColor in ScoreEntry.color_lookup_table:
            self.textColor = ScoreEntry.color_lookup_table[self.textColor]
        self.name = record[1]
        self.scorePercentage = round((record[2]/self.total_num_tiles)*100)
        self.image = Tile.head_tile_image_dict[self.color].image


class ScoreBoard():
    def __init__(self, x, y, total_num_tiles,element_amount = 1):
        self.total_num_tiles = total_num_tiles
        self.x = x
        self.y = y
        self.gap = 60
        self.img_size = 20
        self.placeHolderList = [ScoreEntry(self.x ,self.y+ self.gap*i,self.total_num_tiles) for i in range(element_amount)]

    def update_and_draw(self,records, screen):
        index = 0
        for entry in self.placeHolderList:
            entry.update(records[index])
            entry.draw(screen)
            index+=1
