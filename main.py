import random
import sys
from time import time
import arcade
from librosa.util.utils import frame
import numpy as np
import librosa
from scipy.signal import savgol_filter
import colorsys

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Audio Visualizer"

def hsv2rgb(h,s,v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1/20, resizable=True)
        start = time()
        soundfile = ""
        if len(sys.argv) < 2:
            soundfile = "sound.wav"
        else:
            soundfile = sys.argv[1]
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.music = arcade.Sound(soundfile)
        AUDIO_TIME_SERIES, SAMPLING_RATE = librosa.load(soundfile, sr=48000)
        self.fourier = np.abs(librosa.stft(
            AUDIO_TIME_SERIES, win_length=int(SAMPLING_RATE/60)))
        self.wav = AUDIO_TIME_SERIES
        self.sr = SAMPLING_RATE
        self.smoothWave = savgol_filter(
            abs(AUDIO_TIME_SERIES), window_length=2001, polyorder=3)*2

        self.rectcolor = arcade.csscolor.LIME
        self.circcolor = arcade.csscolor.RED
        self.fourierDb = librosa.amplitude_to_db(self.fourier)
        self.shape = "circ"
        print("__init__ finished ... took " + str(time()-start) + "seconds")
        print("fourier length: " + str(len(self.fourierDb[0])))
        print("fourier amount: " + str(len(self.fourierDb)))
        print("track length: " + str(len(self.wav)))
        print("sampling rate: " + str(SAMPLING_RATE))
        self.player = self.music.play(volume=0.5)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        streampos = self.music.get_stream_position(self.player)
        pos = int(streampos*self.sr)
        progress = int((self.music.get_stream_position(
            self.player)/self.music.source.duration)*self.width)
        if (self.shape == "rect"):
            arcade.draw_rectangle_filled(self.width/2, self.height/2, abs(
                self.smoothWave[pos])*self.width/2, 20, self.rectcolor)
        elif (self.shape == "circ"):
            arcade.draw_circle_filled(
                self.width/2, self.height/2, self.smoothWave[pos]*100*self.width*self.height/(600*1080), self.circcolor)
        if (self.smoothWave[pos] > 0.5):
            if (self.shape == "rect"):
                self.shape = "circ"
            else:
                self.shape = "rect"

        arcade.draw_rectangle_filled(
            0, 10, progress*2, 20, arcade.csscolor.GREEN)
        for i in range(1, 1025):
            x1 = self.width*i/1025
            x2 = self.width*(i+1)/1025
            y1 = int(((self.fourierDb[i-1][int(pos/200)+1])*self.height/200)+150)
            y2 = int(((self.fourierDb[i][int(pos/200)+1])*self.height/200)+150)
            arcade.draw_line(x1, y1, x2, y2, hsv2rgb(i/1024,1,0.5), 1)
        arcade.finish_render()
        if (self.music.is_complete(self.player)):
            arcade.sound.stop_sound(self.player)
            self.close()
        # Code to draw the screen goes here

    def on_close(self):
        arcade.sound.stop_sound(self.player)
        return super().on_close()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if (button == arcade.MOUSE_BUTTON_LEFT):  # LMB
            self.circcolor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))
            self.rectcolor = (random.randint(0, 255), random.randint(
                0, 255), random.randint(0, 255))
        if (button == arcade.MOUSE_BUTTON_MIDDLE):  # mousewheel
            pass
        if (button == arcade.MOUSE_BUTTON_RIGHT):  # RMB
            pass
        return super().on_mouse_press(x, y, button, modifiers)

    def on_key_press(self, symbol: int, modifiers: int):
        if (symbol == 112):
            if (self.player.playing):
                self.player.pause()
            else:
                self.player.play()
        return super().on_key_press(symbol, modifiers)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        volume = self.music.get_volume(self.player)
        volume += 0.1*scroll_y
        volume = min(1, volume)
        volume = max(0, volume)
        self.music.set_volume(volume, self.player)
        return super().on_mouse_scroll(x, y, scroll_x, scroll_y)


def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
