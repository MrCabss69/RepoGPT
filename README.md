# RepoGPT

RepoGPT es una herramienta avanzada diseñada para analizar repositorios de código, generando resúmenes detallados y estructurados de los proyectos. Inspirada en las herramientas gpt-repository-loader y gptrepo, RepoGPT facilita la comprensión de la estructura y los componentes de un proyecto, optimizando su integración con plataformas como ChatGPT.

## Características Principales

- **Análisis de Archivos:** RepoGPT realiza un escaneo profundo de los archivos en el repositorio, recopilando información crucial como el conteo de líneas, las clases y sus métodos, funciones independientes y docstrings asociados.

- **Documentación Mejorada:** La herramienta pone especial énfasis en la claridad y calidad de la documentación del código, promoviendo buenas prácticas como el uso de nomenclaturas claras para variables y docstrings detallados.


## Opciones de Invocación Detalladas

RepoGPT permite personalizar el análisis mediante las siguientes opciones:

- `--repo_path`: Especifica el camino al repositorio a analizar. Por defecto, se utiliza el directorio actual.
  
- `--extensions`: Define las extensiones de archivo a incluir en el análisis. Por defecto, se incluyen archivos .md.
  
- `--start_path`: Permite iniciar el análisis desde un subdirectorio específico del repositorio.

**Ejemplo:**

```bash
python3 run.py --repo_path /camino/al/repo --extensions .py .js --start_path src
```

## Uso de RepoGPT

Para empezar a utilizar RepoGPT, sigue estos sencillos pasos:

1. **Clonar el Repositorio:**

```bash
git clone https://github.com/MrCabss69/RepoGPT.git
```


2. **Navigate to Directory:** Open a terminal or command line and navigate to the directory where the script is located.
```bash
cd repoGPT
```
  
1. **Run the Script:** Run the script using Python, providing the necessary arguments as described in the flexible input features.
```bash
python3 run.py
```


Code example:

```python
import argparse
from tree_builder import TreeBuilder

def main():
     # Script description and command line argument analysis
     tree = TreeBuilder(args.repo_path, args.extensions, args.start_path)
     repo_info = tree.build_tree()
     output_file = "example.txt"
     tree.write_output(repo_info, output_file)
     print(f"Repository contents written to {output_file}")

if __name__ == "__main__":
     main()
```

The TreeBuilder class handles most of the analysis, including extracting information from files, analyzing classes and functions, and generating the project summary.


## Estructura de la Salida

RepoGPT organiza los resultados del análisis en una estructura clara y concisa, que incluye:

- **Resumen del Proyecto:** Presenta un vistazo general del proyecto a través del contenido de archivos clave como README.md y IDEA.md.

- **Resumen de Implementación:** Detalla aspectos técnicos específicos en DEVELOPING.md y ofrece una visión estructurada del proyecto, similar al comando tree, enriquecida con detalles como el número de líneas por archivo.

- **Análisis Detallado por Archivo:** Desglosa la funcionalidad de cada archivo, resaltando clases, métodos y docstrings relevantes.


# TODOs:
Make a module for easy Python usage 