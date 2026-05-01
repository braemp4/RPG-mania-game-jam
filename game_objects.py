import pygame 
import random

class SpriteSheet:
    def __init__(self, sheet_img, w, h):
        self.sheet_img = sheet_img 
        self.w = w 
        self.h = h

    def get_frame_img(self, frame, row, scale, bk_color):
        '''
        Cut out a single frame from the sprite sheet
        '''
        
        # surface for frame image
        img = pygame.Surface((self.w, self.h)).convert_alpha()

        # draw frame onto surface 
        img.blit(self.sheet_img, dest = (0,0), area = ((frame * self.w), (row * self.h), self.w, self.h))

        # scale img
        img = pygame.transform.scale(img, (self.w * scale, self.h * scale))
        
        # remove background 
        img.set_colorkey(bk_color)


        return img

class Animation:
    def __init__(self, name, row, start, steps, cooldown, sheet: SpriteSheet, char_scale, bk_color):
        
        self.name = name

        # sprite sheet object
        self.sprite_sheet = sheet
        self.last_anim = pygame.time.get_ticks()
        self.anim_cooldown = cooldown
        self.char_scale = char_scale

        self.row = row 
        self.start = start 
        self.anim_steps = steps 
        
        # get frames of animation
        self.frame_list = [self.sprite_sheet.get_frame_img(i, self.row, self.char_scale, bk_color) for i in range(self.start, self.anim_steps)]
        
       
 
        # starter frame
        self.frame = 0
        self.bk_color = bk_color
    
    def draw(self, screen, x, y, direction):
        '''
        Draw can return a mask! This will work bcuz draw "knows" what frame is on screen at any given time AND it considers x, y and direction of the character

        '''
        img = self.frame_list[self.frame]
        if direction == "right":
            screen.blit(img, (x,y))
        
        elif direction == "left":
            flipped = pygame.transform.flip(img, True, False)
            flipped.set_colorkey(self.bk_color)
            img = flipped 
            screen.blit(img, (x,y)) 

        return img


    def animate(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_anim >= self.anim_cooldown:
            self.frame +=1
            self.last_anim = current_time
            if self.frame >= len(self.frame_list):
                self.frame = 0


class Char:
    def __init__(self, screen, x, y, anim_mapper: list, walk_speed, floor):
        self.screen = screen
        
        self.x, self.y = x, y

        # implicit height 
        self.implicit_height = y

        self.animations = [Animation(name=param[0], row=param[1], start=param[2], steps=param[3], cooldown = param[4], sheet = param[5],char_scale= param[6],bk_color= param[7]) for param in anim_mapper]

        self.walk_speed = walk_speed 
        self.flip = False
        self.jumping = False
        self.falling = False
        self.grav = 1
        self.jump_height = 30
        self.y_vel_up = self.jump_height
        self.y_vel_down = 0
        
        self.floor = floor

        # testing overhead_coillision
        self.overhead_collision = False

         
    def get_anim(self, name):

        anim_to_return = None 
        for anim in self.animations:
            if anim.name == name:
                anim_to_return = anim

        if anim_to_return is None:
            raise Exception("Animation not found!")

        return anim_to_return


    def jump(self, tiles): 
        if self.jumping:
            for tile in tiles:
                tile.y +=self.y_vel_up 
            
            self.implicit_height -= self.y_vel_up # dont put it in the for loop!
            #self.y -=self.y_vel_up
            self.y_vel_up -=self.grav 

            if self.y_vel_up <= 0:
                self.jumping = False
                #self.y_vel_up = self.jump_height
                self.falling = True
                self.overhead_collision = False
    
    def fall(self, tiles):
        if self.falling:

            self.y_vel_up = 0

            #self.y += self.y_vel_down
            for tile in tiles:
                tile.y -=self.y_vel_down

            self.implicit_height +=self.y_vel_down # dont put it in the for loop
            self.y_vel_down += self.grav


            #if self.y >= self.floor:
            if self.implicit_height >= self.floor:
                # why the bug happened getting stuck in air with new tile height change 
                    # and also why we actually DONT need implicit height 
                    # at the bottom of the game loop, we set char.falling = true depending on distance from floor (char.y) so we changed it to use char.implicit_height 
                    # this could also be acheived with tile.y, but char.implicit_height is a bit safer 

                self.y_vel_up = self.jump_height

                self.falling = False
                self.y_vel_down = 0
        

    def walk(self, direction, right_collide, left_collide, tiles):
        if direction == "right" and not right_collide:
            #self.x +=self.walk_speed
            for tile in tiles:
                tile.x -=self.walk_speed
        if direction == "left" and not left_collide:
            #self.x -=self.walk_speed

            for tile in tiles:
                tile.x +=self.walk_speed

class TilePrototype:
    def __init__(self, x, y, dimensions: tuple,):
        self.x  = x
        self.y = y 
        self.surface = pygame.Surface(dimensions)

        self.surface.fill((255, 255, 255))
        self.mask = pygame.mask.from_surface(self.surface)

    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        


class MapPrototype: 
    def __init__(self, tiles):
        self.tiles = tiles # a list with TilePrototype objects
    def draw_stuff_in_fov(self, screen, char_pos: tuple, fov: tuple ):
        for tile in self.tiles:
#            if ((tile.x < char_pos[0] - fov[0]) and (tile.x > char_pos[0] + fov[0])): 
            # note this dosn't consider the width or right of the object, just the top left corner
            if tile.x >= char_pos[0] - fov[0] and tile.x < char_pos[0] + fov[0]:
                tile.draw(screen)




class DinoTest:
    def __init__(self):
        self.screen = pygame.display.set_mode((1200, 900))

    def run_platformer(self):
        clock = pygame.time.Clock()
        pygame.init()

        sprite_sheet_img = pygame.image.load("dino-spritesheet.png")
        BG = (50, 50, 50)
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        SCALE = 9

        sprite_sheet = SpriteSheet(sheet_img=sprite_sheet_img, w=24, h=24)
        anim_params = [("idle", 0, 0, 4, 150, sprite_sheet, 9, BLACK), ("walk", 0, 3, 10, 50, sprite_sheet, 9, BLACK)]

        dino = Char(screen=self.screen, x=200, y=400, anim_mapper=anim_params, walk_speed=5, floor=400)
        
        # for testing gravity
        dino.falling = True

        anim = "idle"
        direction = "right"
        
        run = True 
        
#        surf_test = pygame.Surface((400, 100)) 
#        surf_test.fill(WHITE)
#        surf_mask = pygame.mask.from_surface(surf_test)
        
        left_collide = False
        right_collide = False
        
        tiles = [TilePrototype(i + random.randint(-20, 20), 300 + random.randint(-20, 20), (50 + random.randint(0, 20), 50 + random.randint(0, 30)) )for i in range(0,2000, 400)]
        tile_map = MapPrototype(tiles=tiles)

        while run:
            self.screen.fill(BG)
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
           
            # key inputs
            key_press = pygame.key.get_pressed()
            
            old_anim = anim # for printing current animation

            if key_press[pygame.K_RIGHT]:
                dino.walk("right", right_collide, left_collide, tiles)
                direction = "right"
                anim = "walk"
            elif key_press[pygame.K_LEFT]:
                dino.walk("left", right_collide, left_collide, tiles)
                direction = "left"
                anim = "walk"
            else:
                anim = "idle"
            
            if anim != old_anim:
                print("current animation: " + dino.get_anim(anim).name)

            if key_press[pygame.K_SPACE] and not dino.jumping:
  
                dino.jumping = True 
            
            if key_press[pygame.K_LALT]:

                dino = Char(screen=self.screen, x=200, y=400, anim_mapper=anim_params, walk_speed=5, floor=400)
                       
            # Jumping and falling
            if dino.jumping and not dino.falling:
                dino.jump(tiles)

            elif not dino.jumping:
                if dino.implicit_height< dino.floor:
                    dino.falling = True
                elif dino.implicit_height >= dino.floor:
                    dino.falling = False

            if dino.falling:
                dino.fall(tiles)
            
             
#            self.screen.blit(surf_test, (500, 400)) # for collision test

            tile_map.draw_stuff_in_fov(self.screen, char_pos=(dino.x, dino.y), fov=(1000, 1000)) # for tile map test

            # animate dino
            dino.get_anim(anim).animate()

            # testing with surf but later char can return mask directly
            dino_surf = dino.get_anim(anim).draw(dino.screen, dino.x, dino.y, direction)
            dino_mask = pygame.mask.from_surface(dino_surf)

#            mask_debug_img = dino_mask.to_surface()
#            self.screen.blit(mask_debug_img)
            
            for tile in tiles:
                overlap = dino_mask.overlap(tile.mask, (tile.x -dino.x, tile.y - dino.y)) 
                if overlap:
                    print(overlap)
                    tile.surface.fill(GREEN)

                    if overlap[1] >=70:
                        # not sure how to fix lol                                                
                        if not dino.jumping:
                            dino.y_vel_down = -1
                        else:
                            dino.y_vel_down = 0
                        
                        dino.floor = tile.y

                        
                    elif overlap[1] <  70: # must pick a good value here! 
                        dino.y_vel_up = -1 * dino.jump_height -1

  
                else:
                    tile.surface.fill(WHITE)
                    right_collide = False
                    left_collide = False
                    dino.floor=400

            '''
            # all for collision testing
            dino_overlap = dino_mask.overlap(surf_mask, (500 - dino.x, 400 - dino.y))

            if dino_overlap: 
                print(dino_overlap)
                surf_test.fill(GREEN)
                
                if dino_overlap[1] >= 100:
                    dino.floor = 7 

                elif dino_overlap[1] <= 70: # must pick a good value here! 
                    dino.y_vel_up = -1 * dino.jump_height -1

                if dino_overlap[0] >= 160 and dino_overlap[1] <=70:
                    dino.x -=1
                    right_collide = True

                elif dino_overlap[0] <=90 and dino_overlap[1] < 70:
                    dino.x +=1
                    left_collide = True


            else:
                surf_test.fill(WHITE)
                dino.falling = True
                right_collide = False
                left_collide = False
                dino.floor=400
            '''
          
            print(dino.implicit_height)
            pygame.display.update()


