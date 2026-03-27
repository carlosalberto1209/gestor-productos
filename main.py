from fastapi.security import APIKeyHeader
from fastapi import Security
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import shutil
import os

from repository.productos_db import ProductosDB

# ================================
# SEGURIDAD
# ================================

API_KEY = os.getenv("API_KEY", "53893735")
api_key_header = APIKeyHeader(name="x-api-key")


def verificar_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="No autorizado")


# ================================
# APP
# ================================

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

# ================================
# INICIALIZACIÓN
# ================================

try:
    ProductosDB.cargar()
except FileNotFoundError:
    pass
except OSError:
    pass
except AttributeError:
    pass

templates = Jinja2Templates(directory="templates")

if not os.path.exists("images"):
    os.makedirs("images")

app.mount("/images", StaticFiles(directory="images"), name="images")


# ================================
# VISTA PRINCIPAL
# ================================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def inicio(request: Request):
    productos = [p.to_dict() for p in ProductosDB.lista]

    return templates.TemplateResponse(
        "catalogo.html",
        {
            "request": request,
            "productos": productos,
            "buscar": ""
        }
    )


# ================================
# ENDPOINTS API
# ================================

@app.get("/productos", tags=["Productos"])
def listar_productos():
    return [p.to_dict() for p in ProductosDB.lista]


@app.get("/productos/{num_parte}", tags=["Productos"])
def obtener_producto(num_parte: str):
    producto = ProductosDB.buscar(num_parte)

    if producto:
        return producto.to_dict()

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.post("/productos", dependencies=[Depends(verificar_api_key)], tags=["Productos"])
def crear_producto(
    num_parte: str = Form(...),
    nombre: str = Form(...),
    descripcion: str = Form(...),
    imagen: UploadFile = File(None)
):
    ruta_imagen = None

    if imagen:
        if "." not in imagen.filename:
            raise HTTPException(status_code=400, detail="Archivo inválido")

        extension = imagen.filename.split(".")[-1].lower()

        if extension not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Formato no permitido")

        nombre_archivo = f"{num_parte}.{extension}"
        ruta_imagen = f"images/{nombre_archivo}"

        with open(ruta_imagen, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    try:
        producto = ProductosDB.crear(num_parte, nombre, descripcion, ruta_imagen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return producto.to_dict()


@app.put("/productos/{num_parte}", dependencies=[Depends(verificar_api_key)], tags=["Productos"])
def modificar_producto(
    num_parte: str,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    imagen: UploadFile = File(None)
):
    ruta_imagen = None

    if imagen:
        if "." not in imagen.filename:
            raise HTTPException(status_code=400, detail="Archivo inválido")

        extension = imagen.filename.split(".")[-1].lower()

        if extension not in ["jpg", "jpeg", "png"]:
            raise HTTPException(status_code=400, detail="Formato no permitido")

        nombre_archivo = f"{num_parte}.{extension}"
        ruta_imagen = f"images/{nombre_archivo}"

        with open(ruta_imagen, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

    producto = ProductosDB.modificar(num_parte, nombre, descripcion, ruta_imagen)

    if producto:
        return producto.to_dict()

    raise HTTPException(status_code=404, detail="Producto no encontrado")


@app.delete("/productos/{num_parte}", dependencies=[Depends(verificar_api_key)], tags=["Productos"])
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

@app.get("/catalogo", response_class=HTMLResponse, tags=["Catálogo"])
def catalogo(request: Request, buscar: str = ""):
    productos = [p.to_dict() for p in ProductosDB.lista]

    if buscar:
        buscar_lower = buscar.lower()
        productos = [
            p for p in productos
            if buscar_lower in p["num_parte"].lower()
            or buscar_lower in p["nombre"].lower()
        ]

    return templates.TemplateResponse(
        "catalogo.html",
        {
            "request": request,
            "productos": productos,
            "buscar": buscar
        }
    )