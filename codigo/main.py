import sys
from pathlib import Path

# --- asegurar que la raíz del proyecto esté en sys.path ---
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from pathlib import Path
from datetime import datetime
import argparse



########################################
# Bitácora
########################################

from datetime import datetime

def _ruta_bitacora(nombre_script="main2.py"):
    """
    Genera una ruta de bitácora con timestamp en formato:
    Bitacora_YYYY-MM-DD_HH_MM_SS.txt
    Guardada siempre en la raíz del proyecto.
    """
    base = Path(__file__).resolve().parents[1]
    timestamp = datetime.now().strftime("%Y%m%d %H%M%S")
    nombre = f"Bitacora_{timestamp}.txt"
    return base / nombre


# variable global para esta corrida
BITACORA_RUTA = _ruta_bitacora()

def anotar_inicio(nombre_script="main2.py"):
    """
    Crea una nueva bitácora con timestamp e indica el inicio del script.
    """
    marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"{marca_tiempo}  Inicio del script: {nombre_script}\n"

    with BITACORA_RUTA.open("a", encoding="utf-8") as f:
        f.write(linea)

    print(f"[bitácora] Archivo creado: {BITACORA_RUTA}")

def _a_texto(obj):
    """Convierte obj en texto legible."""
    if obj is None:
        return "(None)"
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_string()
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    return str(obj)

def anotar(texto):
    """
    Escribe texto en la bitácora actual (creada al inicio).
    """
    cuerpo = _a_texto(texto).rstrip() + "\n"
    with BITACORA_RUTA.open("a", encoding="utf-8") as f:
        f.write(cuerpo)

########################################
# Carga / limpieza de la base
########################################

def cargar_bd(ruta_excel):
    BD = pd.read_excel(ruta_excel)

    interes = [
        'ID paciente', 'Nombre de paciente',
        'Centro referente',
        'Descripción',
        'Modalidad',
        'Fecha estudio', 'Fecha de recepción',
        'Radiólogo', 'Estado',
        'Fecha de finalización',
        'EcoTM'
    ]

    BD = BD[interes].copy()

    # parsear fechas en formato chileno (día/mes/año)
    for x in ['Fecha estudio', 'Fecha de recepción', 'Fecha de finalización']:
        BD[x] = pd.to_datetime(BD[x], dayfirst=True, errors='coerce')

    return BD


########################################
# TECNÓLOGOS MÉDICOS
########################################

def procesar_tecnologos(BD, inicio, fin):
    """
    Filtra el DataFrame para los tecnólogos en base a 'Fecha estudio'
    dentro del rango [inicio, fin], y devuelve:
    - subset TMs
    - info de rango observado
    - conteo por EcoTM
    """
    TMs = BD[(BD['Fecha estudio'] > inicio) & (BD['Fecha estudio'] < fin)].copy()

    # rango real encontrado en los datos filtrados
    rango1 = TMs['Fecha estudio'].min()
    rango2 = TMs['Fecha estudio'].max()

    # cuántos estudios hizo cada TM (EcoTM parece ser el nombre del TM que hizo la eco)
    conteo_por_tm = TMs['EcoTM'].value_counts()

    return TMs, rango1, rango2, conteo_por_tm


def volcar_detalle_tm(TMs):
    """
    Escribe en la bitácora el detalle por cada tecnólogo:
    - nombre
    - tabla con exámenes de esa persona
    """
    tecnologos = TMs.groupby('EcoTM')['Fecha estudio'].count().index

    anotar("###############################")
    anotar("Ahora un resumen de todas las ecografías de los TM")

    for tm_nombre in tecnologos:
        anotar(f"nombre del TM: {tm_nombre}")

        dum = TMs[TMs.EcoTM == tm_nombre][[
            'Nombre de paciente',
            'Centro referente', 'Descripción', 'Fecha estudio',
            'Fecha de recepción', 'Radiólogo', 'Estado',
            'Fecha de finalización'
        ]]

        anotar(dum)
        anotar("########")


########################################
# RADIÓLOGOS
########################################

def procesar_radiologos(BD, inicio, fin):
    """
    - Filtra por rango usando 'Fecha de finalización'
    - Se queda solo con Estado == 'Informado'
    - Excluye centro referente con 'QUILPUE'
    Devuelve DF limpio y también el resumen agrupado.
    """
    Rads = BD[
        (BD['Fecha de finalización'] > inicio) &
        (BD['Fecha de finalización'] < fin)
    ].copy()

    Rads = Rads[Rads['Estado'] == 'Informado'].copy()

    # auditoría: cuántos del Hospital de Quilpué (que se excluirán)
    mask_quilpue = Rads['Centro referente'].str.contains('QUILPUE', case=False, na=False)
    conteo_quilpue = Rads[mask_quilpue]['Modalidad'].value_counts()

    # excluir Quilpué
    Rads = Rads[~mask_quilpue].copy()

    # resumen final por radiólogo y modalidad
    resumen_rads = (
        Rads
        .groupby(['Radiólogo', 'Modalidad'])['Estado']
        .count()
    )

    return Rads, conteo_quilpue, resumen_rads


