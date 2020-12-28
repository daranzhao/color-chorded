
import os

from common.audio import Audio
from common.mixer import Mixer
from common.synth import Synth
from common.clock import SimpleTempoMap, AudioScheduler, quantize_tick_up
from common.wavegen import WaveGenerator
from common.wavesrc import WaveBuffer, WaveFile

import random

ROOTS = ['C', 'E', 'G', 'A']

class AudioController(object):
    def __init__(self, vol = 0.3):
        self.vol = vol
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.synth = Synth("../sounds/FluidR3_GM.sf2", 0.3)

        self.tempo_map = SimpleTempoMap(100)
        self.sched = AudioScheduler(self.tempo_map)

        self.audio.set_generator(self.mixer)
        self.mixer.add(self.sched)
        self.sched.set_generator(self.synth)

        # dot sounds
        self.synth.program(3, 0, 107)
        self.synth.cc(3, 7, 80)

        self.bg_mixer = Mixer()
        self.bg_mixer.set_gain(0.2)
        self.mixer.add(self.bg_mixer)

        # level of chords, drums, accents, each from 0-3
        self.root = None
        self.bg_levels = [0, 0, 0]

        self.set_bg_music(0)
        self.mixer.set_gain(self.vol)

    def set_bg_music(self, tick):
        self.root = random.choice([r for r in ROOTS if r != self.root])
        for idx, level in enumerate(self.bg_levels):
            layer = ['chords', 'drums', 'accents'][idx]
            for l in range(level):
                layer_wavs = os.listdir("../sounds/" + layer + "/" + str(l))
                valid_wavs = [w for w in layer_wavs if self.root in w]
                self.play_wav("../sounds/" + layer + "/" + str(l) + "/" + random.choice(valid_wavs))
        
        if random.random() < 0.45 or sum(self.bg_levels) == 0:
            ambience = random.choice(os.listdir("../sounds/ambience/ocean/"))
            self.play_wav("../sounds/ambience/ocean/" + ambience)

        # call again after 8 beats or 3840 ticks
        self.sched.post_at_tick(self.set_bg_music, self.sched.get_tick() + 3840)

    def play_wav(self, wav_path):
        self.bg_mixer.add(WaveGenerator(WaveFile(wav_path)))

    def play_note(self, pitch):
        channel = 3
        now = self.sched.get_tick()
        self.sched.post_at_tick(self._noteon, now, (channel, pitch))

    def play_chord(self, pitch):
        channel = 3
        next_eighth = quantize_tick_up(self.sched.get_tick(), 240)
        self.sched.post_at_tick(self._noteon, next_eighth, (channel, pitch))

    def set_vol(self, vol):
        self.mixer.set_gain(vol)

    def _noteon(self, tick, channel_pitch):
        self.synth.noteon(*channel_pitch, 120)
        self.sched.post_at_tick(self._noteoff, tick + 240, channel_pitch)

    def _noteoff(self, tick, channel_pitch):
        self.synth.noteoff(*channel_pitch)

    def on_update(self, levels):
        self.bg_levels = [l + 1 for l in levels.values()]
        self.audio.on_update()