"""Hoja de Google -> super cube de MicroStrategy: crear el cubo y mantenerlo actualizado.

Ejecutar desde la raíz del proyecto (el .env se lee desde ahí). Completá los IDs.
"""

from sm_connectors.pipeline import sheet_to_supercube

SHEET_ID = "ID_DEL_SHEET"
PESTANA = "Hoja 1"
TABLA = "Paises"  # nombre lógico de la tabla dentro del cubo; usá el mismo al actualizar


def crear():
    """Se corre una sola vez. Guardá el ID que devuelve."""
    cube_id = sheet_to_supercube(SHEET_ID, PESTANA, TABLA, cube_name="Paises_desde_sheet")
    print(f"Cubo creado: {cube_id}")
    return cube_id


def actualizar(cube_id: str):
    """Se corre cada vez que cambia el Sheet. 'replace' deja el cubo igual al Sheet."""
    sheet_to_supercube(SHEET_ID, PESTANA, TABLA, cube_id=cube_id, policy="replace")
    print("Cubo actualizado")


if __name__ == "__main__":
    actualizar("ID_DEL_CUBO")
