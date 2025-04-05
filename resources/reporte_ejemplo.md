# RepoGPT Analysis Report

## Dependencies Found

- Files: `requirements.txt`
  *(Run with `--dependencies` for details)*


## File Details

### `.gitignore`
- **Lines:** 166

*Structure information not available for this file type or parsing failed early.*

---

### `.trunk/.gitignore`
- **Lines:** 9

*Structure information not available for this file type or parsing failed early.*

---

### `.trunk/configs/.isort.cfg`
- **Lines:** 2

*Structure information not available for this file type or parsing failed early.*

---

### `.trunk/configs/.markdownlint.yaml`
- **Lines:** 2

*Structure information not available for this file type or parsing failed early.*

---

### `.trunk/configs/ruff.toml`
- **Lines:** 5

*Structure information not available for this file type or parsing failed early.*

---

### `.trunk/trunk.yaml`
- **Lines:** 35

*Structure information not available for this file type or parsing failed early.*

---

### `IDEA.md`
- **Lines:** 9

*Structure information not available for this file type or parsing failed early.*

---

### `LICENSE`
- **Lines:** 21

*Structure information not available for this file type or parsing failed early.*

---

### `README.es`
- **Lines:** 201

*Structure information not available for this file type or parsing failed early.*

---

### `README.md`
- **Lines:** 207

*Structure information not available for this file type or parsing failed early.*

---

### `repogpt/__init__.py`
- **Lines:** 13

#### Structure:
- *(L12)* Import: `import logging`

---

### `repogpt/__main__.py`
- **Lines:** 260
- **Tasks Found:** 3 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import argparse`

- *(L3)* Import: `import logging`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import List, Dict, Union, Any`

- *(L7)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

- *(L8)* Import: `from repogpt.utils.logging import configure_logging`

- *(L9)* Import: `from repogpt.extractors import base as extractor_base`

- *(L11)* Import: `from repogpt.extractors import dependencies, git, metrics, todos`

- *(L12)* Import: `from repogpt.reporting import base as reporter_base`

- *(L13)* Import: `from repogpt.reporting import json_reporter, markdown_reporter`

- *(L14)* Import: `from repogpt.exceptions import RepoGPTException`

#### Function `main` *(L31)*
```python
def main():
    ...
```

---

### `repogpt/analyzer.py`
- **Lines:** 180

#### Structure:
- *(L2)* Import: `from concurrent.futures import ThreadPoolExecutor, as_completed`

- *(L3)* Import: `from typing import Any, Dict, Optional, Union`

- *(L4)* Import: `import os`

- *(L5)* Import: `import logging`

- *(L6)* Import: `from pathlib import Path`

- *(L8)* Import: `from parsers.base import get_parser`

- *(L9)* Import: `from utils.file_utils import calculate_file_hash, is_likely_binary`

- *(L10)* Import: `from utils.gitignore_handler import get_gitignore_matcher, is_path_ignored`

#### Class `RepositoryAnalyzer` *(L17)*
**Body:**
  #### Method `__init__` *(L18)*
  ```python
def __init__(self, repo_path: Union[str, Path], start_path: str = '', max_depth: Optional[int] = None, max_workers: int = 4, max_file_size: int = MAX_FILE_SIZE, use_gitignore: bool = True) -> `None`:
    ...
```
  #### Method `_validate_paths` *(L37)*
  ```python
def _validate_paths(self) -> `None`:
    ...
```
  #### Method `is_excluded` *(L49)*
  ```python
def is_excluded(self, path: Path) -> `bool`:
    ...
```
  #### Method `_walk_directory` *(L74)*
  ```python
def _walk_directory(self):
    ...
```
  #### Method `analyze_repository` *(L115)*
  ```python
def analyze_repository(self) -> `Dict[str, Any]`:
    ...
```
  #### Method `process_file` *(L147)*
  ```python
def process_file(self, file_path: Path) -> `Optional[Dict[str, Any]]`:
    ...
```
  > **Docstring:**
  > ```text
  > Procesa un archivo individual.
  > ```

