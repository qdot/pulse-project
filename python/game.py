import sys
import time
import itertools

import lightstone

import pygame
from pygame.locals import *

from OpenGL.GL     import *
from OpenGL.GLU     import *

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

class PulseGame(object):
    def __init__(self):
        pygame.init()
        self.intro_texture_list = ["logosm.jpg", "pulsetitle.jpg"]
        self.intro_iter = itertools.cycle(self.intro_texture_list)
        self.texture = None
        self.screen = pygame.display.set_mode((1024, 768),OPENGL|DOUBLEBUF)
        self.current_render_func = None
        self.fade_step_interval = 5
        self.fade_step_time = 0.025

    def set_ortho_projection(self):
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        gluOrtho2D(0,1024,0,768)
        glMatrixMode(GL_MODELVIEW)

    def render_texture_quad(self):
        glBegin(GL_QUADS)
        glTexCoord2f(0,0); glVertex(0,0)
        glTexCoord2f(1,0); glVertex(1024,0)
        glTexCoord2f(1,1); glVertex(1024,768)
        glTexCoord2f(0,1); glVertex(0,768)
        glEnd()

    def fade_out_current_texture(self):
        for i in range(255, 0, -self.fade_step_interval):
            start_time = time.time()
            glColor4f(i/255.0,i/255.0,i/255.0,i/255.0)
            current_time = time.time()
            while current_time - start_time < self.fade_step_time:
                self.render_texture_quad()
                yield
                current_time = time.time()
        self.current_render_func = self.rebind_texture()
        yield

    def show_textured_quad(self):
        glColor(255,255,255,255)
        start_time = time.time()
        current_time = time.time()
        while current_time - start_time < 2.0:
            self.render_texture_quad()
            yield
            current_time = time.time()
        self.current_render_func = self.fade_out_current_texture()
        yield

    def fade_in_current_texture(self):
        for i in range(0, 255, self.fade_step_interval):
            start_time = time.time()
            current_time = time.time()
            while current_time - start_time < self.fade_step_time:
                glColor4f(i/255.0,i/255.0,i/255.0,i/255.0)
                self.render_texture_quad()
                yield
                current_time = time.time()
        self.current_render_func = self.show_textured_quad()
        yield

    def prepare_buffer(self):
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

    def finalize_buffer(self):
        pygame.display.flip()

    def rebind_texture(self):
        self.bind_texture(self.intro_iter.next())
        self.current_render_func = self.fade_in_current_texture()
        yield

    def bind_texture(self, f):
        # Generate PyOpenGL Texture
        self.texture = glGenTextures(1)
        # Load the image file
        Surface = pygame.image.load(f)
        # Convert it to load any alpha channel
        Surface.convert_alpha()
        # Convert to PyOpenGL Data
        Data = pygame.image.tostring(Surface, "RGBA", 1)
        # Select our Texture Object
        glBindTexture(GL_TEXTURE_2D, self.texture)
        # Load the Data into the Texture
        glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, Surface.get_width(), Surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, Data )
        # Define some Parameters for this Texture
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    def loop(self):
        # logo = pygame.image.load('logosm.jpg').convert()
        self.current_render_func = self.rebind_texture()
        glClearColor(0,0,0,0)
        self.set_ortho_projection()
        glEnable(GL_TEXTURE_2D)
        #glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        # glDisable(GL_DEPTH_TEST)
        while 1:
            self.prepare_buffer()
            self.current_render_func.next()
            #glColor(255,255,255,255)
            #self.render_texture_quad()
            self.finalize_buffer()

            event = pygame.event.poll()
            
            if event.type is QUIT:
                sys.exit(0)
        
            # draw()
  
            if event.type is KEYDOWN:
                if event.key is K_ESCAPE:
                    sys.exit(0)

def main():
    p = PulseGame()
    p.loop()

if __name__ == '__main__':
    sys.exit(main())
