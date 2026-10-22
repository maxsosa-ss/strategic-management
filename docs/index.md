# sm-connectors

Conexiones a MicroStrategy y Google listas para usar, para no reescribirlas en cada proyecto.

La librería envuelve los SDK oficiales (mstrio-py, gspread y google-auth) y suma solo lo que se repite en los proyectos: credenciales, conexión y los flujos que mueven DataFrames entre un sistema y otro.

![Dos flujos: de un reporte de MicroStrategy a una hoja de Google, y de una hoja de Google a un super cube](assets/flujo.svg)

La conexión que devuelve la librería es la `Connection` oficial de mstrio-py, sin capas en el medio. Cuando el SDK agrega una función nueva, ya podés usarla.

## Por dónde empezar

- [Instalación y configuración](configuracion.md): instalá la librería y completá el `.env`.
- [Recetas](recetas.md): los casos de uso más comunes, con código listo para ejecutar.
- [Referencia](referencia.md): parámetros y comportamiento de cada función.
- [Historial de cambios](cambios.md): qué cambió en cada versión.
