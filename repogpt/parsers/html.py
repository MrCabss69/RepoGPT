# repogpt/parsers/html.py
import logging
import re
from pathlib import Path
from typing import Any, Dict

from .base import Parser, register_parser
from ..utils.text_processing import extract_comments_from_content, extract_todos_fixmes_from_comments, count_blank_lines


logger = logging.getLogger(__name__)

class HtmlParser(Parser):
    """Parsea archivos HTML (.html, .htm)."""

    def parse(self, file_path: Path, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae título, scripts y links."""
        logger.debug("Parseando archivo HTML: %s", file_path)
        result: Dict[str, Any] = {'title': '', 'scripts': [], 'links': [], 'style_blocks': 0}
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_info['line_count'] = len(content.splitlines())
            result['blank_lines'] = count_blank_lines(content)

            # Extraer comentarios HTML y TODOs/FIXMEs
            comments = extract_comments_from_content(content, block_comment_patterns=[('<!--', '-->')])
            result['comments_count'] = len(comments)
            result['todos_fixmes'] = extract_todos_fixmes_from_comments(comments)

            # Extraer título
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            result['title'] = title_match.group(1).strip() if title_match else 'N/A'

            # Extraer fuentes de scripts <script src="...">
            script_pattern = re.compile(r'<script[^>]+src\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
            result['scripts'] = script_pattern.findall(content)

            # Extraer HREFs de links <a href="..."> y stylesheets <link href="...">
            link_pattern = re.compile(r'<(?:a|link)[^>]+href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
            result['links'] = link_pattern.findall(content)

            # Contar bloques <style>...</style>
            style_pattern = re.compile(r'<style.*?>.*?</style>', re.IGNORECASE | re.DOTALL)
            result['style_blocks'] = len(style_pattern.findall(content))
            
        except Exception as e:
            logger.error("Error inesperado parseando HTML %s: %s", file_path, e, exc_info=True)
            result['_error'] = f'Unexpected HTML parsing error: {e}'

        return result


register_parser('.html', HtmlParser)
register_parser('.htm', HtmlParser)