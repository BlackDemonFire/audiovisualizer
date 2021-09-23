import random
import arcade
import numpy as np
import librosa
from scipy.signal import savgol_filter

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Audio Visualizer"


class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.BLACK)
        self.music = arcade.Sound("sound.wav")
        AUDIO_TIME_SERIES, SAMPLING_RATE = librosa.load("./sound.wav")
        self.fourier = librosa.stft(AUDIO_TIME_SERIES, win_length=2001)
        self.wav = AUDIO_TIME_SERIES
        self.sr = SAMPLING_RATE
        self.smoothWave = savgol_filter(
            abs(AUDIO_TIME_SERIES), window_length=2001, polyorder=3)*2
        self.sc = librosa.feature.spectral_centroid(
            y=AUDIO_TIME_SERIES, sr=SAMPLING_RATE)
        self.player = self.music.play(volume=0.5)
        self.rectcolor = arcade.csscolor.LIME
        self.circcolor = arcade.csscolor.RED
        self.fourierDb = librosa.amplitude_to_db(abs(self.fourier))
        self.shape = "circ"
        print("__init__ finished")
        print("fourier length:")
        print(len(self.fourier))
        print("track length:")
        print(len(self.sc[0]))

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""
        arcade.start_render()
        pos = int(
            self.music.get_stream_position(self.player)*self.sr)
        progress = int((self.music.get_stream_position(
            self.player)/self.music.source.duration)*self.width)
        if (self.shape == "rect"):
            arcade.draw_rectangle_filled(self.width/2, self.height/2, abs(
                self.smoothWave[pos])*self.width/2, 20, self.rectcolor)
        elif (self.shape == "circ"):
            arcade.draw_circle_filled(
                self.width/2, self.height/2, self.smoothWave[pos]*100, self.circcolor)
        if (self.smoothWave[pos] > 0.5):
            if (self.shape == "rect"):
                self.shape = "circ"
            else:
                self.shape = "rect"

        arcade.draw_rectangle_filled(
            0, 10, progress, 20, arcade.csscolor.GREEN)
        arcade.finish_render()
        if (self.music.is_complete(self.player)):
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
            self.shape = random.choice(["circ", "rect"])
        return super().on_mouse_press(x, y, button, modifiers)

    def on_key_release(self, symbol: int, modifiers: int):
        if (symbol == "p"):
            if (self.player.playing):
                self.player.pause()
            else:
                self.player.play()
        return super().on_key_release(symbol, modifiers)

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
