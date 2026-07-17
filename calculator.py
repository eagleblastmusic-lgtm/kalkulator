"""Desktop calculator with a testable engine and a Tkinter interface."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, localcontext


def format_number(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    text = format(value.normalize(), "f")
    text = text.rstrip("0").rstrip(".") if "." in text else text
    return text if len(text.replace("-", "").replace(".", "")) <= 14 else f"{value:.8E}"


def calculate(left: Decimal, operator: str, right: Decimal) -> Decimal:
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        with localcontext() as context:
            context.prec = 28
            return left / right
    raise ValueError(f"Unsupported operator: {operator!r}")


@dataclass
class CalculatorEngine:
    display: str = "0"
    accumulator: Decimal | None = None
    operator: str | None = None
    replace: bool = False
    error: bool = False

    def digit(self, value: str) -> str:
        if len(value) != 1 or value not in "0123456789":
            raise ValueError("digit must be from 0 to 9")
        if self.error or self.replace or self.display == "0":
            self.display, self.replace, self.error = value, False, False
        else:
            self.display += value
        return self.display

    def decimal(self) -> str:
        if self.error or self.replace:
            self.display, self.replace, self.error = "0.", False, False
        elif "." not in self.display:
            self.display += "."
        return self.display

    def clear(self) -> str:
        self.display, self.accumulator, self.operator = "0", None, None
        self.replace = self.error = False
        return self.display

    def backspace(self) -> str:
        if not self.error and not self.replace:
            self.display = self.display[:-1]
            if self.display in {"", "-"}:
                self.display = "0"
        return self.display

    def sign(self) -> str:
        if not self.error and self.display != "0":
            self.display = self.display[1:] if self.display.startswith("-") else "-" + self.display
        return self.display

    def percent(self) -> str:
        if not self.error:
            self.display = format_number(self._number() / Decimal("100"))
            self.replace = True
        return self.display

    def choose(self, operator: str) -> str:
        if operator not in {"+", "-", "*", "/"}:
            raise ValueError(f"Unsupported operator: {operator!r}")
        if self.error:
            return self.display
        current = self._number()
        if self.accumulator is not None and self.operator and not self.replace:
            if not self._apply(current):
                return self.display
        else:
            self.accumulator = current
        self.operator, self.replace = operator, True
        return self.display

    def equals(self) -> str:
        if not self.error and self.accumulator is not None and self.operator:
            self._apply(self._number())
            self.accumulator, self.operator, self.replace = None, None, True
        return self.display

    def _number(self) -> Decimal:
        try:
            return Decimal(self.display)
        except InvalidOperation as exc:
            raise ValueError(f"Invalid display value: {self.display!r}") from exc

    def _apply(self, right: Decimal) -> bool:
        assert self.accumulator is not None and self.operator is not None
        try:
            result = calculate(self.accumulator, self.operator, right)
        except ZeroDivisionError:
            self.display, self.accumulator, self.operator = "Error", None, None
            self.replace = self.error = True
            return False
        self.accumulator, self.display, self.replace = result, format_number(result), True
        return True


def launch_gui() -> None:
    import tkinter as tk

    engine = CalculatorEngine()
    root = tk.Tk()
    root.title("Kalkulator")
    root.geometry("360x520")
    root.minsize(320, 460)
    root.configure(bg="#111827")

    output = tk.StringVar(value="0")
    tk.Label(
        root, textvariable=output, anchor="e", padx=22, pady=24,
        bg="#111827", fg="#f9fafb", font=("Segoe UI", 34, "bold")
    ).grid(row=0, column=0, columnspan=4, sticky="nsew")

    def run(callback, *args) -> None:
        output.set(callback(*args))

    layout = [
        ("C", engine.clear, None, "#b91c1c"), ("⌫", engine.backspace, None, "#374151"),
        ("±", engine.sign, None, "#374151"), ("÷", engine.choose, "/", "#2563eb"),
        ("7", engine.digit, "7", "#1f2937"), ("8", engine.digit, "8", "#1f2937"),
        ("9", engine.digit, "9", "#1f2937"), ("×", engine.choose, "*", "#2563eb"),
        ("4", engine.digit, "4", "#1f2937"), ("5", engine.digit, "5", "#1f2937"),
        ("6", engine.digit, "6", "#1f2937"), ("−", engine.choose, "-", "#2563eb"),
        ("1", engine.digit, "1", "#1f2937"), ("2", engine.digit, "2", "#1f2937"),
        ("3", engine.digit, "3", "#1f2937"), ("+", engine.choose, "+", "#2563eb"),
        ("%", engine.percent, None, "#374151"), ("0", engine.digit, "0", "#1f2937"),
        (".", engine.decimal, None, "#1f2937"), ("=", engine.equals, None, "#2563eb"),
    ]
    for index, (text, callback, argument, color) in enumerate(layout):
        command = (lambda c=callback, a=argument: run(c) if a is None else run(c, a))
        tk.Button(
            root, text=text, command=command, bd=0, relief="flat",
            bg=color, fg="white", activebackground="#4b5563",
            activeforeground="white", font=("Segoe UI", 17, "bold")
        ).grid(row=index // 4 + 1, column=index % 4, padx=5, pady=5, sticky="nsew")

    for column in range(4):
        root.grid_columnconfigure(column, weight=1, uniform="column")
    root.grid_rowconfigure(0, weight=2)
    for row in range(1, 6):
        root.grid_rowconfigure(row, weight=1, uniform="row")

    def key(event) -> str:
        char = event.char
        if char in "0123456789":
            run(engine.digit, char)
        elif char in "+-*/":
            run(engine.choose, char)
        elif char in ".,":
            run(engine.decimal)
        elif event.keysym in {"Return", "KP_Enter"} or char == "=":
            run(engine.equals)
        elif event.keysym == "BackSpace":
            run(engine.backspace)
        elif event.keysym in {"Escape", "Delete"}:
            run(engine.clear)
        elif char == "%":
            run(engine.percent)
        return "break"

    root.bind("<Key>", key)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
