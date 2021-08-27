import pygame
import random
import math
from pygame.locals import *
from general_functions import *

class Chon(pygame.sprite.Sprite):
    def __init__(self, pos=None, timer = 0):
        """Inicializa un nuevo Chon, con una imagen prediseñada, asígnale coordenadas y orientación."""
        pygame.sprite.Sprite.__init__(self) # Inicializa el modulo interno
        self.image = pygame.image.load('chon.bmp').convert()    # Carga la imagen
        self.rect = self.image.get_rect()   # Calcula el rectángulo contenedor
        
        # si no recibe una posición predeterminada, asignale una aleatoria
        if pos == None:
            self.rect = self.rect.move(random.randrange(0, 800, 10), random.randrange(0, 800, 10))
        else:
            self.rect = self.rect.move(pos[0],pos[1])

        self.real_pose = [self.rect.x, self.rect.y] # Guarda las coordenadas continuas del Chon
        self.theta = (random.randrange(0, 360) * math.pi) / 180 # Asigna una orientación aleatoria
        self.timer = timer

    def update(self, sells):
        """Actualiza al Chon en su cronómetro interno y su posición"""
        # Aumenta el contador de tiempo de gracia para no ser absorbido inmediatamente
        if self.timer < MERCY_TIME:
            self.timer += 1
        
        self.move(sells)    # Mueve el Chon

    def move(self, sells):
        """Mueve al Chon"""
        step = (random.randrange(-15, 15) * math.pi) / 180  # Calcula el vector de cambio
        # Traduce el vector de cambio en cambio de coordenadas
        xstep = 4*math.cos(self.theta+step) 
        ystep = 4*math.sin(self.theta+step)
        
        next_pos = [self.real_pose[0] + xstep, self.real_pose[1] + ystep]   # Actualiza las coordenadas reales
        next_pos = check_boundaries(next_pos)   # Checa que la nueva posición caiga dentro de la pantalla

        pos = [round(next_pos[0], -1), round(next_pos[1], -1)]  # Ajusta la posición discreta
        pos = check_boundaries(pos) # Checa que la nueva posición caiga dentro de la pantalla

        collide = sprite_collisions(sells, pos) # Regresa True si exite una Selula que esté en la nueva locación
                
        # Solo muévelo si no choca con otra cosa
        if not collide:
            self.rect.x = pos[0]
            self.rect.y = pos[1]
            self.real_pose = next_pos
    
def new_chon(chon_sprites, pos=None, timer = 0):
    """Crea un nuevo Chon y agrégalo a la lista de Chons"""
    s = Chon(pos=pos, timer=timer)
    chon_sprites.add(s)

def kill_n_chons(chon_sprites, number2kill = 1):
    """Kill n Chons de la lista de Chons"""
    for i in range(number2kill):
        chsp = chon_sprites.sprites()
        if len(chsp) > 0:
            chsp[0].kill()