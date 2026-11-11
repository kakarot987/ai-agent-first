"""Deterministic, allowlisted tools constrained to a caller-owned workspace."""

import ast
import json
import operator
from decimal import Decimal, DecimalException
from pathlib import Path
from typing import Any, Callable


class ToolError(ValueError):
    """A safe, user-facing failure from a built-in tool."""


_OPERATIONS: dict[type, Callable[..., Decimal]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_LIMIT = Decimal("1000000000000")


def calculate(expression: str) -> str:
    """Evaluate only +, -, *, /, numeric literals, and parentheses."""
    if not isinstance(expression, str) or not 0 < len(expression) <= 120:
        raise ToolError("Expression must have 1–120 characters")
    try:
        root = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ToolError("Invalid arithmetic expression") from exc
    if sum(1 for _ in ast.walk(root)) > 40:
        raise ToolError("Expression is too complex")

    def evaluate(node: ast.AST, depth: int = 0) -> Decimal:
        if depth > 12:
            raise ToolError("Expression is too deeply nested")
        if isinstance(node, ast.Expression):
            return evaluate(node.body, depth + 1)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            result = Decimal(str(node.value))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            number = evaluate(node.operand, depth + 1)
            result = number if isinstance(node.op, ast.UAdd) else -number
        elif isinstance(node, ast.BinOp) and type(node.op) in _OPERATIONS:
            left, right = evaluate(node.left, depth + 1), evaluate(node.right, depth + 1)
            try:
                result = _OPERATIONS[type(node.op)](left, right)
            except (ZeroDivisionError, DecimalException) as exc:
                raise ToolError("Invalid arithmetic operation") from exc
        else:
            raise ToolError("Only numeric arithmetic (+, -, *, /) is allowed")
        if not result.is_finite() or abs(result) > _LIMIT:
            raise ToolError("Result exceeds the numeric limit")
        return result

    value = evaluate(root)
    return format(value.normalize(), "f")


class WorkspaceTools:
    """Allowlist: read inputs/, calculate, create reports/ inside workspace."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "inputs").mkdir(exist_ok=True)
        (self.root / "reports").mkdir(exist_ok=True)

    def _path(self, relative_path: str, directory: str, extensions: set[str]) -> Path:
        if not isinstance(relative_path, str) or len(relative_path) > 160:
            raise ToolError("Invalid relative path")
        if "\\" in relative_path or ":" in relative_path:
            raise ToolError("Use a relative forward-slash path")
        parts = Path(relative_path).parts
        if len(parts) < 2 or parts[0] != directory or any(
            part in (".", "..") for part in parts
        ):
            raise ToolError(f"Path must be under {directory}/")
        destination = (self.root / relative_path).resolve()
        allowed_dir = (self.root / directory).resolve()
        if not destination.is_relative_to(allowed_dir) or destination == allowed_dir:
            raise ToolError("Path escapes the allowed directory")
        if destination.suffix.lower() not in extensions:
            raise ToolError("Unsupported file extension")
        return destination

    def read_text(self, path: str) -> str:
        file = self._path(path, "inputs", {".md", ".txt", ".csv", ".json"})
        if not file.is_file():
            raise ToolError("Input file not found")
        if file.stat().st_size > 32768:
            raise ToolError("Input file exceeds 32 KiB")
        try:
            return file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise ToolError("Unable to read input as UTF-8 text") from exc

    def write_report(self, path: str, content: str) -> str:
        file = self._path(path, "reports", {".md", ".txt"})
        if not isinstance(content, str) or not content.strip():
            raise ToolError("Report content cannot be empty")
        if len(content.encode("utf-8")) > 16384:
            raise ToolError("Report exceeds 16 KiB")
        file.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Never silently overwrite a file created by the user or a prior run.
            with file.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError as exc:
            raise ToolError("Report already exists; choose a new path") from exc
        except OSError as exc:
            raise ToolError("Unable to write report") from exc
        return str(file.relative_to(self.root))

    @staticmethod
    def schemas() -> list[dict[str, Any]]:
        def schema(name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
            return {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": list(properties),
                        "additionalProperties": False,
                    },
                },
            }

        string = {"type": "string"}
        return [
            schema(
                "read_text",
                "Read a UTF-8 text document under inputs/ in the selected workspace.",
                {"path": string},
            ),
            schema(
                "calculate",
                "Evaluate arithmetic with + - * / and parentheses; no Python code.",
                {"expression": string},
            ),
            schema(
                "write_report",
                "Create a new .md or .txt report under reports/; existing files are protected.",
                {"path": string, "content": string},
            ),
        ]

    def execute(
        self, name: str, arguments: str
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Validate model arguments before dispatch; return an error as tool output."""
        public: dict[str, Any] = {}
        try:
            if not isinstance(arguments, str) or len(arguments) > 20000:
                raise ToolError("Tool arguments are too long")
            try:
                values = json.loads(arguments)
            except (ValueError, TypeError) as exc:
                raise ToolError("Tool arguments must be valid JSON") from exc
            if not isinstance(values, dict):
                raise ToolError("Tool arguments must be a JSON object")
            required = {
                "read_text": {"path"},
                "calculate": {"expression"},
                "write_report": {"path", "content"},
            }
            if name not in required:
                raise ToolError("Unknown or disallowed tool")
            if set(values) != required[name] or not all(
                isinstance(value, str) for value in values.values()
            ):
                raise ToolError("Tool arguments must match the declared string fields")
            public = (
                {"path": values["path"], "content_chars": len(values["content"])}
                if name == "write_report"
                else values.copy()
            )
            if name == "read_text":
                result = self.read_text(values["path"])
            elif name == "calculate":
                result = calculate(values["expression"])
            else:
                result = self.write_report(values["path"], values["content"])
            return {"ok": True, "result": result}, public
        except (ToolError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}, public
