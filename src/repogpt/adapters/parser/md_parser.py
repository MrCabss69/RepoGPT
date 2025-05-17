# repogpt/adapters/parser/md_parser.py
import re
from uuid import uuid4

from repogpt.models import CodeNode, ParserInput, ParserInterface
from repogpt.utils.text_processing import count_blank_lines, extract_comments


class MarkdownParser(ParserInterface):
    """Parser para archivos Markdown, construye un árbol de CodeNode."""

    HEADING_RE = re.compile(r"^(#+)\s+(.*)$", re.MULTILINE)
    LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    FENCE_RE = re.compile(r"^```", re.MULTILINE)

    def __init__(self) -> None:
        """Initialize the Markdown parser."""
        pass

    def parse(self, input: ParserInput) -> CodeNode:
        """
        Parse a Markdown file and build a CodeNode tree.

        Args:
            input: ParserInput containing the file path and info

        Returns:
            CodeNode: Root node of the parsed tree
        """
        path = input.file_path
        content = path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        total_lines = len(lines)

        root = CodeNode(
            id=str(uuid4()),
            type="Module",
            name=path.stem,
            language="markdown",
            path=str(path),
            start_line=1,
            end_line=total_lines,
            metrics={
                "blank_lines": count_blank_lines(content),
                "lines_of_code": len([line for line in lines if line.strip()]),
            },
        )

        # 1. Headings como nodos hijos
        headings = [
            {
                "level": len(m.group(1)),
                "title": m.group(2).strip(),
                "start_line": content.count("\n", 0, m.start()) + 1,
            }
            for m in self.HEADING_RE.finditer(content)
        ]
        for h in headings:
            root.children.append(
                CodeNode(
                    id=str(uuid4()),
                    type="Heading",
                    name=str(h["title"]),
                    language="markdown",
                    path=root.path,
                    start_line=int(h["start_line"]),
                    end_line=int(
                        h["start_line"]
                    ),  # No sabemos el rango, solo el inicio
                    parent_id=root.id,
                    metrics={"level": h["level"]},
                )
            )

        # 2. Links como dependencias
        for m in self.LINK_RE.finditer(content):
            root.dependencies.append({"text": m.group(1), "url": m.group(2)})

        # 3. Code blocks como hijos anónimos
        code_blocks = []
        for m in self.FENCE_RE.finditer(content):
            code_blocks.append(content.count("\n", 0, m.start()) + 1)
        # Group code blocks by pairs (start, end)
        for i in range(0, len(code_blocks), 2):
            try:
                start = code_blocks[i]
                end = code_blocks[i + 1]
                root.children.append(
                    CodeNode(
                        id=str(uuid4()),
                        type="CodeBlock",
                        name=None,
                        language="markdown",
                        path=root.path,
                        start_line=start,
                        end_line=end,
                        parent_id=root.id,
                    )
                )
            except IndexError:
                # Unmatched ```
                continue

        # 4. Comentarios HTML
        comments = extract_comments(content, language="markdown")
        for c in comments:
            root.comments.append(c)
            # Extra tags tipo TODO/FIXME
            text = c["text"].lower()
            if "todo" in text:
                root.tags.append("TODO")
            if "fixme" in text:
                root.tags.append("FIXME")

        return root
