from enum import Enum


class Type(Enum):
    Line = 1
    Command = 2
    Data = 3


class Content:
    def __str__(self) -> str:
        return "line"

    def __ini__(self) -> str:
        return ""

    def __dict__(self):
        return self.__str__()


class LineWrapper:
    def __init__(self, line: str | Content, type: Type) -> None:
        self.line = line
        self.type = type

    def __dict__(self):
        match self.type:
            case Type.Data:
                return self.line
            case _:
                return self.line.__dict__()


class PlainText(Content):
    __txt: str

    def __init__(self, txt) -> None:
        self.__txt = txt

    def get_txt(self) -> str:
        return self.__txt

    def __str__(self) -> str:
        return f"({self.__class__.__name__}){self.__txt}"

    def __ini__(self) -> str:
        return self.__txt


class Comment(PlainText):
    def __ini__(self) -> str:
        return "\n;" + self.get_txt()
