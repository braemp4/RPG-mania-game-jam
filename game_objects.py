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

        self.frame_list = [self.sprite_sheet.get_frame_img(i, self.row, self.char_scale, bk_color) for i in range(self.start, self.anim_steps)]
        
        # starter frame
        self.frame = 0
        self.bk_color = bk_color

    def draw(self, screen, x, y, direction):

        if direction == "right":
            screen.blit(self.frame_list[self.frame], (x,y))

        elif direction == "left":
            surf = pygame.transform.flip(self.frame_list[self.frame], True, False)
            surf.set_colorkey(self.bk_color)

            screen.blit(surf, (x,y))

    def animate(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_anim >= self.anim_cooldown:
            self.frame +=1
            self.last_anim = current_time
            if self.frame >= len(self.frame_list):
                self.frame = 0



class Char:
    def __init__(self, screen, x, y, anim_mapper: list, walk_speed):
        self.screen = screen
        self.x = x 
        self.y = y 

        self.animations = [Animation(name=param[0], row=param[1], start=param[2], steps=param[3], cooldown = param[4], sheet = param[5],char_scale= param[6],bk_color= param[7]) for param in anim_mapper]

        self.walk_speed = walk_speed 
        self.flip = False
        self.jumping = False
        self.falling = False
        self.grav = 1
        self.jump_height = 20
        self.y_vel = self.jump_height
    
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
            self.y -=self.y_vel 
            self.y_vel -=self.grav 

            if self.y_vel < -self.jump_height:
                self.jumping = False
                self.y_vel = self.jump_height

    def walk(self, direction):
        if direction == "right":
            self.x +=self.walk_speed
        if direction == "left":
            self.x -=self.walk_speed

class DinoTest:
    def __init__(self):
        self.screen = pygame.display.set_mode((500, 500))

    def run(self):
        clock = pygame.time.Clock()
        pygame.init()

        sprite_sheet_img = pygame.image.load("test-spritesheet.png")
        BG = (50, 50, 50)
        BLACK = (0, 0, 0)
        SCALE = 6

        sprite_sheet = SpriteSheet(sheet_img=sprite_sheet_img, w=24, h=24)
        anim_params = [("idle", 0, 0, 4, 150, sprite_sheet, 9, BLACK), ("walk", 0, 3, 10, 50, sprite_sheet, 9, BLACK)]

        dino = Char(screen=self.screen, x=200, y=0, anim_mapper=anim_params, walk_speed=5)
        
        # for testing gravity
        dino.falling = True

        anim = "idle"
        direction = "right"
        
        FLOOR = 300

        y_vel = 0
        grav = 1
        run = True 

        while run:
            self.screen.fill(BG)
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            key_press = pygame.key.get_pressed()

            if key_press[pygame.K_RIGHT]:
                dino.walk("right")
                direction = "right"
                anim = "walk"
            elif key_press[pygame.K_LEFT]:
                dino.walk("left")
                direction = "left"
                anim = "walk"


            else:
                anim = "idle"

            if key_press[pygame.K_SPACE] and not dino.jumping:
  
                dino.jumping = True 
            
            if key_press[pygame.K_LALT]:

                dino = Char(screen=self.screen, x=200, y=0, anim_mapper=anim_params, walk_speed=5)
            
            if dino.jumping:
                dino.jump()
            elif not dino.jumping:
                if dino.y < FLOOR:
                    dino.falling = True
                    dino.y += y_vel
                    y_vel += 1
                elif dino.y >= FLOOR:
                    dino.falling = False
                    dino.y = FLOOR 
                    y_vel = 0




            # if not jumping apply grav
            # if collision apply equal and opposite force

            print("current animation: " + dino.get_anim(anim).name)
            
            dino.get_anim(anim).animate()
            dino.get_anim(anim).draw(dino.screen, dino.x, dino.y, direction)
            pygame.display.update()