---

### `repogpt/codigo_concatenado.txt`
- **Lines:** 2819

*Structure information not available for this file type or parsing failed early.*

---

### `repogpt/concat.py`
- **Lines:** 84

#### Structure:
- *(L4)* Import: `import os`

#### Function `concatenar_py_recursivo` *(L6)*
```python
def concatenar_py_recursivo(directorio_raiz = '.', archivo_salida = 'codigo_concatenado.txt'):
    ...
```
> **Docstring:**
> ```text
> Busca recursivamente archivos .py en directorio_raiz y sus subdirectorios,
> y concatena su contenido en archivo_salida, añadiendo una cabecera
> con la ruta del archivo antes de cada contenido.
> 
> Args:
>     directorio_raiz (str): La ruta al directorio desde donde empezar la búsqueda.
>                            Por defecto es el directorio actual ('.').
>     archivo_salida (str): El nombre del archivo donde se guardará el resultado.
>                           Por defecto es 'codigo_concatenado.txt'.
> ```

---

### `repogpt/exceptions.py`
- **Lines:** 26

#### Structure:
#### Class `RepoGPTException`(`Exception`) *(L3)*
> **Docstring:**
> ```text
> Clase base para excepciones específicas de RepoGPT.
> ```

#### Class `ConfigurationError`(`RepoGPTException`) *(L7)*
> **Docstring:**
> ```text
> Error relacionado con la configuración del análisis.
> ```

#### Class `ParsingError`(`RepoGPTException`) *(L11)*
> **Docstring:**
> ```text
> Error durante la fase de parsing de un archivo.
> ```
**Body:**
  #### Method `__init__` *(L13)*
  ```python
def __init__(self, message: str, file_path: str = None, parser_name: str = None):
    ...
```

#### Class `AnalysisError`(`RepoGPTException`) *(L20)*
> **Docstring:**
> ```text
> Error durante la fase principal de análisis del repositorio.
> ```

#### Class `ReportingError`(`RepoGPTException`) *(L24)*
> **Docstring:**
> ```text
> Error durante la generación del reporte.
> ```

---

### `repogpt/extractors/__init__.py`
- **Lines:** 20

#### Structure:
- *(L4)* Import: `from . import dependencies`

- *(L5)* Import: `from . import git`

- *(L6)* Import: `from . import metrics`

- *(L7)* Import: `from . import structure`

- *(L8)* Import: `from . import todos`

- *(L11)* Import: `from base import ExtractorModule`

---

### `repogpt/extractors/base.py`
- **Lines:** 34

#### Structure:
- *(L3)* Import: `import abc`

- *(L4)* Import: `import logging`

- *(L5)* Import: `from typing import Any, Dict`

- *(L8)* Import: `from typing import TYPE_CHECKING`

#### Class `ExtractorModule`(`abc.ABC`) *(L14)*
> **Docstring:**
> ```text
> Clase base abstracta para módulos que extraen información específica.
> ```
**Body:**
  #### Method `extract` *(L18)*
  > Decorator: `@abc.abstractmethod`
  ```python
def extract(self, analyzer: 'RepositoryAnalyzer', analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae información específica del repositorio o de los datos ya analizados.
  > 
  > Args:
  >     analyzer: La instancia de RepositoryAnalyzer (para acceso a repo_path, etc.).
  >     analyzed_data: El diccionario que contiene los resultados del análisis
  >                    de archivos realizado por RepositoryAnalyzer (bajo la clave 'files').
  >                    Este diccionario puede ser modificado por extractores anteriores.
  > 
  > Returns:
  >     Un diccionario que contiene la información extraída. La clave principal
  >     debe ser única para este extractor (ej. 'dependencies', 'git_info').
  >     Este diccionario se fusionará con los resultados generales.
  >     Debe devolver un diccionario vacío ({}) si no se extrae nada.
  > ```

---

