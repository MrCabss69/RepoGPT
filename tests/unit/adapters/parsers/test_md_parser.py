# import os
# from pathlib import Path
# from repogpt.adapters.parser.md_parser import MarkdownParser
# from repogpt.models import ParserConf, ParserInput

# DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data")

# def load_path(filename):
#     return Path(os.path.join(DATA_DIR, filename))

# def test_basic_md_headings():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("basic.md"), file_info={})
#     result = parser.parse(input_)
#     assert [h["level"] for h in result.headings] == [1, 2]
#     assert [h["title"] for h in result.headings] == ["Título 1", "Subtítulo"]
#     assert result.links == []

#     assert result.code_blocks == 0

# def test_with_comments_md_comments_and_todos_fixmes():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("with_comments.md"), file_info={})
#     result = parser.parse(input_)
#     # Los comentarios extraídos deben coincidir con los del archivo
#     assert any(
#         comment in result.todos_fixmes
#         for comment in [
#             "Este es un comentario en markdown",
#             "TODO: Completar sección",
#             "FIXME: Revisar formato"
#         ]
#     )
#     # Testea también single_comments_count y blank_lines
#     assert result.single_comments_count == 3
#     # TODO y FIXME separados:
#     assert "TODO: Completar sección" in result.todos_fixmes
#     assert "FIXME: Revisar formato" in result.todos_fixmes

# def test_with_comments_md_headings_links_codeblocks():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("with_comments.md"), file_info={})
#     result = parser.parse(input_)

#     assert any(h["level"] == 1 and h["title"] == "Título" for h in result.headings)
#     assert result.links == []
#     assert result.code_blocks == 1

# def test_edge_cases_md():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("edge_cases.md"), file_info={})
#     result = parser.parse(input_)
#     # Headings y links
#     assert result.headings == []

#     assert result.links == [{"text": "OpenAI", "url": "https://openai.com"}]
#     # Code blocks: hay un bloque ```

#     assert result.code_blocks == 1
#     # La preview incluye el comienzo del texto
#     assert "🎉" in result.content_preview
#     assert result.blank_lines >= 0  # Según el archivo

# def test_edge_cases_md_in_line_comment():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("edge_cases.md"), file_info={})
#     result = parser.parse(input_)
#     # Busca el comentario en línea (no es HTML, así que según el extractor,
#     # puede que no lo detecte)
#     assert "Comentario en línea" not in result.todos_fixmes  # Solo se detectan <!-- ... -->

# def test_blank_lines_basic_md():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("basic.md"), file_info={})
#     result = parser.parse(input_)
#     assert result.blank_lines >= 1  # Según el contenido

# def test_no_comments_basic_md():
#     parser = MarkdownParser(ParserConf(language="markdown"))
#     input_ = ParserInput(file_path=load_path("basic.md"), file_info={})
#     result = parser.parse(input_)
#     assert result.single_comments_count == 0
#     assert result.comments_count == 0
