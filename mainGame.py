import sys
import pygame
import Tilemap
from Personaje import Personaje
from EstadoJuego import EstadoJuego
from HUD import HUD
from ConfiguracionMapa import cargar_mapa_misterio, obtener_puntos_misterio


def bezier_cubo(t: float, p0, p1, p2, p3):
    # Formula de gameCurva.py copiada aqui para el movimiento del personaje.
    x0, y0 = p0
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x = (pow(1 - t, 3) * x0 + 3 * pow(1 - t, 2) * t * x1
         + 3 * (1 - t) * pow(t, 2) * x2 + pow(t, 3) * x3)
    y = (pow(1 - t, 3) * y0 + 3 * pow(1 - t, 2) * t * y1
         + 3 * (1 - t) * pow(t, 2) * y2 + pow(t, 3) * y3)
    return x, y



def esta_cerca(personaje, casilla):
    columna = int((personaje.x + personaje.ancho / 2) // 64)
    fila = int((personaje.y + personaje.alto / 2) // 64)
    return abs(columna - casilla[0]) + abs(fila - casilla[1]) <= 1


def revisar_punto(personaje, estado, puntos):
    # Revisa la pista o el barril que este cerca del personaje.
    datos = puntos[estado.mapa_actual]
    for pista in datos["pistas"]:
        if esta_cerca(personaje, pista["casilla"]):
            personaje.detener()
            estado.recoger_pista(pista["clave"], pista["texto"])
            return pista["texto"], False
    objetivo = datos.get("objetivo")
    if objetivo and esta_cerca(personaje, objetivo["casilla"]):
        personaje.detener()
        if estado.completado:
            return "Ya recuperaste la llave del guardabosques.", False
        if not all(clave in estado.pistas for clave in objetivo["pistas_necesarias"]):
            return "Necesitas las tres pistas antes de abrir el barril.", False
        return "Escribe tres cifras. Enter: confirmar. Esc: cancelar.", True
    return "Acercate a una marca amarilla y presiona E.", False


def dibujar_puntos(pantalla, tilemap, estado, puntos, fuente):
    # Las marcas indican donde investigar y donde cambiar de zona.
    datos = puntos[estado.mapa_actual]
    casillas = [pista["casilla"] for pista in datos["pistas"]
                if pista["clave"] not in estado.pistas]
    if "objetivo" in datos and not estado.completado:
        casillas.append(datos["objetivo"]["casilla"])
    for columna, fila in casillas:
        x = int(columna * 64 + 32 - tilemap.scroll_x)
        y = int(fila * 64 + 32 - tilemap.scroll_y)
        pygame.draw.circle(pantalla, (255, 225, 80), (x, y), 14)
        etiqueta = fuente.render("?", True, (30, 30, 30))
        pantalla.blit(etiqueta, etiqueta.get_rect(center=(x, y)))
    for salida in datos["salidas"]:
        columna, fila = salida["casillas"][0]
        x = columna * 64 - tilemap.scroll_x
        y = fila * 64 - tilemap.scroll_y
        pygame.draw.rect(pantalla, (90, 235, 215), (x, y, 64, 128), 3)
        etiqueta = fuente.render(salida["destino"].capitalize(), True, (20, 20, 20),
                                (90, 235, 215))
        pantalla.blit(etiqueta, (x, y + 45))


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Juego')

# Las cinco poses de arriba se usan para caminar.
personaje = Personaje(0, 0, ["./personaje.png"], funcion_curva=bezier_cubo)
recortes = [(170, 170, 330, 310), (510, 170, 320, 310),
            (830, 170, 340, 310), (1170, 170, 350, 310),
            (1520, 170, 340, 310)]
personaje.cargar_hoja_animacion("./personaje.png", recortes)
puntos = obtener_puntos_misterio()
estado = EstadoJuego()
for nombre in ("bosque", "claro"):
    mapa_zona = cargar_mapa_misterio(nombre)
    columna, fila = puntos[nombre]["inicio"]
    posicion = (columna * 64 + (64 - personaje.ancho) / 2,
                fila * 64 + (64 - personaje.alto) / 2)
    estado.agregar_mapa(nombre, mapa_zona, posicion)
tilemap = estado.obtener_mapa_actual()["tilemap"]
personaje.colocar_en_mapa(*estado.obtener_mapa_actual()["posicion"], tilemap)
tilemap.actualizar_scroll(personaje.x + personaje.ancho / 2,
                         personaje.y + personaje.alto / 2,
                         SCREEN_WIDTH, SCREEN_HEIGHT)
hud = HUD()
superficie_hud = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
alto_hud = SCREEN_HEIGHT
mensaje = "Busca las tres pistas para recuperar la llave del guardabosques."
ingresando_codigo = False
codigo = ""

fps = 0
fps_ant = 0
fps_limite = 60
ms_por_frame = 1000.0 / fps_limite

tiempoInicial = pygame.time.get_ticks()
print("Tiempo inicial: ", tiempoInicial)
anterior = pygame.time.get_ticks()
gameRunning = True
while gameRunning == True:
    inicioCiclo = pygame.time.get_ticks()

    # Tiempo entre ciclos, en segundos.
    ahora = inicioCiclo
    delta = (ahora - anterior) / 1000.0
    anterior = ahora

    # Este ciclo es para poder cerrar la ventana.
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            gameRunning = False
        elif event.type == pygame.KEYDOWN:
            if ingresando_codigo:
                if event.key == pygame.K_ESCAPE:
                    ingresando_codigo = False
                    codigo = ""
                    mensaje = "Puedes seguir explorando."
                elif event.key == pygame.K_BACKSPACE:
                    codigo = codigo[:-1]
                elif event.key == pygame.K_RETURN:
                    objetivo = puntos[estado.mapa_actual]["objetivo"]
                    if len(codigo) != 3:
                        mensaje = "Escribe las tres cifras antes de confirmar."
                    elif estado.comprobar_solucion(codigo, objetivo["solucion"],
                                                   objetivo["pistas_necesarias"]):
                        estado.recoger_objeto("llave", "Llave del guardabosques")
                        ingresando_codigo = False
                        mensaje = "Encontraste la llave. Misterio resuelto."
                    else:
                        codigo = ""
                        mensaje = "Codigo incorrecto. Revisa las pistas e intenta otra vez."
                elif event.unicode in "0123456789" and len(codigo) < 3:
                    codigo += event.unicode
            elif event.key == pygame.K_ESCAPE:
                gameRunning = False
            elif event.key == pygame.K_c:
                personaje.alternar_movimiento(tilemap)
            elif event.key == pygame.K_e:
                mensaje, ingresando_codigo = revisar_punto(personaje, estado, puntos)
                codigo = ""
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not ingresando_codigo and event.pos[1] >= alto_hud:
                if not personaje.procesar_evento(event, tilemap):
                    mensaje = "Ese punto esta bloqueado o no hay camino."

    screen.fill((127, 127, 127))      # Colorea la pantalla en gris para refrescar los pixeles viejos.
    personaje.actualizar(delta, tilemap)

    # Guarda una posicion fuera del paso para poder regresar sin rebotar.
    columna = int((personaje.x + personaje.ancho / 2) // 64)
    fila = int((personaje.y + personaje.alto / 2) // 64)
    cambio_mapa = False
    for salida in puntos[estado.mapa_actual]["salidas"]:
        if (columna, fila) in salida["casillas"]:
            posicion_segura = estado.obtener_mapa_actual()["posicion"]
            posicion = estado.cambiar_mapa(salida["destino"], posicion_segura)
            tilemap = estado.obtener_mapa_actual()["tilemap"]
            personaje.colocar_en_mapa(*posicion, tilemap)
            mensaje = "Entraste al " + estado.mapa_actual + ". Busca las marcas amarillas."
            cambio_mapa = True
            break
    if not cambio_mapa:
        estado.guardar_posicion(personaje.x, personaje.y)

    tilemap.actualizar_scroll(personaje.x + personaje.ancho / 2,
                             personaje.y + personaje.alto / 2,
                             SCREEN_WIDTH, SCREEN_HEIGHT)
    tilemap.dibujar_capas(screen)
    dibujar_puntos(screen, tilemap, estado, puntos, hud.fuente)
    personaje.dibujar(screen, tilemap)

    # El HUD se dibuja al final y sus clics no mueven al personaje.
    mensaje_visible = mensaje
    if ingresando_codigo:
        mensaje_visible += " Codigo: " + codigo.ljust(3, "_")
    superficie_hud.fill((0, 0, 0, 0))
    hud.dibujar(superficie_hud, estado, mensaje=mensaje_visible)
    alto_texto = superficie_hud.get_bounding_rect().height
    modo = "Curvo" if personaje.movimiento_curvo else "Lineal"
    ayuda = (estado.mapa_actual.capitalize() + " | " + modo
             + " (C) | Clic: caminar | E: investigar | Esc: salir")
    pygame.draw.rect(superficie_hud, hud.color_fondo,
                     (0, alto_texto, SCREEN_WIDTH, 26))
    superficie_hud.blit(hud.fuente.render(ayuda, True, hud.color_texto),
                        (10, alto_texto + 3))
    alto_hud = alto_texto + 26
    screen.blit(superficie_hud, (0, 0))

    pygame.display.flip()

    fps = fps + 1                               # Contador de fps
    tiempoActual = pygame.time.get_ticks()      # Obtiene el tiempo transcurrido total
    if (tiempoActual-tiempoInicial >= 1000):    # Si ya pasó un segundo
        print(fps)                              # Muestra los fps que han pasado
        fps_ant = fps
        fps = 0                                 # Reinicia los fps (ya cumplió su ciclo)
        tiempoInicial = tiempoActual            # Se recalcula el tiempo inicial

    # Espera hasta completar el tiempo del frame.
    while pygame.time.get_ticks() - inicioCiclo < ms_por_frame:
        pass

pygame.quit()
sys.exit()