### `repogpt/extractors/dependencies.py`
- **Lines:** 153
- **Tasks Found:** 2 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L3)* Import: `import json`

- *(L4)* Import: `import logging`

- *(L5)* Import: `import re`

- *(L6)* Import: `from pathlib import Path`

- *(L7)* Import: `from typing import Any, Dict, List, Optional`

- *(L9)* Import: `from base import ExtractorModule`

- *(L10)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

#### Class `DependencyExtractor`(`ExtractorModule`) *(L27)*
> **Docstring:**
> ```text
> Extrae información de dependencias de archivos comunes.
> ```
**Body:**
  #### Method `extract` *(L42)*
  ```python
def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Busca y parsea archivos de dependencias conocidos en la raíz del repo.
  > ```
  #### Method `_parse_package_json` *(L69)*
  ```python
def _parse_package_json(self, path: Path) -> `Dict[str, Any]`:
    ...
```
  #### Method `_parse_requirements_txt` *(L87)*
  ```python
def _parse_requirements_txt(self, path: Path) -> `List[str]`:
    ...
```
  #### Method `_parse_pipfile` *(L106)*
  ```python
def _parse_pipfile(self, path: Path) -> `Dict[str, Any]`:
    ...
```
  #### Method `_parse_pyproject` *(L120)*
  ```python
def _parse_pyproject(self, path: Path) -> `Dict[str, Any]`:
    ...
```
  #### Method `_parse_environment_yaml` *(L139)*
  ```python
def _parse_environment_yaml(self, path: Path) -> `Dict[str, Any]`:
    ...
```

---

### `repogpt/extractors/git.py`
- **Lines:** 82

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import subprocess`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import Any, Dict`

- *(L7)* Import: `from base import ExtractorModule`

- *(L8)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

#### Class `GitInfoExtractor`(`ExtractorModule`) *(L12)*
> **Docstring:**
> ```text
> Extrae información del repositorio Git si existe.
> ```
**Body:**
  #### Method `extract` *(L15)*
  ```python
def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Ejecuta comandos git para obtener información del último commit, rama, etc.
  > ```

---

### `repogpt/extractors/metrics.py`
- **Lines:** 90

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from pathlib import Path`

- *(L4)* Import: `from typing import Any, Dict`

- *(L6)* Import: `from base import ExtractorModule`

- *(L7)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

#### Class `CodeMetricsExtractor`(`ExtractorModule`) *(L11)*
> **Docstring:**
> ```text
> Calcula métricas básicas del código analizado.
> ```
**Body:**
  #### Method `extract` *(L14)*
  ```python
def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Calcula totales y estadísticas por tipo de archivo.
  > ```

---

### `repogpt/extractors/structure.py`
- **Lines:** 59

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from pathlib import Path`

- *(L4)* Import: `from typing import Any, Dict, List`

- *(L6)* Import: `from base import ExtractorModule`

- *(L7)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

#### Class `StructureExtractor`(`ExtractorModule`) *(L11)*
> **Docstring:**
> ```text
> Extrae una visión general de la estructura (clases, funciones) por archivo.
> ```
**Body:**
  #### Method `extract` *(L14)*
  ```python
def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Itera sobre los archivos analizados y extrae elementos estructurales clave.
  > ```

---

### `repogpt/extractors/todos.py`
- **Lines:** 49
- **Tasks Found:** 1 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from typing import Any, Dict, List`

- *(L5)* Import: `from base import ExtractorModule`

- *(L6)* Import: `from repogpt.analyzer import RepositoryAnalyzer`

#### Class `TodoFixmeExtractor`(`ExtractorModule`) *(L10)*
> **Docstring:**
> ```text
> Agrega todos los TODOs y FIXMEs encontrados por los parsers.
> ```
**Body:**
  #### Method `extract` *(L13)*
  ```python
