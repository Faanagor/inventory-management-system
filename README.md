# Inventory Management System

## API de gestión de inventario con FastAPI , basada en una arquitectura modular y optimizada para pruebas, escalabilidad y despliegue. La aplicación permite manejar productos, movimientos de inventario y otras operaciones clave.

### Caracteristicas de la aplicacion:

1. Arquitectura y principios de software usados:
    - Arquitectura de microservicios.
    - MVC (Modelo vista controlador).
    - Clean Code.
    - Programacion Orientada a Objetos.
    - Principios SOLID.

2. Manejo de Bases de Datos SQL Postgres, donde se manejan 3 tablas diferentes relacionadas:
    - Tabla productos.
    - Tabla Inventario.
    - Tabla movimientos.
    - Para las pruebas unitarias se mockeo una BD en SQLite que lo hace mas ligera y no toca datos reales.

3. Creacion de diferentes endpoints, para manejo de la aplicacion. Para ello se trabajaron varios modulos diferentes, por cada tabla:
    - Models -> Donde se crean las clases de cada una de las tablas de la BD con todos sus atributos. Por ejemplo: ID, nombre, cantidad, precio... y las relaciones con las otras tablas
    - Schemas -> Permite la validacion de datos con Pydantic, la serializacion y deserializacion (Convertir un objeto en una entidad de la BD y viceversa).
    - Service -> Logica de negocio de la aplicacion y capa intermedia entre las rutas y la base de datos.
    - Routes -> Concatena la logica de negocio con la ruta de cada endpoint

4. Uso de Asyncio y aprovechamiento de las ventajas de asincronismo de Fastapi.

5. Pruebas:
    - Pruebas unitarias para cada modulo de la aplicacion usando Pytest.
    - Pruebas de covertura mayor a 90%.
    - Pruebas de integracion usando httpx.
    - Pruebas de carga con Locust que muestra el comportamiento de la aplicacion.

6. Conexion a BD:
    - Archivo Database.py que configura la conexion asincrona a la BD.
    - Manejo del ORM SQLAlchemy para el CRUD de la aplicacion, sin necesidad de usar lenguaje SQL.
    - Manejo de Alembic para las migraciones a la BD.

7. Manejo de Dependencias:
    - Uso de Poetry para configuracion de la aplicacion y manejo de librerias (dev, test, y general).
    - Uso de Makefile para automatizacion en la instalacion, correr pruebas, formaters, linters y run.

8. Manejo de Docker.

9. Coleccion de endpoints con Swagger.

10. Manejo de repositorio:
    - Github como herramienta de repositorio.
    - Archivo  pre-commit-config para asegurar codigo limpio y estable.
    - Uso de conventional-commits para manejo de documentacion correcta en cada commit creado antes de hacer push.

11. Manejo de linters y formatters para automatizar el uso de buenas practicas de programacion (PEP8):
    - Black.
    - Flake8.
    - Isort.

12. Documentacion de codigo.
