from collections import deque


def buscar_ruta(tilemap, inicio, destino):
    # Las posiciones son (columna, fila), no pixeles.
    if tilemap.es_solido(*inicio) or tilemap.es_solido(*destino):
        return []

    pendientes = deque([inicio])
    anteriores = {inicio: None}

    while pendientes:
        actual = pendientes.popleft()
        if actual == destino:
            break

        columna, fila = actual
        vecinos = [(columna + 1, fila), (columna - 1, fila),
                   (columna, fila + 1), (columna, fila - 1)]
        for vecino in vecinos:
            if vecino not in anteriores and not tilemap.es_solido(*vecino):
                anteriores[vecino] = actual
                pendientes.append(vecino)

    if destino not in anteriores:
        return []

    # Reconstruye el camino desde el destino.
    ruta = []
    actual = destino
    while actual != inicio:
        ruta.append(actual)
        actual = anteriores[actual]
    ruta.reverse()
    return ruta


def obtener_puntos_ruta(tilemap, ruta):
    # Devuelve el centro de cada casilla en pixeles del mapa.
    puntos = []
    for columna, fila in ruta:
        x = columna * tilemap.tile_witdh + tilemap.tile_witdh / 2
        y = fila * tilemap.tile_height + tilemap.tile_height / 2
        puntos.append((x, y))
    return puntos
