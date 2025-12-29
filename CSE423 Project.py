from pickle import GLOBAL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from OpenGL.GLU import *
from math import*
from random import*
import time as time

fovY = 90  # Field of view
GRID_LENGTH = 1000  # Length of grid lines
game_start = False
game_over=False

types=["chair", "table", "lamp"]
props={"chair":[], "table":[], "lamp":[]}
prop_type=choice(types)

last_time = time.time()
camera_pos = (0,GRID_LENGTH-200 , GRID_LENGTH-200)
player_pos = (0, 0, 0)
player_angle=0

speed=30
first_person = False
t=0
t1=0
normal=(0,0,1)
look=(0,0,0)

width, height = 1280, 720
ASPECT = width/height
screen_w, screen_h = width, height

STATE_SPLASH, STATE_MENU, STATE_DIFF, STATE_GAME = 0,1,2,3
state = STATE_SPLASH
splash_start = None

DIFFS = {"Easy":5.0, "Medium":10.0, "Hard":20.0}
difficulty = "Easy"

MATCH_DURATION = 120.0
game_start_time = None
round_over = False
winner_text = ""
winner_printed = False
time_frozen_at = None

BASE_SPEED = 18.0
MOVE_SPEED = BASE_SPEED
TURN_DEG = 6.0
cam_theta = 0.0
cam_radius = GRID_LENGTH - 0
cam_height = GRID_LENGTH - 0
CAM_RADIUS_MIN = 400.0
CAM_RADIUS_MAX = GRID_LENGTH * 1.2

DASH_MULT = 2.0
DASH_DUR  = 2.0
CD_E = 6.0
CD_F = 3.0
CD_Q = 20.0

dash_active = False
dash_until  = 0.0
e_ready_at  = 0.0

f_ready_at  = 0.0
catch_radius = 200.0

q_ready_at  = 0.0
ping_radius = 500.0     
prop_reveal_until = 0.0 
INVIS_DURATION  = 3.0   
INVIS_COOLDOWN  = 12.0



DEEP_NAVY    = (0.0, 0.0, 0.4)
CHARCOAL     = (0.1, 0.1, 0.1)
FOREST_GREEN = (0.0, 0.3, 0.0)


def initialize():
    global game_start, game_over, camera_pos, player_pos
    global player_angle, first_person, t, t1, normal, look
    seed(time.time())
    game_start = False
    game_over=False
    camera_pos = (0,GRID_LENGTH-200,GRID_LENGTH-200)
    player_pos = (0, 0, 0)
    player_angle=0

    first_person = False
    t=0
    t1=0
    normal=(0,0,1)
    look=(0,0,0)
    Prop.props={"chair":[], "table":[], "lamp":[]}
    Prop.generate_prop()

