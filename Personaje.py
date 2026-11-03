import math
import pygame
from Sprite import SpriteAnimado
from Navegacion import buscar_ruta, obtener_puntos_ruta


class Personaje(SpriteAnimado):

    def __init__(self, x, y, rutas_imagenes, velocidad=160, tiempo_frame=0.15,
                 funcion_curva=None):
        super().__init__(x, y)
        if velocidad <= 0 or tiempo_frame <= 0:
            raise ValueError("La velocidad y el tiempo por imagen deben ser positivos.")
        self.velocidad = velocidad
        self.cambio = tiempo_frame
        self.indice_actual = 0
        self.ruta = []
        self.funcion_curva = funcion_curva
        self.movimiento_curvo = funcion_curva is not None
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
        if self.movimiento_curvo and self.ruta:
            self.ruta = self.crear_ruta_curva((centro_x, centro_y),
                                             self.ruta, tilemap)
        return True

    def alternar_movimiento(self, tilemap):
        if self.funcion_curva is None:
            return
        self.movimiento_curvo = not self.movimiento_curvo
        if self.ruta:
            self.establecer_destino(*self.ruta[-1], tilemap)

    def muestrear_curva(self, p0, p1, p2, p3):
        # Tramos de hasta 4 pixeles: el recorrido conserva la velocidad habitual
        # y el sistema de colisiones revisa tambien los pasos de la curva.
        longitud = sum(math.dist(a, b)
                       for a, b in ((p0, p1), (p1, p2), (p2, p3)))
        pasos = max(1, math.ceil(longitud / 4))
        return [self.funcion_curva(i / pasos, p0, p1, p2, p3)
                for i in range(1, pasos + 1)]

    def trayecto_libre(self, inicio, puntos, tilemap):
        anterior_x, anterior_y = inicio
        for x, y in puntos:
            if self.hay_solidos(tilemap,
                                min(anterior_x, x) - self.ancho / 2,
                                min(anterior_y, y) - self.alto / 2,
                                max(anterior_x, x) + self.ancho / 2,
                                max(anterior_y, y) + self.alto / 2):
                return False
            anterior_x, anterior_y = x, y
        return True

    def crear_ruta_curva(self, inicio, puntos, tilemap):
        destino = puntos[-1]
        dx, dy = destino[0] - inicio[0], destino[1] - inicio[1]
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            return puntos

        # En espacios abiertos usa un arco hasta el clic. Prueba ambos lados
        # y reduce su amplitud si hay paredes cerca.
        amplitud = min(distancia / 4, tilemap.tile_witdh)
        for factor in (1, -1, 0.5, -0.5, 0.25, -0.25):
            offset_x = -dy / distancia * amplitud * factor
            offset_y = dx / distancia * amplitud * factor
            p1 = (inicio[0] + dx / 3 + offset_x,
                  inicio[1] + dy / 3 + offset_y)
            p2 = (inicio[0] + 2 * dx / 3 + offset_x,
                  inicio[1] + 2 * dy / 3 + offset_y)
            curva = self.muestrear_curva(inicio, p1, p2, destino)
            if self.trayecto_libre(inicio, curva, tilemap):
                return curva

        # Si debe rodear obstaculos, conserva la ruta y redondea sus giros.
        esquinas = [inicio]
        for i, punto in enumerate(puntos[:-1]):
            anterior, siguiente = esquinas[-1], puntos[i + 1]
            entrada = (punto[0] - anterior[0], punto[1] - anterior[1])
            salida = (siguiente[0] - punto[0], siguiente[1] - punto[1])
            if (abs(entrada[0] * salida[1] - entrada[1] * salida[0]) > 1e-6
                    or entrada[0] * salida[0] + entrada[1] * salida[1] <= 0):
                esquinas.append(punto)
        esquinas.append(destino)
        ruta = []
        for i in range(1, len(esquinas) - 1):
            anterior, esquina, siguiente = esquinas[i - 1:i + 2]
            largo_entrada = math.dist(anterior, esquina)
            largo_salida = math.dist(esquina, siguiente)
            radio = min(largo_entrada / 2, largo_salida / 2,
                        min(tilemap.tile_witdh, tilemap.tile_height) * 0.4)
            entrada = tuple(esquina[j] + (anterior[j] - esquina[j])
                            * radio / largo_entrada for j in (0, 1))
            salida = tuple(esquina[j] + (siguiente[j] - esquina[j])
                           * radio / largo_salida for j in (0, 1))
            curva = self.muestrear_curva(entrada, esquina, esquina, salida)
            tramo = [entrada] + curva
            if self.trayecto_libre(ruta[-1] if ruta else inicio, tramo, tilemap):
                ruta.extend(tramo)
            else:
                ruta.append(esquina)
        ruta.append(destino)
        return ruta

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

