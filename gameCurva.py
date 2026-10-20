import sys
import pygame
import sprite
import Tilemap

x0 = 0
y0 = 500
x1 = 250
y1 = 120
x2 = 550
y2 = 120
x3 = 800
y3 = 600

t : float = 0

def bezier_cubo (t:float):
    x: float = pow ( 1 - t, 3) * x0 + 3 * pow (1 - t, 2) * t * x1 + 3 * (1 - t) * pow (t,2) * x2 + pow(t,3) * x3
    y: float = pow (1 -t, 3) * y0 + 3 * pow (1 - t, 2) * t * y1 + 3 * (1 - t) * pow (t , 2) * y2 + pow( t, 3) * y3


mapa = [
    [16,16,16,16,16],
    [16,16,16,16,16],
    [16,16,16,16,16],
    [26,16,16,16,16],
    [16,16,16,16,16]
]


pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Hola')

anim_spr = sprite.SpriteAnimado(0,0)
anim_spr.agrego_imagenes("monito1.png")
anim_spr.agrego_imagenes ("monito2.png")

# lista_sprites = []
## lista_sprites.append(sprite.Sprite(  0,   0, './assets/mon.jpg'))
# lista_sprites.append(sprite.Sprite(100, 100, './assets/imagen2.jpg'))

fps = 0
fps_ant = 0
dx = 0

fps_limite = 60

tiempoInicial = pygame.time.get_ticks()
print("Tiempo inicial: ", tiempoInicial)

tile_map = Tilemap.TileMap ("tileset.png",64,64)
gameRunning = True
while gameRunning == True:
    # Este ciclo es para poder cerrar la ventana.
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameRunning = False
 
    screen.fill((0, 0, 0)) # Colorea la pantalla de negro para refrescar los pixeles viejos.

   ## tile_x, tile_y = tile_map.obtengo_coordenada_tile(17)
    
    for renglon in mapa:
        for indice in renglon:
            tile_x, tile_y = tile_map.obtengo_coordenada_tile(indice)
            screen.blit (tile_map.tileset, (0, 0), (tile_x ,0, tile_map.tile_width, tile_map.tite_height))
            coord_x = coord_x + tile_map.tile_width
        coord_x = 0
        coord_y = coord_y + tile_map.tile_height
    
   #  screen.blit (tile_map.tileset, (0, 0), (tile_x ,0, tile_map.tile_width, tile_map.tite_height))   # Carga la imagen en pantalla
   
   
    spr.x , spr.y = bezier_cubo (t)
    
    spr = sprite.Sprite (x0,y0,"imagen1.jpg")
    
    # screen. blit (spr.image, (spr.x, spr.y)) Clase 20/10/2026
    
    t = t + 0.0001
    if (t >= 1):
        t = 1
    
    pygame.display.flip()

    fps += 1                                    # Contador de fps
    tiempoActual = pygame.time.get_ticks()      # Obtiene el tiempo transcurrido total
    if (tiempoActual-tiempoInicial >= 1000):    # Si ya pasó un segundo
        print(fps)                              # Muestra los fps que han pasado
        dx = 100 / fps                          # Calcula el cambio en la posición horizontal
        fps_ant = fps
        fps = 0                                 # Reinicia los fps (ya cumplió su ciclo)
        tiempoInicial = tiempoActual            # Se recalcula el tiempo inicial
        
        




pygame.quit()
sys.exit()