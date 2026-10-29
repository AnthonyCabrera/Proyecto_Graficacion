import pygame


class Sprite:

    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(path).convert()
        self.cont = 0
        self.cambio = 500
        self.indice_actual = 0
        self.alto = self.image.get_height()
        self.ancho = self.image.get_width()
    
    def incremento_Cont(self):
        self.cont = self.cont + 1
        if self.cont >= self.cambio:
            self.cont = 0
            
            self.indice_actual = self.indice_actual + 1
            if self.indice_actual >= len (self.lista_imagenes):
                self.indice_actual = 0


    def estaColisionando(self, s2):
        x1 = self.x
        y1 = self.y
        alto1 = self.alto
        ancho1 = self.ancho

        x2 = s2.x
        y2 = s2.y
        alto2 = s2.alto
        ancho2 = s2.ancho

        if (
            ((x2 >= x1 and x2 <= x1 + ancho1) and (y2 >= y1 and y2 <= y1 + alto1))
            or (
                (x2 >= x1 and x2 <= x1 + ancho1)
                and (y2 + alto2 >= y1 and y2 + alto2 <= y1 + alto1)
            )
            or (
                (x2 + ancho2 >= x1 and x2 + ancho2 <= x1 + ancho1)
                and (y2 >= y1 and y2 <= y1 + alto1)
            )
            or (
                (x2 + ancho2 >= x1 and x2 + ancho2 <= x1 + ancho1)
                and (y2 + alto2 >= y1 and y2 + alto2 <= y1 + alto1)
            )
            or ((x1 >= x2 and x1 <= x2 + ancho2) and (y1 >= y2 and y1 <= y2 + alto2))
            or (
                (x1 >= x2 and x1 <= x2 + ancho2)
                and (y1 + alto1 >= y2 and y1 + alto1 <= y2 + alto2)
            )
            or (
                (x1 + ancho1 >= x2 and x1 + ancho1 <= x2 + ancho2)
                and (y1 >= y2 and y1 <= y2 + alto2)
            )
            or (
                (x1 + ancho1 >= x2 and x1 + ancho1 <= x2 + ancho2)
                and (y1 + alto1 >= y2 and y1 + alto1 <= y2 + alto2)
            )
        ):
            return True

        return False

    def noEstaColisionando(self, s2):
        x1 = self.x
        y1 = self.y
        alto1 = self.alto
        ancho1 = self.ancho

        x2 = s2.x
        y2 = s2.y
        alto2 = s2.alto
        ancho2 = s2.ancho

        if x1 > x2 + ancho2 or x1 + ancho1 < x2 or y1 > y2 + alto2 or y1 + alto1 < y2:
            return True

        return False

    def mueveteX(self, speed, delta):
        self.x += speed * delta

    def mueveteY(self, speed, delta):
        self.y += speed * delta


class SpriteAnimado(Sprite):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cont = 0
        self.lista_imagenes = []

    def agrego_imagenes(self, path):
        img = pygame.image.load(path).convert()
        self.lista_imagenes.append(img)

    def obtengo_image_actual(self):
        # Validar que la lista tenga imagenes
        return self.lista_imagenes[self.indice_actual]

    