def extract(self, analyzer: RepositoryAnalyzer, analyzed_data: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Recopila las entradas 'todos_fixmes' de cada archivo analizado.
  > ```

---

### `repogpt/parsers/__init__.py`
- **Lines:** 15

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from . import python`

- *(L4)* Import: `from . import markdown`

- *(L5)* Import: `from . import javascript`

- *(L6)* Import: `from . import yaml_parser`

- *(L7)* Import: `from . import html`

- *(L9)* Import: `from . import generic`

- *(L13)* Import: `from base import get_parser`

---

### `repogpt/parsers/base.py`
- **Lines:** 147
- **Tasks Found:** 2 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L3)* Import: `import abc`

- *(L4)* Import: `import logging`

- *(L5)* Import: `from pathlib import Path`

- *(L6)* Import: `from typing import Any, Dict, Optional, Type`

- *(L9)* Import: `from utils.file_utils import is_likely_binary`

#### Class `Parser`(`abc.ABC`) *(L15)*
> **Docstring:**
> ```text
> Clase base abstracta para todos los parsers de archivos.
> ```
**Body:**
  #### Method `parse` *(L19)*
  > Decorator: `@abc.abstractmethod`
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Analiza el contenido del archivo dado.
  > 
  > Args:
  >     file_path: Ruta al archivo a analizar.
  >     file_info: Diccionario con metadatos pre-calculados (size, hash, etc.).
  >                El parser puede añadir o modificar este diccionario.
  > 
  > Returns:
  >     Un diccionario con la información extraída específica del tipo de archivo.
  >     Este diccionario será fusionado con file_info.
  >     Debe devolver un diccionario vacío ({}) si no hay nada específico que extraer.
  >     Puede lanzar excepciones si el parsing falla catastróficamente,
  >     aunque es preferible devolver {'error': 'mensaje'} si es posible.
  > ```

#### Function `register_parser` *(L40)*
```python
def register_parser(extension: str, parser_class: Type[Parser]) -> `None`:
    ...
```
> **Docstring:**
> ```text
> Registra una clase Parser para una extensión de archivo específica.
> ```

#### Function `get_parser` *(L57)*
```python
def get_parser(file_path: Path) -> `Optional[Parser]`:
    ...
```
> **Docstring:**
> ```text
> Obtiene una instancia del parser adecuado para el archivo.
> Prioriza el nombre de archivo 'Dockerfile' y luego la extensión.
> 
> Args:
>     file_path: Ruta al archivo.
> 
> Returns:
>     Una instancia del Parser registrado, o None si no hay parser adecuado.
> ```

---

### `repogpt/parsers/dockerfile_.py`
- **Lines:** 172
- **Tasks Found:** 5 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import re`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import Any, Dict, List`

- *(L8)* Import: `from base import Parser, register_parser`

#### Class `DockerfileParser`(`Parser`) *(L12)*
> **Docstring:**
> ```text
> Parsea archivos Dockerfile.
> ```
**Body:**
  #### Method `parse` *(L40)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae instrucciones, argumentos, imágenes base, puertos y tareas.
  > ```

---

### `repogpt/parsers/generic.py`
- **Lines:** 88
- **Tasks Found:** 3 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from pathlib import Path`

- *(L4)* Import: `from typing import Any, Dict, List`

- *(L6)* Import: `from base import Parser`

- *(L8)* Import: `from utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments`

#### Class `GenericTextParser`(`Parser`) *(L16)*
> **Docstring:**
> ```text
> Parser genérico para archivos de texto no reconocidos por otros parsers.
> ```
**Body:**
  #### Method `parse` *(L19)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae información básica como conteo de líneas y TODOs/FIXMEs usando streaming.
  > ```

---

### `repogpt/parsers/html.py`
- **Lines:** 54
- **Tasks Found:** 1 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import re`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import Any, Dict`

- *(L7)* Import: `from base import Parser, register_parser`

- *(L8)* Import: `from utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines`