class Prop:
    global prop_type, INVIS_DURATION, INVIS_COOLDOWN
    button=None
    types=["chair", "table", "lamp"]
    props={"chair":[], "table":[], "lamp":[]}
    prop_player_type=prop_type
    player=None
    invisible_cd=(False, time.time())
    swap_cd=time.time()
    decoy= (False,time.time())
    shield=True
    hp=3
    angle=0
    NEIGHBORHOOD = [(dx, dy) 
                for dx in range(-45, 46)
                for dy in range(-45, 46)]
    all = {(x, y) for x in range(-GRID_LENGTH+50, GRID_LENGTH-50+1)
                        for y in range(-GRID_LENGTH+50, GRID_LENGTH-50+1)}
    available=all

    def __init__(self, t="chair", p=(0,0,0),q=False):
        self.type=t
        self.pos=p
        self.player=q
        self.angle=randint(0,359)

    @classmethod
    def generate_prop(cls):
        all=cls.all
        NEIGHBORHOOD=cls.NEIGHBORHOOD
        global player_pos, GRID_LENGTH
        x1, y1, z1 = [int(i) for i in player_pos]
        exclude = {(x, y) for x in range(x1-45, x1+46) for y in range(y1-45, y1+46)}

        for x, y, z in [prp.pos for prp in cls.props["chair"] + cls.props["table"] + cls.props["lamp"]]:
            for xi in range(int(x-45), int(x+45)+1):
                for yi in range(int(y-45), int(y+45)+1):
                    exclude.add((xi, yi))
        cls.available = set(all - exclude)

        for t in cls.types:
            max_count = 10
            while len(cls.props[t]) < max_count and len(cls.available)>0:
                pos = choice(list(cls.available))
                temp = (*pos, 0)
                cls.props[t].append(cls(t, temp))
                for dx, dy in NEIGHBORHOOD:
                    cls.available.discard((pos[0] + dx, pos[1] + dy))
        cls.player=cls.props[cls.prop_player_type][-1]
        cls.player.player=True

    @classmethod
    def swap(cls):
        now=time.time()
        if now-cls.swap_cd<8:
            return
        temp=choice(cls.props[cls.prop_player_type][:-2])
        temp.pos,cls.player.pos= cls.player.pos, temp.pos
        cls.swap_cd=now


    @staticmethod
    def _begin_color(highlight, r,g,b):
        if not highlight:
            glColor3f(r,g,b)

    @classmethod
    def draw_chair(cls,pos, player=False, highlight=False):
        k=45
        t=0 if player==False else cls.angle

        # single base color if highlight
        if highlight: 
            glColor3f(1.0, 0.0, 0.0)

        # pointer
        glPushMatrix()
        cls._begin_color(highlight, 0,0,1)
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glTranslatef(0,0,80) 
        glRotatef(90,1,0,0)
        gluCylinder(gluNewQuadric(), 10, 1, 70, 10, 10)
        glPopMatrix()

        # four legs
        for mul in (1,3,7,5):
            glPushMatrix()
            cls._begin_color(highlight, 193/255, 154/255, 107/255)
            glTranslatef(*pos) 
            glRotatef(t,0,0,1)
            glTranslatef(45*cos(2*pi*0.125*mul+t),45*sin(2*pi*0.125*mul+t),0)
            gluCylinder(gluNewQuadric(), 10, 10, 80, 10, 10)
            glPopMatrix()

        # seat
        glPushMatrix()
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glBegin(GL_QUADS)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        glVertex3f(45*cos(2*pi*0.125*5+t),45*sin(2*pi*0.125*5+t),80)
        glVertex3f(45*cos(2*pi*0.125*7+t),45*sin(2*pi*0.125*7+t),80)
        glVertex3f(45*cos(2*pi*0.125+t),  45*sin(2*pi*0.125+t),80)
        glVertex3f(45*cos(2*pi*0.125*3+t),45*sin(2*pi*0.125*3+t),80)
        glEnd()
        glPopMatrix()

        # back legs
        for mul in (7,5):
            glPushMatrix()
            cls._begin_color(highlight, 193/255, 154/255, 107/255)
            glTranslatef(*pos) 
            glRotatef(t,0,0,1)
            glTranslatef(45*cos(2*pi*0.125*mul+t),45*sin(2*pi*0.125*mul+t),80)
            gluCylinder(gluNewQuadric(), 10, 10, 80, 10, 10)
            glPopMatrix()

        # lean
        glPushMatrix()
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glBegin(GL_QUADS)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        glVertex3f(45*cos(2*pi*0.125*5+t),45*sin(2*pi*0.125*5+t),115)
        glVertex3f(45*cos(2*pi*0.125*7+t),45*sin(2*pi*0.125*7+t),115)
        glVertex3f(45*cos(2*pi*0.125*7+t),45*sin(2*pi*0.125*7+t),140)
        glVertex3f(45*cos(2*pi*0.125*5+t),45*sin(2*pi*0.125*5+t),140)
        glEnd()
        glPopMatrix()

    @classmethod
    def draw_table(cls,pos, player=False, highlight=False):
        k=45
        t=0 if player==False else cls.angle
        if highlight: 
            glColor3f(1.0, 0.0, 0.0)

        # pointer
        glPushMatrix()
        cls._begin_color(highlight, 0,0,1)
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glTranslatef(0,0,80) 
        glRotatef(90,1,0,0)
        gluCylinder(gluNewQuadric(), 10, 1, 70, 10, 10)
        glPopMatrix()

        # legs
        for mul in (1,3,7,5):
            glPushMatrix()
            cls._begin_color(highlight, 193/255, 154/255, 107/255)
            glTranslatef(*pos) 
            glRotatef(t,0,0,1)
            glTranslatef(k*cos(2*pi*0.125*mul+t),k*sin(2*pi*0.125*mul+t),0)
            gluCylinder(gluNewQuadric(), 10, 10, 80, 10, 10)
            glPopMatrix()

        # top
        glPushMatrix()
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glBegin(GL_QUADS)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        K=55
        glVertex3f(K*cos(2*pi*0.125*5+t),K*sin(2*pi*0.125*5+t),80)
        glVertex3f(K*cos(2*pi*0.125*7+t),K*sin(2*pi*0.125*7+t),80)
        glVertex3f(K*cos(2*pi*0.125+t),  K*sin(2*pi*0.125+t),80)
        glVertex3f(K*cos(2*pi*0.125*3+t),K*sin(2*pi*0.125*3+t),80)
        glEnd()
        glPopMatrix()

    @classmethod
    def draw_lamp(cls,pos, player=False, highlight=False):
        t=0 if player==False else cls.angle
        if highlight: 
            glColor3f(1.0, 0.0, 0.0)

        # pointer
        glPushMatrix()
        cls._begin_color(highlight, 0,0,1)
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glTranslatef(0,0,70) 
        glRotatef(90,1,0,0)
        gluCylinder(gluNewQuadric(), 10, 1, 70, 10, 10)
        glPopMatrix()

        # stand
        glPushMatrix()
        cls._begin_color(highlight, 193/255, 154/255, 107/255)
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        gluCylinder(gluNewQuadric(), 10, 10, 70, 10, 10)
        glPopMatrix()

        # head
        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(t,0,0,1)
        glTranslatef(0,0,50)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        gluCylinder(gluNewQuadric(), 30, 20, 20, 10, 10)
        glPopMatrix()


        glPushMatrix()
        glTranslatef(*pos) 
        glRotatef(t,0,0,1)
        glBegin(GL_QUADS)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        glVertex3f(20*cos(pi/4),20*sin(pi/4),70)
        glVertex3f(20*cos(pi/4),20*sin(pi/4),70)
        glVertex3f(20*cos(pi/4),20*sin(pi/4),70)
        glVertex3f(20*cos(pi/4),20*sin(pi/4),70)
        glEnd()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(*pos)
        glRotatef(t,0,0,1)
        glBegin(GL_QUADS)
        cls._begin_color(highlight, 101/255, 67/255, 33/255)
        glVertex3f(30*cos(pi/4),30*sin(pi/4),0)
        glVertex3f(30*cos(pi/4),30*sin(pi/4),0)
        glVertex3f(30*cos(pi/4),30*sin(pi/4),0)
        glVertex3f(30*cos(pi/4),30*sin(pi/4),0)
        glEnd()
        glPopMatrix()

    @classmethod
    def draw_prop(cls):
        now=time.time()
        for t in cls.types:
            for prp in cls.props[t]:
                if prp.player:
                    if cls.invisible_cd[0]:
                        elapsed = now - cls.invisible_cd[1]
                        if elapsed < INVIS_DURATION:
                            continue
                        else:
                            cls.invisible_cd = (False, cls.invisible_cd[1])

                highlight = False
                if prp.player and now < prop_reveal_until:
                    highlight = True

                if t=="chair":
                    cls.draw_chair(prp.pos,prp.player,highlight)
                elif t=="table":
                    cls.draw_table(prp.pos,prp.player,highlight)
                else:
                    cls.draw_lamp(prp.pos,prp.player,highlight)

    @classmethod
    def mouse(cls,button, state, x, y):
        global GRID_LENGTH
        player= cls.player
        new_player_pos = cls.player.pos
        T=radians(cls.angle)
        speed=30
        dx= speed * -cos(T+pi/2)
        dy= speed * -sin(T+pi/2)

        if state == GLUT_DOWN:
            if button == GLUT_LEFT_BUTTON:
                cls.swap()
            elif button == GLUT_MIDDLE_BUTTON:
                now = time.time()
                if (not cls.invisible_cd[0]) and (now - cls.invisible_cd[1] >= INVIS_COOLDOWN):
                    cls.invisible_cd=(True, time.time())
            elif button == GLUT_RIGHT_BUTTON:
                cls.decoy_go()
            elif button == 3:  # scroll up
                now=time.time()
                cls.button="scroll up"
                if (not cls.decoy[0]) or now-cls.decoy[1]>3:
                    new_player_pos = ((player.pos[0] + dx), 
                            (player.pos[1] + dy),
                            player.pos[2])
                    if (new_player_pos[0]>GRID_LENGTH or new_player_pos[0]<-GRID_LENGTH
                        or new_player_pos[1]>GRID_LENGTH or new_player_pos[1]<-GRID_LENGTH):
                        player.pos=(-player.pos[0],-player.pos[1],player.pos[2])
                    else:
                        player.pos=new_player_pos
                else:
                    temp=cls.props["chair"]+cls.props["table"]+cls.props["lamp"]
                    for prp in temp:
                        new_pos = ((prp.pos[0] + dx), 
                            (prp.pos[1] + dy),
                            prp.pos[2])
                        if (new_pos[0]>GRID_LENGTH or new_pos[0]<-GRID_LENGTH
                            or new_pos[1]>GRID_LENGTH or new_pos[1]<-GRID_LENGTH):
                            prp.pos=(-prp.pos[0],-prp.pos[1],prp.pos[2])
                        else:
                            prp.pos=new_pos
                    if now-cls.decoy[1]>3:
                        cls.decoy= (False,now)
            elif button == 4:  # scroll down
                cls.button="scroll down"
                cls.angle = (cls.angle + 20) % 360

    @classmethod
    def decoy_go(cls):
        now=time.time()
        if now-cls.decoy[1]<20: #cooldown
            return
        cls.decoy=(True, now)

