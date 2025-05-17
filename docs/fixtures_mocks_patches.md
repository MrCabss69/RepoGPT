## 1. **Fixtures**

* **Qué son:**
  Son *datos, objetos, o recursos* que preparas antes de un test y/o limpias después.
  Por ejemplo, un archivo temporal, un objeto de base de datos, una instancia de clase, etc.

* **Para qué sirven:**
  Proveen un *entorno controlado y repetible* para ejecutar tests.
  Permiten evitar duplicar código de setup/teardown, y ayudan a aislar los tests.

* **Ejemplo:**

  ```python
  import pytest

  @pytest.fixture
  def user_dict():
      return {"name": "alice", "id": 1}

  def test_username(user_dict):
      assert user_dict["name"] == "alice"
  ```

  *(Aquí `user_dict` es el fixture.)*

* **Otra utilidad:**
  Con `tmp_path` o `tmpdir` de pytest puedes crear archivos/directorios temporales (muy útil para testear collectors).

---

## 2. **Mocks**

* **Qué son:**
  Son *objetos que sustituyen* a objetos reales en los tests.
  Su función es simular comportamientos de dependencias externas o complejas, para aislar el código que realmente quieres probar.
* **Para qué sirven:**

  * Para testear unidades de código sin ejecutar dependencias reales (API, base de datos, filesystem, etc).
  * Para verificar cómo tu código interactúa con esas dependencias (por ejemplo, ¿llama correctamente a cierto método?).
* **Ejemplo:**

  ```python
  from unittest.mock import Mock

  def test_service_calls_api():
      fake_api = Mock()
      fake_api.get_data.return_value = 42
      service = MyService(api=fake_api)
      assert service.get_data() == 42
      fake_api.get_data.assert_called_once()
  ```

  *(Aquí `fake_api` es un mock del API real.)*

---

## 3. **Patches**

* **Qué son:**
  Son una *técnica para sustituir/inyectar* implementaciones de funciones, métodos, o clases **en tiempo de ejecución** (durante un test).
  Usualmente lo implementas con `unittest.mock.patch` o `pytest-mock`.
* **Para qué sirven:**

  * Para sustituir dependencias *en el sitio* donde se usan.
  * Para espiar/interceptar llamadas a funciones de módulos externos.
* **Ejemplo:**

  ```python
  from unittest.mock import patch

  def get_time():
      import time
      return time.time()

  def test_get_time():
      with patch("time.time", return_value=123):
          assert get_time() == 123
  ```

  *(Aquí, el import `time.time` se sustituye durante el test por un valor fijo.)*

---

## **Similitudes y diferencias**

|                        | Fixture                                     | Mock                         | Patch                                                   |
| ---------------------- | ------------------------------------------- | ---------------------------- | ------------------------------------------------------- |
| **Para qué**           | Setup/teardown de datos/recursos            | Simular objetos/dependencias | Sustituir implementaciones puntuales                    |
| **Cómo se usa**        | Con decorador `@pytest.fixture` o argumento | Con `Mock()` o similares     | Con `patch()` o como decorador/contexto                 |
| **En qué nivel actúa** | Proporciona datos u objetos a tests         | Sustituye objetos o métodos  | Sustituye funciones/métodos/clases por nombre de import |
| **Ejemplo típico**     | Crear usuario temporal, archivo, DB, etc    | Fake de API, objeto dummy    | Sustituir `requests.get` para no hacer HTTP real        |

---

## **Ejemplo concreto usando los tres**

```python
import pytest
from unittest.mock import Mock, patch

# Imagina que esta función consulta un API
def get_user_age(api, user_id):
    return api.fetch_age(user_id)

# Test usando fixture y mock
@pytest.fixture
def fake_api():
    api = Mock()
    api.fetch_age.return_value = 30
    return api

def test_get_user_age(fake_api):
    assert get_user_age(fake_api, user_id=1) == 30

# Patch de función global
def external_call():
    import requests
    return requests.get("https://example.com").status_code

def test_external_call():
    with patch("requests.get", return_value=Mock(status_code=200)):
        assert external_call() == 200
```

---

## **Resumen**

* **Fixtures**: gestionan *setup/teardown* y proveen datos/recursos reutilizables.
* **Mocks**: crean *sustitutos* para objetos/dependencias, controlando su comportamiento y espiando sus llamadas.
* **Patches**: *inyectan o reemplazan* funciones/métodos/clases importadas en un punto concreto durante el test.
