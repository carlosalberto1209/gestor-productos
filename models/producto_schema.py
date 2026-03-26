from pydantic import BaseModel, Field, field_validator
import re


class ProductoCreate(BaseModel):

    num_parte: str = Field(
        ...,
        description="Formato: A123456 o 123456789"
    )

    nombre: str
    descripcion: str

    @field_validator("num_parte")
    @classmethod
    def validar_num_parte(cls, value):

        value = value.upper().strip()

        patron = r'^([A-Z][0-9]{6}|[0-9]{9})$'

        if not re.match(patron, value):
            raise ValueError(
                "num_parte debe ser 1 letra + 6 números o 9 números"
            )

        return value