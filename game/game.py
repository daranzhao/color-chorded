
import sys, os
sys.path.insert(0, os.path.abspath('..'))

from common.core import BaseWidget, run
from common.gfxutil import CLabelRect
from common.screen import ScreenManager, Screen

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.clock import Clock as kivyClock

from audiocontroller import AudioController
from dots import Dot, ChordLine
from player import Player
from seaweed import Seaweed

from functools import partial
import random
import itertools

# 5eb1bf, f5ff75, f7ce5b, c1ffd7
GRID_SIZE = 8
DOT_RADIUS = 60
SCREEN_LEFT = 0.6
SCREEN_RIGHT = 1 - SCREEN_LEFT
WAVE_HEIGHT = 0.75

class myScreenManager(ScreenManager):
    volume = 100
    zen = False

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)
        Window.clearcolor = (0.93725, 0.94902, 0.84314, 1)
        self.logo_w = 600
        self.logo_h = 300
        src = '../assets/loading.gif'
        #src = '../assets/logo.png'
        pos = ((Window.width-self.logo_w)/2,(Window.height-self.logo_h)/2)
        self.logo = Image(source=src, size=(self.logo_w,self.logo_h), pos=pos,mipmap=True, anim_loop=1)
        self.add_widget(self.logo)

        self.font_color = Color(0.4902,0.6392,0.6667,1)
        self.canvas.add(self.font_color)
        self.notice = CLabelRect((Window.width/2,150), text="Press Any Key To Continue", font_size=18, font_name="Krungthep")
        self.canvas.add(self.notice)

    def on_layout(self, win_size):
        w, h = win_size
        self.logo.pos = ((w-self.logo_w)/2,(h-self.logo_h)/2)
        self.notice.cpos = (Window.width/2,150)

    def on_key_down(self, keycode, modifiers):
        self.switch_to('menu')


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        Window.clearcolor = (0.93725, 0.94902, 0.84314, 1)

        self.font_color = Color(0.0784313,0.0784313,0.33333,1)
        self.canvas.add(self.font_color)
        self.title = CLabelRect((Window.width/2,Window.height*(3/5)), text="GAME SETTINGS", font_size=26, font_name="Krungthep")
        self.canvas.add(self.title)

        self.font_color = Color(0.0784313,0.0784313,0.33333,1)
        self.canvas.add(self.font_color)
        self.vol = CLabelRect((Window.width/2,Window.height*(8/15)), text="VOLUME", font_size=20, font_name="DIN Alternate Bold")
        self.canvas.add(self.vol)

        self.zen = CLabelRect((Window.width/2-100,Window.height*(7/15)), text="ZEN MODE", font_size=20, font_name="DIN Alternate Bold")
        self.canvas.add(self.zen)

        self.slider = Slider(min=0,max=1000,value=3,cursor_image="../assets/cursor.png",background_horizontal="../assets/slider.png", background_width=300)
        self.slider.size = (300,300)
        self.add_widget(self.slider)
        
        self.toggle = ToggleButton(background_normal="../assets/toggle_off.png",background_down="../assets/toggle_on.png",border=(0, 0, 0, 0))
        self.toggle.size = (180,52)
        self.add_widget(self.toggle)

        self.menu_button = Button(text='<MENU', font_name="DIN Alternate Bold",font_size=50, color=[0,0,58/255,1], background_color=[0,0,0,0])
        self.menu_button.size = (200,100)
        self.menu_button.bind(on_release= lambda x: self.switch_to('menu'))
        self.add_widget(self.menu_button)

    def on_layout(self, win_size):
        w, h = win_size
        self.title.set_cpos((Window.width/2,Window.height*(10/15)))
        self.vol.set_cpos((Window.width/2-150,Window.height*(8/15)))
        self.zen.set_cpos((Window.width/2-130,Window.height*(7/15)))
        self.toggle.pos = (Window.width/2+150-self.toggle.size[0]/2,Window.height*(7/15)-self.toggle.size[1]/2)
        self.slider.pos = ((Window.width/2+120-self.slider.size[0]/2,Window.height*(8/15)-self.slider.size[0]/2))
        self.menu_button.pos = (50, 0.93 * h - self.menu_button.size[1]/2)
    
    def on_exit(self):
        self.manager.volume = self.slider.value
        if self.toggle.state == 'down':
            self.manager.zen = True
        else:
            self.manager.zen = False

