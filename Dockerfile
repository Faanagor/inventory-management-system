# 1. Imagen base
FROM python:3.12

# 2. Directorio de trabajo dentro del contenedor
WORKDIR /inventory_management_system

# 3. Copiar solo los archivos esenciales
COPY pyproject.toml poetry.lock Makefile ./

# 4. Instalar dependencias
RUN make install

# 5. Copiar el código restante de la aplicación
COPY . .

# 6. Exponer el puerto en el que corre la aplicación
EXPOSE 8000

# 7. Comando para ejecutar la aplicación
CMD ["make", "run"]
