# RepoGPT

RepoGPT es una herramienta avanzada diseñada para analizar repositorios de código, generando resúmenes de proyectos detallados y estructurados. Inspirado en las herramientas gpt-repository-loader y gptrepo, RepoGPT facilita la comprensión de la estructura y los componentes de un proyecto, optimizando su integración con plataformas como ChatGPT.

**Ejemplo:**

```bash
python3 run.py --repo_path /ruta/al/repo --extensions .py .js --start_path src
```


# Uso de RepoGPT

La estructura del proyecto y el proceso de uso han sido actualizados. Sigue estos pasos para comenzar a utilizar RepoGPT:

## Clona el Repositorio:

```bash
git clone https://github.com/MrCabss69/RepoGPT.git
```

## Navega al Directorio del Proyecto:

Abre una terminal o línea de comandos y navega al directorio raíz del proyecto clonado.

```bash
cd RepoGPT
```

## Instala el módulo 
```bash
pip install -e .
```

## Ejecuta RepoGPT:

Una vez instalado, puedes ejecutar RepoGPT directamente desde la línea de comandos, proporcionando los argumentos necesarios como se describió anteriormente.

```bash
repogpt --repo_path /ruta/al/repo --extensions .py .js --start_path src
```

## Características Principales

- **Análisis de Archivos:** RepoGPT realiza un escaneo profundo de los archivos en el repositorio, recopilando información crucial como el conteo de líneas, las clases y sus métodos, funciones independientes y cadenas de documentación asociadas.

- **Mejora de Documentación:** La herramienta pone especial énfasis en la claridad y calidad de la documentación del código, promoviendo buenas prácticas como el uso de nomenclaturas claras para variables y cadenas de documentación detalladas.

## Opciones de Análisis Detallado

RepoGPT te permite personalizar el análisis utilizando las siguientes opciones:

- `--repo_path`: Especifica la ruta del repositorio a analizar. Por defecto, se utiliza el directorio actual.
- `--extensions`: Define las extensiones de archivo a incluir en el análisis. Por defecto, se incluyen archivos .md.
- `--start_path`: Permite iniciar el análisis desde un subdirectorio específico del repositorio.

# Estructura
```bash.
├── README.md
├── repogpt
│   ├── docs
│   │   ├── DEVELOPING.md
│   │   ├── IDEA.md
│   │   └── TODO.md
│   ├── __init__.py
└── setup.py

```