import pygame
import Tilemap


def obtener_tiles_solidos():
    # Los extremos de cada rango tambien son solidos.
    rangos = [(0, 96), (98, 111), (114, 125), (130, 148),
              (153, 164), (169, 180), (185, 185), (187, 195),
              (206, 211), (222, 227), (238, 239), (243, 246),
              (249, 255)]
    solidos = set()
    for inicio, fin in rangos:
        solidos.update(range(inicio, fin + 1))
    return solidos


def cargar_mapa_principal():
    # Llamar despues de crear la ventana de Pygame.
    mapa = Tilemap.Tilemap("./tileset.png", 64, 64)
    # Conserva la transparencia sin cambiar el constructor existente.
    mapa.tile_set = pygame.image.load("./tileset.png").convert_alpha()
    mapa.preparar_mapa("./archivoMapa.txt", "./archivoSobreMapa.txt",
                      obtener_tiles_solidos())
    return mapa


def cargar_mapa_misterio(nombre):
    # Los mapas nuevos usan archivos separados de los originales.
    if nombre not in ("bosque", "claro"):
        raise ValueError("El mapa debe ser bosque o claro.")
    mapa = Tilemap.Tilemap("./tileset.png", 64, 64)
    mapa.tile_set = pygame.image.load("./tileset.png").convert_alpha()
    mapa.preparar_mapa("./mapas/" + nombre + "_piso.txt",
                      "./mapas/" + nombre + "_objetos.txt",
                      obtener_tiles_solidos())
    return mapa


def obtener_puntos_misterio():
    # Todas las posiciones son casillas (columna, fila), desde cero.
    return {
        "bosque": {
            "inicio": (5, 16),
            "pistas": [
                {"clave": "casa_verde", "casilla": (5, 6),
                 "texto": "Primera cifra: 3. Busca la casa roja y el letrero del claro."},
                {"clave": "casa_roja", "casilla": (22, 6),
                 "texto": "Segunda cifra: 1. El letrero del claro tiene la ultima."},
            ],
            "salidas": [
                {"casillas": [(29, 10), (29, 11)], "destino": "claro",
                 "entrada": (2, 10)},
            ],
        },
        "claro": {
            "inicio": (2, 10),
            "pistas": [
                {"clave": "letrero_claro", "casilla": (8, 6),
                 "texto": "Ultima cifra: 4. El barril guarda la llave del guardabosques."},
            ],
            "salidas": [
                {"casillas": [(0, 10), (0, 11)], "destino": "bosque",
                 "entrada": (27, 10)},
            ],
            "objetivo": {
                "casilla": (18, 6), "objeto": (18, 5), "solucion": "314",
                "pistas_necesarias": ["casa_verde", "casa_roja", "letrero_claro"],
            },
        },
    }
