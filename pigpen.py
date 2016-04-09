import sys
import pygame
import random
from pygame.locals import *

WHITE = 255,255,255
GREEN = 0,255,0
BLACK = 0,0,0
BLUE  = 0,0,255
RED   = 255,0,0

pygame.init()

sqsize = 100
GRID_W = 8
GRID_H = 6
size = width, height = GRID_W * sqsize, GRID_H * sqsize

screen = pygame.display.set_mode(size)

pigimg = pygame.image.load('pics/pigmyeye.gif').convert()

fence_width = 20

class Parcel:
    def __init__(self, pos):
        self.pos = pos
        self.pig = False
        self.checked = False
        self.set_fences(False)

    def set_fences(self, fence_bool):
        self.north = fence_bool
        self.east  = fence_bool
        self.south = fence_bool
        self.west  = fence_bool

class GParcel(Parcel):
    def __init__(self, pos, size, fence_width):
        super(GParcel, self).__init__(pos)
        r = Rect(pos[0]*size, pos[1]*size, size, size)
        fw = fence_width
        self.rect = r
        self.nrect = Rect(r.left,     r.top,       size, fw)
        self.erect = Rect(r.right-fw, r.top,       fw,   size)
        self.srect = Rect(r.left,     r.bottom-fw, size, fw)
        self.wrect = Rect(r.left,     r.top,       fw,   size)

class Field:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = []
        for w in range(grid_width):
            self.grid.append([])
            for h in range(grid_height):
                self.grid[w].append(Parcel(pos=(w,h)))
        self.reset_fences()

    def reset_fences(self):
        for w in range(self.grid_width):
            for h in range(self.grid_height):
                parcel = self.grid[w][h]
                parcel.set_fences(False)
                if h == 0:
                    parcel.north = True
                if h == self.grid_height-1:
                    parcel.south = True
                if w == 0:
                    parcel.west = True
                if w == self.grid_width-1:
                    parcel.east = True

    def find_enclosures(self, screen = None):
        # recursively explore parcels in grid
        pos_set = [parcel.pos for parcel in self.flatgrid()]
        enclosures = []
        while len(pos_set) > 0:

            checklist = self.get_enclosure(pos_set[0][0], pos_set[0][1], checklist=[], screen=screen)
            pos_set = [pos for pos in pos_set if pos not in checklist]
            enclosures.append(checklist)

            if screen is not None:
                 for w,h in checklist:
                    pygame.draw.circle(screen, BLACK, self.grid[w][h].rect.center, 15)

            #print(len(checklist), self.grid_width*self.grid_height, len(pos_set))

        return enclosures

    def get_enclosure(self, w, h, checklist=[], screen = None) -> [Parcel]:
        parcel = self.grid[w][h]
        if (w,h) in checklist:
            print(checklist)
            raise Exception('BABOO')
        try:
            pygame.draw.circle(screen, GREEN, self.grid[w][h].rect.center, 15)
            pygame.display.flip()
            pygame.time.wait(80)
            pygame.draw.circle(screen, BLUE, self.grid[w][h].rect.center, 15)
        except:
            pass

        checklist.append((w,h))
        if not parcel.north and h != 0 and (w, h-1) not in checklist:
            #print('({},{}) -> NORTH'.format(w,h))
            checklist = self.get_enclosure(w, h-1, checklist, screen)
        if not parcel.east and w != self.grid_width-1 and (w+1, h) not in checklist:
            #print('({},{}) -> EAST'.format(w,h))
            checklist = self.get_enclosure(w+1, h, checklist, screen)
        if not parcel.south and h != self.grid_height-1 and (w, h+1) not in checklist:
            #print('({},{}) -> SOUTH'.format(w,h))
            checklist = self.get_enclosure(w, h+1, checklist, screen)
        if not parcel.west and w != 0 and (w-1, h) not in checklist:
            #print('({},{}) -> WEST'.format(w,h))
            checklist = self.get_enclosure(w-1, h, checklist, screen)

        try:
            pygame.draw.circle(screen, RED, self.grid[w][h].rect.center, 15)
            pygame.display.flip()
            pygame.time.wait(20)
        except:
            pass
        #print('({},{}) TAPPED OUT at {}'.format(w,h,len(checklist)))
        return checklist


    def flatgrid(self):
        return [item for sublist in self.grid for item in sublist]