# def get_boundary(x0, y0, angle, grid):
#     m = tan(radians(angle)+pi/2)
#     if 45<=angle<=135:
#         x = grid
#         y = m * (x - x0) + y0
#     elif 225<=angle<=315:
#         x = -grid
#         y = m * (x - x0) + y0
#     elif 135<angle<225:
#         y = grid
#         if abs(m) > 1e-9:
#             x = (y - y0)/m + x0
#         else:
#             x=0
#     else:
#         y = -grid
#         if abs(m) > 1e-9:
#             x = (y - y0)/m + x0
#         else:
#             x=0
#     return (x,y)


# def specialKeyListener(key, x, y):
#     global camera_pos, t, t1, normal, look, GRID_LENGTH, first_person
#     if first_person:
#         return
#     if key == GLUT_KEY_LEFT:  t += 0.1 
#     if key == GLUT_KEY_RIGHT: t -= 0.1 
#     L = GRID_LENGTH-200
#     camera_pos = (L*sin(t), L*cos(t), L)

def mouseListener(button, state, x, y):
    Prop.mouse(button,state,x,y)

# def setupCamera():
#     global camera_pos, fovY, normal,look
#     glMatrixMode(GL_PROJECTION); glLoadIdentity()
#     gluPerspective(fovY, screen_w / screen_h, 0.1, 2500)
#     glMatrixMode(GL_MODELVIEW); glLoadIdentity()
#     x, y, z = camera_pos; x2,y2,z2=look
#     gluLookAt(x, y, z,  x2,y2,z2,  0, 0, 1)





