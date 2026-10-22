import pygame

class Tilemap:

    def __init__(self, path, width, height):
        self.tile_witdh = width
        self.tile_height = height
        self.tile_set = pygame.image.load(path).convert()

        img_width, img_height = self.tile_set.get_size()

        self.num_tiles_x = img_width  / self.tile_witdh
        self.num_tiles_y = img_height / self.tile_height

    def obtengo_coordenada_tile(self, tile_index):
        x = (tile_index %  self.num_tiles_x) * self.tile_witdh
        y = (tile_index // self.num_tiles_x) * self.tile_height
        return x, y

    def obtiene_mapa(self, path):
        mapa = []
        with open(path, "r", encoding="utf-8") as f:
            for linea in f:
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue
                elementos_texto = linea_limpia.split()
                renglon_enteros = []
                for elemento in elementos_texto:
                    renglon_enteros.append(int(elemento))
                mapa.append(renglon_enteros)
        return mapa
    
