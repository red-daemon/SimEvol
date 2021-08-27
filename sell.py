import pygame
import random
import math
from pygame.locals import *
from general_functions import *
from text_render import *
from chon import *

NSELLS = 0

# ToDo: color, absorber, mover, soltar


class Sell(pygame.sprite.Sprite):
    def __init__(self, screen, text_sprite, id, pos=None, theta=None):
        """Inicializa una Selula.
        
        Recibe el Sprite de texto, el identificador, la posicion inicial, 
        y las dimensiones de la pantalla para no pasar los bordes."""
        pygame.sprite.Sprite.__init__(self) # Inicializa el Sprite
        self.id = id    # Asigna identificador
        
        # Si no se le asigna una posición, asigna una aleatoria
        if not pos:
            ##self.rect = self.rect.move(random.randrange(0, WIDTH, 10), random.randrange(0, HEIGHT, 10))
            nx = random.randrange(0, WIDTH, 10)
            ny = random.randrange(0, HEIGHT, 10)
        else: 
            ##self.rect = self.rect.move(pos[0], pos[1])
            nx = pos[0]
            ny = pos[1]

        radius = 5
        self.image = pygame.Surface([radius*2, radius*2])
        self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        
        pygame.draw.circle(self.image, (0, 0, 255), (radius, radius), radius)
        ##self.image = pygame.image.load('sell.bmp').convert()    # Carga la imagen de la Selula
        # Crea y asigna el rectángulo contenedor de la imagen
        self.rect = self.image.get_rect(center=(nx,ny))

        # Guarda las coordenadas del la imagen
        self.real_pose = [self.rect.x, self.rect.y]
        # Genera la orientacion de la Selula de forma aleatoria
        if not theta:
            self.theta = (random.randrange(0, 360) * math.pi) / 180
        else:
            self.theta = theta
            self._adjust_theta()

        self.speed = 0.5

        self.ners = INITIAL_NERS     # Unidades de energia iniciales
        self.nuts = INITIAL_NUTS     # Nutrientes iniciales
        self.nchons = INITIAL_CHONS     # Chons iniciales
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

        self._set_theta()   # Modifica la orientación
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
            self.data = "{:d} {:d} {:0.2f} {:0.2f} ({:0.1f}, {:0.1f}) {:0.1f}".format(
                self.nchons, 
                self.total_chons, 
                self.nuts, self.ners, 
                int(self.real_pose[0]), int(self.real_pose[1]),
                (self.theta*180)/math.pi) 
        else:
            self.data = "{:d} {:d} {:0.2f} {:0.2f} {:0.1f}".format(
                self.nchons, 
                self.total_chons, 
                self.nuts, self.ners,
                (self.theta*180)/math.pi) 
        
        # Prepara el render del texto en la locación de la Selula
        self.text_sprite.print_text(self.data, [int(self.real_pose[0]), int(self.real_pose[1])])

    def _move(self, sells):
        """
        Mueve la Selula a una nueva posición
        """
        # Calcula la nueva posición enfunción de la orientación y la velocidad
        xstep = math.cos(self.theta) * self.speed
        ystep = math.sin(self.theta) * self.speed

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

    def _set_theta(self, delta = None):
        """Modifica la orientación"""
        if not delta:
            delta = (random.randrange(-15, 15) * math.pi) / 180  # Delta del ángulo en radianes
        self.theta += delta
        
        self._adjust_theta()

    def _adjust_theta(self):
        if self.theta > 2 * math.pi:
            self.theta -= 2 * math.pi
        if self.theta < 0:
            self.theta += 2 * math.pi

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
        if self.nuts <= 0 and self.nchons > 0 and self.ners >= COST_DIGEST:
            self.ners -= COST_DIGEST    # Utiliza la energía para digerir
            self.nchons -= 1    # Elimina el Chon a digerir
            self.nuts += 1  # Aumenta el contador de nutrientes

    def _reproduce(self, sells, texts, screen):
        """Para reproducirse debe tener N Chons, y sepárala en dos Selulas con la mitad cada una, 
        que surjan en el mismo lugar, pero con orientaciones opuestas
        """
        # Checa que tenga suficientes Chons y energía para la reproducción
        if self.nchons >= CHONS_FOR_REPRODUCTION and self.ners >= REPRODUCTION_ENERGY_COST:
            self.ners -= REPRODUCTION_ENERGY_COST  # Usa la energía
            self.nchons -= CHONS_FOR_REPRODUCTION // 2    # Usa los chons

            # Crea una nueva Selula en la misma locación, pero con la orientación opuesta
            new_sell(screen, sells, texts, [self.rect.x, self.rect.y], theta=self.theta+ math.pi/2)
            
            # Asigna una orientación perpendicualar a la actual
            self._set_theta(self.theta - math.pi/2)

def new_sell(screen, sell_sprites, text_sprites, pos=None, theta = None):
    """Crea una nueva Selula, la grega a la lista de Sprites e incrementa el contador"""
    global NSELLS   # Usa el contador global de Selulas
    
    # Crea el texto para los datos de la nueva Selula
    text = RenderText(
        screen, '', size=12, pos=[50, 50+10*NSELLS],
        pos_rel=(RIGHT, BOTTOM))
    text_sprites.add(text)
    
    s = Sell(screen, text, NSELLS, pos, theta)  # Crea una nueva Selula
    sell_sprites.add(s) # Agrega la Selula a la lista de Sprites
    NSELLS += 1 # Incrementa el contador de Selulas