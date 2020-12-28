import itertools
import os
import random

class Player(object):
    def __init__(self, display, audio_ctrl):
        super(Player, self).__init__()
        self.display = display
        self.audio_ctrl = audio_ctrl
        self.score = 0
        self.current_chord = []
        self.paused = False

    def on_update(self):
        if not self.paused:
            self.display.on_update(self.current_chord, self.score)
            
            levels = self.display.get_seaweed_levels()
            self.audio_ctrl.on_update(levels)
        

    def on_touch_down(self, touch_pos):
        if not self.paused:
            dots = self.display.dots
            for dot in itertools.chain.from_iterable(dots):
                    within = self.in_radius(touch_pos, dot.center, dot.rad)
                    if within:
                        self.current_chord.append(dot)
                        dot.set_selected(True)
                        self.audio_ctrl.play_note(dot.pitch)
            

    def reachable(self, last_dot):
        x,y = last_dot.get_pos()
        move_dir = [(0,1), (1,0), (-1,0), (0,-1), (0,0)]
        reachable_dots = []
        size = self.display.size
        for x_delta, y_delta in move_dir:
            new_x, new_y = x + x_delta, y + y_delta
            if new_x < size and new_x >= 0 and new_y < size and new_y >= 0:
                if self.display.dots[new_x][new_y].color == last_dot.color:
                    reachable_dots.append(self.display.dots[new_x][new_y])

        return reachable_dots

    def on_move(self, touch_pos):
        if not self.paused: 
        
            dots = self.display.dots
            if len(self.current_chord) > 0: 
                last_dot = self.current_chord[-1]
                reachable = self.reachable(last_dot)
            else: 
                reachable = [dot for dot in itertools.chain.from_iterable(dots)]
            for dot in reachable:
                clicked = self.in_radius(touch_pos, dot.center, dot.rad)
                if clicked:
                    if dot not in self.current_chord:
                        dot.set_chord_pitch(len(self.current_chord))
                        if self.current_chord:
                            self.audio_ctrl.play_note(dot.pitch)
                        self.current_chord.append(dot)
                        dot.set_selected(True)
                    if len(self.current_chord) > 1 and dot == self.current_chord[-2]:
                        unselect = self.current_chord[-1]
                        self.current_chord.remove(unselect)
                        unselect.set_selected(False)

    def on_touch_up(self, touch_pos):
        self.display.handle_button(touch_pos)

        if not self.paused:
            if len(self.current_chord) >= 2:
                unique_shapes = []
                unique_pitches = []
                for dot in self.current_chord:
                    if dot.pitch not in unique_pitches:
                        unique_pitches.append(dot.pitch)
                        self.audio_ctrl.play_chord(dot.pitch)
                    if dot.shape not in unique_shapes:
                        unique_shapes.append(dot.shape)
            
                self.display.on_clear(self.current_chord, unique_shapes)
                self.score += len(self.current_chord)

                if len(unique_shapes) == 1:
                    bonus_wav = random.choice(os.listdir("../sounds/bonus"))
                    self.audio_ctrl.play_wav("../sounds/bonus/" + bonus_wav)
                    
            for dot in self.current_chord:
                dot.set_selected(False)
            self.current_chord = []


    def pause(self):
        self.paused = not self.paused
    
    def in_radius(self, pos1, pos2, radius):
        dist_sq = (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2
        # added buffer so we cannot be in two dots at once
        return dist_sq <= (radius * 3/4)**2