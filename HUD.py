import pygame


class HUD:

    def __init__(self):
        self.fuente = pygame.font.Font(None, 22)
        self.color_texto = (255, 255, 255)
        self.color_fondo = (30, 30, 40)

    def ajustar_texto(self, texto, ancho):
        # Divide el texto para que quepa en la pantalla.
        lineas = []
        linea = ""
        for palabra in texto.split():
            propuesta = (linea + " " + palabra).strip()
            if linea and self.fuente.size(propuesta)[0] > ancho:
                lineas.append(linea)
                linea = palabra
            else:
                linea = propuesta
        lineas.append(linea)
        return lineas

    def dibujar(self, pantalla, estado, tiempo_restante=None, mensaje=""):
        textos = ["Pistas: " + str(len(estado.pistas))]
        for texto in estado.pistas.values():
            textos.append("- " + texto)
        nombres = ", ".join(estado.objetos.values()) or "ninguno"
        textos.append("Objetos: " + nombres)
        if tiempo_restante is not None:
            segundos = max(0, int(tiempo_restante))
            textos.append("Tiempo: " + str(segundos) + " s")
        if estado.completado:
            textos.append("Misterio resuelto")
        if mensaje:
            textos.append(mensaje)

        lineas = []
        for texto in textos:
            lineas.extend(self.ajustar_texto(texto, pantalla.get_width() - 20))
        paso = self.fuente.get_linesize()
        alto = len(lineas) * paso + 20

        # Se dibuja al final y sin restar el scroll.
        pygame.draw.rect(pantalla, self.color_fondo,
                         (0, 0, pantalla.get_width(), alto))
        y = 10
        for linea in lineas:
            imagen = self.fuente.render(linea, True, self.color_texto)
            pantalla.blit(imagen, (10, y))
            y += paso
