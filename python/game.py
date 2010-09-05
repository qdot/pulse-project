import sys
import time
import itertools

import math
import Queue
import threading
import lightstone

import json
import pygame
from pygame.locals import *

from OpenGL.GL     import *
from OpenGL.GLU     import *

from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid.axislines import SubplotZero

# State Machines:

# Intro:
# - Show Logo
# - Show Title Screen
# - Show Instruction Screen?
# - Show High Scores
# - On finger clip detection, show Title Screen
# - On button press w/o clip detection, show Title Screen, wait for finger clip detection
# - On button press w/ clip detection, start game
# - Music?

# Game State:
# - Show instruction screen, wait for button press
# - Countdown from 3
# - 60 second gameplay
# - Calculate score, save to file

# Score State:
# - Show score
# - Name entry for top ten (morse code)
# - Show High Scores and Score Index

readings = Queue.Queue()

class LightstoneRecorder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = threading.Event()
        self.record = threading.Event()
        self.read_lock = threading.Lock()
        self.hrv = 0
        self.scl = 0
        return

    def get_hrv(self):
        return self.hrv

    def get_scl(self):
        return self.scl

    def run(self):
        global readings
        while not self.stop.is_set():
            self.l = lightstone.lightstone.open()
            self.l.get_data()
            self.read_lock.acquire()
            self.hrv = self.l.hrv
            self.scl = self.l.scl
            self.read_lock.release()
            if self.record.is_set():
                readings.append({"time": time.time(), "scl": l.scl, "hrv": l.hrv})
        print "Exiting Lightstone Thread"

class KeyRecorder():
    def __init__(self):
        """
        """

    def addKey(self):
        global readings
        readings.append({"time": time.time()})

class GameStateNode(object):
    """
    Any frame in this game is going to do one of two things: 
    - Sit there and show a graphic
    - Sit there and show nothing
 
    This implements that behavior. The state machine is inherent to
    the game because I'm lazy.
    """

    def __init__(self):
        """
        """
        self.done = False
        self.next_node = None
        self.texture = None
        self.current_surface_width = None
        self.current_surface_height = None

    def runGameLoop(self, ):
        """
        """
        raise Exception("Must implement runGameLoop!")

    def load_texture(self, f):
        print "Loading texture %s" % (f)
        # Load the image file
        Surface = pygame.image.load(f)
        self.load_surface_to_texture(Surface)

    def load_surface_to_texture(self, Surface):
        self.texture = glGenTextures(1)
        # Convert it to load any alpha channel
        Surface.convert_alpha()
        # Convert to PyOpenGL Data
        Data = pygame.image.tostring(Surface, "RGBA", 1)
        # Load the Data into the Texture
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, Surface.get_width(), Surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, Data )
        self.current_surface_width = Surface.get_width()
        self.current_surface_height = Surface.get_height()
        print "%s %s" % (Surface.get_width(), Surface.get_height())
        # Define some Parameters for this Texture
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def prepare_buffer(self):
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    def finalize_buffer(self):
        pygame.display.flip()

    def set_ortho_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0,1024,0,768)
        glMatrixMode(GL_MODELVIEW)

    def bind_texture(self):
        # Select our Texture Object
        glBindTexture(GL_TEXTURE_2D, self.texture)

    def render_small_quad(self):
        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex(512-(self.current_surface_width/2),384-(self.current_surface_height/2))
        glTexCoord2f(1,0); glVertex(512+(self.current_surface_width/2),384-(self.current_surface_height/2))
        glTexCoord2f(1,1); glVertex(512+(self.current_surface_width/2),384+(self.current_surface_height/2))
        glTexCoord2f(0,1); glVertex(512-(self.current_surface_width/2),384+(self.current_surface_height/2))
        glEnd()

    # def render_texture_quad(self):
    #     glBegin(GL_QUADS)
    #     glTexCoord2f(0,0); glVertex(0,0)
    #     glTexCoord2f(1,0); glVertex(1024,0)
    #     glTexCoord2f(1,1); glVertex(1024,768)
    #     glTexCoord2f(0,1); glVertex(0,768)
    #     glEnd()

    def show_textured_quad(self):
        glColor4f(1.0,1.0,1.0,1.0)
        self.bind_texture()
        self.render_small_quad()

    # def fade_out_current_texture(self):
    #     for i in range(255, 0, -self.fade_step_interval):
    #         start_time = time.time()
    #         glColor4f(i/255.0,i/255.0,i/255.0,i/255.0)
    #         current_time = time.time()
    #         while current_time - start_time < self.fade_step_time:
    #             self.render_texture_quad()
    #             yield
    #             current_time = time.time()
    #     self.current_render_func = self.rebind_texture()
    #     yield

    # def fade_in_current_texture(self):
    #     for i in range(0, 255, self.fade_step_interval):
    #         start_time = time.time()
    #         current_time = time.time()
    #         while current_time - start_time < self.fade_step_time:
    #             glColor4f(i/255.0,i/255.0,i/255.0,i/255.0)
    #             self.render_texture_quad()
    #             yield
    #             current_time = time.time()
    #     self.current_render_func = self.show_textured_quad()
    #     yield

