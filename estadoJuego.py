class EstadoJuego:

    def __init__(self):
        self.mapas = {}
        self.mapa_actual = None
        self.pistas = {}
        self.objetos = {}
        self.completado = False

    def agregar_mapa(self, nombre, tilemap, posicion_inicial):
        # No sobrescribe el progreso de un mapa registrado.
        if nombre in self.mapas:
            raise ValueError("El mapa ya esta registrado: " + nombre)
        self.mapas[nombre] = {
            "tilemap": tilemap,
            "posicion": posicion_inicial,
            "recogidos": set(),
        }
        if self.mapa_actual is None:
            self.mapa_actual = nombre

    def obtener_mapa_actual(self):
        if self.mapa_actual is None:
            raise ValueError("Primero agrega un mapa.")
        return self.mapas[self.mapa_actual]

    def guardar_posicion(self, x, y):
        self.obtener_mapa_actual()["posicion"] = (x, y)

    def cambiar_mapa(self, nombre, posicion_salida):
        # Guarda la salida y recupera la posicion del otro mapa.
        if nombre not in self.mapas:
            raise ValueError("El mapa no esta registrado: " + nombre)
        self.guardar_posicion(*posicion_salida)
        self.mapa_actual = nombre
        return self.obtener_mapa_actual()["posicion"]

    def recoger_pista(self, clave, texto):
        mapa = self.obtener_mapa_actual()
        if clave in self.pistas:
            return False
        self.pistas[clave] = texto
        mapa["recogidos"].add(("pista", clave))
        return True

    def recoger_objeto(self, clave, nombre):
        mapa = self.obtener_mapa_actual()
        if clave in self.objetos:
            return False
        self.objetos[clave] = nombre
        mapa["recogidos"].add(("objeto", clave))
        return True

    def comprobar_solucion(self, respuesta, solucion, pistas_necesarias):
        # Solo permite resolver el misterio con las pistas necesarias.
        if self.completado:
            return True
        for clave in pistas_necesarias:
            if clave not in self.pistas:
                return False
        if respuesta.strip().casefold() != solucion.strip().casefold():
            return False
        self.completado = True
        return True