def volcar_detalle_radiologos(Rads):
    """
    Escribe en la bitácora el detalle por cada radiólogo:
    - nombre
    - tabla ordenada cronológicamente con sus estudios
    """
    anotar("##########################")
    anotar("Produccion por Radiólogo")

    lista_rads = Rads.groupby('Radiólogo')['Fecha de finalización'].count().index

    for rnom in lista_rads:

        dum = Rads[Rads['Radiólogo'] == rnom][[
            'ID paciente', 'Modalidad',
            'Fecha estudio', 'Fecha de recepción', 'Fecha de finalización',
            'Radiólogo', 'Estado',
        ]].sort_values('Fecha de finalización')

        dum2 = dum.Modalidad.value_counts()

        anotar(f"nombre del Radiólogo: {rnom}")
        print(f"nombre del Radiólogo: {rnom}")
        anotar(f"cantidad de estudios {dum.shape[0]}")
        anotar(f"Tipo de estudios {dum2}")
        print(f"Tipo de estudios {dum2}")
        anotar(dum)

        anotar("################################################")
        anotar(" ")


########################################
# MAIN
########################################

from codigo.configuracion import leer_config

if __name__ == "__main__":
    # ---------------------------------
    # 0. argumentos de línea de comando
    # ---------------------------------
    parser = argparse.ArgumentParser(description="Cálculo de producción/sueldos TM y radiólogos")
    parser.add_argument(
        "--config",
        type=str,
        help="Ruta al archivo de configuración. Si no se entrega, se usa el config.txt estándar.",
        default=None,
    )
    args = parser.parse_args()

    # 1. marcar inicio en bitácora
    anotar_inicio(nombre_script="main2.py")

    # 2. resolver ruta al archivo de configuración
    base = Path(__file__).resolve().parents[1]

    if args.config is not None:
        # el usuario pasó un archivo explícito
        ruta_cfg = Path(args.config).expanduser().resolve()
        print(f"[INFO] Usando configuración personalizada: {ruta_cfg}")
        anotar(f"Configuración usada (custom): {ruta_cfg}")
    else:
        # fallback: config estándar
        # si tu config.txt vive en la raíz del repo, usa esta:
        ruta_cfg = base / "config.txt"

        # si prefieres mantenerlo en codigo/config.txt, cambia a:
        # ruta_cfg = base / "codigo" / "config.txt"

        print(f"[INFO] Usando configuración estándar: {ruta_cfg}")
        anotar(f"Configuración usada (default): {ruta_cfg}")

    # 3. leer configuración
    cfg = leer_config(ruta_cfg)

    ruta_excel = cfg["archivo"]
    inicio_tm  = cfg["inicio_tm"]
    fin_tm     = cfg["fin_tm"]
    inicio_rad = cfg["inicio_rad"]
    fin_rad    = cfg["fin_rad"]

    # registrar en bitácora las ventanas y archivo fuente
    anotar("Archivo de entrada: " + str(ruta_excel))
    anotar(f"Rango TM: {inicio_tm} → {fin_tm}")
    anotar(f"Rango Rads: {inicio_rad} → {fin_rad}")

    # 4. cargar datos crudos
    BD = cargar_bd(ruta_excel)

    # --------------------------
    # TECNÓLOGOS
    # --------------------------
    anotar("Fechas de inicio y término TMs (aplican a Fecha estudio)")
    anotar(f"inicio TM: {inicio_tm}")
    anotar(f"fin TM: {fin_tm}")

    TMs, rango1, rango2, conteo_por_tm = procesar_tecnologos(BD, inicio_tm, fin_tm)

    print("Descripción de Fecha estudio en TMs:")
    print(TMs['Fecha estudio'].describe())

    print("\nConteo por EcoTM:")
    print(conteo_por_tm)

    anotar(f"Primer estudio TM en el rango: {rango1}")
    anotar(f"Último estudio TM en el rango: {rango2}")
    anotar("Conteo por EcoTM:")
    anotar(conteo_por_tm)

    volcar_detalle_tm(TMs)

    # --------------------------
    # RADIÓLOGOS
    # --------------------------
    anotar("##############################################################")
    anotar("Vamos a ver a los radiologos!!!!!")

    Rads, conteo_quilpue, resumen_rads = procesar_radiologos(BD, inicio_rad, fin_rad)

    anotar("Cuantos son del Hospital de Quilpue?")
    anotar(conteo_quilpue)
    print("\nCuantos son del Hospital de Quilpue?")
    print(conteo_quilpue)

    anotar("Este es el resumen total a calcular (Radiólogo x Modalidad)")
    anotar(resumen_rads)
    print("\nResumen total a calcular (Radiólogo x Modalidad):")
    print(resumen_rads)

    volcar_detalle_radiologos(Rads)