def move_dir(angle_deg):
    rad = radians(angle_deg)
    return sin(rad), -cos(rad)



def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    line_y = y
    for line in text.split("\n"):
        glRasterPos2f(x, line_y)
        for ch in line:
            glutBitmapCharacter(font, ord(ch))
        line_y -= 22
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_fullscreen_quad(r,g,b):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,width,0,height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(r,g,b)
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(width,0)
    glVertex2f(width,height)
    glVertex2f(0,height)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_tricolor_bg():
    third = width // 3
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,width,0,height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(*DEEP_NAVY)
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(third,0)
    glVertex2f(third,height)
    glVertex2f(0,height)
    glEnd()
    glColor3f(*CHARCOAL)
    glBegin(GL_QUADS)
    glVertex2f(third,0)
    glVertex2f(2*third,0)
    glVertex2f(2*third,height)
    glVertex2f(third,height)
    glEnd()
    glColor3f(*FOREST_GREEN)
    glBegin(GL_QUADS)
    glVertex2f(2*third,0)
    glVertex2f(width,0)
    glVertex2f(width,height)
    glVertex2f(2*third,height)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_splash():
    draw_tricolor_bg()
    draw_text(width//2 - 70, height//2 - 10, "Chameleon Chase 3D")

# Menus
BTN_W, BTN_H = 360, 64
def rect_center(xc, yc, w, h): 
    return (xc-w/2, yc-h/2, xc+w/2, yc+h/2)
def inside_rect(px,py,rc):
    x1,y1,x2,y2=rc
    if x1>x2:
        x1,x2=x2,x1
    if y1>y2:
        y1,y2=y2,y1
    return x1<=px<=x2 and y1<=py<=y2

menu_btns = {"start":None, "exit":None}
def layout_menu():
    cx, cy = width*0.5, height*0.58
    gap=22
    menu_btns["start"] = rect_center(cx, cy, BTN_W, BTN_H)
    menu_btns["exit"]  = rect_center(cx, cy-(BTN_H+gap), BTN_W, BTN_H)

def draw_button(rc, label):
    x1,y1,x2,y2 = rc
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,width,0,height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(0.15,0.15,0.15)
    glBegin(GL_QUADS)
    glVertex2f(x1,y1)
    glVertex2f(x2,y1)
    glVertex2f(x2,y2)
    glVertex2f(x1,y2)
    glEnd()
    glColor3f(0.6,0.6,0.6)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x1,y1)
    glVertex2f(x2,y1)
    glVertex2f(x2,y2)
    glVertex2f(x1,y2)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    draw_text((x1+x2)/2-60, (y1+y2)/2-9, label)

def draw_menu():
    draw_fullscreen_quad(0,0,0)
    draw_text(width*0.5 - 80, height*0.70, "Chameleon Chase 3D")
    layout_menu()
    draw_button(menu_btns["start"], "Start Game")
    draw_button(menu_btns["exit"],  "Exit")

diff_btns = {}
def layout_diff():
    cx, cy = width*0.5, height*0.65
    gap=16
    ys=[cy, cy-(BTN_H+gap), cy-2*(BTN_H+gap)]
    for lab,y in zip(["Easy","Medium","Hard"], ys):
        diff_btns[lab]=rect_center(cx,y,BTN_W,BTN_H)

