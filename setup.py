# setup.py

from setuptools import setup, find_packages

# Leer el contenido de README.md para la descripción larga
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Leer dependencias opcionales si se usan extras
extras_require = {
    'yaml': ['PyYAML>=5.0'],
    'toml': ['toml>=0.10'],
    'js': ['pyjsparser>=2.7'],
    'dev': [ # Dependencias para desarrollo y testing
        'pytest>=6.0',
        'PyYAML>=5.0', # Incluir opcionales aquí también
        'toml>=0.10',
        'pyjsparser>=2.7',
        # 'gitignore-parser>=0.1', # Si se usa
    ]
}
# Crear un extra 'full' que instale todo
extras_require['full'] = list(set(sum(extras_require.values(), [])))


setup(
    name="repogptv2",
    version="0.2.0", # Mantener sincronizado con repogpt/__init__.py
    author="MrCabss69 (y contribuciones IA)", # Actualizar autor
    author_email="your.email@example.com", # Actualizar email
    description="Analiza y resume repositorios de código para LLMs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MrCabss69/RepoGPT", # Actualizar URL
    packages=find_packages(exclude=["tests*", "docs*", "experiments*"]), # Excluir directorios no deseados
    # Incluir archivos de datos si los hubiera (ej. prompts por defecto)
    # package_data={
    #     'repogpt': ['prompts/*.txt'],
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License", # ¡Añadir una licencia! MIT es común.
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.8', # Especificar versión mínima de Python
    install_requires=[
        # Dependencias estrictas
        'gitignore-parser>=0.1', 
    ],
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'repogpt=repogpt.__main__:main', # Define el comando 'repogpt'
        ],
    },
)