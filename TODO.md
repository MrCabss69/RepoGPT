




 Estado actual: lista plana de “top_level”
Qué hace ahora:
El parser de Python recorre el AST y extrae una lista plana de “top-level” nodes:

Cada import, clase, función (sin anidamiento explícito).

Solo el “nivel más superficial” (lo que hay en el tree.body).

Qué devuelve:
Un ParserResult con campos “headings”, “links”, etc., y opcionalmente una lista structure (comentada) con ese “top_level”.

Limitaciones:

Pierdes jerarquía: Métodos dentro de clases, funciones anidadas, imports dentro de funciones, etc., no quedan reflejados como una estructura anidada.

Si quieres responder preguntas como “¿qué métodos tiene cada clase?” o “dame sólo la lista de imports de cada módulo”, tienes que hacer un post-procesamiento bastante torpe.

Solo ves la arquitectura en modo “flat”.

2. Qué necesitas para un árbol consultable y true RAG estructurado
Debes construir y guardar explícitamente la estructura de árbol del archivo.

Cada nodo es un dict (o dataclass) con tipo (“class”, “function”, “import”, etc.), nombre, atributos relevantes, y subnodos (children).

El root es el archivo, hijos directos son imports, clases, funciones, y cada clase tiene hijos con sus métodos, etc.

Idealmente, cada nodo tiene:

Tipo

Nombre (si aplica)

Línea de inicio y fin

Docstring/comentario si existe

Lista de hijos (children)

(Opcional) Decoradores, argumentos, tipo de retorno, etc.