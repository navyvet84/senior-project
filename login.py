# USE INSTRUCTIONS! PLEASE READ!
# Requires pygame-ce, I think: pip install pygame-ce
# Requires SQL database I call "game_db", with table called login with columns "name" and "password" put test login and password there

# injections to test

# Username: test' OR '1'='1
# Password: password
# Username: ' OR 1=1 --

# Password: UPDATE party SET level = 99 WHERE name = 'jim';
# Password: UPDATE party SET level = 3 WHERE name = 'jim';

# ' UNION SELECT name FROM login LIMIT 1 --
# ' UNION SELECT password FROM login LIMIT 1 --

# ' DROP TABLE testtable --


try:
    import pyperclip # If you dont import pyperclip you cannot copy paste
    import hashlib
    #from config import *
    import pygame
    import sqlite3
    import random
except ImportError:
    print("Module 'paperclip' not found, continuing without it.")

#import os
#import pygame
#import sqlite3
#import random

#high_score_path = 'C:/Users/Andy/Desktop/AndyRPG/Senior_project/score.txt' # enter the path to the text file so you can keep track high score
db_path = r"C:\Users\Andy\Desktop\AndyRPG\Senior_project\game_db.db"

# if not os.path.exists(high_score_path):
#     with open(high_score_path, 'w') as f:
#         f.write('0')

# with open(high_score_path, 'r') as f:
#     data = f.read().strip()
#     pulled_high_score_from_txt = int(data) if data else 0



CAMERA_WIDTH = 960
CAMERA_HEIGHT = 640

pygame.init()

screen = pygame.display.set_mode((CAMERA_WIDTH, CAMERA_HEIGHT))
pygame.display.set_caption("Login Screen")

screen_font = pygame.font.Font(None, 30) # input font and size


# --- Center Input Boxes ---
center_x = CAMERA_WIDTH // 2
input_box_w = 240
box_adjust_x = 95
box_adjust_y = 0
score = 0
high_score = 0#pulled_high_score_from_txt
lives = 3
max_hp = 0
level = 1
global_timer = 300
loose_life_timer = global_timer # 4 seconds = 240
game_over_timer = global_timer
x_move = 0
x_move2 = 0
shoot_speed = 40
tank_damage = 25


