from common.gfxutil import KFAnim

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line
from kivy.uix.image import Image
from kivy.clock import Clock as kivyClock

import random

ROOT_COLOR_INFO = [
    ("red", 72), #C
    ("orange", 76), #E
    ("green", 79), #G
    ("purple", 81) #A
    #("blue", 83) #B
]

ROOT_PITCH_INFO = {
    'red': [72, 76, 79, 84, 79, 76],
    'orange': [76, 79, 83, 88, 83, 79],
    'green': [79, 83, 86, 91, 86, 83],
    'purple': [81, 84, 88, 93, 88, 84]
}

class Dot(InstructionGroup):
    def __init__(self, rad, x, y, size, screen, gridlen, xshift, yshift):
        super(Dot, self).__init__()

        self.rad = rad
        self.grid_len = gridlen
        self.x_shift = xshift
        self.y_shift = yshift

        self.shape = random.sample((['circle','square','triangle']),1)[0]
        self.screen = screen

        self.x, self.y, self.size = x, y, size
        x = self.grid_len/(self.size + 1) * (1 + self.x) + self.x_shift
        y = self.grid_len/(self.size + 1) * (1 + self.y) + self.y_shift
        
        self.color, self.pitch = random.choice(ROOT_COLOR_INFO)

        src = "../assets/" + self.shape + self.color + ".png"
        self.center = x, y
        self.pos = (x-self.rad,y-self.rad)
        self.img = Image(source=src, size=(self.rad,self.rad), pos=self.pos,allow_stretch=True)

        screen.add_widget(self.img)

        self.selected = False
        self.pop = False
        self.move = False

    def set_selected(self, bool):
        self.selected = bool

    def set_chord_pitch(self, pos):
        self.pitch = ROOT_PITCH_INFO.get(self.color)[pos % 6]

    def on_layout(self, grid_len, x_shift):
        self.grid_len = grid_len
        self.x_shift = x_shift
        x = self.grid_len/(self.size + 1) * (1 + self.x) + self.x_shift
        y = self.grid_len/(self.size + 1) * (1 + self.y) + self.y_shift
        self.center = x,y
        self.pos = x-self.rad/2, y-self.rad/2
        self.img.pos = self.pos

    def pop_anim(self):
        self.time = 0
        self.radius_anim = KFAnim((0, self.rad+8), (0.4, self.rad+14))
        self.alpha_anim = KFAnim((0, 1), (0.4, 0))
        self.pop = True
        self.on_update()

    def get_pos(self):
        return self.x, self.y

    def move_anim(self, y):
        self.y = y
        x = self.grid_len/(self.size + 1) * (1 + self.x) + self.x_shift
        y = self.grid_len/(self.size + 1) * (1 + self.y) + self.y_shift
        
        self.pos_anim = KFAnim((0, self.pos[1]), (0.4, y-self.rad/2))
        self.move = True
        self.time = 0 
        self.on_update()
        
        self.center = x,y
        self.pos = x-self.rad/2, y-self.rad/2
    
    def on_update(self):
        x = self.grid_len/(self.size + 1) * (1 + self.x) + self.x_shift
        y = self.grid_len/(self.size + 1) * (1 + self.y) + self.y_shift

        if self.selected:
            self.img.size = (self.rad+8,self.rad+8)
            self.img.pos = x-4-self.rad/2,y-4-self.rad/2
        else:
            self.img.size = (self.rad,self.rad)
            self.img.pos = x-self.rad/2, y-self.rad/2

        if self.pop:
            dt = kivyClock.frametime
            rad = int(self.radius_anim.eval(self.time))
            self.img.size = rad,rad
            self.img.pos = x-rad/2,y-rad/2

            alpha = self.alpha_anim.eval(self.time)
            self.img.color[3] = alpha
            self.time += dt

            if not self.radius_anim.is_active(self.time):
                self.screen.remove_widget(self.img)
        if self.move:
            dt = kivyClock.frametime
            y = int(self.pos_anim.eval(self.time))
            self.img.pos[1] = y
            
            self.time += dt
            if not self.pos_anim.is_active(self.time):
                self.move = False


class ChordLine(InstructionGroup):
    def __init__(self):
        super(ChordLine, self).__init__()
        self.color = Color((1,1,1,0.5))
        self.line = Line(width = 2)

        self.add(self.color)
        self.add(self.line)
    
    def on_update(self,linepoints):
        self.line.points = linepoints