#### Class `HtmlParser`(`Parser`) *(L13)*
> **Docstring:**
> ```text
> Parsea archivos HTML (.html, .htm).
> ```
**Body:**
  #### Method `parse` *(L16)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae título, scripts y links.
  > ```

---

### `repogpt/parsers/javascript.py`
- **Lines:** 140
- **Tasks Found:** 3 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import re`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import Any, Dict, Set`

- *(L7)* Import: `from base import Parser, register_parser`

- *(L8)* Import: `from utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines`

#### Class `JavaScriptParser`(`Parser`) *(L23)*
> **Docstring:**
> ```text
> Parsea archivos JavaScript/TypeScript (.js, .jsx, .ts, .tsx).
> ```
**Body:**
  #### Method `parse` *(L26)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Intenta usar AST si está disponible, si no, usa Regex.
  > ```
  #### Method `_parse_with_regex` *(L92)*
  ```python
def _parse_with_regex(self, content: str) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Análisis basado en Regex para JS/TS (menos preciso).
  > ```

---

### `repogpt/parsers/markdown.py`
- **Lines:** 59
- **Tasks Found:** 1 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import re`

- *(L4)* Import: `from pathlib import Path`

- *(L5)* Import: `from typing import Any, Dict`

- *(L7)* Import: `from base import Parser, register_parser`

- *(L8)* Import: `from utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines`

#### Class `MarkdownParser`(`Parser`) *(L12)*
> **Docstring:**
> ```text
> Parsea archivos Markdown (.md, .mdx).
> ```
**Body:**
  #### Method `parse` *(L15)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae encabezados, links y fragmentos de código.
  > ```

---

### `repogpt/parsers/python.py`
- **Lines:** 304
- **Tasks Found:** 5 TODOs, 1 FIXMEs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L4)* Import: `import ast`

- *(L5)* Import: `import logging`

- *(L6)* Import: `from pathlib import Path`

- *(L7)* Import: `from typing import Any, Dict, List, Union`

- *(L8)* Import: `import tokenize`

- *(L11)* Import: `from base import Parser, register_parser`

- *(L12)* Import: `from utils.text_processing import extract_todos_fixmes_from_comments, count_blank_lines`

#### Function `get_comment_text` *(L16)*
```python
def get_comment_text(comment_token: tokenize.TokenInfo) -> `str`:
    ...
```
> **Docstring:**
> ```text
> Extrae el texto limpio de un token de comentario.
> ```

#### Class `PythonParser`(`Parser`) *(L22)*
> **Docstring:**
> ```text
> Parsea archivos Python (.py) usando ast y tokenize.
> Extrae una estructura ordenada de elementos: imports, comentarios,
> clases (con métodos y docstrings) y funciones (con docstrings).
> ```
**Body:**
  #### Method `parse` *(L29)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Analiza el archivo Python para extraer su estructura ordenada.
  > ```
  #### Method `_get_node_end_lineno` *(L126)*
  ```python
def _get_node_end_lineno(self, node: ast.AST) -> `int`:
    ...
```
  > **Docstring:**
  > ```text
  > Obtiene la línea final de un nodo AST, manejando nodos sin end_lineno.
  > ```
  #### Method `_parse_import` *(L130)*
  ```python
def _parse_import(self, node: Union[ast.Import, ast.ImportFrom]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae información de una declaración de import.
  > ```
  #### Method `_parse_class` *(L145)*
  ```python
def _parse_class(self, node: ast.ClassDef) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae información detallada de una definición de clase y su cuerpo.
  > ```
  #### Method `_parse_function` *(L175)*
  ```python
def _parse_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], is_method = False, clean_docstring = True) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Extrae información detallada de una definición de función/método.
  > ```
  #### Method `_get_decorator_names` *(L190)*
  ```python
def _get_decorator_names(self, decorator_list: List[ast.expr]) -> `List[str]`:
    ...
```
  > **Docstring:**
  > ```text
  > Intenta obtener los nombres de los decoradores usando ast.unparse.
  > ```
  #### Method `_get_qual_names` *(L206)*
  ```python
