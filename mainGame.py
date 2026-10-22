import sys
import pygame
import Tilemap

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tiles 13/10/2026')

tilemap = Tilemap.Tilemap("./tileset.png", 64, 64)

mapa = tilemap.obtiene_mapa("./archivoMapa.txt")
mapa2 = tilemap.obtiene_mapa ("./archivoSobreMapa.txt")

fps = 0
fps_ant = 0

tiempoInicial = pygame.time.get_ticks()
print("Tiempo inicial: ", tiempoInicial)
gameRunning = True
while gameRunning == True:
    # Este ciclo es para poder cerrar la ventana.
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameRunning = False

    pygame.display.flip()
    screen.fill((127, 127, 127))      # Colorea la pantalla en gris para refrescar los pixeles viejos.
    coord_x = 0
    coord_y = 0
    for renglon in mapa:
        for indice in renglon:
            
            tile_x, tile_y = tilemap.obtengo_coordenada_tile(indice)
            screen.blit(tilemap.tile_set, (coord_x, coord_y), (tile_x, tile_y, tilemap.tile_witdh, tilemap.tile_height))
            coord_x = coord_x + tilemap.tile_witdh
        coord_x = 0
        coord_y = coord_y + tilemap.tile_height
    coord_x = 0
    coord_y = 0
    for renglon in mapa2:
            for indice in renglon:
                tile_x, tile_y = tilemap.obtengo_coordenada_tile(indice)
                screen.blit(tilemap.tile_set, (coord_x, coord_y), (tile_x, tile_y, tilemap.tile_witdh, tilemap.tile_height))
                coord_x = coord_x + tilemap.tile_witdh
            coord_x = 0
            coord_y = coord_y + tilemap.tile_height

    fps = fps + 1                               # Contador de fps
    tiempoActual = pygame.time.get_ticks()      # Obtiene el tiempo transcurrido total
    if (tiempoActual-tiempoInicial >= 1000):    # Si ya pasó un segundo
        print(fps)                              # Muestra los fps que han pasado
        fps_ant = fps
        fps = 0                                 # Reinicia los fps (ya cumplió su ciclo)
        tiempoInicial = tiempoActual            # Se recalcula el tiempo inicial

pygame.quit()
sys.exit()