## Python Engineering Fundamentals
- **Strict data modeling:** Model domain states with `@dataclass(frozen=True, slots=True)`, `TypedDict`, `Enum`, or Pydantic at system boundaries. Never pass raw `dict[str, Any]` across internal functions.
- **Explicit error handling:** Catch only specific exceptions you can recover from. Never write bare `except:` or `except Exception: pass` to silence failures.
- **Type hints required:** Annotate all function signatures and return types using modern Python syntax (`list[str]`, `X | None`). Never use `Any` or `# type: ignore` to force a passing check.
- **Standard library & simplicity:** Prefer `pathlib`, `itertools`, `collections`, and flat comprehensions over third-party helpers or deep class inheritance.
- **Pure core, thin shell:** Keep business logic pure and deterministic; isolate I/O, network calls, and database writes at the edges.
- **Safe defaults:** Never use mutable default arguments (`def f(x=[])`) or hidden module-level global state.