alien_damage = 10
input_boxes = {
    "username": pygame.Rect(center_x - (input_box_w / 2), CAMERA_HEIGHT // 2 - 100, input_box_w, 40), #x,y,w,h
    "password": pygame.Rect(center_x - (input_box_w / 2), CAMERA_HEIGHT // 2 - 10, input_box_w, 40)
}
active_box = None
user_input = {"username": "", "password": ""}

# --- Buttons ---
login_btn = pygame.Rect(center_x - 80, CAMERA_HEIGHT // 2 + 70, 160, 40)#rect size at end
sqli_btn = pygame.Rect(center_x - 80, CAMERA_HEIGHT // 2 + 130, 160, 40)
show_pwd_btn = pygame.Rect(center_x - 80, CAMERA_HEIGHT // 2 + 190, 160, 40)
alien_level = 1
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
sqli_protection = False
show_password = False
clock = pygame.time.Clock()
cursor_visible = True
cursor_timer = 0
login_running = True
game_start = False
tank_start = False

# --- Draw Text ---
def draw_text(text, x, y, size, color):
    font = pygame.font.Font(None, size)
    txt = font.render(text, True, color)
    screen.blit(txt, (x, y))



# --- Check Login ---
def check_login(name, password):
    global login_running, active_box
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        if sqli_protection:
            # SAFE MODE: parameterized query blocks injection
            c.execute("SELECT password FROM login WHERE name=?", (name,))
        else:
            # VULNERABLE MODE: raw string formatting opens up SQL injection
            query = f"SELECT password FROM login WHERE name='{name}'"
            print(f"Executing injection: {query}")  # Debugging: print the query
            c.execute(query)

            # If password field contains injection, execute it
            if any(sql in password.upper() for sql in ["INSERT", "UPDATE", "DELETE", ";", "DROP"]):
                try:
                    # Execute the injected SQL script
                    print(f"Executing injection: {password}")  # Debugging: print the injection
                    c.executescript(password)  # Executes injection like UPDATE, DELETE, etc.
                    print("Injected!")
                except Exception as inj_err:
                    print("Injection error:", inj_err)

        row = c.fetchone()
        conn.close()

        if row and row[0] == password:
            print("Correct Creds")
            login_running = False
            #config.running = True
        else:
            print("Wrong username or password")
    except Exception as e:
        print("DB Error:", e)

class Comet:
    def __init__(self,x,y,speed):
        self.x = x + random.randint(1, 3)
        self.y = y + random.randint(1, 3)
        self.speed = speed
        self.r = random.randint(200, 255)
        self.g = random.randint(10, 200)
        self.b = random.randint(10, 200)
        self.color = (self.r, self.g, self.b)
        self.timer = random.randint(30, 120)
        self.correction_x = random.uniform(-0.5, 0.5)
        self.correction_y = random.uniform(-0.2, 0.2)
        self.speed_correction = random.uniform(0.01, 0.1)
        self.size = random.randint(1,3)

    def draw(self,sparklelist):
        self.x -= self.correction_x
        self.y -= self.correction_y
        self.speed -= self.speed_correction - 0.001
        self.x += self.speed - 0.001
        self.y += self.speed - 0.001
        self.timer -= 1
        self.r -= 1
        self.r = max(1, self.r)
        self.g -= 1
        self.g = max(1, self.g)
        self.b -= 1
        self.b = max(1, self.b)
        self.color = (self.r, self.g, self.b)

        pygame.draw.rect(screen, (self.color), (self.x, self.y, self.size, self.size))
        if self.timer < 0:
            sparklelist.remove(self)
        elif self.speed < -3:
            sparklelist.remove(self)
        elif self.color == (1, 1, 1):
            sparklelist.remove(self)

class Moon:
    def __init__(self):
        self.x = random.randint(20, 150)
        self.y = random.randint(20, 150)
        self.size = random.randint(5, 25)
        self.color = (random.randint(100, 255),random.randint(100, 255),random.randint(200, 255))
        self.angle = random.randint(1,10)
        self.radius = random.randint(500, 900)
        self.speed = random.uniform(0.0001, 0.0003)
        self.center_distance = 300
        self.hit = False
        self.hp = self.size * 10
        self.moon_hitbox = pygame.Rect(0, 0, self.size * 2 - 2, self.size * 2 -2)
        self.clicked = 0
        self.score = int(self.hp /3)
        self.one_tank = False

    def draw(self, moonlist, alienlist , tanklist):
        global game_start, tank_start, score
        self.angle += self.speed # rotate speed
        self.center = pygame.math.Vector2(CAMERA_WIDTH // 2, CAMERA_HEIGHT + self.center_distance)
        self.offset = pygame.math.Vector2(self.radius, 0).rotate_rad(self.angle)
        pos = self.center + self.offset
        self.x, self.y = pos.x, pos.y
        pygame.draw.circle(screen, (self.color), (self.x, self.y), self.size) # The moon

        self.moon_hitbox.center = (self.x, self.y)
        #pygame.draw.rect(screen, RED, self.moon_hitbox) #visual of moon hitbox

        if self.hit:
            if tanklist: # Prob need more of these for bug fix
                self.hp -= tanklist[0].damage
                self.hit = False
            if self.hp < 1:
                blowed_up(self.x,self.y, self.size * 5, self.size * 6)
                alien = Alien()
                game_start = True
                score += self.score
                alienlist.append(alien)
                moonlist.remove(self)

                new_moon = Moon()
                new_moon.x = random.randint(-150, -15)
                new_moon.y = random.randint(700, 900)
                moonlist.append(new_moon)

        if self.clicked == 10 and self.one_tank == False and not tanklist:
            self.one_tank = True
            new_tank = Tank(level)
            tanklist.append(new_tank)
            tank_start = True

class Shooting_star:
    def __init__(self, cometlist):
        self.sparklelist = []
        self.counter = 0
        self.time = 500
        self.x = random.randint(-1000, -10)
        self.y = random.randint(-1000, -10)
        self.color = (random.randint(1,200), random.randint(1,100), random.randint(100,255))
        self.length = random.randint(200, 400)

        self.line_width = random.randint(1,5)
        #self.speed = random.randint(15, 30)
        if self.line_width == 1:
            self.speed = 35
        elif self.line_width == 2:
            self.speed = 30
        elif self.line_width == 3:
            self.speed = 25
        elif self.line_width == 4:
            self.speed = 20
        elif self.line_width == 5:
            self.speed = 15
        roll_comet = random.randint(1,100)
        self.comet = False
        if roll_comet < 5 and not cometlist and not game_start:
            cometlist.append(self)
            self.length = 15
            self.line_width = 6
            self.speed = random.randint(4,7)
            self.comet = True
        dx = 0.7071 * self.length
        dy = 0.7071 * self.length
        self.end_x = self.x + dx
        self.end_y = self.y + dy
        #self.comet_size = random.randint(15,100)

    def draw(self, drop_list):
        global cometlist
        #self.x -= 1
        self.counter += 1
        self.color = (
            max(1, self.color[0] - 1),
            max(1, self.color[1] - 1),
            max(1, self.color[2] - 1)
        )
        if self.counter < self.time:
            self.x += self.speed
            self.y += self.speed
            self.end_x += self.speed
            self.end_y += self.speed
            pygame.draw.line(screen, (self.color), (self.x, self.y), (self.end_x, self.end_y), self.line_width)
            if self.comet:
                sparks = random.randint(5, 25)
                for i in range(sparks):
                    spark = Comet(self.end_x, self.end_y, self.speed)
                    self.sparklelist.append(spark)
                for spark in self.sparklelist:
                    spark.draw(self.sparklelist)
        else:
            drop_list.remove(self)
            if self.comet:
                cometlist.remove(self)

class Stars:
    def __init__(self):
        self.x = random.randint(1,CAMERA_WIDTH)
        self.y = random.randint(1,CAMERA_HEIGHT)
        self.start_frame_twinkle = random.randint(1, 480)
        self.start_twinkle = False
        self.twinkle_timer = 60
        self.size = random.choices([1, 2, 3], [8, 6, 1], k=1)[0] # weighted
        self.color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

        #self.color_timer = 90 # 3 shades for twinkle
        if self.size == 1:
            dull_choice = random.randint(1,2)
            if dull_choice == 1:
                dull = random.randint(20,255)
                self.color = (self.color[0] - dull, self.color[1] - dull, self.color[2] - dull)
        elif self.size == 2:
            dull_choice = random.randint(1,2)
            if dull_choice == 1:
                dull = random.randint(10,75)
                self.color = (self.color[0] - dull, self.color[1] - dull, self.color[2] - dull)
        elif self.size == 3:
            dull_choice = random.randint(1,2)
            if dull_choice == 1:
                dull = random.randint(1,50)
                self.color = (self.color[0] - dull, self.color[1] - dull, self.color[2] - dull)
        r = max(150, min(255, self.color[0]))
        g = max(150, min(255, self.color[1]))
        b = max(150, min(255, self.color[2]))

        self.color = (r, g, b)
        self.c1 = (self.color[0], self.color[1], self.color[2]) # full bright
        self.c2 =  (self.c1[0] - 50, self.c1[1] - 50, self.c1[2] - 50) # less
        self.c3 =  (self.c2[0] - 50, self.c2[1] - 50, self.c2[2] - 50) # almost off

    def draw(self):
        global starlist
        self.x -= .2
        

        if twinkle_frame_counter == self.start_frame_twinkle:
            self.start_twinkle = True

        if self.start_twinkle:
            self.twinkle_timer -= 1
            if self.twinkle_timer > 30:
                pygame.draw.circle(screen, (self.c2), (self.x, self.y), self.size)
            elif self.twinkle_timer > 15:
                pygame.draw.circle(screen, (self.c3), (self.x, self.y), self.size)
            elif self.twinkle_timer > 1:
                pygame.draw.circle(screen, (0,0,0), (self.x, self.y), self.size)
            
            elif self.twinkle_timer == 0:
                self.start_twinkle = False
                self.twinkle_timer = 60
        else:
            
            pygame.draw.circle(screen, (self.color), (self.x, self.y), self.size)

        if self.x < 1: # make new star if goes off screen
            starlist.remove(self)
            star = Stars()
            star.x = CAMERA_WIDTH + 5
            starlist.append(star)

class Title_banner:
    def __init__(self, x, y, letter):
        self.x = x
        self.y = y
        self.color = (0, 0, 80)
        self.size = 100
        self.letter = letter
        self.font = pygame.font.Font(None, self.size)

    def draw(self):
        draw_text(self.letter, self.x, self.y, self.size, self.color)

class Fire_effect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (0, 0, 0)
        self.color_1 = (255, 255, 255)
        self.color_2 = (255, 255, 150)
        self.color_3 = (255, 200, 10)
        self.color_4 = (255, 120, 10)
        self.color_5 = (255, 60, 10)
        self.color_6 = (180, 15, 15)
        if game_start:
            self.color_2 = (180, 220, 255) 
            self.color_3 = (100, 170, 255) 
            self.color_4 = (50, 100, 255) 
            self.color_5 = (80, 50, 180)
            self.color_6 = (120, 0, 150)
        self.timer = random.randint(70, 130)
        self.size = random.randint(8, 14)
        self.direction = random.choice([1, -1])

    def draw(self, firelist):

        mouse_x, mouse_y = pygame.mouse.get_pos() # avoid mouse
        dist_x = self.x - mouse_x
        dist_y = self.y - mouse_y
        distance = max(1, (dist_x**2 + dist_y**2) ** 0.5) # pythag
        if distance < 50:  # adjust radius
            repel_strength = 4  # tweak this
            self.x += (dist_x / distance) * repel_strength
            self.y += (dist_y / distance) * repel_strength
        self.timer -= 1


        self.size -= 0.01
        if self.timer > 80:
            self.color = self.color_1
            self.x -= self.direction
        elif self.timer > 60:
            self.color = self.color_2
            self.x += self.direction
        elif self.timer > 40:
            self.color = self.color_3
            self.x -= self.direction
        elif self.timer > 30:
            self.color = self.color_4
            self.x += self.direction
        elif self.timer > 20:
            self.color = self.color_5
            self.x -= self.direction
        elif self.timer > 10:
            self.color = self.color_6
            self.x += self.direction
        self.y -= random.randint(0,2)
        pygame.draw.rect(screen, (self.color), (self.x, self.y, self.size, self.size))
        if self.timer == 0:
            firelist.remove(self)
        elif self.size == 0:
            firelist.remove(self)

class Bullet:
    def __init__(self, x, y, color, direction):
        self.name = random.randint(1,1000)
        self.x = x
        self.y = y - 2
        self.size = 8
        self.color = color
        self.hit = False
        self.bullet_hitbox = pygame.Rect(0, 0, self.size * 2 - 2, self.size * 2 -2)
        self.reverse = direction # only 1 or neg -1
        self.targetx = 0
        self.targety = 0
        self.inertia = 0
        self.missile = False
        self.speed = 1

    def draw(self, bulletlist):
        pygame.draw.circle(screen, (self.color), (self.x, self.y), self.size)
        self.bullet_hitbox.center = (self.x, self.y)
        #pygame.draw.rect(screen, RED, self.bullet_hitbox) #visual of bullet hitbox
        self.y -= 5 * self.reverse
        if bulletlist:
            if self.hit:
                bulletlist.remove(self)
                blowed_up(self.x, self.y, 25, 35)
            if self.y < -10:
                bulletlist.remove(self)
        self.find_target = True
        if self.missile:
            self.find_target = True
            if alienlist:
                self.target = alienlist[0]
                target_x = self.target.x
                target_y = self.target.y
                self.speed += 0.025 - ((self.inertia * .001) * 1)
                self.speed = max(-1, min(12, self.speed))

                self.y -= self.speed  # Constant forward speed

                x_distance = self.target.x - self.x
                y_distance = self.target.y - self.y
                # if self.target.direction == "left": # moving
                #     adjusted_x_left = 1
                # if self.target.direction == "right": # moving
                #     adjusted_x_right = 1
                if x_distance > 1:
                    
                    self.inertia += .25
                    self.inertia = max(-25, min(self.inertia, 25))

                elif x_distance < 1:
                    self.inertia -= .25
                    self.inertia = max(-25, min(self.inertia, 25))
                elif x_distance == 0:
                    pass
                print("name ",self.name, " inertia ",self.inertia," speed ",self.speed)
                self.inertia = max(-25, min(self.inertia, 25))
                self.x += self.inertia

class Tank:
    def __init__(self, level):
        self.size = 50
        self.speed = 6
        self.x = CAMERA_WIDTH / 2 - self.size + 20
        self.y = CAMERA_HEIGHT - self.size
        self.color = (random.randint(200, 210), random.randint(200, 210), random.randint(200, 210))
        
        self.size_2 = 2
        self.level = level
        self.max_hp = 5 * self.level
        self.hp = self.max_hp
        self.damage = tank_damage
        self.bullet_color = (0, 100, 199)
        self.kills = 0
        self.shooting = False
        self.tank_hitbox = pygame.Rect(0, 0, self.size, self.size)
        self.hit = False
        self.shoot_reset = shoot_speed
        self.shooting_timer = 0
        self.shooting_timer2 = shoot_speed / 2 #has to be this or double cannon breaks
        self.double_cannon = False
        
    def draw(self, tanklist):
        global game_start, tank_start, score, lives, loose_life_timer, alien_level, alienlist, alienbulletlist, alien_damage, game_over_timer, level, shoot_speed, tank_damage
        self.tank_hitbox.center = (self.x + self.size / 2, self.y + self.size / 2)
        self.shooting_timer = int(self.shooting_timer)
        self.shooting_timer2 = int(self.shooting_timer2)
        barrel_y_single = self.y  # default position when not shooting
        barrel_y_double1 = self.y  # default position when not shooting
        barrel_y_double2 = self.y  # default position when not shooting
        if self.kills == 3:
            self.level += 1
            level += 1 #global
            self.kills = 0
            self.max_hp += 5 
            self.hp = self.max_hp
            self.damage += 1
            tank_damage += 1
            shoot_speed -= .5

        self.shoot_reset = max(1, self.shoot_reset)
        if self.shooting:
            self.shooting_timer -= 1
            self.shooting_timer2 -= 1
            if self.double_cannon:
                if self.shooting_timer == 0:
                    bullets = Bullet(self.x + 16, self.y - 22, self.bullet_color, 1) #left cannon
                    bulletlist.append(bullets)
                    self.shooting_timer = self.shoot_reset
                    barrel_y_double1 = self.y + 5  # animate barrel moving down
                    self.shooting = False

                elif self.shooting_timer2 == 0:
                    bullets = Bullet(self.x + 42, self.y - 22, self.bullet_color, 1)
                    bulletlist.append(bullets)
                    self.shooting_timer2 = self.shoot_reset
                    barrel_y_double2 = self.y + 5  # animate barrel moving down
                    self.shooting = False
            else:    
                if self.shooting_timer == 0:
                    bullets = Bullet(self.x + 30, self.y - 22, self.bullet_color, 1) #single shot
                    #bullets.missile = True
                    bulletlist.append(bullets)
                    self.shooting_timer = self.shoot_reset
                    barrel_y_single = self.y + 5  # animate barrel moving down
                    self.shooting = False
        else:
            self.shooting = False

                
        if self.x < 0:
            self.x = 0
        elif self.x > CAMERA_WIDTH - self.size:
            self.x = CAMERA_WIDTH - self.size

        # draw tank body
        pygame.draw.rect(screen, (self.color), (self.x + 4, self.y - 1, self.size, self.size - 20))
        # draw tank barrel 
        if self.double_cannon:
            pygame.draw.rect(screen, (self.color), (self.x + 6, barrel_y_double1 - 30, 20, 25))
            pygame.draw.rect(screen, (self.color), (self.x + 32, barrel_y_double2 - 30, 20, 25))
        else:
            pygame.draw.rect(screen, (self.color), (self.x + 20, barrel_y_single - 30, 20, 25))
        #pygame.draw.rect(screen, RED, self.tank_hitbox) #visual of tank hitbox

        if self.hit:
            self.hp -= alien_damage
            self.hit = False

        if self.hp < 1: # End game code here!!!
            lives -= 1
            blowed_up(self.x,self.y, 100, 150)
            tanklist.remove(self)

        if self.shooting_timer <1: 
            self.shooting_timer = self.shoot_reset
        
class Alien:
    def __init__(self):
        self.name = random.randint(1,1000)
        self.width = 100
        self.height = 25
        self.x = CAMERA_WIDTH + self.width
        self.y = 50
        self.level = alien_level
        self.color = (random.randint(1,255), 255, 0)
        self.hp = 25 * self.level
        self.hit = False
        self.alien_hitbox = pygame.Rect(0, 0, self.width, self.height)
        self.speed = int(8 + self.level) / 5
        print(self.speed)
        self.down_speed = 2
        self.direction_timer = 35
        self.direction = "left" # starting
        self.bullet_color = (0, 255, 0)
        self.start = True
        self.score = max(1, 300 + (self.level * 5))

    def draw(self, alienlist, poweruplist):
        global alien_level, alien_damage, game_start, tank_start, score
        self.check_x_right = self.x - 101
        self.check_x_left = self.x + 101
        self.check_y_up = -self.height
        self.check_y_down = self.height
        pygame.draw.circle(screen, (0, 50, 200), (self.x + 50, self.y + 5), 20) 
        pygame.draw.ellipse(screen, self.color, (self.x, self.y, self.width, self.height))
        self.alien_hitbox.center = (self.x + self.width / 2, self.y + self.height / 2)
        #pygame.draw.rect(screen, RED, self.alien_hitbox) #visual of alien hitbox
        if self.hit:
            if tanklist:
                self.hp -= tanklist[0].damage
                self.hit = False
                if self.hp < 1:
                    alien1 = Alien()
                    alienlist.append(alien1)
                    
                    blowed_up(self.x,self.y, 100, 150)
                    tanklist[0].kills += 1
                    alien_level += 1
                    alien_damage += 5
                    score += self.score
                    alienlist.remove(self)
                    if random.randint(1, 3)  == 2:
                        powerup = Powerup(self.x, self.y)
                        poweruplist.append(powerup)


        self.x -= self.speed
        self.y -= 0

        if self.x < CAMERA_WIDTH / 2 and self.start: #so it does not pop in
            self.start = False

        if self.start == False:
            
            if self.x < 5: # Left wall
                self.direction_timer -= 1
                if self.direction_timer > 1:
                    self.direction = "down"
                    self.y += self.down_speed
                    self.score -= 1
                    self.x = 5
                else:
                    self.direction_timer = self.height + 10 # reset
                    self.speed = -self.speed # reverse
            elif self.x > CAMERA_WIDTH - self.width - 5: # Right wall
                self.direction_timer -= 1
                if self.direction_timer > 1:
                    self.direction = "down"
                    self.y += self.down_speed
                    self.score -= 1
                    self.x = CAMERA_WIDTH - self.width - 5
                else:
                    self.direction_timer = self.height + 10 # reset
                    self.speed = -self.speed # reverse
        if self.speed > 1:
            self.direction = "right"
        else:
            self.direction = "left"

        # if self.y > CAMERA_HEIGHT + 5: # reaches end, game over
        #     alienlist.remove(self)
        #     tanklist[0].hp = 0

        roll_shoot = random.randint(1,100) # shoot alien bullet
        if roll_shoot < 2:
                bullets = Bullet(self.x + 50, self.y + 25, self.bullet_color, -1)
                alienbulletlist.append(bullets)

class Explosion:
    def __init__(self, x, y):
        self.x = x + random.uniform(-2.0, 2.0)
        self.y = y + random.uniform(-2.0, 2.0)
        self.size = 10
        self.color = (random.randint(200, 255), random.randint(120, 200), random.randint(120, 200))
        self.dx = random.uniform(-5.0, 5.0)
        self.dy = random.uniform(-5.0, 5.0)
        self.timer = random.randint(20, 55)

    def draw(self, explosionlist):
        self.size -= 0.1
        self.timer -= 1
        self.dx -= 0.01
        self.dx -= 0.01
        self.x -= self.dx
        self.y -= self.dy
        r = max(0, self.color[0] - 0.001)
        g = max(0, self.color[1] - 0.01)
        b = max(0, self.color[2] - 0.1)
        self.color = (r, g, b)
        
        if self.timer > self.timer / 2: # solid color for first half timer
            pygame.draw.rect(screen, (self.color), (self.x, self.y, self.size, self.size))
            if self.timer % 2 == 0: # If remainder is zero AKA even number / flicker
                pygame.draw.rect(screen, (self.color), (self.x, self.y, self.size, self.size))

        if self.timer == 0:
            explosionlist.remove(self)

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.height = 20
        self.width = 60
        self.color = (255, 215, 0)
        self.hit = False
        self.powerup_hitbox = pygame.Rect(0, 0, self.width, self.height)
        self.powerup_hitbox.x = self.x
        self.powerup_hitbox.y = self.y
        self.roll_powerup = random.choice(["damage", "damage", "damage", "speed", "speed", "1up", "double"])
        if self.roll_powerup == "speed": #gold
            self.c1 = (230, 155, 54)
            self.c2 = (251, 251, 251)
            self.c3 = (177, 53, 41)
        if self.roll_powerup == "damage":
            self.c1 = (200, 50, 50)    # strong red
            self.c2 = (255, 150, 150)  # light pinkish-red
            self.c3 = (120, 20, 20)    # dark deep red
        if self.roll_powerup == "double":
            self.c1 = (180, 180, 200)  # light silver-blue
            self.c2 = (240, 240, 255)  # bright silver highlight
            self.c3 = (100, 100, 120)  # shadow silver
        if self.roll_powerup == "1up":
            self.c1 = (48, 80, 200)    # deep blue
            self.c2 = (140, 190, 255)  # light blue
            self.c3 = (20, 40, 120)    # dark shadow blue
        self.timer = 20

    def draw(self, poweruplist):
        global shoot_speed, lives, tank_damage
        self.timer -= 1
        if self.timer == 0:
            self.timer = 20
        if self.timer > 15:
            self.color = self.c1
        elif self.timer > 10:
            self.color = self.c2
        elif self.timer > 5:
            self.color = self.c1
        elif self.timer > 0:
            self.color = self.c3
        self.y += 3
        #self.powerup_hitbox.center = (self.x + self.width, self.y + self.height)
        self.powerup_hitbox.y += 3
        pygame.draw.rect(screen, (self.color), (self.x, self.y, self.width, self.height))
        #pygame.draw.rect(screen, RED, self.powerup_hitbox) #visual of powerup hitbox
        if tanklist:
            if self.roll_powerup == "speed" and self.hit: #gold
                tanklist[0].damage += 10
                tank_damage + 10
                tanklist[0].hp = tanklist[0].max_hp
                poweruplist.remove(self)
            if self.roll_powerup == "damage" and self.hit: #gold
                tanklist[0].shoot_reset -= 1
                tanklist[0].hp = tanklist[0].max_hp
                poweruplist.remove(self)
            if self.roll_powerup == "1up" and self.hit: #gold
                lives += 1
                tanklist[0].hp = tanklist[0].max_hp
                poweruplist.remove(self)
            if self.roll_powerup == "double" and self.hit: #gold
                tanklist[0].double_cannon = True
                tanklist[0].hp = tanklist[0].max_hp
                poweruplist.remove(self)

        if self.y > CAMERA_HEIGHT:
            poweruplist.remove(self)


shootingstarlist = []
starlist = []
cometlist = []
moonlist = []
firelist = []
bannerlist = []
bannerlist2 = []
bulletlist = []
explosionlist = []
alienlist = []
alienbulletlist = []
tanklist = []
poweruplist = []
title =  ["A", "N", "D", "Y", "R", "P", "G"]
title2 = ["E", "N", "V", "A", "D", "E", "R"]



for letter in title:
    x_move += 50
    letter = Title_banner(250 + x_move, 100, letter)
    bannerlist.append(letter)
for letter in title2:
    x_move2 += 50
    letter = Title_banner(250 + x_move2, 100, letter)
    bannerlist2.append(letter)

amount_of_stars = 150
amount_of_moons = random.randint(20, 25)

for i in range(amount_of_stars):
    star = Stars()
    starlist.append(star)


for i in range(amount_of_moons):
    moons = Moon()
    moonlist.append(moons)

def draw_button(button, label, mouse_pos):
    hover_color = (150, 150, 150) if button.collidepoint(mouse_pos) else (80, 80, 80)
    pygame.draw.rect(screen, hover_color, button)
    draw_text(label, button.x + (button.width - screen_font.size(label)[0]) // 2, button.y + (button.height - 32) // 2 + 10, 25, WHITE)#button text x and y here

def blowed_up(x, y, min, max):
    global explosionlist
    size_blast = random.randint(min, max)
    for boom in range(size_blast):
        boom = Explosion(x, y)
        explosionlist.append(boom)

tank_x = 0
tank_y = 0

can_shoot = False
can_tank = False # Hide tank as secret thing
# tank = Tank() # 1 tank at bottom for mini game
# tanklist.append(tank)
twinkle_frame_counter = 0 # for stars
def login_loop():
    global login_running, active_box, show_password, sqli_protection, cursor_timer
    global cursor_visible, shootingstarlist, starlist, tank_x, tank_y, can_shoot
    global alienlist, score, high_score, alien_level, alien_damage, game_start,tank_start,alienbulletlist,lives,loose_life_timer,game_over_timer
    global tanklist, global_timer, twinkle_frame_counter
    while login_running:

        screen.fill(BLACK)
        mouse_pos = pygame.mouse.get_pos()
        
        twinkle_frame_counter += 1
        if twinkle_frame_counter == 480:
            twinkle_frame_counter = 0

        # Fire
        for fire in range(12): # how many spawns per frame
            fire_x = random.randint(1, 430)
            fire_y = random.randint(1, 25)
            start_x = 260 # screen position 
            start_y = 150
            fire = Fire_effect(fire_x + start_x, fire_y + start_y) #adjust fire here
            firelist.append(fire)
        # End Fire

        for star in starlist:
            star.draw()

        for moon in moonlist:
            moon.draw(moonlist, alienlist, tanklist)

        # Draws start here =======
        if not game_start:
            roll_comet = random.randint(1,600)
            for shooting_star in shootingstarlist:
                shooting_star.draw(shootingstarlist)
            if roll_comet < 100:
                shooting_star = Shooting_star(cometlist)
                shootingstarlist.append(shooting_star)

        for fire in firelist:
            fire.draw(firelist)

        if not game_start:
            for letter in bannerlist:
                letter.draw()
        else:
            for letter in bannerlist2:
                letter.draw()

        if game_start:
            for alien in alienlist:
                alien.draw(alienlist, poweruplist)
        else:
            alienlist = []

        for bullet in bulletlist: # fix
            bullet.draw(bulletlist)

        for bullet in alienbulletlist:
            bullet.draw(alienbulletlist)


        for explosion in explosionlist:
            explosion.draw(explosionlist)

        if tank_start:
            for tank in tanklist:
                if loose_life_timer == global_timer: # only show tank when active game
                    tank.draw(tanklist)

        for powerup in poweruplist:
            powerup.draw(poweruplist)

        # Collision checks
        for moon in moonlist:
            for bullet in bulletlist:
                if moon.moon_hitbox.colliderect(bullet.bullet_hitbox):
                    moon.hit = True
                    bullet.hit = True

        for alien in alienlist:
            for bullet in bulletlist:
                if alien.alien_hitbox.colliderect(bullet.bullet_hitbox):
                    alien.hit = True
                    bullet.hit = True
            if alien.alien_hitbox.colliderect(tank.tank_hitbox):
                alien.hp = 0
                tank.hp = 0

        for bullet in alienbulletlist:
            if tank.tank_hitbox.colliderect(bullet.bullet_hitbox):
                tank.hit = True
                bullet.hit = True

        for bullet in bulletlist:
            for alienbullet in alienbulletlist:
                if bullet.bullet_hitbox.colliderect(alienbullet.bullet_hitbox):
                    alienbullet.hit = True
                    bullet.hit = True

        for powerup in poweruplist:
            if tank.tank_hitbox.colliderect(powerup.powerup_hitbox):
                powerup.hit = True

        # --- Draw Input Boxes ---
        if  not game_start:
            for key, rect in input_boxes.items():
                pygame.draw.rect(screen, WHITE if active_box == key else (200, 200, 200), rect, 2)
                if key == "password" and not show_password:
                    txt = "*" * len(user_input[key])
                else:
                    txt = user_input[key]
                draw_text(txt, rect.x + 8, rect.y + 10, 30, WHITE) # USER INPUT TEXT

                # Draw cursor
                if active_box == key and cursor_visible:
                    cursor_x = rect.x + 5 + screen_font.size(txt)[0]
                    pygame.draw.line(screen, WHITE, (cursor_x, rect.y + 8), (cursor_x, rect.y + 32), 2)



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                login_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    login_running = False


            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for moon in moonlist:
                    moon_hitbox = pygame.Rect(0, 0, moon.size * 2 - 2, moon.size * 2 - 2)
                    moon_hitbox.center = (moon.x, moon.y)
                    if moon_hitbox.collidepoint(mouse_pos):
                        moon.clicked += 1

            if event.type == pygame.MOUSEBUTTONDOWN and not game_start:
                # Check input focus
                active_box = None
                for key, rect in input_boxes.items():
                    if rect.collidepoint(event.pos):
                        active_box = key
                # Check buttons
                if login_btn.collidepoint(event.pos):
                    check_login(user_input["username"], user_input["password"]) # stored in dict at top
                if sqli_btn.collidepoint(event.pos):
                    sqli_protection = not sqli_protection
                if show_pwd_btn.collidepoint(event.pos):
                    show_password = not show_password

            if event.type == pygame.KEYDOWN and active_box and not game_start:
                if event.key == pygame.K_RETURN:
                    if active_box == "username":
                        active_box = "password"
                    else:
                        check_login(user_input["username"], user_input["password"])
                elif event.key == pygame.K_BACKSPACE:
                    user_input[active_box] = user_input[active_box][:-1]
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    try:
                        clip_text = pyperclip.paste()
                        user_input[active_box] += clip_text
                    except:
                        pass
                else:
                    user_input[active_box] += event.unicode
        if tanklist:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                tanklist[0].x -= tanklist[0].speed
            if keys[pygame.K_d]:
                tanklist[0].x += tanklist[0].speed
            if keys[pygame.K_SPACE]:
                tanklist[0].shooting = True
                can_shoot = True
            else:
                tanklist[0].shooting = False
        # --- Draw Labels ---
        if not game_start:
            draw_text('USERNAME:', center_x - 60, CAMERA_HEIGHT // 2 - 120, 30, WHITE) #adjust x and y of text for user and password
            draw_text('PASSWORD:', center_x - 60, CAMERA_HEIGHT // 2 - 30, 30, WHITE)
            #draw_text("Please Enter Username and Password", center_x - 80, CAMERA_HEIGHT // 2 + 48, 30, WHITE)
        # --- Draw Buttons with Hover Effect ---
            toggle_text = "    PROTECT OFF" if sqli_protection else "    PROTECT ON"

            # Buttons
            draw_button(login_btn, "   LOGIN", mouse_pos)
            draw_button(sqli_btn, toggle_text, mouse_pos)
            draw_button(show_pwd_btn, "     SHOW PASS" if not show_password else "     HIDE PASS", mouse_pos)

            # --- Blink Cursor ---
            cursor_timer += clock.get_time()
            if cursor_timer >= 500:
                cursor_visible = not cursor_visible
                cursor_timer = 0


        
        if game_start and tanklist:
            draw_text(f'HEALTH: {tank.hp} / {tank.max_hp}', 2, 5, 35, WHITE)
            draw_text(f' LIVES: {lives}', 330, 5, 35, WHITE)

            draw_text(f'     SCORE:{score}', 482, 5, 35, WHITE) 
            draw_text(f'HIGH SCORE: {high_score}', 690, 5, 35, WHITE) 
            draw_text(f'DAMAGE: {tank_damage} LEVEL: {level} GUN DELAY: {shoot_speed}    {tanklist[0].shooting_timer}', 5, CAMERA_HEIGHT - 20, 30, WHITE) 

            

            if score > high_score:
                high_score = score
        else:
            draw_text("© 2025 AndySoft. All rights reserved. Pre-Alpha 0.1", 330, CAMERA_HEIGHT - 15, 18, WHITE)
        if not tanklist and tank_start:
            alienbulletlist = [] #empty lists
            alienlist = []
            
            if lives < 1:
                game_over_timer -= 1
                draw_text(f'              GAME OVER \nSEE YOU SPACE COWBOY...', CAMERA_WIDTH / 2 - 230, 290, 50, WHITE)
                if game_over_timer == 0:
                    # with open(high_score_path, 'w') as f:
                    #     f.write(str(high_score))
                    tank_start = False
                    game_start = False
                    lives = 3 # reset lives for next play
                    alien_level = 1
                    alien_damage = 10
                    score = 0
                    game_over_timer = global_timer

            else:
            
                if loose_life_timer > 1 and lives >= 1: #show this for a few seconds
                    loose_life_timer -= 1 # minus till zero than do resets
                    if lives == 1:
                        draw_text(f'{lives} LIFE REMAINING', CAMERA_WIDTH / 2 - 190, 300, 50, WHITE)
                    else:
                        draw_text(f'{lives} LIVES REMAINING', CAMERA_WIDTH / 2 - 188, 300, 50, WHITE)
                else:
                    print("new tank after loose life")
                    loose_life_timer = global_timer # reset timer
                    new_tank = Tank(level)
                    new_alien = Alien()
                    alienlist.append(new_alien)
                    tanklist.append(new_tank)


        game_fps = int(clock.get_fps())
        pygame.display.set_caption(f"Andy RPG! - FPS: {game_fps}")
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
login_loop()
