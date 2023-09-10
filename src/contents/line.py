from abc import ABCMeta


class Content(metaclass=ABCMeta):
    def __str__(self) -> str:
        raise NotImplementedError()

    def __ini__(self) -> str:
        return self.__str__()

    def __dict__(self):
        return self.__str__()



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
