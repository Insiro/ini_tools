from enum import Enum

from contents.line import Content
from contents.section.section import Section
from contents.wrapper import CommandWrapper, DataWrapper


class Comparer(Enum):
    Equal = 0
    NotEqual = 1
    GT = 2
    LT = 3

    def __str__(self) -> str:
        match self:
            case Comparer.Equal:
                return "=="
            case Comparer.NotEqual:
                return "!="
            case Comparer.GT:
                return ">"
            case Comparer.LT:
                return "<"

    @staticmethod
    def from_str(string: str):
        match string.lower().strip():
            case "==":
                return Comparer.Equal
            case "!=":
                return Comparer.NotEqual
            case "<":
                return Comparer.LT
            case ">":
                return Comparer.GT
            case _:
                raise NotImplementedError()


class BranchCondtition(Content):
    def __init__(self, x, y, comparer: Comparer):
        self.x = x
        self.y = y
        self.comparer = comparer

    def __str__(self) -> str:
        return f"{self.x} {str(self.comparer)} {self.y}"


class BranchSection(Section):
    def __init__(self, parentName: str):
        super().__init__(parentName + "_branch")
        self.conditions: list[BranchCondtition] = []

    def __ini__(self) -> str:
        contents = [f"if states"]
        for content in self.get_lines():
            if isinstance(content, DataWrapper):
                key = content.get_key()
                contents.append(f"{key} = {self.get_value(key)}")
            elif isinstance(content, CommandWrapper):
                key = content.get_key()
                contents.append(f"run = {self.get_command(key)}")
            elif isinstance(content, Content):
                contents.append(content.__ini__())

        return "\n".join(contents) + "\nendif"

    def add_content(self, content: Content) -> bool:
        if isinstance(content, BranchCondtition):
            super()._add_line(content)
            # TODO: add branch
            return True
        return super().add_content(content)
