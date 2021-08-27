import pygame
import random
import math
from pygame.locals import *
from general_functions import *
from sell import *
from chon import *


class App:
    
    def __init__(self):
        """Inicializa el simulador"""
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = WIDTH, HEIGHT # Asigna el tamanio de la pantalla
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('SimEvol')   # Titulo de la ventana

        
    def on_init(self):
        """Cuando se inicializa el la simulación, iniciliza los componentes, carga el fondo, 
        y crea los Sprites"""
        pygame.init()   # inicializa el simulador interno
        self.font = pygame.font.SysFont('mono', 8)
        #self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        self._running = True    # Si todo sale bien, prende la bandera de que esta corriendo
        

        # Carga la imagen de fondo
        self.background = pygame.image.load('background.bmp').convert() 
        self._display_surf.blit(self.background, (0,0))

        pygame.display.flip()

        # Inicializa las listas de Sprites
        self.chon_sprites = pygame.sprite.RenderUpdates()
        self.sell_sprites = pygame.sprite.RenderUpdates()
        self.text_sprites = pygame.sprite.RenderUpdates()

        # Crea las Selulas
        for _ in range(START_SELLS):
            new_sell(self._display_surf, self.sell_sprites, self.text_sprites, 
            None)

        # Crea los Chons
        for _ in range(START_CHONS):
            new_chon(self.chon_sprites, None, 10)

        # Crea los Sprites de texto
        self.chons_txt = RenderText(
            self._display_surf, '', size=18, pos=[50, 50],
            pos_rel=(LEFT, TOP))    # Este es el contador general
        self.text_sprites.add(self.chons_txt)

    def on_event(self, event):
        """Revisa si hay algun evento pendiente y ejecutalo"""
        # Checa si se cierra la ventana o se aprieta Esc
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self._running = False 
        # Si se aprieta Enter, crea una nueva Selula    
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            kill_n_chons(self.chon_sprites, INITIAL_CHONS)
            new_sell(self._display_surf, self.sell_sprites, 
            self.text_sprites, None)
        
    def on_loop(self):
        pass
        

    def on_render(self):
        pass
        

    def on_cleanup(self):
        """Una vez terminada la simulacion, cierra todo"""
        pygame.quit()
 
    def on_execute(self):
        """Ejecuta el simulador"""
        # Inicializa todo y si hay algun error detiene el simulador
        if self.on_init() == False:
            self._running = False
 
        # Ejecuta seccion mientras el simulador corra sin interrupciones       
        while( self._running ):
            self.clock.tick(6)  # La velocidad del simulador. 
            # Revisa si hay eventos pendientes y ejecutalos
            for event in pygame.event.get():
                self.on_event(event)

            # Limpia la pantalla y redibuja el fondo
            self.sell_sprites.clear(self._display_surf, self.background)
            self.chon_sprites.clear(self._display_surf, self.background)
            self.text_sprites.clear(self._display_surf, self.background)

            # Llama los metodos de actualizacion de los Sprites
            self.sell_sprites.update(self.sell_sprites, self.chon_sprites, self.text_sprites, self._display_surf)
            self.chon_sprites.update(self.sell_sprites)
            self.chons_txt.print_text(str(len(self.chon_sprites.sprites())) + " " + str(len(self.sell_sprites.sprites())))
            
            # Redibuja los Sprites
            dirty = self.sell_sprites.draw(self._display_surf)
            dirty += self.chon_sprites.draw(self._display_surf)
            dirty += self.text_sprites.draw(self._display_surf)

            pygame.display.flip()
            # Metodos necesarios pero vacios
            self.on_loop()
            self.on_render()
        # Una vez terminada la simulacion, cierra todo
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()  # Crea el simulador
    theApp.on_execute() # Inicia el simulador