def _get_qual_names(self, nodes: List[ast.expr]) -> `List[str]`:
    ...
```
  > **Docstring:**
  > ```text
  > Intenta obtener nombres calificados (ej. module.Class) usando ast.unparse.
  > ```
  #### Method `_format_arguments` *(L217)*
  ```python
def _format_arguments(self, args: ast.arguments) -> `List[str]`:
    ...
```
  > **Docstring:**
  > ```text
  > Formatea los argumentos de una función/método a una lista de strings.
  > ```

---

### `repogpt/parsers/yaml_parser.py`
- **Lines:** 93
- **Tasks Found:** 1 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from pathlib import Path`

- *(L4)* Import: `from typing import Any, Dict`

- *(L6)* Import: `from base import Parser, register_parser`

- *(L7)* Import: `from utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines`

#### Class `YamlParser`(`Parser`) *(L23)*
> **Docstring:**
> ```text
> Parsea archivos YAML (.yaml, .yml).
> ```
**Body:**
  #### Method `parse` *(L26)*
  ```python
def parse(self, file_path: Path, file_info: Dict[str, Any]) -> `Dict[str, Any]`:
    ...
```
  > **Docstring:**
  > ```text
  > Intenta cargar el archivo YAML y extrae claves principales.
  > ```
  #### Method `_get_structure_preview` *(L70)*
  ```python
def _get_structure_preview(self, data: Any, depth = 0, max_depth = 2) -> `Any`:
    ...
```
  > **Docstring:**
  > ```text
  > Genera una vista previa de la estructura YAML/Dict.
  > ```

---

### `repogpt/reporting/__init__.py`
- **Lines:** 12

#### Structure:
- *(L3)* Import: `from . import json_reporter`

- *(L4)* Import: `from . import markdown_reporter`

- *(L6)* Import: `from base import Reporter`

---

### `repogpt/reporting/base.py`
- **Lines:** 21

#### Structure:
- *(L3)* Import: `import abc`

- *(L4)* Import: `from typing import Any, Dict`

#### Class `Reporter`(`abc.ABC`) *(L6)*
> **Docstring:**
> ```text
> Clase base abstracta para generadores de reportes.
> ```
**Body:**
  #### Method `generate` *(L10)*
  > Decorator: `@abc.abstractmethod`
  ```python
def generate(self, analysis_data: Dict[str, Any]) -> `str`:
    ...
```
  > **Docstring:**
  > ```text
  > Genera el contenido del reporte a partir de los datos analizados.
  > 
  > Args:
  >     analysis_data: El diccionario completo que contiene todos los datos
  >                    recopilados por el analizador y los extractores.
  > 
  > Returns:
  >     Una cadena de texto que representa el reporte formateado.
  > ```

---

### `repogpt/reporting/json_reporter.py`
- **Lines:** 39

#### Structure:
- *(L1)* Import: `import json`

- *(L2)* Import: `import logging`

- *(L3)* Import: `from typing import Any, Dict`

- *(L4)* Import: `import argparse`

- *(L6)* Import: `from base import Reporter`

- *(L8)* Import: `from repogpt.exceptions import ReportingError`

#### Class `JsonReporter`(`Reporter`) *(L12)*
> **Docstring:**
> ```text
> Genera el reporte en formato JSON.
> ```
**Body:**
  #### Method `generate` *(L16)*
  ```python
def generate(self, analysis_data: Dict[str, Any], report_options: argparse.Namespace) -> `str`:
    ...
```
  > **Docstring:**
  > ```text
  > Convierte los datos de análisis a una cadena JSON formateada.
  > ```

---

### `repogpt/reporting/markdown_reporter.py`
- **Lines:** 286
- **Tasks Found:** 4 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L3)* Import: `import logging`

- *(L4)* Import: `from typing import Any, Dict, List`

- *(L5)* Import: `import json`

- *(L6)* Import: `import argparse`

- *(L8)* Import: `from base import Reporter`

