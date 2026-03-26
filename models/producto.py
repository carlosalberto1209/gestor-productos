import re


class Producto:

    def __init__(self, num_parte, nombre, descripcion, imagen=None):

        num_parte = num_parte.upper().strip()
        descripcion = descripcion.strip()

        if not self._validar_num_parte(num_parte):
            raise ValueError(
                "num_parte debe tener formato:\n"
                "• 1 letra + 7 números (A1234567)\n"
                "• ó 8 números (12345678)"
            )

        if not self._validar_descripcion(descripcion):
            raise ValueError(
                "descripcion debe tener entre 5 y 100 caracteres"
            )

        self.num_parte = num_parte
        self.nombre = nombre
        self.descripcion = descripcion
        self.imagen = imagen   # ← nuevo campo

    @staticmethod
    def _validar_num_parte(num_parte):
        patron = r'^([A-Z][0-9]{6}|[0-9]{9})$'
        return bool(re.match(patron, num_parte))

    @staticmethod
    def _validar_descripcion(descripcion):
        return 5 <= len(descripcion) <= 100

    def __str__(self):
        return f"({self.num_parte}) {self.nombre} {self.descripcion}"