class AboutScreen(Screen):
    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)

        self.menu_button = Button(text='<MENU', font_name="DIN Alternate Bold",font_size=50, color=[0,0,58/255,1], background_color=[0,0,0,0])
        self.menu_button.size = (200,100)
        self.menu_button.bind(on_release= lambda x: self.switch_to('menu'))
        self.add_widget(self.menu_button)

        self.about = Image(source="../assets/about_text.png", size=(Window.width*3/4,Window.height*3/4))
        self.add_widget(self.about)

    def on_layout(self, win_size):
        w, h = win_size
        self.menu_button.pos = (50, 0.93 * h - self.menu_button.size[1]/2)
        self.about.size = (Window.width*3/4,Window.height*3/4)
        self.about.pos = (w/2-self.about.size[0]/2,h/2-self.about.size[1]/2)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)

        src = '../assets/logo.png'
        self.logo = Image(source=src, size=(700,350))
        self.add_widget(self.logo)

        self.settings = Button(background_normal='../assets/settings.png', background_down='../assets/settings_down.png',border=(0, 0, 0, 0))
        self.settings.size = (400,400)
        self.settings.bind(on_release= lambda x: self.switch_to('settings'))
        self.add_widget(self.settings)

        self.play = Button(background_normal='../assets/play.png', background_down='../assets/play_down.png',border=(0, 0, 0, 0))
        self.play.size = (550,420)
        self.play.bind(on_release= lambda x: self.switch_to('game'))
        self.add_widget(self.play)

        self.about = Button(background_normal='../assets/about.png', background_down='../assets/about_down.png',border=(0, 0, 0, 0))
        self.about.size = (350,350)
        self.about.bind(on_release= lambda x: self.switch_to('about'))
        self.add_widget(self.about)

    
    def on_layout(self, win_size):
        w, h = win_size

        self.logo.size = (int(w/2.2857),int(h/3.42857))
        self.logo.pos = ((w-self.logo.size[0])/2,(h*6/7-self.logo.size[1]/2))
        
        self.play.size = (int(w/2.90901),int(h/2.857143))
        self.play.pos = ((w*4/7-self.play.size[0]/2),(h*15/28-self.play.size[1]/2))
        
        self.settings.size =  (w/4,h/3)
        self.settings.pos = ((w*2/5-self.settings.size[0]/2),(h*9/14-self.settings.size[1]/2))
        
        self.about.size = (int(w/4.57143),int(h/3.42857))
        self.about.pos = ((w*2/5-self.about.size[0]/2),(h*4/14-self.about.size[1]/2))


class GameScreen(Screen) :
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.display = GameDisplay(self)

        self.audio_ctrl = AudioController()
        self.player = Player(self.display, self.audio_ctrl)
        self.canvas.add(self.display)

    def on_touch_move(self,touch):
        self.player.on_move(touch.pos)

    def on_touch_up(self,touch):
        self.player.on_touch_up(touch.pos)
        
    def on_touch_down(self, touch):
        self.player.on_touch_down(touch.pos)

    def on_layout(self, win_size):
        self.display.on_layout(win_size)

    def on_enter(self):
        vol = self.manager.volume
        zen = self.manager.zen

        self.display = GameDisplay(self, zen)
        
        self.audio_ctrl = AudioController(vol/10)
        self.player = Player(self.display, self.audio_ctrl)
        self.canvas.add(self.display)

    def on_update(self):
        self.player.on_update()


class InfoBar(InstructionGroup):
    def __init__(self, screen):
        super(InfoBar, self).__init__()
        w,h = Window.size
        self.score_label = CLabelRect(cpos = (w/2, 0.95 * h), text= 'SCORE: 0',font_name="DIN Alternate Bold", font_size=26)

        self.color = Color(0,0,58/255)
        self.add(self.color)
        self.add(self.score_label)
        
        self.menu_button = Button(text='MENU', font_name="DIN Alternate Bold",font_size=50, color=[0,0,58/255,1], background_color=[0,0,0,0])
        self.menu_button.size = (200,100)
        screen.add_widget(self.menu_button)

        self.pause_button = Button(text='PAUSE', font_name="DIN Alternate Bold",font_size=50, color=[0,0,58/255,1], background_color=[0,0,0,0])
        self.pause_button.size = (250,100)
        screen.add_widget(self.pause_button)

    def set_score(self,score):
        score_str = "SCORE: "
        score_str += str(score)
        self.score_label.set_text(score_str)

    def on_layout(self,win_size):
        w,h = win_size
        self.score_label.set_cpos((w/2, 0.95 * h))
        self.menu_button.pos = (100, 0.95 * h - self.menu_button.size[1]/2)
        self.pause_button.pos = (w-350, 0.95 * h - self.pause_button.size[1]/2)



