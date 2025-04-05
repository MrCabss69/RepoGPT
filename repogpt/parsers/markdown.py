# repogpt/parsers/markdown.py
import logging
import re
from pathlib import Path
from typing import Any, Dict

from .base import Parser, register_parser
from ..utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines

logger = logging.getLogger(__name__)

class MarkdownParser(Parser):
    """Parsea archivos Markdown (.md, .mdx)."""

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae encabezados, links y fragmentos de código."""
        logger.debug("Parseando archivo Markdown: %s", file_path)
        result: Dict[str, Any] = {'headings': [], 'links': [], 'code_blocks': 0, 'content_preview': ''}
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_info['line_count'] = len(content.splitlines())

            # Extraer encabezados (simplificado)
            heading_pattern = re.compile(r'^(#+)\s+(.*)', re.MULTILINE)
            for match in heading_pattern.finditer(content):
                level = len(match.group(1))
                title = match.group(2).strip()
                result['headings'].append({'level': level, 'title': title})

            # Extraer links [text](url)
            link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
            for match in link_pattern.finditer(content):
                text = match.group(1)
                url = match.group(2)
                result['links'].append({'text': text, 'url': url})

            # Contar bloques de código (```)
            code_block_pattern = re.compile(r'^```', re.MULTILINE)
            result['code_blocks'] = len(code_block_pattern.findall(content)) // 2 # Cada bloque tiene inicio y fin

            # Vista previa del contenido
            result['content_preview'] = content[:500] + ('...' if len(content) > 500 else '')
            result['blank_lines'] = count_blank_lines(content)

            # Extraer comentarios HTML <!-- ... --> y TODOs/FIXMEs
            # Patrón básico para comentarios HTML
            # No tenemos un patrón de comentario de línea estándar en Markdown puro
            comments = extract_comments_from_content(content, block_comment_patterns=[('<!--', '-->')])
            result['comments_count'] = len(comments)
            result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)
        except Exception as e:
            logger.error("Error parseando Markdown %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected Markdown parsing error: {e}'

        return result
    
# Registrar para .md y .mdx
register_parser('.md', MarkdownParser)
register_parser('.mdx', MarkdownParser) # MDX puede contener sintaxis adicional