class ShowImageState(GameStateNode):
    """
    Shows an image until the trigger button is pressed.
    """

    def __init__(self, texture):
        super(ShowImageState,self).__init__()
        self.texture_filename = texture

    def initialize(self):
        self.load_texture(self.texture_filename)
        glClearColor(0,0,0,0)
        self.set_ortho_projection()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)

    def runGameLoop(self):
        while True:
            self.prepare_buffer()
            self.show_textured_quad()
            self.finalize_buffer()
            event = pygame.event.poll()
            
            if event.type is QUIT:
                sys.exit(0)
  
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    sys.exit(0)
                if event.key is K_SPACE:
                    self.done = True
                    glDeleteTextures([self.texture])
                    return
            yield
        
class MenuState(ShowImageState):
    def __init__(self):
        super(MenuState,self).__init__("pulsetitle.jpg")
        self.next_node = StartState

class StartState(ShowImageState):
    def __init__(self):
        super(StartState, self).__init__("startbutton.001.jpg")
        self.next_node = InstructionState

class InstructionState(ShowImageState):
    def __init__(self):
        super(InstructionState,self).__init__("logosm.jpg")
        self.next_node = CountdownState

class CountdownState(GameStateNode):
    def __init__(self):
        super(CountdownState,self).__init__()
        self.next_node = GameState
        self.font = None

    def initialize(self):
        self.font = pygame.font.SysFont("arial", 60)        
        self.load_surface_to_texture(self.font.render("3", True, (255, 255, 255)))
        return

    def runGameLoop(self):
        time_limit = time.time() + 3
        time_gap = 3
        while True:
            self.prepare_buffer()
            self.show_textured_quad()
            self.finalize_buffer()

            current_gap = (int)(time_limit - time.time())
            if current_gap < 0:
                glDeleteTextures([self.texture])
                return
            if current_gap != time_gap:
                glDeleteTextures([self.texture])
                self.load_surface_to_texture(self.font.render("%s" % (current_gap + 1), True, (255, 255, 255)))

            event = pygame.event.poll()
            
            if event.type is QUIT:
                sys.exit(0)
  
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    sys.exit(0)
            yield

class GameState(GameStateNode):
    def __init__(self):
        super(GameState,self).__init__()
        self.next_node = ScoreState

    def initialize(self):
        return
        
    def runGameLoop(self):
        """
        Show blank screen and take recordings for 60 seconds
        """
        time_limit = time.time() + 5
        l = LightstoneRecorder()
        k = KeyRecorder()     
        while True:
            self.prepare_buffer()
            self.finalize_buffer()
            event = pygame.event.poll()
            
            if time_limit - time.time() < 0:
                return

            if event.type is QUIT:
                sys.exit(0)
  
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    sys.exit(0)
                if event.key is K_SPACE:
                    k.addKey()
            yield
        
