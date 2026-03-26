import json
import os
from models.producto import Producto


class ProductosDB:

    archivo = "productos.json"
    lista = []

    @classmethod
    def cargar(cls):

        if not os.path.exists(cls.archivo):
            return

        with open(cls.archivo, "r", encoding="utf-8") as f:
            try:
                datos = json.load(f)
            except json.JSONDecodeError:
                datos = []

        cls.lista = [
            Producto(
                p["num_parte"],
                p["nombre"],
                p["descripcion"],
                p.get("imagen")
            )
            for p in datos
        ]

    @classmethod
    def guardar(cls):

        datos = [p.to_dict() for p in cls.lista]

        with open(cls.archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    @classmethod
    def buscar(cls, num_parte):

        num_parte = num_parte.upper().strip()

        for producto in cls.lista:
            if producto.num_parte == num_parte:
                return producto

        return None

    @classmethod
    def crear(cls, num_parte, nombre, descripcion, imagen=None):

        if cls.buscar(num_parte):
            raise ValueError("El número de parte ya existe.")

        producto = Producto(num_parte, nombre, descripcion, imagen)

        cls.lista.append(producto)

        cls.guardar()

        return producto

    @classmethod
    def modificar(cls, num_parte, nombre, descripcion, imagen=None):

        producto = cls.buscar(num_parte)

        if producto:

            producto.nombre = nombre
            producto.descripcion = descripcion.strip()

            if imagen:
                producto.imagen = imagen

            cls.guardar()

            return producto

        return None

    @classmethod
    def borrar(cls, num_parte):

        producto = cls.buscar(num_parte)

        if producto:

            cls.lista.remove(producto)

            cls.guardar()

            return producto

        return None