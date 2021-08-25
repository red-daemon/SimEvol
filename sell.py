import pygame
import random
import math
from pygame.locals import *
from general_functions import *
from text_render import *
from chon import *

NSELLS = 0

# ToDo: reproduccion, color, absorber, mover, soltar


class Sell(pygame.sprite.Sprite):
    def __init__(self, text_sprite, id, pos=None, height=None, width=None):
        """Inicializa una Selula.
        
        Recibe el Sprite de texto, el identificador, la posicion inicial, 
        y las dimensiones de la pantalla para no pasar los bordes."""
        pygame.sprite.Sprite.__init__(self) # Inicializa el Sprite
        self.id = id    # Asigna identificador
        self.image = pygame.image.load('sell.bmp').convert()    # Carga la imagen de la Selula
        # Crea y asigna el rectángulo contenedor de la imagen
        self.rect = self.image.get_rect()

        # Si no se le asigna una posición, asigna una aleatoria
        if not pos:
            self.rect = self.rect.move(random.randrange(0, WIDTH, 10), random.randrange(0, HEIGHT, 10))
        else: 
            self.rect = self.rect.move(pos[0], pos[1])
        # Guarda las coordenadas del la imagen
        self.real_pose = [self.rect.x, self.rect.y]
        # Genera la orientacion de la Selula de forma aleatoria
        self.theta = (random.randrange(0, 360) * math.pi) / 180

        self.ners = 1.0     # Unidades de energia iniciales
        self.nuts = 1.0     # Nutrientes iniciales
        self.nchons = 0     # Chons iniciales
        self.total_chons = 0        #   Chons totales
        self.text_sprite = text_sprite      # Sprite de texto de datos
    
    def update(self, sells, chons, texts, screen):
        """Actualiza los valores de la Selula, gasta nutrientes y recibe energía del sol, 
        absorbe los Chons de su vecindad, digiere los chons en reserva, reprodúcelo, 
        muévelo, actualiza el texto, y mátalo si es necesario."""
        self.nuts -= 1/24.0     # Cada dia pierde 1 NUTS de nutrientes
        self.ners += 1/24.0     # Cada dia gana 1 NERS de energia
        self._absorb_chon(chons)    # Si hay un Chon cerca, absórbelo
        self._convert_chon()    # Convierte un Chon en nutrientes
        self._reproduce(sells, texts, screen)   # Si tienen suficientes nutrientes y energía, crea una nueva Selula en su vecindad

        self._move(sells)   # Mueve la Selula a una nueva posición
        self._update_data() # Obtiene los nuevos datos para mostrarlos en pantalla
        self._death(chons)  # Determina si debe morir y, en su caso, elimina la Selula
        

    def _death(self, chons):
        """Determina si debe morir y, en su caso, elimina la Selula"""
        # Al acabarse los nutrientes, muere
        if self.nuts < 0:
            # Al morir se dispersa en unidades de nutrientes predefinidos
            for _ in range(CHONS_DECOMPSED):
                s = Chon([self.rect.x, self.rect.y])
                chons.add(s)
            # Se elimina la Selula y su sprite de texto
            self.text_sprite.kill()
            self.kill()

    def _update_data(self, coord = False):
        """Obtiene los nuevos datos para mostrarlos en pantalla"""
        # Checa si se desean mostrar las coordenadas o no
        if coord:
            self.data = "{:d} {:d} {:0.2f} {:0.2f} - ({:d}, {:0d})".format(
                self.total_chons, self.nchons, self.nuts, self.ners, 
                int(self.real_pose[0]), int(self.real_pose[1])) 
        else:
            self.data = "{:d} {:d} {:0.2f} {:0.2f}".format(
                self.total_chons, self.nchons, self.nuts, self.ners) 
        
        # Prepara el render del texto en la locación de la Selula
        self.text_sprite.print_text(self.data, [int(self.real_pose[0]), int(self.real_pose[1])])

    def _move(self, sells):
        """
        Mueve la Selula a una nueva posición
        """
        # Calcula direccion aleatoria de movimiento 
        step = (random.randrange(-15, 15) * math.pi) / 180  
        xstep = math.cos(self.theta+step)/10 
        ystep = math.sin(self.theta+step)/10

        # Calcula la nueva posicion de la Selula
        next_pos = [self.real_pose[0] + xstep, self.real_pose[1] + ystep]
        next_pos = check_boundaries(next_pos)   # Checa que no se salga de los bordes
        pos = [round(next_pos[0], -1), round(next_pos[1], -1)]  # Obtiene las coordenadas válidas de la nueva locación
        pos = check_boundaries(pos) # Checa que no se salga de los bordes

        collide = sprite_collisions(sells, pos, self.id)    # Checa si al moverse choca con otra Selula

        # Si no choca con nadie, se mueve a la nueva posición        
        if not collide:
            self.rect.x = pos[0]
            self.rect.y = pos[1]
            self.real_pose = next_pos   # Guarda la posición real de la Selula

    def _absorb_chon(self, chons):
        """Si un Chon se acerca, absorbelo"""
        # Checa que los Chons que ha absorbido sean menos que el limite
        if self.nchons < MAX_CHONS:
            # Busca si hay un Chon en su vecindad
            chon2absorb = sprite_neighbors(chons.sprites(), self.rect)
            # Ejecuta si lo encuentra y ademas está a punto de moverse
            if chon2absorb and chon2absorb.timer == 10: # Un Chon solo puede absorberse después de los primeros 10 segundos
                chon2absorb.kill()  # Mata al Chon
                self.nchons += 1    # Agrega 1 al contador de Chons que tiene adentro
                self.total_chons += 1   # Agrega 1 al contador de Chons absorbidos totales

                dlt = pick_direction()    # Obten una posición aleatoria en la vecindad
                pos = [self.rect.x+dlt[0], self.rect.y+dlt[1]]
                s = Chon(pos=pos)   # Crea un nuevo Chon en la posición obtenida 
                chons.add(s)
    
    def _convert_chon(self):
        """Convierte un Chon en nutrientes si tiene Chons para digerir y suficiente enrgía para hacerlo"""
        # Checa que haya al menos un Chon sin digerir y suficiente energía para hacerlo
        if self.nchons > 0 and self.ners >= COST_DIGEST:
            self.ners -= COST_DIGEST    # Utiliza la energía para digerir
            self.nchons -= 1    # Elimina el Chon a digerir
            self.nuts += 1  # Aumenta el contador de nutrientes

