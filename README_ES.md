Claro, la descripción original ya es bastante buena: es exhaustiva, bien estructurada y clara. Sin embargo, siempre es posible mejorar ciertos aspectos, principalmente desde estas perspectivas:

- **Claridad y precisión del lenguaje**
- **Mayor énfasis en los casos prácticos y utilidades reales**
- **Reducción de redundancias**
- **Inclusión de contexto sobre beneficios y casos de uso específicos**
- **Consistencia en estilo y formatos**

Aquí tienes una versión mejorada y optimizada de la documentación de tu proyecto:

---

# RepoGPT 📚

**RepoGPT** es una herramienta de análisis automatizado de repositorios de software que genera reportes estructurados, ideales para ser consumidos rápidamente por Modelos de Lenguaje (LLMs) o revisión humana. Recorre recursivamente las carpetas del proyecto, analiza múltiples tipos de archivos, extrae información estructural, metadatos, dependencias y tareas pendientes, generando informes detallados en formatos Markdown o JSON.

*Inspirado en [gpt-repository-loader](https://github.com/mpoon/gpt-repository-loader) y [gptrepo](https://github.com/zackees/gptrepo/tree/main).*

## ¿Por qué usar RepoGPT? 💡

- **Simplifica la comprensión del código**:
  - Extrae clases, métodos, funciones, interfaces (en TS), importaciones, decoradores y documentación integrada en el código.
  - Muestra claramente la estructura jerárquica del código.
  
- **Automatiza tareas tediosas**:
  - Identifica automáticamente `TODO` y `FIXME` en el código.
  - Recopila metadatos relevantes (autoría, ramas, commits, dependencias).

- **Flexible y configurable**:
  - Informes personalizables en Markdown o JSON.
  - Respeta `.gitignore` y admite configuraciones avanzadas.

---

## Funcionalidades Principales ⚙️

| Característica                 | Descripción                                                     |
|--------------------------------|-----------------------------------------------------------------|
| **Soporte multilenguaje**      | Python, JavaScript, TypeScript, JSX/TSX, Markdown, YAML, HTML, Dockerfile y análisis básico de archivos genéricos. |
| **Metadatos avanzados**        | Información de Git (autor, rama, commits recientes), dependencias del proyecto (`package.json`, `requirements.txt`, `pyproject.toml`), métricas de código (número de líneas, tipos de archivo, tamaño). |
| **Identificación de tareas**   | Recopilación centralizada de comentarios del tipo `TODO` y `FIXME`. |
| **Generación flexible de reportes** | Formatos Markdown (por defecto) enriquecidos con resaltado sintáctico, o JSON completo. Control detallado de secciones incluidas. |
| **Ejecución paralela**         | Procesamiento concurrente de archivos para análisis más veloz. |
| **Integración `.gitignore`**   | Exclusión automática de archivos no relevantes según reglas `.gitignore` (opcionalmente desactivable). |
| **Configuración avanzada**     | Selección específica de subdirectorios iniciales, extractores activos y tamaño máximo de archivos. |

---

## Instalación 🚀

### 📋 **Requisitos previos**

- Python 3.9 o superior
- Git (necesario solo para extractor `git`)

### 💻 **Pasos de instalación**

1. Clona el repositorio:

```bash
git clone https://github.com/MrCabss69/RepoGPT.git
```

2. Dirígete a la carpeta del proyecto:

```bash
cd RepoGPT
```

3. Instala el módulo (recomendado en modo editable):

```bash
pip install -e .
```

**Dependencias adicionales (recomendado para soporte completo):**

```bash
pip install -e .[js,yaml,gitignore]
```

> **Nota**: Define estos extras en `setup.py` o `pyproject.toml`.

---

## Uso básico ▶️

Desde tu terminal ejecuta:

```bash
repogpt
```

**Ejemplos comunes:**

- Análisis completo guardado en Markdown:

```bash
repogpt --summary --dependencies --tasks --file-metadata -o reporte_detallado.md
```

- Generar salida JSON:

```bash
repogpt -f json -o reporte.json
```

- Análisis específico de subcarpeta (`src`):

```bash
repogpt --start-path src -o src_reporte.md
```

- Omitir reglas de `.gitignore`:

```bash
repogpt --no-gitignore -o reporte_sin_ignorar.md
```

- Ajustar tamaño máximo de archivos (10 MB):

```bash
repogpt --max-file-size 10485760 -o reporte_archivos_grandes.md
```

- Incrementar paralelismo:

```bash
repogpt --max-workers 8
```

- Extraer métricas puntuales con `jq`:

```bash
repogpt -f json | jq '.code_metrics.total_files'
```

---

## 📖 **Estructura del Proyecto (Interna)**

```
repogpt/
├── __init__.py
├── __main__.py               # Entrada CLI
├── analyzer.py               # Lógica principal del análisis
├── exceptions.py             # Excepciones personalizadas
├── extractors/               # Extractores especializados
│   ├── base.py
│   ├── dependencies.py
│   ├── git.py
│   ├── metrics.py
│   ├── structure.py          # Estructura (no usado por defecto)
│   └── todos.py
├── parsers/                  # Análisis según tipo de archivo
│   ├── python.py
│   ├── javascript.py
│   ├── markdown.py
│   ├── yaml_parser.py
│   ├── html.py
│   ├── dockerfile_.py
│   └── generic.py
├── reporting/                # Generación de reportes
│   ├── json_reporter.py
│   └── markdown_reporter.py
├── utils/                    # Utilidades internas
│   ├── file_utils.py
│   ├── gitignore_handler.py
│   ├── logging.py
│   └── text_processing.py
├── README.md
├── setup.py                  # o pyproject.toml
└── repogpt_analyzer.log      # Log por defecto
```

---

## 🧑‍💻 **Opciones Avanzadas (CLI)**

| Parámetro | Descripción | Valor predeterminado |
|-----------|-------------|-----------------------|
| `repo_path` (posicional) | Ruta al repositorio objetivo | `.` (directorio actual) |
| `--start-path` | Carpeta inicial de análisis relativa a `repo_path` | `""` |
| `-o`, `--output-file` | Archivo para guardar reporte | Consola (si no se especifica) |
| `-f`, `--format` | Formato del reporte (`md`, `json`) | `md` |
| `--extractors` | Extractores específicos a utilizar | Todos |
| `--max-workers` | Número máximo de procesos paralelos | `4` |
| `--max-file-size` | Tamaño máximo de archivo en bytes | `2097152` (2MB) |
| `--no-gitignore` | Ignorar reglas `.gitignore` | Desactivado (usa `.gitignore`) |
| `--log-level` | Nivel de detalle en logs (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) | `INFO` |
| `--version` | Muestra la versión instalada |  |

---

## 🔖 **Ejemplos y Referencias**

- [`reporte_ejemplo.md`](resources/reporte_ejemplo.md)
- [`reporte_ejemplo.json`](resources/reporte_ejemplo.json)