class GameDisplay(InstructionGroup):
    def __init__(self, screen, zen=False):
        super(GameDisplay, self).__init__()
        self.screen = screen

        bg_src = '../assets/sea.png'
        self.background = Image(source=bg_src, size=(Window.width,Window.height), pos=(0,0), allow_stretch = True, keep_ratio = False)
        screen.add_widget(self.background)

        wave1_src = '../assets/wave1.png'
        self.wave1 = Image(source=wave1_src, size=(Window.width,Window.height), pos=(0,0), allow_stretch = True, keep_ratio = False)
        screen.add_widget(self.wave1)
        self.wave1_h = 1.01
        self.wave1_diff = -0.001

        wave2_src = '../assets/wave2.png'
        self.wave2 = Image(source=wave2_src, size=(Window.width,Window.height), pos=(0,0), allow_stretch = True, keep_ratio = False)
        screen.add_widget(self.wave2)

        self.size = GRID_SIZE

        self.gridlen = Window.height * (WAVE_HEIGHT*0.9)
        self.xshift = (Window.width * SCREEN_LEFT-self.gridlen)/2
        self.yshift = (Window.height * WAVE_HEIGHT-self.gridlen)/2
        self.dots = [[Dot(DOT_RADIUS, x, y, self.size, screen, self.gridlen, self.xshift, self.yshift) for y in range(self.size)] for x in range(self.size)]
        self.seaweeds = {"circle": Seaweed("circle", screen, SCREEN_LEFT, SCREEN_RIGHT, WAVE_HEIGHT, zen),
                         "square": Seaweed("square", screen, SCREEN_LEFT, SCREEN_RIGHT, WAVE_HEIGHT, zen),
                         "triangle": Seaweed("triangle", screen, SCREEN_LEFT, SCREEN_RIGHT, WAVE_HEIGHT, zen)}
        self.chordline = ChordLine()
        self.add(self.chordline)

        self.infobar = InfoBar(screen)
        self.add(self.infobar)

        self.on_layout(Window.size)

    def on_layout(self, win_size):
        w,h = win_size
        self.gridlen = WAVE_HEIGHT * h
        self.gridshift = (w * SCREEN_LEFT -self.gridlen)/2

        self.background.size = win_size
        self.wave1.size = win_size
        self.wave2.size = win_size
        
        self.infobar.on_layout(win_size)
        for dot in itertools.chain.from_iterable(self.dots):
                dot.on_layout(self.gridlen, self.gridshift)
        
        for seaweed in self.seaweeds.values():
            seaweed.on_layout(win_size)

    def on_clear(self,chord, shapes):
        if len(shapes) == 1:
            multiplier = 5
        else:
            multiplier = 1

        for dot in chord: 
            dot.pop_anim()
            self.seaweeds.get(dot.shape).update_progress(0.2 * multiplier)

        kivyClock.schedule_once(partial(self.replace_dots,chord), 0.4)

    def replace_dots(self,chord,dt):   
        clear_dict = {}
        for dot in chord:
            x,y = dot.get_pos()
            if x not in clear_dict:
                clear_dict[x] = [y]
            else:
                clear_dict[x].append(y)

        for col, ys in clear_dict.items():
            num_clear = len(ys)
     
            dots_remaining = [j for i, j in enumerate(self.dots[col]) if i not in ys]
            for idx, dot in enumerate(dots_remaining):
                dot.move_anim(idx)
            new_dots = [Dot(DOT_RADIUS, col, y+num_clear, self.size, self.screen, self.gridlen, self.gridshift, self.yshift) for y in range(self.size-num_clear, self.size)]
            for dot in new_dots:
                dot.move_anim(dot.y-num_clear)
            self.dots[col] = dots_remaining + new_dots
        
    def get_seaweed_levels(self):
        levels = {}
        for shape,seaweed in self.seaweeds.items():
            levels[shape] = seaweed.level
            if seaweed.level == 0 and seaweed.progress == 0:
                levels[shape] = -1
        return levels

    def on_update(self,chord,score):
        w,h = Window.size
        if (self.wave1_h > 1.01 and self.wave1_diff>0) or (self.wave1_h < 0.96 and self.wave1_diff<0):
            self.wave1_diff = -self.wave1_diff
        self.wave1_h += self.wave1_diff
        self.wave1.size = (w,h*self.wave1_h)

        wave2_h = 0.96 + 1.01 - self.wave1_h
        self.wave2.size = (w,h*wave2_h)

        for dot in itertools.chain.from_iterable(self.dots):
                if dot not in self.children:
                    self.add(dot)
                dot.on_update()

        for seaweed in self.seaweeds.values():
            seaweed.on_update()

        linepoints = ()
        for dot in chord:
            linepoints+=(dot.center)
        self.chordline.on_update(linepoints)
        self.infobar.set_score(score)
        
    def handle_button(self,touch_pos):
        #jank menu/pause button bindings because could not get those things to work for my life
        x,y = touch_pos
        menu = self.infobar.menu_button
        pause = self.infobar.pause_button
        menux = menu.pos[0] < x < (menu.pos[0]+menu.size[0])
        menuy = menu.pos[1] < y < (menu.pos[1]+menu.size[1])
        pausex = pause.pos[0] < x < (pause.pos[0]+pause.size[0])
        pausey = pause.pos[1] < y < (pause.pos[1]+pause.size[1])

        if menux and menuy:
            self.screen.switch_to("menu")

        if pausex and pausey:
            return self.screen.player.pause()

        return False

if __name__ == "__main__":
    sm = myScreenManager()
    sm.add_screen(StartScreen(name='intro'))
    sm.add_screen(MenuScreen(name='menu'))
    sm.add_screen(GameScreen(name='game'))
    sm.add_screen(SettingsScreen(name='settings'))
    sm.add_screen(AboutScreen(name='about'))

    run(sm)
