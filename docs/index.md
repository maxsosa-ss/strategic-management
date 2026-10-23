<h1><img src="assets/smpy.svg" alt="smpy" class="portada"></h1>

Conexiones a MicroStrategy y Google listas para usar, para no reescribirlas en cada proyecto, más un lugar para las funciones de conversión de datos que no dependen de ninguna conexión.

La librería se organiza en `smpy.connectors` (conexiones y flujos) y `smpy.transforms` (conversión y limpieza de datos, por ahora vacío).

La parte de conexiones envuelve los SDK oficiales (mstrio-py, gspread y google-auth) y suma solo lo que se repite en los proyectos: credenciales, conexión y los flujos que mueven DataFrames entre un sistema y otro.

La conexión que devuelve la librería es la `Connection` oficial de mstrio-py, sin capas en el medio. Cuando el SDK agrega una función nueva, ya podés usarla.

## Por dónde empezar

- [Instalación y configuración](configuracion.md): instalá la librería y completá el `.env`.
- [Recetas](recetas.md): los casos de uso más comunes, con código listo para ejecutar.
- [Referencia](referencia.md): parámetros y comportamiento de cada función.
- [Historial de cambios](cambios.md): qué cambió en cada versión.