def _reproduce(self, sells, texts, screen):
        """Si tienen suficientes nutrientes y energía, crea una nueva Selula en su vecindad"""
        # Checa que tenga suficientes nutrientes y energía para la reproducción
        if self.nuts >= MAX_NUTS and self.ners >= REPRODUCTION_ENERGY_COST:
            self.ners -= 1  # Usa la energía
            self.nuts -= 1  # Usa los nutrientes

            # Escoge una locación en la vecindad
            dlt = pick_direction()    
            pos = [self.rect.x+dlt[0], self.rect.y+dlt[1]]
            pos = check_boundaries(pos) # Asegura que la nueva locación esté dentro de la pantalla
            opos = pos
            # Itera hasta encontrar una locación donde no hayan otros Sprites
            collide = sprite_collisions(sells, pos)
            # Si hay otro Sprite en la locación escogida, intentarlo un paso más lejos en la misma dirección
            while collide:
                pos = [pos[0] + dlt[0], pos[1] + dlt[1]]
                pos = check_boundaries(pos)
                
                # En caso de que toda la linea esté llena, deja de intentarlo
                if pos == opos: 
                    break
                collide = sprite_collisions(sells, pos)

            # Si encuentra una locación libre, crea una nueva Selula ahí
            if not collide:
                new_sell(screen, sells, texts, pos)


def new_sell(screen, sell_sprites, text_sprites, pos=None, height=None, width=None):
    """Crea una nueva Selula, la grega a la lista de Sprites e incrementa el contador"""
    global NSELLS   # Usa el contador global de Selulas
    
    # Crea el texto para los datos de la nueva Selula
    text = RenderText(
        screen, '', size=12, pos=[50, 50+10*NSELLS],
        pos_rel=(RIGHT, BOTTOM))
    text_sprites.add(text)
    
    s = Sell(text, NSELLS, pos, height, width)  # Crea una nueva Selula
    sell_sprites.add(s) # Agrega la Selula a la lista de Sprites
    NSELLS += 1 # Incrementa el contador de Selulas