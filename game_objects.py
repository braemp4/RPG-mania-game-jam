import pygame 


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


    def jump(self): 
        if self.jumping:
            self.y -=self.y_vel_up
            self.y_vel_up -=self.grav 

            if self.y_vel_up <= 0:
                self.jumping = False
                #self.y_vel_up = self.jump_height
                self.falling = True
                self.overhead_collision = False
    
    def fall(self):
        if self.falling:

            self.y_vel_up = 0

            self.y += self.y_vel_down
            self.y_vel_down += self.grav

            if self.y >= self.floor:

                self.y_vel_up = self.jump_height

                self.falling = False
                self.y_vel_down = 0
        

    def walk(self, direction, right_collide, left_collide):
        if direction == "right" and not right_collide:
            self.x +=self.walk_speed
        if direction == "left" and not left_collide:
            self.x -=self.walk_speed


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

        dino = Char(screen=self.screen, x=200, y=0, anim_mapper=anim_params, walk_speed=5, floor=400)
        
        # for testing gravity
        dino.falling = True

        anim = "idle"
        direction = "right"
        
        run = True 
        
        surf_test = pygame.Surface((400, 100)) 
        surf_test.fill(WHITE)
        surf_mask = pygame.mask.from_surface(surf_test)
        
        left_collide = False
        right_collide = False

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
                dino.walk("right", right_collide, left_collide)
                direction = "right"
                anim = "walk"
            elif key_press[pygame.K_LEFT]:
                dino.walk("left", right_collide, left_collide)
                direction = "left"
                anim = "walk"
            else:
                anim = "idle"
            
            if anim != old_anim:
                print("current animation: " + dino.get_anim(anim).name)

            if key_press[pygame.K_SPACE] and not dino.jumping:
  
                dino.jumping = True 
            
            if key_press[pygame.K_LALT]:

                dino = Char(screen=self.screen, x=200, y=0, anim_mapper=anim_params, walk_speed=5, floor=400)
           
            
            # Jumping and falling
            if dino.jumping and not dino.falling:
                dino.jump()

            elif not dino.jumping:
                if dino.y < dino.floor:
                    dino.falling = True
                elif dino.y >= dino.floor:
                    dino.falling = False

            if dino.falling:
                dino.fall()
            
                        
            self.screen.blit(surf_test, (500, 400))

            # animate dino
            dino.get_anim(anim).animate()

            # testing with surf but later char can return mask directly
            dino_surf = dino.get_anim(anim).draw(dino.screen, dino.x, dino.y, direction)
            dino_mask = pygame.mask.from_surface(dino_surf)

#            mask_debug_img = dino_mask.to_surface()
#            self.screen.blit(mask_debug_img)

 
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
                right_collide = False
                left_collide = False
                dino.floor=400
          

            pygame.display.update()


