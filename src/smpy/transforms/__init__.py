"""Funciones de conversión y limpieza de datos, independientes de las conexiones.

Cada función recibe un DataFrame (o una columna) y devuelve el resultado, sin conectarse a nada, así
se pueden probar con datos de ejemplo. Se agregan funciones cuando una transformación se repite en
dos o más proyectos.

- `smpy.transforms.filters`: filtrado por valores de columnas, con validación.
"""