class ScoreState(GameStateNode):
    def __init__(self):
        global readings
        super(ScoreState,self).__init__()
        self.next_node = MenuState
        self.font = None
        self.peaks = []

        f = open("game_output.txt", "r")
        l = json.load(f)
        for a in l:
            readings.put(a)

        self.readings = []
        self.score = 0
        while not readings.empty():
            self.readings.append(readings.get())

    def initialize(self):
        # self.font = pygame.font.SysFont("arial", 60)        
        # self.load_surface_to_texture(self.font.render("Your Score Is: %s" % 0, True, (255, 255, 255)))
        glClearColor(0,0,0,0)
        self.set_ortho_projection()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        return

    def calculate_peaks(self):
        hrv_dict = []
        for el in self.readings: 
            try:
                hrv_dict.append((el["time"], el["hrv"]))
            except KeyError:
                pass

        hrv_window = deque()
        hrv_limit = 20
        hrv_total = []
        stop_counter = 0
        hrv_itr = hrv_dict.__iter__()
        b = hrv_itr.next()
        
        while 1:
            a = [b[0], b[1], 0]
            hrv_window.append(a)
            hrv_total.append(a)
            if len(hrv_window) > hrv_limit:
                hrv_window.popleft()
            m = max(hrv_window, key=lambda (x): x[1])
            m[2] = m[2] + 1
            # Move the iterator forward. If we're done iterating, just
            # readd the last element onto the end.
            try:
                c = hrv_itr.next()
                b = c
            except StopIteration:
                stop_counter = stop_counter + 1
                if stop_counter == hrv_limit:
                    break
            
        for (time, hrv, score) in hrv_total:
            if score > 15:
                self.peaks.append({"time" : time, "hrv" : hrv})

    def draw_graph(self):
        min_time = 0
        max_time = 0
        for val in self.readings:
            if min_time == 0:
                min_time = val["time"]
            if val["time"] < min_time:
                min_time = val["time"]
            if max_time == 0:
                max_time = val["time"]
            if val["time"] > max_time:
                max_time = val["time"]
                
        fig = plt.figure(1)

        fig.subplots_adjust(right=0.85)
        ax = SubplotZero(fig, 1, 1, 1)
        fig.add_subplot(ax)
        plt.title("Score for Game: %s" % self.score)
        # make right and top axis invisible
        ax.axis["right"].set_visible(False)
        ax.axis["top"].set_visible(False)

        # make xzero axis (horizontal axis line through y=0) visible.
        ax.axis["xzero"].set_visible(False)

        ax.set_xlim(min_time, max_time)
        ax.set_ylim(0, 4)
        ax.set_xlabel("Time")
        ax.set_ylabel("HRV")

        t_hrv = []
        hrv = []
        for val in self.readings:
            if "hrv" in val.keys():
                t_hrv.append(val["time"])
                hrv.append(val["hrv"])
            else:
                ax.plot(val["time"], 2.0, 'r.')

        for peak in self.peaks:
            ax.plot(peak["time"], peak["hrv"], 'g.', markersize=10)
        ax.plot(t_hrv, hrv, 'b-')

        plt.savefig('pulse_graph')

    def calculate_score(self):
        keys = []
        peaks = {}
        for val in self.readings:
            if "key" in val:
                closest = None
                for p in self.peaks:
                    if closest is None:
                        closest = p
                    elif math.fabs(p["time"] - val["time"]) < math.fabs(closest["time"] - val["time"]):
                        closest = p
                if closest["time"] in peaks.keys():
                    peaks[closest["time"]].append(val)
                else:
                    peaks[closest["time"]] = [val]
        score = 0
        for (peak_time, presses) in peaks.items():
            print "Peak time: %s" % peak_time
            minimum = 1000
            total_time = 0
            for p in presses:
                print " Press %s\n  Difference from Peak Time %s" % (p, math.fabs(p["time"] - peak_time))
                total_time += math.fabs(p["time"] - peak_time)
                if math.fabs(p["time"] - peak_time) < minimum:
                    minimum = math.fabs(p["time"] - peak_time)
                # remove the minimum from the total time, scale it (10%), and readd to minimum for score
                total_time = ((total_time - minimum) * .1) + minimum
                self.score += total_time
            # find the keyhit with the minimum amount of time between the hit and the peak and add it to the score

    def runGameLoop(self):
        self.calculate_peaks()
        self.calculate_score()
        self.draw_graph()

        self.load_texture("pulse_graph.png")
        while True:
            self.prepare_buffer()
            self.show_textured_quad()
            self.finalize_buffer()
            event = pygame.event.poll()

            if event.type is QUIT:
                sys.exit(0)
  
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    sys.exit(0)
                if event.key is K_SPACE:
                    glDeleteTextures([self.texture])
                    return
            yield

class HighScoreState(GameStateNode):
    def __init__(self, texture):
        super(ScoreState,self).__init__()    

class PulseGame(object):
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((1024, 768),OPENGL|DOUBLEBUF)
        # self.fade_step_interval = 5
        # self.fade_step_time = 0.025
        self.node = ScoreState()
    
    def loop(self):        
        while 1:
            self.node.initialize()
            l = self.node.runGameLoop()
            while True:
                try:
                    l.next()
                except StopIteration:
                    break
            self.node = self.node.next_node()

def main():
    p = PulseGame()
    p.loop()

if __name__ == '__main__':
    sys.exit(main())