def draw_diff():
    draw_fullscreen_quad(0,0,0)
    draw_text(width*0.5 - 60, height*0.80, "Select Difficulty")
    layout_diff()
    for lab,rc in diff_btns.items():
        draw_button(rc, lab)

def update_camera():
    global camera_pos
    x = cam_radius * sin(cam_theta)
    y = cam_radius * cos(cam_theta)
    z = cam_height
    camera_pos = (x,y,z)

def setup_camera_game():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, ASPECT, 0.1, 5000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x,y,z = camera_pos
    gluLookAt(x,y,z,  0,0,0,  0,0,1)

# Dynamic walls
WALL_THICK = 6.0
def make_h_wall(y, x1, x2, z0=0, z1=120): 
    return {'o':'h','y':y,'x1':x1,'x2':x2,'z0':z0,'z1':z1}
def make_v_wall(x, y1, y2, z0=0, z1=120): 
    return {'o':'v','x':x,'y1':y1,'y2':y2,'z0':z0,'z1':z1}

# Wave A (20s)
waveA = [
    make_h_wall(   0, -400,  400),
    make_v_wall(   0, -400,  400),
    make_h_wall(-250, -700, -250),
    make_h_wall( 250,  250,  700),
    make_v_wall(-250, -700, -250),
    make_v_wall( 250,  250,  700),
]

# Wave B (80s)
waveB = [
    make_h_wall(-500, -850, -150),
    make_h_wall( 500,  150,  850),
    make_v_wall(-600, -850, -100),
    make_v_wall( 600,  100,  850),
    make_h_wall(   150, -900, -300),
    make_h_wall(  -150,  300,  900),
]

WAVE1_START = 20.0
WAVE2_START = 80.0
def dyn_durations(): 
    return DIFFS[difficulty]
def dyn_active(now_s):
    dur = dyn_durations()
    a = (WAVE1_START <= now_s < WAVE1_START + dur)
    b = (WAVE2_START <= now_s < WAVE2_START + dur)
    return a,b
def active_dyn_walls(now_s):
    a,b = dyn_active(now_s)
    walls = []
    if a: 
        walls += waveA
    if b: 
        walls += waveB
    return walls

# Floor + boundary + effects
FLOOR_A = (1.0,1.0,1.0)
FLOOR_B = (0.7,0.5,0.95)
BOUND_COLS = [(0.9,0.2,0.2),(0.2,0.9,0.2),(0.2,0.6,1.0),(0.9,0.7,0.2)]
def effect_active(now_s): 
    return 60.0 <= now_s < 60.0 + DIFFS[difficulty]
def effect_phase(now_s):  
    return int((now_s-60.0)*10.0)

def draw_floor(now_s):
    swap = effect_active(now_s) and (effect_phase(now_s) % 2 == 0)
    cA = FLOOR_B if swap else FLOOR_A
    cB = FLOOR_A if swap else FLOOR_B
    step=100
    for i in range(-GRID_LENGTH, GRID_LENGTH, step):
        flip = ((i // step) & 1) == 0
        for j in range(-GRID_LENGTH, GRID_LENGTH, step):
            glColor3f(*(cA if flip else cB))
            glBegin(GL_QUADS)
            glVertex3f(i,j,0)
            glVertex3f(i+step,j,0)
            glVertex3f(i+step,j+step,0)
            glVertex3f(i,j+step,0)
            glEnd()
            flip = not flip

def rotate_cols(cols,k): 
    k%=len(cols)
    return cols[-k:]+cols[:-k]
def draw_boundary(now_s):
    cols = BOUND_COLS
    if effect_active(now_s):
        cols = rotate_cols(cols[:], effect_phase(now_s))
    glColor3f(*cols[0]); glBegin(GL_QUADS)
    glVertex3f( GRID_LENGTH, GRID_LENGTH,0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH,0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH,120)
    glVertex3f( GRID_LENGTH, GRID_LENGTH,120)
    glEnd()
    glColor3f(*cols[1])
    glBegin(GL_QUADS)
    glVertex3f( GRID_LENGTH,-GRID_LENGTH,0)
    glVertex3f( GRID_LENGTH, GRID_LENGTH,0)
    glVertex3f( GRID_LENGTH, GRID_LENGTH,120)
    glVertex3f( GRID_LENGTH,-GRID_LENGTH,120)
    glEnd()
    glColor3f(*cols[2])
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH,-GRID_LENGTH,0)
    glVertex3f( GRID_LENGTH,-GRID_LENGTH,0)
    glVertex3f( GRID_LENGTH,-GRID_LENGTH,120)
    glVertex3f(-GRID_LENGTH,-GRID_LENGTH,120)
    glEnd()
    glColor3f(*cols[3])
    glBegin(GL_QUADS)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH,0)
    glVertex3f(-GRID_LENGTH,-GRID_LENGTH,0)
    glVertex3f(-GRID_LENGTH,-GRID_LENGTH,120)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH,120)
    glEnd()

