from setuptools import setup, find_packages

setup(
    name='repogpt',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'repogpt=repogpt:main',
        ],
    },
    install_requires=[
    ],
    # metadata to display on PyPI
    author="Tu Nombre",
    author_email="tu.email@example.com",
    description="Repo summary generation.",
    keywords="GPT github repository summary",
    url="", 
    project_urls={
        "Código Fuente": "https://github.com/zackees/gptrepo",
    }
)