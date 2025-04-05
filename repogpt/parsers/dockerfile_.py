# repogpt/parsers/dockerfile.py
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

# Importar desde .base para obtener Parser y register_parser
from .base import Parser, register_parser

logger = logging.getLogger(__name__)

class DockerfileParser(Parser):
    """Parsea archivos Dockerfile."""

    # Instrucciones comunes de Dockerfile
    # Lista más completa y ordenada alfabéticamente
    KNOWN_INSTRUCTIONS = sorted([
        'ADD', 'ARG', 'CMD', 'COPY', 'ENTRYPOINT', 'ENV', 'EXPOSE', 'FROM',
        'HEALTHCHECK', 'LABEL', 'MAINTAINER', # Maintainer está obsoleto pero puede aparecer
        'ONBUILD', 'RUN', 'SHELL', 'STOPSIGNAL', 'USER', 'VOLUME', 'WORKDIR'
    ])
    # Patrón mejorado para capturar instrucciones, incluyendo comentarios y continuación de línea
    # Busca la instrucción al inicio de línea (insensible a mayúsculas)
    # Maneja espacios y continuación de línea (\) antes de los argumentos
    INSTRUCTION_PATTERN = re.compile(
        rf'^\s*({"|".join(KNOWN_INSTRUCTIONS)})\s*(.*?)(\s*#.*)?$',
        re.IGNORECASE | re.MULTILINE
    )
    # Patrón específico para FROM para capturar imagen, tag, digest y alias
    FROM_PATTERN = re.compile(
        r'^\s*(--platform=\S+\s+)?([\w./\-:]+)(?:[:@]([\w.\-]+))?(?:\s+as\s+([\w.\-]+))?',
        re.IGNORECASE
    )
    # Patrón para comentarios de línea
    COMMENT_PATTERN = re.compile(r'^\s*#\s*(.*)')
    # Patrón para TODO/FIXME dentro de comentarios
    TODO_FIXME_PATTERN = re.compile(r'(TODO|FIXME)[\s:]?(.*)', re.IGNORECASE)


    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae instrucciones, argumentos, imágenes base, puertos y tareas."""
        logger.debug("Parseando Dockerfile: %s", file_path)
        result: Dict[str, Any] = {
            'instructions': [],
            'base_images': [],
            'exposed_ports': [],
            'labels': {},
            'envs': {},
            'args_defined': [],
            'comments': [],
            'todos_fixmes': {'todos': [], 'fixmes': []}
        }
        try:
            # Leer todo el contenido manejando continuaciones de línea (escaped newlines)
            # Esto simplifica el parseo de argumentos multilínea en instrucciones RUN, etc.
            raw_content = file_path.read_text(encoding='utf-8', errors='replace')
            content = re.sub(r'\\\n', '', raw_content) # Eliminar continuaciones de línea

            file_info['line_count'] = len(raw_content.splitlines()) # Contar sobre el original

            current_line_num = 0 # Aproximado para errores/todos
            raw_lines = raw_content.splitlines()

            # Procesar línea por línea para comentarios y TODOs
            for i, line in enumerate(raw_lines):
                current_line_num = i + 1
                # Extraer comentarios
                comment_match = self.COMMENT_PATTERN.match(line)
                if comment_match:
                     text = comment_match.group(1).strip()
                     # Ignorar pragmas comunes
                     if not line.strip().startswith('# syntax='):
                          result['comments'].append({'line': current_line_num, 'text': text})
                          # Buscar TODOs/FIXMEs dentro de comentarios
                          todo_match = self.TODO_FIXME_PATTERN.search(text)
                          if todo_match:
                              marker = todo_match.group(1).upper()
                              message = todo_match.group(2).strip()
                              entry = {'line': current_line_num, 'message': message}
                              if marker == 'TODO':
                                  result['todos_fixmes']['todos'].append(entry)
                              else:
                                  result['todos_fixmes']['fixmes'].append(entry)

            # Procesar instrucciones usando el contenido sin continuaciones
            for match in self.INSTRUCTION_PATTERN.finditer(content):
                instruction = match.group(1).upper()
                # Los argumentos pueden contener espacios, quitar solo los extremos
                arguments = match.group(2).strip()

                # Guardar instrucción básica
                instruction_detail = {'instruction': instruction, 'arguments': arguments}
                # Intentar obtener línea aproximada (no es perfecto debido a continuaciones)
                # instruction_detail['line_approx'] = content[:match.start()].count('\n') + 1
                result['instructions'].append(instruction_detail)

                # Extraer info específica de instrucciones comunes
                if instruction == 'FROM':
                    from_match = self.FROM_PATTERN.match(arguments)
                    if from_match:
                        platform, image, tag_or_digest, alias = from_match.groups()
                        base_image_info = {'image': image}
                        if tag_or_digest:
                            # Determinar si es tag o digest (simplificado)
                            if len(tag_or_digest) > 15 and any(c in tag_or_digest for c in 'abcdef'): # Heurística para digest
                                base_image_info['digest'] = tag_or_digest
                            else:
                                base_image_info['tag'] = tag_or_digest
                        if alias:
                            base_image_info['alias'] = alias
                        if platform:
                             base_image_info['platform'] = platform.strip()
                        result['base_images'].append(base_image_info)
                    else:
                        # Fallback si el regex complejo falla
                        result['base_images'].append({'image': arguments.split(' ')[0], '_parse_warning': 'Complex FROM not fully parsed'})

                elif instruction == 'EXPOSE':
                    # Extraer puertos expuestos (números y opcionalmente /tcp o /udp)
                    ports = re.findall(r'\d+(?:/(?:tcp|udp))?', arguments, re.IGNORECASE)
                    result['exposed_ports'].extend(ports)

                elif instruction == 'LABEL':
                    # Parsear labels estilo clave="valor" clave2=valor2 ...
                    # Simplificado: asume pares separados por espacio, puede fallar con comillas
                    try:
                       # Intenta parsear como clave=valor (puede fallar con espacios en valores)
                       label_pairs = re.findall(r'([\w.-]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))', arguments)
                       for key, v_dq, v_sq, v_nq in label_pairs:
                           result['labels'][key] = v_dq or v_sq or v_nq
                    except Exception:
                         result['labels']['_parse_warning'] = f"Could not fully parse LABEL arguments: {arguments}"

                elif instruction == 'ENV':
                     # Parsear ENV clave=valor clave valor ...
                     # Simplificado: asume un solo par o clave+valor
                     env_parts = arguments.split(None, 1)
                     if len(env_parts) == 1: # Estilo ENV clave valor
                          # Buscar clave=valor
                          if '=' in env_parts[0]:
                               key, value = env_parts[0].split('=', 1)
                               result['envs'][key.strip()] = value.strip().strip('"\'')
                          else: # Solo clave? Dockerfile permite esto pero es raro.
                              result['envs'][env_parts[0]] = '' # Asignar vacío
                     elif len(env_parts) == 2: # Estilo ENV clave valor
                          key, value = env_parts
                          result['envs'][key.strip()] = value.strip().strip('"\'')


                elif instruction == 'ARG':
                     # Extraer nombre del argumento (puede tener valor por defecto)
                     arg_name = arguments.split('=')[0].strip()
                     result['args_defined'].append(arg_name)

            # Actualizar el conteo de comentarios para reflejar solo los reales
            file_info['comments_count'] = len(result['comments'])


        except FileNotFoundError:
            logger.error("Archivo Dockerfile no encontrado durante parsing: %s", file_path)
            result['_error'] = 'File not found during parsing'
        except Exception as e:
            logger.error("Error inesperado parseando Dockerfile %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected Dockerfile parsing error: {e}'

        return result

# Registrar para la extensión .dockerfile
register_parser('.dockerfile_', DockerfileParser)

# Nota: La detección de archivos llamados 'Dockerfile' (sin extensión)
# se maneja ahora en parsers/base.py/get_parser