#### Class `MarkdownReporter`(`Reporter`) *(L12)*
> **Docstring:**
> ```text
> Genera el reporte en formato Markdown, incluyendo estructura detallada del código.
> ```
**Body:**
  #### Method `generate` *(L16)*
  ```python
def generate(self, analysis_data: Dict[str, Any], report_options: argparse.Namespace) -> `str`:
    ...
```
  > **Docstring:**
  > ```text
  > Crea una cadena de texto Markdown a partir de los datos de análisis.
  > ```
  #### Method `_render_structure` *(L176)*
  ```python
def _render_structure(self, lines: List[str], structure: List[Dict[str, Any]], indent_level: int = 0):
    ...
```
  > **Docstring:**
  > ```text
  > Renderiza recursivamente la lista de elementos estructurales.
  > ```
  #### Method `_render_function` *(L195)*
  ```python
def _render_function(self, lines: List[str], element: Dict[str, Any], indent: str):
    ...
```
  > **Docstring:**
  > ```text
  > Renderiza una función o método.
  > ```
  #### Method `_render_class` *(L231)*
  ```python
def _render_class(self, lines: List[str], element: Dict[str, Any], indent: str, indent_level: int):
    ...
```
  > **Docstring:**
  > ```text
  > Renderiza una clase y su cuerpo.
  > ```
  #### Method `_format_size` *(L265)*
  ```python
def _format_size(self, size_bytes: int) -> `str`:
    ...
```
  #### Method `_append_task_section` *(L274)*
  ```python
def _append_task_section(self, lines: List[str], title: str, task_map: Dict[str, List[Dict[str, Any]]]):
    ...
```

---

### `repogpt/utils/__init__.py`
- **Lines:** 6

*Structure information not available for this file type or parsing failed early.*

---

### `repogpt/utils/file_utils.py`
- **Lines:** 80

#### Structure:
- *(L3)* Import: `import hashlib`

- *(L4)* Import: `import logging`

- *(L5)* Import: `from pathlib import Path`

- *(L6)* Import: `from typing import Optional`

#### Function `calculate_file_hash` *(L12)*
```python
def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> `Optional[str]`:
    ...
```
> **Docstring:**
> ```text
> Calcula el hash de un archivo usando el algoritmo especificado.
> 
> Args:
>     file_path: Ruta al archivo.
>     algorithm: Algoritmo de hash a usar (ej. 'sha256', 'md5').
> 
> Returns:
>     El hash en formato hexadecimal como string, o None si ocurre un error.
> ```

#### Function `is_likely_binary` *(L42)*
```python
def is_likely_binary(file_path: Path, check_bytes: int = 1024) -> `bool`:
    ...
```
> **Docstring:**
> ```text
> Intenta determinar si un archivo es probablemente binario.
> 
> Actualmente usa una heurística simple: la presencia de un byte NULL
> dentro de los primeros 'check_bytes'.
> 
> Args:
>     file_path: Ruta al archivo.
>     check_bytes: Número de bytes iniciales a revisar.
> 
> Returns:
>     True si el archivo parece binario, False en caso contrario o si hay error.
> ```

---

### `repogpt/utils/gitignore_handler.py`
- **Lines:** 102

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `from pathlib import Path`

- *(L4)* Import: `from typing import Callable, Optional, Dict`

#### Function `_load_matcher_uncached` *(L23)*
```python
def _load_matcher_uncached(gitignore_path: Path) -> `Optional[Callable[[str], bool]]`:
    ...
```
> **Docstring:**
> ```text
> Carga el matcher desde un archivo .gitignore sin usar caché.
> ```

#### Function `get_gitignore_matcher` *(L51)*
```python
def get_gitignore_matcher(repo_path: Path, use_cache: bool = True) -> `Optional[Callable[[str], bool]]`:
    ...
```
> **Docstring:**
> ```text
> Obtiene la función matcher para el .gitignore del repositorio, opcionalmente desde caché.
> 
> Args:
>     repo_path: La ruta raíz del repositorio donde buscar .gitignore.
>     use_cache: Si se debe usar la caché de matchers.
> 
> Returns:
>     Una función que toma un path (string) y devuelve True si debe ser ignorado,
>     o None si no hay .gitignore o no se pudo parsear.
> ```

