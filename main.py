import colorsys
import os
import random
import sys
from time import time

import arcade
import librosa
import numpy as np
from scipy.signal import savgol_filter

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Audio Visualizer"

trans_colors = []

clr = os.environ.get("COLOR")
if clr:
    clr = clr.lower()
else:
    clr = "rainbow"


def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))


def get_color(i: int):
    if clr == "rainbow":
        return hsv2rgb(i / 1024, 1, 0.5)
    if clr == "white":
        return arcade.csscolor.WHITE
    if clr == "trans":
        if i < 205:
            return 91, 206, 250
        if i < 410:
            return 245, 169, 184
        if i < 615:
            return arcade.csscolor.WHITE
        if i < 820:
            return 245, 169, 184
        return 91, 206, 250
    if clr == "enby":
        if i < 256:
            return 255, 244, 48
        if i < 512:
            return arcade.csscolor.WHITE
        if i < 768:
            return 156, 89, 209
        return arcade.csscolor.BLACK
    if clr == "pan":
        if i < 342:
            return 33, 177, 255
        if i < 683:
            return 255, 216, 0
        return 255, 33, 140


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1 / 20, resizable=True)
        start = time()
        if len(sys.argv) < 2:
            sound_file = "sound.wav"
        else:
            sound_file = sys.argv[1]
        arcade.set_background_color((54, 57, 62))
        self.music = arcade.Sound(sound_file)
        audio_time_series, sampling_rate = librosa.load(sound_file, sr=None)
        self.fourier = np.abs(librosa.stft(
            audio_time_series, win_length=int(sampling_rate / 60)))
        self.wav = audio_time_series
        self.sr = sampling_rate
        self.smoothWave = savgol_filter(
            abs(audio_time_series), window_length=2001, polyorder=3) * 2

        self.rectColor = arcade.csscolor.LIME
        self.circColor = arcade.csscolor.RED
        self.fourierDb = librosa.amplitude_to_db(self.fourier)
        self.shape = "circ"
        self.lengthConversion = len(self.wav) / len(self.fourierDb[0])
        print("__init__ finished ... took " + str(time() - start) + "seconds")
        print("fourier length: " + str(len(self.fourierDb[0])))
        print("fourier amount: " + str(len(self.fourierDb)))
        print("track length: " + str(len(self.wav)))
        print("sampling rate: " + str(sampling_rate))
        self.player = self.music.play(volume=0.5)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        stream_position = self.music.get_stream_position(self.player)
        pos = int(stream_position * self.sr)
        progress = int((self.music.get_stream_position(
            self.player) / self.music.source.duration) * self.width)
        if self.shape == "rect":
            arcade.draw_rectangle_filled(self.width / 2, self.height / 2, abs(
                self.smoothWave[pos]) * self.width / 2, 20, self.rectColor)
        elif self.shape == "circ":
            arcade.draw_circle_filled(
                self.width / 2, self.height / 2, self.smoothWave[pos] * 100 * self.width * self.height / (600 * 1080),
                self.circColor)
        if self.smoothWave[pos] > 0.5 and self.player.playing:
            if self.shape == "rect":
                self.shape = "circ"
            else:
                self.shape = "rect"

        if self.smoothWave[pos] > 0.875 and self.player.playing:
            self.circColor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))
            self.rectColor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))

        arcade.draw_rectangle_filled(
            0, 10, progress * 2, 20, arcade.csscolor.GREEN)
        for i in range(1, 1025):
            x1 = self.width * i / 1025
            x2 = self.width * (i + 1) / 1025
            y1 = int(((self.fourierDb[i - 1][int(pos / self.lengthConversion) + 1]) * self.height / 200) + 150)
            y2 = int(((self.fourierDb[i][int(pos / self.lengthConversion) + 1]) * self.height / 200) + 150)
            arcade.draw_line(x1, y1, x2, y2, get_color(i), 1)
        arcade.finish_render()
        if self.music.is_complete(self.player):
            arcade.sound.stop_sound(self.player)
            self.close()
        # Code to draw the screen goes here

    def on_close(self):
        arcade.sound.stop_sound(self.player)
        return super().on_close()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.circColor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))
            self.rectColor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))
        if button == arcade.MOUSE_BUTTON_MIDDLE:
            pass
        if button == arcade.MOUSE_BUTTON_RIGHT:
            pass
        return super().on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == 112:
            if self.player.playing:
                self.player.pause()
            else:
                self.player.play()
        return super().on_key_press(symbol, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        volume = self.music.get_volume(self.player)
        volume += 0.1 * scroll_y
        volume = min(1., volume)
        volume = max(0., volume)
        self.music.set_volume(volume, self.player)
        return super().on_mouse_scroll(x, y, scroll_x, scroll_y)


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
