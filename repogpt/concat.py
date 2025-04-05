#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def concatenar_py_recursivo(directorio_raiz='.', archivo_salida='codigo_concatenado.txt'):
    """
    Busca recursivamente archivos .py en directorio_raiz y sus subdirectorios,
    y concatena su contenido en archivo_salida, añadiendo una cabecera
    con la ruta del archivo antes de cada contenido.

    Args:
        directorio_raiz (str): La ruta al directorio desde donde empezar la búsqueda.
                               Por defecto es el directorio actual ('.').
        archivo_salida (str): El nombre del archivo donde se guardará el resultado.
                              Por defecto es 'codigo_concatenado.txt'.
    """
    contador_archivos = 0
    ruta_salida_abs = os.path.abspath(archivo_salida)

    try:
        # Abrimos el archivo de salida en modo escritura ('w') - Se sobreescribirá si ya existe. Usamos utf-8 por compatibilidad.
        with open(archivo_salida, 'w', encoding='utf-8') as f_salida:
            print(f"Buscando archivos .py en: '{os.path.abspath(directorio_raiz)}'")
            print(f"Guardando resultado en: '{ruta_salida_abs}'")

            # os.walk recorre el árbol de directorios de forma recursiva
            for dirpath, _, filenames in os.walk(directorio_raiz):
                for filename in filenames:
                    if filename.endswith('.py'):
                        ruta_completa = os.path.join(dirpath, filename)
                        ruta_completa_abs = os.path.abspath(ruta_completa)

                        # Evitar que el propio script (si se llama .py)
                        # o el archivo de salida (si se llamara .py) se incluyan
                        if ruta_completa_abs == os.path.abspath(__file__):
                           print(f"-> Omitiendo el propio script: {ruta_completa}")
                           continue
                        if ruta_completa_abs == ruta_salida_abs:
                            print(f"-> Omitiendo el archivo de salida: {ruta_completa}")
                            continue

                        print(f"-> Procesando: {ruta_completa}")
                        contador_archivos += 1

                        # Escribimos la cabecera con el nombre del archivo
                        cabecera = f"# ==================== INICIO: {ruta_completa} ====================\n"
                        f_salida.write(cabecera)

                        try:
                            # Abrimos el archivo .py encontrado en modo lectura ('r')
                            with open(ruta_completa, 'r', encoding='utf-8') as f_entrada:
                                contenido = f_entrada.read()
                                f_salida.write(contenido)
                                if contenido and not contenido.endswith('\n'):
                                    f_salida.write('\n')

                        except UnicodeDecodeError:
                            print(f"  [AVISO] No se pudo leer {ruta_completa} con UTF-8. Omitiendo contenido.")
                            f_salida.write(f"# [ERROR] No se pudo decodificar el archivo {ruta_completa} con UTF-8.\n")
                        except IOError as e:
                            print(f"  [ERROR] No se pudo leer {ruta_completa}: {e}")
                            f_salida.write(f"# [ERROR] Error de E/S leyendo {ruta_completa}: {e}\n")
                        except Exception as e:
                             print(f"  [ERROR] Error inesperado procesando {ruta_completa}: {e}")
                             f_salida.write(f"# [ERROR] Error inesperado procesando {ruta_completa}: {e}\n")

                        pie_pagina = f"# ==================== FIN: {ruta_completa} ======================\n\n"
                        f_salida.write(pie_pagina)

        print("\n¡Proceso completado!")
        print(f"Se concatenaron {contador_archivos} archivos .py en '{archivo_salida}'.")

    except IOError as e:
        print(f"[ERROR FATAL] No se pudo abrir o escribir en el archivo de salida '{archivo_salida}': {e}")
    except Exception as e:
        print(f"[ERROR FATAL] Ocurrió un error inesperado: {e}")

# --- Ejecución del script ---
if __name__ == "__main__":
    concatenar_py_recursivo()

    # Para ejecutar otro directorio y/o archivo de salida:
    # concatenar_py_recursivo(directorio_raiz='/ruta/a/tu/proyecto', archivo_salida='mi_proyecto_completo.txt')