#### Function `is_path_ignored` *(L77)*
```python
def is_path_ignored(absolute_path: Path, matcher: Optional[Callable[[str], bool]]) -> `bool`:
    ...
```
> **Docstring:**
> ```text
> Verifica si una ruta absoluta debe ser ignorada según el matcher de .gitignore.
> 
> Args:
>     absolute_path: La ruta absoluta del archivo o directorio a verificar.
>     matcher: La función matcher obtenida de get_gitignore_matcher.
> 
> Returns:
>     True si la ruta debe ser ignorada, False en caso contrario.
> ```

---

### `repogpt/utils/logging.py`
- **Lines:** 27

#### Structure:
- *(L2)* Import: `import logging`

- *(L3)* Import: `import sys`

#### Function `configure_logging` *(L5)*
```python
def configure_logging(log_level: str) -> `None`:
    ...
```

---

### `repogpt/utils/text_processing.py`
- **Lines:** 128
- **Tasks Found:** 2 TODOs, 1 FIXMEs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L2)* Import: `import re`

- *(L3)* Import: `import logging`

- *(L4)* Import: `from typing import List, Dict, Any, Tuple`

#### Function `extract_todos_fixmes_from_comments` *(L12)*
```python
def extract_todos_fixmes_from_comments(comments: List[Dict[str, Any]]) -> `Dict[str, List[Dict[str, Any]]]`:
    ...
```
> **Docstring:**
> ```text
> Extrae TODOs y FIXMEs encontrados dentro de una lista de comentarios pre-extraídos.
> 
> Args:
>     comments: Una lista de diccionarios, donde cada dict representa un comentario
>               y debe tener al menos las claves 'line' (int o str) y 'text' (str).
> 
> Returns:
>     Un diccionario con claves 'todos' y 'fixmes', cada una conteniendo una lista
>     de diccionarios {'line': ..., 'message': ...}.
> ```

#### Function `extract_comments_from_content` *(L48)*
```python
def extract_comments_from_content(content: str, line_comment_patterns: List[str] = [], block_comment_patterns: List[Tuple[str, str]] = [], include_docstrings: bool = False) -> `List[Dict[str, Any]]`:
    ...
```
> **Docstring:**
> ```text
> Extrae comentarios de un bloque de contenido usando patrones Regex.
> 
> Args:
>     content: El contenido completo del archivo como string.
>     line_comment_patterns: Lista de patrones regex para comentarios de una línea.
>                            El grupo 1 debe capturar el texto del comentario.
>     block_comment_patterns: Lista de tuplas (start_regex, end_regex) para comentarios de bloque.
>                             La extracción será básica (extrae todo entre start y end).
>     include_docstrings: (No implementado aún) Si intentar extraer docstrings genéricos.
> 
> 
> Returns:
>     Lista de diccionarios de comentarios {'line': int, 'text': str} o {'line': 'block', 'text': str}.
>     El número de línea es aproximado para bloques.
> ```

#### Function `count_blank_lines` *(L122)*
```python
def count_blank_lines(content: str) -> `int`:
    ...
```
> **Docstring:**
> ```text
> Cuenta las líneas que están vacías o contienen solo espacios en blanco.
> ```

---

### `requirements.txt`
- **Lines:** 8

*Structure information not available for this file type or parsing failed early.*

---

### `setup.py`
- **Lines:** 63
- **Tasks Found:** 1 TODOs
  *(Run with `--tasks` for full list)*

#### Structure:
- *(L3)* Import: `from setuptools import setup, find_packages`

---


*Note: Some sections may be hidden. Use flags like `--summary`, `--dependencies`, `--tasks`, `--file-metadata` to show more details.*