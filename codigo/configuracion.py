from pathlib import Path
import pandas as pd

def leer_config(ruta_txt):
    """
    Lee un archivo .txt estilo clave=valor.
    Ignora líneas vacías y comentarios (#).
    Devuelve un diccionario con las claves parseadas.
    Convierte fechas a pd.Timestamp automáticamente.
    """
    ruta = Path(ruta_txt)
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {ruta}")

    cfg = {}
    with open(ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue

            if "=" in linea:
                clave, valor = [x.strip() for x in linea.split("=", 1)]
                cfg[clave] = valor

    # Conversión automática de fechas
    for k, v in cfg.items():
        if "inicio" in k or "fin" in k:
            try:
                cfg[k] = pd.to_datetime(v, dayfirst=True)
            except Exception:
                pass  # si no es fecha, lo deja como string

    # Ruta absoluta del archivo Excel
    if "archivo" in cfg:
        base = Path(__file__).resolve().parents[1]
        cfg["archivo"] = (base / cfg["archivo"]).resolve()

    return cfg
