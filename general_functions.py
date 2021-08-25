import random

LEFT, CENTER, RIGHT = range(3)
TOP, MIDDLE, BOTTOM = range(3)
WIDTH = 800
HEIGHT = 600

START_SELLS = 1
START_CHONS = 0

MAX_CHONS = 4
MAX_NUTS = 4
COST_DIGEST = 0.6
REPRODUCTION_ENERGY_COST = 1
CHONS_DECOMPSED = 3

def sprite_collisions(sprites, pos, id = -1):
    """Regresa True si exite otro Sprite que esté en la locación 'pos'"""
    collide = False
    for i, s in enumerate(sprites):
        if id == i: 
            continue
        if s.rect.x == pos[0] and s.rect.y == pos[1]:
            collide = True
            break

    return collide
 
def sprite_neighbors(sprites, pos):
    """Busca en la lista de sprites el primero que este en la vecindad y regresalo"""
    neighbors = None
    for s in sprites:
        if abs(s.rect.x - pos.x) <= 10 and abs(s.rect.y - pos.y) <= 10:
            neighbors = s
            break

    return neighbors

def check_boundaries(next_pos):
    """Si la nueva posición se sale del borde, regresa la posición del lado opuesto de la pantalla"""
    if next_pos[1] >= HEIGHT:
        next_pos[1] -= HEIGHT
    elif next_pos[1] < 0:
        next_pos[1] += HEIGHT
    
    if next_pos[0] >= WIDTH:
        next_pos[0] -= WIDTH
    elif next_pos[0] < 0:
        next_pos[0] += WIDTH

    return next_pos

def pick_direction():
    """Selecciona una dirección aleatoria en la vecindad de una Selula"""
    d = random.randint(0,7)
    # d=0
    if d == 0:
        dlt = [10, 0]
    elif d == 1:
        dlt = [10, 10]
    elif d == 2:
        dlt = [0, 10]
    elif d == 3:
        dlt = [-10, 10]
    elif d == 4:
        dlt = [-10, 0]
    elif d == 5:
        dlt = [-10, -10]
    elif d == 6:
        dlt = [10, -10]
    elif d == 7:
        dlt = [0, -10]
    
    return dlt