class GField(Field):
    def __init__(self, field, sqsize, fence_width):
        self.grid_width, self.grid_height = field.grid_width, field.grid_height

        self.grid = []
        for w in range(field.grid_width):
            self.grid.append([])
            for h in range(field.grid_height):
                assert field.grid[w][h].pos == (w,h)
                parcel = GParcel(field.grid[w][h].pos, sqsize, fence_width)
                self.grid[w].append(parcel)
        self.reset_fences()

        self.fence_posts = []
        for w in range(self.grid_width+1):
            for h in range(self.grid_height+1):
                self.fence_posts.append((w*sqsize,h*sqsize))







field = GField(Field(GRID_W, GRID_H), 100, 10)

for post_pos in field.fence_posts:
    pygame.draw.circle(screen, WHITE, post_pos, 10)

pos = (-100,-100)
pos_click = (-100,-100)
run = True
while run:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.display.quit()
            sys.exit(0)
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            pygame.display.quit()
            run = False
            #sys.exit(0)
        elif event.type == pygame.MOUSEBUTTONUP:
            pos_click = pygame.mouse.get_pos()

            for w in range(field.grid_width):
                for h in range(field.grid_height):
                    if field.grid[w][h].nrect.collidepoint(pos_click) and h!=0:
                        field.grid[w][h].north = True
                        try: field.grid[w][h-1].south = True
                        except: pass
                    if field.grid[w][h].erect.collidepoint(pos_click) and w != field.grid_width-1:
                        field.grid[w][h].east = True
                        try: field.grid[w+1][h].west = True
                        except: pass
                    if field.grid[w][h].srect.collidepoint(pos_click) and h != field.grid_height-1:
                        field.grid[w][h].south = True
                        try: field.grid[w][h+1].north = True
                        except: pass
                    if field.grid[w][h].wrect.collidepoint(pos_click) and w != 0:
                        field.grid[w][h].west = True
                        try: field.grid[w-1][h].east = True
                        except: pass

            print()
            enclosures = field.find_enclosures(screen)
            for enc in enclosures:
                pigsum = 0
                for w,h in enc:
                    if field.grid[w][h].pig:
                        pigsum += 1
                print('pigsum={} , enclen={}'.format(pigsum, len(enc)))

                # count pigs in loop, score pigs, remove pigs from loop
                # gain more fences

            sq = random.choice(field.flatgrid())
            sq.pig = True


    pos = pygame.mouse.get_pos()

    for w in range(field.grid_width):
        for h in range(field.grid_height):
            parcel = field.grid[w][h]
            if parcel.pig:
                pigrect = pigimg.get_rect()
                pigrect.center = parcel.rect.center
                screen.blit(pigimg, pigrect)
            else:
                pigrect = pigimg.get_rect()
                pigrect.center = parcel.rect.center
                pygame.draw.rect(screen, BLACK, pigrect)

            if parcel.north:
                pygame.draw.rect(screen, WHITE, parcel.nrect)
            elif parcel.nrect.collidepoint(pos):
                pygame.draw.rect(screen, BLUE, parcel.nrect)
            else:
                pygame.draw.rect(screen, BLACK, parcel.nrect)

            if parcel.south:
                pygame.draw.rect(screen, WHITE, parcel.srect)
            elif parcel.srect.collidepoint(pos):
                pygame.draw.rect(screen, BLUE, parcel.srect)
            else:
                pygame.draw.rect(screen, BLACK, parcel.srect)

            if parcel.east:
                pygame.draw.rect(screen, WHITE, parcel.erect)
            elif parcel.erect.collidepoint(pos):
                pygame.draw.rect(screen, BLUE, parcel.erect)
            else:
                pygame.draw.rect(screen, BLACK, parcel.erect)

            if parcel.west:
                pygame.draw.rect(screen, WHITE, parcel.wrect)
            elif parcel.wrect.collidepoint(pos):
                pygame.draw.rect(screen, BLUE, parcel.wrect)
            else:
                pygame.draw.rect(screen, BLACK, parcel.wrect)


    for post_pos in field.fence_posts:
        pygame.draw.circle(screen, WHITE, post_pos, 14)
        #pygame.draw.circle(screen, BLACK, post_pos, 10)


    pygame.display.flip()
    pygame.time.delay(50)

