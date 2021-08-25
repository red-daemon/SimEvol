import pygame
import random
import math
from pygame.locals import *
from general_functions import *


class RenderText(pygame.sprite.Sprite):
    pos = None
    pos_rel = None

    def __init__(self, screen, text='text', pos=(0, 0), pos_rel=(LEFT, TOP),
                 font=None, size=20, color=(255, 255, 255), antialias=True):
        """Inicializa Sprite de texto"""
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(font, size)    # Tamaño del texto
        self.color = color  # Color de la fuente
        self.text = text    # Texto a mostrar
        self.pos = pos  # Posición del texto
        self.pos_rel = pos_rel  # Posición relativa con respecto a la pantalla
        self.screen = screen    # Screen en donde se va a hacer el render del texto
        self.antialias = antialias

        self.rerender() # Prepara el render del texto

    def update(self):
        pass

    def calculate_position(self):
        """Calcula la posición real en función de la posición relativa"""
        return (
            self.pos_rel[0]*(self.screen.get_size()[0]/2 - self.rect.width/2)
            + (1-2*(self.pos_rel[0]/2))*self.pos[0],
            self.pos_rel[1]*(self.screen.get_size()[1]/2 - self.rect.height/2)
            + (1-2*(self.pos_rel[1]/2))*self.pos[1],
            )

    def print_text(self, text, pos=None):
        """Actualiza el texto con los datos y se asigna locación para mostrarlos"""
        self.text = text
        if pos:
            self.pos = pos
        self.rerender(pos)

    def rerender(self, pos = None):
        """Prepara el render del texto"""
        self.image = self.font.render(self.text, self.antialias, self.color)
        self.rect = self.image.get_rect()
        # Si se pasa locación, renderea ahí
        if pos: 
            self.rect.x, self.rect.y = pos[0], pos[1]
        
        # Si no se pasa locación, renderealo en la esquina inferior derecha
        else:   
            self.rect.x, self.rect.y = self.calculate_position()