def draw_dyn_walls(now_s):
    a_on,b_on = dyn_active(now_s)
    on_col=(0.9,0.3,0.3)
    def draw_w(w):
        glColor3f(*on_col)
        half=WALL_THICK*0.5
        if w['o']=='h':
            y=w['y']
            x1=min(w['x1'],w['x2'])
            x2=max(w['x1'],w['x2'])
            glBegin(GL_QUADS)
            glVertex3f(x1, y-half, w['z0'])
            glVertex3f(x2, y-half, w['z0'])
            glVertex3f(x2, y+half, w['z1'])
            glVertex3f(x1, y+half, w['z1'])
            glEnd()
        else:
            x=w['x']
            y1=min(w['y1'],w['y2'])
            y2=max(w['y1'],w['y2'])
            glBegin(GL_QUADS)
            glVertex3f(x-half, y1, w['z0'])
            glVertex3f(x+half, y1, w['z0'])
            glVertex3f(x+half, y2, w['z1'])
            glVertex3f(x-half, y2, w['z1']); glEnd()
    if a_on:
        for w in waveA: 
            draw_w(w)
    if b_on:
        for w in waveB: 
            draw_w(w)

# Hunter model
def draw_hunter():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    glRotatef(player_angle, 0,0,1)

    quad = gluNewQuadric()
    # legs
    glColor3f(0,0,1)
    glPushMatrix()
    glTranslatef(-10,0,0)
    gluCylinder(quad,3.2,6.0,36,20,20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef( 10,0,0)
    gluCylinder(quad,3.2,6.0,36,20,20)
    glPopMatrix()
    # body
    glColor3f(0.5,0.5,0.0)
    glPushMatrix()
    glTranslatef(0,0,36+30)
    glScalef(40,16,60)
    glutSolidCube(1)
    glPopMatrix()
    # arms
    glColor3f(1.0, 0.8, 0.6)
    glPushMatrix()
    glTranslatef(-26,0,36+40)
    glRotatef(90,1,0,0)
    gluCylinder(quad,5,3,28,20,20)
    glPopMatrix()
    glPushMatrix()
    glTranslatef( 26,0,36+40)
    glRotatef(90,1,0,0)
    gluCylinder(quad,5,3,28,20,20)
    glPopMatrix()
    # head
    glColor3f(0,0,0)
    glPushMatrix()
    glTranslatef(0,0,36+60+12)
    glutSolidSphere(12,20,20)
    glPopMatrix()

    glPopMatrix()

# HUD
def draw_hud(disp_now_s):
    now = time.time()
    rem = max(0, int(MATCH_DURATION - disp_now_s))
    cdE = max(0, int(e_ready_at - time.time()))
    cdF = max(0, int(f_ready_at - time.time()))
    cdQ = max(0, int(q_ready_at - time.time()))
    cdSwap = max(0, int(8 - (now - Prop.swap_cd)))
    cdInv = max(0, int(INVIS_COOLDOWN - (now - Prop.invisible_cd[1])))
    cdDecoy = max(0, int(20 - (now - Prop.decoy[1])))
    draw_text(10, height-24, f"Time: {rem}s  |  Difficulty: {difficulty}")
    draw_text(10, height-48, f"E(dash) CD:{cdE}s  F(catch) CD:{cdF}s  Q(ping) CD:{cdQ}s")
    draw_text(10, height-72, f"Prop - Swap:{cdSwap}s  Invis:{cdInv}s  Decoy:{cdDecoy}s")
    
    # winner banner
    if round_over:
        draw_text(10, height-96, winner_text)

# Collision
PLAYER_RADIUS = 22.0
def clampv(v, lo, hi): 
    return max(lo, min(hi, v))
def clamp_to_arena(nx, ny):
    lim = GRID_LENGTH - PLAYER_RADIUS
    return clampv(nx,-lim,lim), clampv(ny,-lim,lim)

def would_cross(px,py,nx,ny,w):
    half = WALL_THICK*0.5
    if w['o']=='h':
        y=w['y']
        x1=min(w['x1'],w['x2'])
        x2=max(w['x1'],w['x2'])
        if (py - y) * (ny - y) < 0:
            tpar = (y - py) / (ny - py)
            xc = px + tpar*(nx-px)
            return (x1 - PLAYER_RADIUS <= xc <= x2 + PLAYER_RADIUS)
        return (x1 - PLAYER_RADIUS <= nx <= x2 + PLAYER_RADIUS) and (y - half - PLAYER_RADIUS <= ny <= y + half + PLAYER_RADIUS)
    else:
        x=w['x']
        y1=min(w['y1'],w['y2'])
        y2=max(w['y1'],w['y2'])
        if (px - x) * (nx - x) < 0:
            tpar = (x - px) / (nx - px)
            yc = py + tpar*(ny-py)
            return (y1 - PLAYER_RADIUS <= yc <= y2 + PLAYER_RADIUS)
        return (y1 - PLAYER_RADIUS <= ny <= y2 + PLAYER_RADIUS) and (x - half - PLAYER_RADIUS <= nx <= x + half + PLAYER_RADIUS)

def try_move_hunter(dx,dy,now_s):
    global player_pos
    px,py,pz = player_pos
    nx,ny = clamp_to_arena(px+dx, py+dy)
    for w in active_dyn_walls(now_s):
        if would_cross(px,py,nx,ny,w):
            tx,ty = clamp_to_arena(px+dx, py)
            blocked_x = any(would_cross(px,py,tx,py,ww) for ww in active_dyn_walls(now_s))
            if not blocked_x:
                player_pos = (tx,py,pz)
                return
            tx,ty = clamp_to_arena(px, py+dy)
            blocked_y = any(would_cross(px,py,px,ty,ww) for ww in active_dyn_walls(now_s))
            if not blocked_y:
                player_pos = (px,ty,pz)
                return
            return
    player_pos = (nx,ny,pz)

# Props vs dyn walls
last_safe = {}
def props_respect_dyn(now_s):
    decoy_on, t0 = Prop.decoy
    if decoy_on and (time.time() - t0) <= 3.0:
        return
    walls = active_dyn_walls(now_s)
    for tname in Prop.types:
        for idx, prp in enumerate(Prop.props[tname]):
            key = (tname, idx)
            pos = prp.pos
            inside = False
            for w in walls:
                if w['o']=='h':
                    y=w['y']
                    x1=min(w['x1'],w['x2'])
                    x2=max(w['x1'],w['x2'])
                    half=WALL_THICK*0.5
                    if (x1-PLAYER_RADIUS<=pos[0]<=x2+PLAYER_RADIUS) and (y-half-PLAYER_RADIUS<=pos[1]<=y+half+PLAYER_RADIUS):
                        inside=True
                        break
                else:
                    x=w['x']
                    y1=min(w['y1'],w['y2'])
                    y2=max(w['y1'],w['y2'])
                    half=WALL_THICK*0.5
                    if (y1-PLAYER_RADIUS<=pos[1]<=y2+PLAYER_RADIUS) and (x-half-PLAYER_RADIUS<=pos[0]<=x+half+PLAYER_RADIUS):
                        inside=True
                        break
            if inside:
                if key in last_safe:
                    prp.pos = (last_safe[key][0], last_safe[key][1], prp.pos[2])
            else:
                last_safe[key]=(pos[0],pos[1])

# Ability helpers
def distance_xy(a,b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def hunter_catch():
    
    global round_over, winner_text, winner_printed, time_frozen_at
    hx,hy,_ = player_pos
    px,py,pz = Prop.player.pos
    if distance_xy((hx,hy),(px,py)) <= catch_radius:
        round_over = True
        winner_text = "Hunter caught the prop! Hunter wins."
        if not winner_printed:
            print("Hunter wins (caught the prop).")
            winner_printed = True
        # freeze HUD timer at this moment
        if game_start_time is not None:
            time_frozen_at = time.time() - game_start_time

def try_ping():
    global prop_reveal_until
    hx,hy,_ = player_pos
    px,py,pz = Prop.player.pos
    if distance_xy((hx,hy),(px,py)) <= ping_radius:
        prop_reveal_until = time.time() + 1.0  # 1s highlight


def display():
    global state, splash_start, round_over, winner_text, MOVE_SPEED, dash_active, winner_printed, time_frozen_at
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glViewport(0,0,width,height)

    if state == STATE_SPLASH:
        if splash_start is None: splash_start = time.time()
        draw_splash()
        if time.time() - splash_start >= 3.0:
            state = STATE_MENU

    elif state == STATE_MENU:
        draw_menu()

    elif state == STATE_DIFF:
        draw_diff()

    elif state == STATE_GAME:
        now_s = time.time() - game_start_time if game_start_time is not None else 0.0
        disp_now_s = time_frozen_at if (round_over and time_frozen_at is not None) else now_s

        update_camera()
        setup_camera_game()
        draw_floor(now_s)
        draw_boundary(now_s)
        draw_dyn_walls(now_s)

        draw_hunter()

        Prop.draw_prop()
        if not round_over:
            props_respect_dyn(now_s)


        draw_hud(disp_now_s)

        if not round_over and now_s >= MATCH_DURATION:
            round_over = True
            winner_text = "Time up! Prop wins."
            if not winner_printed:
                print("Prop wins (time up).")
                winner_printed = True
            time_frozen_at = MATCH_DURATION  # freeze HUD at 0s remaining

    glutSwapBuffers()

def idle():
    global dash_active, MOVE_SPEED
    if dash_active and time.time() >= dash_until:
        dash_active = False
        MOVE_SPEED = BASE_SPEED
    glutPostRedisplay()

def screen_to_ui(mx,my): 
    return mx, (height - my)

def mouse_cb(button, state_btn, x, y):
    global state, difficulty
    if state_btn != GLUT_DOWN:
        return
    ui_x, ui_y = screen_to_ui(x,y)

    if state == STATE_MENU and button == GLUT_LEFT_BUTTON:
        if inside_rect(ui_x,ui_y, menu_btns["start"]):
            state = STATE_DIFF
            return
        if inside_rect(ui_x,ui_y, menu_btns["exit"]):
            glutLeaveMainLoop()
            return

    elif state == STATE_DIFF and button == GLUT_LEFT_BUTTON:
        for lab,rc in diff_btns.items():
            if inside_rect(ui_x,ui_y,rc):
                difficulty = lab
                reset_game()
                state = STATE_GAME
                start_timer()
                return

    elif state == STATE_GAME:
        if round_over:
            return  # freeze prop controls after game end
        mouseListener(button, state_btn, x, y)

def start_timer():
    global game_start_time, winner_printed, time_frozen_at
    game_start_time = time.time()
    winner_printed = False
    time_frozen_at = None

def keyboard_cb(key, x, y):
    global player_pos, player_angle, state
    global dash_active, dash_until, e_ready_at, MOVE_SPEED
    global f_ready_at, q_ready_at, round_over

    if key == b'\x1b':
        state = STATE_MENU
        return

    if key == b'r':
        reset_game()
        start_timer()
        return

    if state != STATE_GAME:
        return

    if round_over:
        return  

    now = time.time()
    now_s = now - game_start_time

    # movement
    if key == b'w':
        dx,dy = move_dir(player_angle)
        try_move_hunter(MOVE_SPEED*dx, MOVE_SPEED*dy, now_s)
    if key == b's':
        dx,dy = move_dir(player_angle)
        try_move_hunter(-MOVE_SPEED*dx, -MOVE_SPEED*dy, now_s)
    if key == b'a':
        player_angle = (player_angle + TURN_DEG) % 360
    if key == b'd':
        player_angle = (player_angle - TURN_DEG) % 360

    # abilities
    if key == b'e':
        if now >= e_ready_at:
            dash_active = True
            MOVE_SPEED = BASE_SPEED * DASH_MULT
            dash_until = now + DASH_DUR
            e_ready_at = now + CD_E
    if key == b'f':
        if now >= f_ready_at:
            hunter_catch()
            f_ready_at = now + CD_F
    if key == b'q':
        if now >= q_ready_at:
            try_ping()
            q_ready_at = now + CD_Q

def special_cb(key, x, y):
    global cam_theta, cam_radius, cam_height
    if state != STATE_GAME or round_over: 
        return
    if key == GLUT_KEY_LEFT:  
        cam_theta += 0.05
    if key == GLUT_KEY_RIGHT: 
        cam_theta -= 0.05
    if key == GLUT_KEY_UP:
        cam_radius = max(CAM_RADIUS_MIN, cam_radius - 30.0)
        cam_height = max(300.0, cam_height - 20.0)
    if key == GLUT_KEY_DOWN:
        cam_radius = min(CAM_RADIUS_MAX, cam_radius + 30.0)
        cam_height = min(GRID_LENGTH*1.2, cam_height + 20.0)

def reset_game():
    global player_pos, player_angle, cam_theta, cam_radius, cam_height
    global dash_active, dash_until, e_ready_at, f_ready_at, q_ready_at, prop_reveal_until
    global MOVE_SPEED, round_over, winner_text, winner_printed, time_frozen_at

    player_pos = (0.0,0.0,0.0)
    player_angle = 0.0
    cam_theta = 0.0
    cam_radius = GRID_LENGTH - 200
    cam_height = GRID_LENGTH - 200
    dash_active = False
    dash_until = 0.0
    e_ready_at = 0.0
    f_ready_at = 0.0
    q_ready_at = 0.0
    prop_reveal_until = 0.0
    MOVE_SPEED = BASE_SPEED
    round_over = False
    winner_text = ""
    winner_printed = False
    time_frozen_at = None
    initialize()


def init_gl():
    glClearColor(0,0,0,1)

def main():
    global screen_w, screen_h, state
    Prop.generate_prop()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    screen_w = width; screen_h = height
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Chameleon Chase 3D")
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMouseFunc(mouse_cb)
    glutKeyboardFunc(keyboard_cb)
    glutSpecialFunc(special_cb)
    init_gl()
    state = STATE_SPLASH
    glutMainLoop()

if __name__ == "__main__":
    main()
