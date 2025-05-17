# repogpt/exceptions.py


class RepoGPTException(Exception):
    """Clase base para excepciones específicas de RepoGPT."""

    pass


class ConfigurationError(RepoGPTException):
    """Error relacionado con la configuración del análisis."""

    pass


class ParsingError(RepoGPTException):
    """Error durante la fase de parsing de un archivo."""

    def __init__(
        self,
        message: str,
        file_path: str | None = None,
        parser_name: str | None = None,
    ) -> None:
        self.file_path = file_path
        self.parser_name = parser_name
        detail = f"Parser: {parser_name or 'N/A'}, File: {file_path or 'N/A'}"
        full_message = f"{message} ({detail})"
        super().__init__(full_message)


class AnalysisError(RepoGPTException):
    """Error durante la fase principal de análisis del repositorio."""

    pass


class ReportingError(RepoGPTException):
    """Error durante la generación del reporte."""

    pass
