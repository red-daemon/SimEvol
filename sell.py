import pygame
import random
import math
from pygame.locals import *
from general_functions import *
from text_render import *
from chon import *

NSELLS = 0

# ToDo: visión, tamanio

class Sell(pygame.sprite.Sprite):
    def __init__(self, screen, text_sprite, id, pos=None, theta=None, color=None):
        """Inicializa una Selula.
        
        Recibe el Sprite de texto, el identificador, la posicion inicial, 
        y las dimensiones de la pantalla para no pasar los bordes.
        Al crearse, asígnale un color aleatorio para que lo herede a sus clones"""
        pygame.sprite.Sprite.__init__(self) # Inicializa el Sprite
        self.id = id    # Asigna identificador

        # Si no se le asigna una posición, asigna una aleatoria
        if not pos:
            ##self.rect = self.rect.move(random.randrange(0, WIDTH, 10), random.randrange(0, HEIGHT, 10))
            nx = random.randrange(0, WIDTH, 10)
            ny = random.randrange(0, HEIGHT, 10)
        else: 
            nx = pos[0]
            ny = pos[1]

        radius = 5
        self.image = pygame.Surface([radius*2, radius*2])
        self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        
        # Asigna color aleatorio como atributo de la Selula
        if not color:
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            self.color = (r,g,b)
        else:
            self.color = color

        pygame.draw.circle(self.image, self.color, (radius, radius), radius)
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

        self.speed = 1

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
        self._convert_chon(chons)    # Convierte un Chon en nutrientes
        self._reproduce(sells, texts, screen)   # Si tienen suficientes nutrientes y energía, crea una nueva Selula en su vecindad

        self._change_vector(self._delta_theta())   # Modifica la orientación
        self._move(sells)   # Mueve la Selula a una nueva posición
        self._update_data() # Obtiene los nuevos datos para mostrarlos en pantalla
        self._death(chons)  # Determina si debe morir y, en su caso, elimina la Selula
        

    def _death(self, chons):
        """Determina si debe morir y, en su caso, elimina la Selula. 
        Cuando muere, has que suelte el mismo numero de chons que tiene adentro al morir"""
        # Al acabarse los nutrientes, muere
        if self.nuts < 0:
            # Al morir suelta los Chons que contiene adentro
            for _ in range(self.nchons):
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
            self.data = "{:d} {:0.2f} {:0.2f}".format(
                self.nchons, 
                self.nuts, self.ners) 
    
        # Prepara el render del texto en la locación de la Selula
        self.text_sprite.print_text(self.data, [int(self.real_pose[0]), int(self.real_pose[1])])

    def _move(self, sells):
        """
        Mueve la Selula a una nueva posición. Moverse cuesta energía y nutrientes

        """
        # Calcula la nueva posición enfunción de la orientación y la velocidad
        xstep = math.cos(self.theta) * self.speed
        ystep = math.sin(self.theta) * self.speed

        # La energía y los nutrientes se gastan proporcionalmente a la velocidad. 
        self.ners -= (MOVE_ENERGY_COST * self.speed) - MOVE_ENERGY_COST
        self.nuts -= (MOVE_NUTS_COST * self.speed) - MOVE_NUTS_COST

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

    def _change_vector(self, d_theta=None, d_speed=None):
        """Modifica el vector de movimiento dados los cmabios en orientación y velocidad"""
        if d_theta:
            self.theta += d_theta 
        if d_speed:
            self.speed += d_speed

    def _delta_theta(self, rango=15):
        """Calcula el cambio del ángulo en radianes dentro del rango dado (en grados)"""
        return (random.randrange(-rango, rango) * math.pi) / 180  

    def _adjust_theta(self):
        """Checa que el ángulo de la orientación se mantenga en rango de 0 a 360 grados"""
        if self.theta > 2 * math.pi:
            self.theta -= 2 * math.pi
        if self.theta < 0:
            self.theta += 2 * math.pi

    def _absorb_chon(self, chons):
        """Si un Chon se acerca, absorbelo.
        La decisión de absorber un Chon o no, es independiente de la acción"""
        # Busca si hay un Chon en su vecindad
        chon2absorb = sprite_neighbors(chons.sprites(), self.rect)
        # Checa que los Chons que ha absorbido sean menos que el limite
        if chon2absorb:
            self._absorb(chon2absorb)   # Agrega 1 al contador de Chons absorbidos totales

    def _absorb(self, chon2absorb):
        """Verifica las condiciones necesarias para poder absorber un Chon, y lo mata al hacerlo"""
        # Checa que los Chons que ha absorbido sean menos que el limite
        # Un Chon solo puede absorberse después de los primeros 10 segundos
        if self.nchons < MAX_CHONS and chon2absorb.timer == 10: 
            # Ejecuta si lo encuentra y ademas está a punto de moverse
                chon2absorb.kill()  # Mata al Chon
                self.nchons += 1    # Agrega 1 al contador de Chons que tiene adentro
                self.total_chons += 1   # Agrega 1 al contador de Chons absorbidos totales

    def _convert_chon(self, chons):
        """Convierte un Chon en nutrientes si tiene Chons para digerir y suficiente enrgía para hacerlo.
        Al digerir un Chon, suelta uno nuevo que no puede ser comido inmediatamente"""
        # Checa que haya al menos un Chon sin digerir y suficiente energía para hacerlo
        if self.nuts <= 0 and self.nchons > 0 and self.ners >= COST_DIGEST:
            self._release(chons) # Suelta el Chon que va a consumir
            
            self.ners -= COST_DIGEST    # Utiliza la energía para digerir
            self.nchons -= 1    # Elimina el Chon a digerir
            self.nuts += 1  # Aumenta el contador de nutrientes
            

    def _release(self, chons):
        """Suelta Chons que tenga adentro, bajando el contador y creando uno nuevo"""
        if self.nchons > 0:
            dlt = pick_direction()    # Obten una posición aleatoria en la vecindad
            pos = [self.rect.x+dlt[0], self.rect.y+dlt[1]]
            s = Chon(pos=pos)   # Crea un nuevo Chon en la posición obtenida 
            chons.add(s)

    def _reproduce(self, sells, texts, screen):
        """Para reproducirse debe tener N Chons, y sepárala en dos Selulas con la mitad cada una, 
        que surjan en el mismo lugar, pero con orientaciones opuestas
        """
        # Checa que tenga suficientes Chons y energía para la reproducción
        if self.nchons >= CHONS_FOR_REPRODUCTION and self.ners >= REPRODUCTION_ENERGY_COST:
            self.ners -= REPRODUCTION_ENERGY_COST  # Usa la energía
            self.nuts -= REPRODUCTION_NUTS_COST  # Usa la energía
            self.nchons -= CHONS_FOR_REPRODUCTION // 2    # Usa los chons

            # Modifica un poco el color para la nueva Sélula
            rgb = modify_color(self.color)

            # Crea una nueva Selula en la misma locación, pero con la orientación opuesta
            new_sell(screen, sells, texts, [self.rect.x, self.rect.y], 
                     theta=self.theta+ math.pi/2, color=rgb)
            
            # Asigna una orientación perpendicualar a la actual
            self._change_vector(self.theta - math.pi/2)

def new_sell(screen, sell_sprites, text_sprites, pos=None, theta = None, color=None):
    """Crea una nueva Selula, la grega a la lista de Sprites e incrementa el contador"""
    global NSELLS   # Usa el contador global de Selulas
    
    # Crea el texto para los datos de la nueva Selula
    text = RenderText(
        screen, '', size=12, pos=[50, 50+10*NSELLS],
        pos_rel=(RIGHT, BOTTOM))
    text_sprites.add(text)
    
    s = Sell(screen, text, NSELLS, pos, theta, color)  # Crea una nueva Selula
    sell_sprites.add(s) # Agrega la Selula a la lista de Sprites
    NSELLS += 1 # Incrementa el contador de Selulas