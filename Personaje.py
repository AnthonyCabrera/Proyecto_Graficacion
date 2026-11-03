import math
import pygame
from Sprite import SpriteAnimado
from Navegacion import buscar_ruta, obtener_puntos_ruta


class Personaje(SpriteAnimado):

    def __init__(self, x, y, rutas_imagenes, velocidad=160, tiempo_frame=0.15):
        super().__init__(x, y)
        if velocidad <= 0 or tiempo_frame <= 0:
            raise ValueError("La velocidad y el tiempo por imagen deben ser positivos.")
        self.velocidad = velocidad
        self.cambio = tiempo_frame
        self.indice_actual = 0
        self.ruta = []
        self.cargar_animacion(rutas_imagenes)

    def cargar_animacion(self, rutas_imagenes):
        # Todos los cuadros deben tener el mismo tamano.
        imagenes = []
        for path in rutas_imagenes:
            imagen = pygame.image.load(path).convert_alpha()
            if imagenes and imagen.get_size() != imagenes[0].get_size():
                raise ValueError("Las imagenes del personaje deben medir lo mismo.")
            imagenes.append(imagen)
        if not imagenes:
            raise ValueError("Agrega al menos una imagen para el personaje.")
        self.lista_imagenes = imagenes
        self.ancho, self.alto = imagenes[0].get_size()
        self.detener()

    def detener(self):
        self.ruta = []
        self.cont = 0
        self.indice_actual = 0

    def hay_solidos(self, tilemap, izquierda, arriba, derecha, abajo):
        # Revisa las casillas que toca el area, sin contar solo el borde.
        columna_inicial = math.floor(izquierda / tilemap.tile_witdh)
        columna_final = math.ceil(derecha / tilemap.tile_witdh)
        fila_inicial = math.floor(arriba / tilemap.tile_height)
        fila_final = math.ceil(abajo / tilemap.tile_height)
        for fila in range(fila_inicial, fila_final):
            for columna in range(columna_inicial, columna_final):
                if tilemap.es_solido(columna, fila):
                    return True
        return False

    def colisiona_con_mapa(self, tilemap, x=None, y=None):
        if x is None:
            x = self.x
        if y is None:
            y = self.y
        return self.hay_solidos(tilemap, x, y, x + self.ancho, y + self.alto)

    def colocar_en_mapa(self, x, y, tilemap):
        # Usa coordenadas de la esquina superior izquierda.
        if self.ancho > tilemap.tile_witdh or self.alto > tilemap.tile_height:
            raise ValueError("El personaje debe caber dentro de un tile.")
        if self.colisiona_con_mapa(tilemap, x, y):
            raise ValueError("La posicion del personaje esta bloqueada.")
        self.x = x
        self.y = y
        self.detener()

    def mover_a(self, x_pantalla, y_pantalla, tilemap):
        x, y = tilemap.pantalla_a_mapa(x_pantalla, y_pantalla)
        return self.establecer_destino(x, y, tilemap)

    def establecer_destino(self, x, y, tilemap):
        # El centro del personaje llegara al punto seleccionado.
        if self.ancho > tilemap.tile_witdh or self.alto > tilemap.tile_height:
            raise ValueError("El personaje debe caber dentro de un tile.")
        if self.colisiona_con_mapa(tilemap):
            return False
        if self.colisiona_con_mapa(tilemap, x - self.ancho / 2,
                                  y - self.alto / 2):
            return False

        centro_x = self.x + self.ancho / 2
        centro_y = self.y + self.alto / 2
        inicio = (math.floor(centro_x / tilemap.tile_witdh),
                  math.floor(centro_y / tilemap.tile_height))
        destino = (math.floor(x / tilemap.tile_witdh),
                   math.floor(y / tilemap.tile_height))
        casillas = buscar_ruta(tilemap, inicio, destino)
        if inicio != destino and not casillas:
            return False

        puntos = []
        if inicio != destino:
            # Primero se centra para no cortar las esquinas de los obstaculos.
            puntos = obtener_puntos_ruta(tilemap, [inicio] + casillas)
        puntos.append((x, y))
        self.ruta = []
        anterior = (centro_x, centro_y)
        for punto in puntos:
            if punto != anterior:
                self.ruta.append(punto)
                anterior = punto
        return True

    def procesar_evento(self, evento, tilemap):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            return self.mover_a(*evento.pos, tilemap)
        return False

    def actualizar_animacion(self, delta):
        if delta < 0:
            raise ValueError("Delta no puede ser negativo.")
        self.cont += delta
        while self.cont >= self.cambio or math.isclose(self.cont, self.cambio):
            self.cont = max(0, self.cont - self.cambio)
            self.indice_actual = (self.indice_actual + 1) % len(self.lista_imagenes)

    def actualizar(self, delta, tilemap):
        if delta < 0:
            raise ValueError("Delta no puede ser negativo.")
        disponible = self.velocidad * delta
        tiempo_movido = 0
        while self.ruta and disponible > 0:
            destino_x, destino_y = self.ruta[0]
            destino_x -= self.ancho / 2
            destino_y -= self.alto / 2
            dx = destino_x - self.x
            dy = destino_y - self.y
            distancia = math.hypot(dx, dy)
            if distancia == 0:
                self.ruta.pop(0)
                continue

            paso = min(disponible, distancia)
            nuevo_x = self.x + dx / distancia * paso
            nuevo_y = self.y + dy / distancia * paso
            if paso == distancia:
                nuevo_x, nuevo_y = destino_x, destino_y

            # Revisa todo el trayecto del paso, incluso si delta es grande.
            if self.hay_solidos(tilemap, min(self.x, nuevo_x),
                                min(self.y, nuevo_y),
                                max(self.x, nuevo_x) + self.ancho,
                                max(self.y, nuevo_y) + self.alto):
                self.detener()
                break

            tiempo_paso = paso / self.velocidad
            self.mueveteX(dx / distancia * self.velocidad, tiempo_paso)
            self.mueveteY(dy / distancia * self.velocidad, tiempo_paso)
            if paso == distancia:
                self.x, self.y = destino_x, destino_y
                self.ruta.pop(0)
            disponible -= paso
            tiempo_movido += tiempo_paso

        if self.ruta:
            self.actualizar_animacion(tiempo_movido)
        else:
            self.cont = 0
            self.indice_actual = 0

    def dibujar(self, pantalla, tilemap):
        imagen = self.obtengo_image_actual()
        pantalla.blit(imagen, (self.x - tilemap.scroll_x,
                               self.y - tilemap.scroll_y))

    def cargar_hoja_animacion(self, path, rectangulos, tamano=(48, 48)):
        # Recorta las poses y alinea sus pies en cuadros del mismo tamano.
        if not rectangulos or tamano[0] <= 0 or tamano[1] <= 0:
            raise ValueError("Indica los recortes y un tamano positivo.")
        hoja = pygame.image.load(path).convert_alpha()
        cuadros = []
        for datos in rectangulos:
            rectangulo = pygame.Rect(datos)
            if not hoja.get_rect().contains(rectangulo):
                raise ValueError("Un recorte queda fuera de la hoja.")
            cuadro = hoja.subsurface(rectangulo)
            contenido = cuadro.get_bounding_rect()
            if contenido.width == 0 or contenido.height == 0:
                raise ValueError("Un recorte no contiene una imagen visible.")
            cuadros.append(cuadro.subsurface(contenido).copy())
        ancho = max(cuadro.get_width() for cuadro in cuadros)
        alto = max(cuadro.get_height() for cuadro in cuadros)
        escala = min(tamano[0] / ancho, tamano[1] / alto)
        medida = (max(1, int(ancho * escala)), max(1, int(alto * escala)))
        imagenes = []
        for cuadro in cuadros:
            lienzo = pygame.Surface((ancho, alto), pygame.SRCALPHA)
            lienzo.blit(cuadro, ((ancho - cuadro.get_width()) // 2,
                                 alto - cuadro.get_height()))
            reducido = pygame.transform.smoothscale(lienzo, medida)
            imagen = pygame.Surface(tamano, pygame.SRCALPHA)
            imagen.blit(reducido, ((tamano[0] - medida[0]) // 2,
                                  tamano[1] - medida[1]))
            imagenes.append(imagen)
        self.lista_imagenes = imagenes
        self.ancho, self.alto = tamano
        self.detener()

