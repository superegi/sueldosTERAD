# Sueldos TERAD

Herramienta interna para calcular producción y sueldos del servicio de imagenología (ecografías / informes radiológicos).

Este script:
- Lee una planilla de estudios realizados (Excel).
- Aplica ventanas de fechas para cada rol.
- Genera un resumen de trabajo por Tecnólogo Médico y por Radiólogo.
- Excluye centros específicos según reglas internas (por ejemplo, ciertos hospitales convenidos que no se pagan igual).
- Genera una bitácora de auditoría con todo lo calculado.

> Importante: Este repositorio **no** calcula montos en dinero todavía. Solo genera la base trazable para liquidación (qué hizo cada quién, cuándo y cuántos estudios califican para pago).


## Estructura del proyecto

```text
Sueldos/
├── codigo/
│   ├── main2.py              # Script principal (orquestador)
│   ├── configuracion.py      # Lector de config.txt
│   ├── ...                   # Lógica de filtrado (tecnólogos / radiólogos)
│
├── data/
│   └── studies-....xlsx      # Planilla de origen con los estudios (NO subir a GitHub público)
│
├── config.txt                # Archivo de configuración por período
├── requirements.txt          # Dependencias de Python
├── venv/                     # Virtualenv local (NO subir)
└── Bitacora_YYYY-MM-DD_...txt# Bitácora generada automáticamente por cada corrida
```

### `config.txt`

El script no tiene fechas fijas. Usa un archivo de configuración externo con este formato:

```text
# Archivo de entrada
archivo = data/studies-excel-20251031094110.xlsx

# Fechas Tecnólogos (se paga por Fecha estudio)
inicio_tm = 26-09-2025 08:00
fin_tm    = 31-10-2025 08:00

# Fechas Radiólogos (se paga por Fecha de finalización de informe)
inicio_rad = 26-09-2025 08:00
fin_rad    = 31-10-2025 08:00
```

Notas:
- Formato de fecha/hora: `DD-MM-YYYY HH:MM` (día primero).
- `archivo` se resuelve relativo a la carpeta raíz del repo.
- `inicio_tm` / `fin_tm` definen la ventana para Tecnólogos Médicos.
- `inicio_rad` / `fin_rad` definen la ventana para Radiólogos.


## Cómo correr el script

### 1. Activar el entorno virtual

```bash
cd /ruta/a/Sueldos
source venv/bin/activate
```

### 2. Ejecutar con la configuración por defecto

```bash
python codigo/main2.py
```

### 3. Ejecutar con otra configuración

```bash
python codigo/main2.py --config /ruta/a/mi_config_mensual.txt
```

## Dependencias

```bash
pip install -r requirements.txt
```

## Seguridad y datos sensibles

- **NO subir la carpeta `data/` a GitHub público**.
- **NO subir las bitácoras (`Bitacora_*.txt`)**.
- **NO subir el `venv/`**.
- Si el repo se hace público: incluir solo el código (`codigo/`), `requirements.txt` y un `config_ejemplo.txt` sin datos reales.

## Licencia y uso

Uso interno dentro del marco de la empresa de teleradiología TERAD.  
Contiene información potencialmente sensible (datos de salud).  
Cumplir con la Ley 19.628 (Chile) sobre protección de datos personales.
