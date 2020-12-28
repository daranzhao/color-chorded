from kivy.graphics.instructions import InstructionGroup
from kivy.uix.stencilview import StencilView
from kivy.uix.image import Image


shape_dict = {'circle': 0,'square':1,'triangle':2}

class Seaweed(InstructionGroup):
    def __init__(self, shape, screen, scrn_l, scrn_r, wave_height, zen):
        super(Seaweed, self).__init__()
        self.level = 0
        self.progress = 0
        self.min_progress = 0
        self.max_progress = 10
        self.max_level = 2
        self.zen = zen

        self.x = (scrn_r*0.8)/3 * (shape_dict[shape]) + scrn_l + 0.05
        self.y = wave_height/2 

        src = "../assets/seaweed" + str(self.level) + ".png"
        self.bg = Image(source=src, allow_stretch=True)
        screen.add_widget(self.bg)

        src = "../assets/progress" + str(self.level) + ".png"

        self.stencil = StencilView()
        with self.stencil.canvas:
            self.fill = Image(source=src, allow_stretch=True)
        
        screen.add_widget(self.stencil)

        src = "../assets/" + shape + "rock.png"
        self.rock = Image(source=src,allow_stretch=True)
        screen.add_widget(self.rock)

    def update_progress(self, change):
        self.progress += change
        if self.progress >= self.max_progress:
            if self.level<self.max_level: 
                self.level += 1
                self.change_level(self.level)
                self.progress -= self.max_progress
            else:
                self.progress = self.max_progress
        elif self.progress < self.min_progress:
            self.progress = self.min_progress
            '''
            if self.level == 0:
                self.progress = self.min_progress
            else:
                self.level -= 1
                self.progress += self.max_progress
                self.change_level(self.level)
            '''

    def change_level(self, level):
        bg_src = "../assets/seaweed" + str(level) + ".png"
        self.bg.source = bg_src 

        fill_src = "../assets/progress" + str(level) + ".png"
        self.fill.source = fill_src

        
    def on_layout(self,win_size):
        w,h = win_size
        self.size = (w * 0.1,h * 0.49)
        self.pos = (self.x*w-self.size[0]/2,h*self.y-self.size[1]/2)
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.fill.size = self.size
        self.fill.pos = self.pos

        self.stencil.pos = self.pos
        self.stencil.size = (self.size[0],self.size[1]*self.progress/self.max_progress)

        self.rock_size = (w*0.035,w*0.035)
        self.rock_pos = (self.pos[0]+w*0.034, self.pos[1]+0.01*h)
        self.rock.size = self.rock_size
        self.rock.pos = self.rock_pos

    def on_update(self):
        self.stencil.size = (self.size[0],self.size[1]*self.progress/self.max_progress)
        if not self.zen:
            self.update_progress(-0.0025)