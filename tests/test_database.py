import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import unittest
import copy
from repository.productos_db import ProductosDB
from models.producto import Producto


class TestDatabase(unittest.TestCase):

    def setUp(self):

        ProductosDB.lista = [
            Producto('A1234567', 'Loctite241', 'Pegante bajo'),
            Producto('B7654321', 'Loctite242', 'Pegante medio'),
            Producto('12345678', 'Loctite266', 'Pegante fuerte')
        ]

    def test_buscar_producto(self):

        producto_existente = ProductosDB.buscar('A1234567')
        producto_no_existente = ProductosDB.buscar('Z9999999')

        self.assertIsNotNone(producto_existente)
        self.assertIsNone(producto_no_existente)

    def test_crear_producto(self):

        nuevo_producto = ProductosDB.crear(
            'C1111111',
            'Producto nuevo',
            'Descripcion valida'
        )

        self.assertEqual(len(ProductosDB.lista), 4)
        self.assertEqual(nuevo_producto.num_parte, 'C1111111')

    def test_modificar_producto(self):

        producto_original = copy.copy(
            ProductosDB.buscar('12345678')
        )

        producto_modificado = ProductosDB.modificar(
            '12345678',
            'Loctite266',
            'Descripcion nueva'
        )

        self.assertEqual(producto_original.descripcion, 'Pegante fuerte')
        self.assertEqual(producto_modificado.descripcion, 'Descripcion nueva')

    def test_borrar_producto(self):

        producto_borrado = ProductosDB.borrar('B7654321')

        self.assertIsNotNone(producto_borrado)
        self.assertEqual(len(ProductosDB.lista), 2)


if __name__ == '__main__':
    unittest.main()