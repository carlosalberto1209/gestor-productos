from fastapi.security import APIKeyHeader
from fastapi import Security
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os

from repository.productos_db import ProductosDB

API_KEY = os.getenv("API_KEY", "53893735")

api_key_header = APIKeyHeader(name="x-api-key")

def verificar_api_key(api_key: str = Security(api_key_header)):

    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")

app = FastAPI(
    title="Gestor de Productos",
    description="""
API para gestionar productos con imágenes.

### Funcionalidades:
- Crear productos con imagen
- Listar productos
- Buscar productos
- Modificar productos
- Eliminar productos
- Visualizar catálogo HTML

Desarrollado con FastAPI 🚀
""",
    version="1.0.0"
)

# Cargar datos al iniciar
ProductosDB.cargar()

# Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

# Crear carpeta de imágenes si no existe
if not os.path.exists("images"):
    os.makedirs("images")

# Servir imágenes
app.mount("/images", StaticFiles(directory="images"), name="images")


# ================================
# ENDPOINTS API
# ================================

@app.get("/", include_in_schema=False)
def inicio():
    return {"mensaje": "API Gestor de Productos"}


@app.get(
    "/productos",
    tags=["Productos"],
    summary="Listar productos",
    description="Devuelve todos los productos registrados"
)
def listar_productos():
    return [vars(producto) for producto in ProductosDB.lista]


@app.get(
    "/productos/{num_parte}",
    tags=["Productos"],
    summary="Obtener producto",
    description="Busca un producto por su número de parte"
)
def obtener_producto(num_parte: str):

    producto = ProductosDB.buscar(num_parte)

    if producto:
        return vars(producto)

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.post(
    "/productos",
    dependencies=[Depends(verificar_api_key)],
    tags=["Productos"],
    summary="Crear producto",
    description="Crea un nuevo producto y permite subir una imagen"
)
def crear_producto(
        num_parte: str = Form(
            ...,
            description="Formato: 1 letra + 6 números (A123456) o 9 números"
        ),
        nombre: str = Form(
            ...,
            description="Nombre del producto"
        ),
        descripcion: str = Form(
            ...,
            description="Descripción (máximo 100 caracteres)"
        ),
        imagen: UploadFile = File(None)
):

    ruta_imagen = None

    if imagen:

        if "." not in imagen.filename:
            raise HTTPException(status_code=400, detail="Archivo inválido")

        extension = imagen.filename.split(".")[-1].lower()

        if extension not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

        nombre_archivo = f"{num_parte}.{extension}"
        ruta_imagen = f"images/{nombre_archivo}"

        with open(ruta_imagen, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    try:
        nuevo_producto = ProductosDB.crear(
            num_parte,
            nombre,
            descripcion,
            ruta_imagen
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return vars(nuevo_producto)


@app.put(
    "/productos/{num_parte}",
    dependencies=[Depends(verificar_api_key)],
    tags=["Productos"],
    summary="Modificar producto",
    description="Actualiza un producto existente"
)
def modificar_producto(
        num_parte: str,
        nombre: str = Form(..., description="Nuevo nombre"),
        descripcion: str = Form(..., description="Nueva descripción"),
        imagen: UploadFile = File(None)
):

    ruta_imagen = None

    if imagen:

        if "." not in imagen.filename:
            raise HTTPException(status_code=400, detail="Archivo inválido")

        extension = imagen.filename.split(".")[-1].lower()

        if extension not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

        nombre_archivo = f"{num_parte}.{extension}"
        ruta_imagen = f"images/{nombre_archivo}"

        with open(ruta_imagen, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    producto = ProductosDB.modificar(num_parte, nombre, descripcion, ruta_imagen)

    if producto:
        return vars(producto)

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.delete(
    "/productos/{num_parte}",
    dependencies=[Depends(verificar_api_key)],
    tags=["Productos"],
    summary="Eliminar producto",
    description="Elimina un producto y su imagen asociada"
)
def borrar_producto(num_parte: str):

    producto = ProductosDB.borrar(num_parte)

    if producto:

        if producto.imagen and os.path.exists(producto.imagen):
            os.remove(producto.imagen)

        return {"mensaje": "Producto eliminado"}

    raise HTTPException(status_code=404, detail="Producto no encontrado")


# ================================
# CATÁLOGO HTML
# ================================

@app.get(
    "/catalogo",
    response_class=HTMLResponse,
    tags=["Catálogo"],
    summary="Ver catálogo",
    description="Muestra los productos en formato visual"
)
def catalogo(request: Request, buscar: str = ""):

    productos = ProductosDB.lista

    if buscar:
        buscar = buscar.lower()

        productos = [
            p for p in productos
            if buscar in p.num_parte.lower()
            or buscar in p.nombre.lower()
        ]

    return templates.TemplateResponse(
        "catalogo.html",
        {
            "request": request,
            "productos": productos,
            "buscar": buscar
        }
    )