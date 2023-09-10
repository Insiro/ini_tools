import json
from abc import ABCMeta, abstractmethod

from contents.content import DataContent
from contents.line import Comment, Content
from contents.wrapper import CommandWrapper, DataWrapper, KeyContentWrapper


class SectionBase(Content, metaclass=ABCMeta):
    def __init__(self, name: str):
        self.__lines: list[Content] = []
        self.__name: str = name

    # region getter
    def get_name(self) -> str:
        return self.__name

    def get_lines(self) -> list[Content]:
        return self.__lines

    # endregion

    @abstractmethod
    def add_content(self, content: Content) -> bool:
        raise NotImplementedError()

    def _add_line(self, line: str | Content):
        self.__lines.append(line)

    def add_comment(self, comment: str):
        self._add_line(Comment(comment))

    def __ini__(self) -> str:
        return f"\n[{self.get_name()}]"

    @abstractmethod
    def __dict__(self):
        raise NotImplementedError()


class Section(SectionBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__data: dict[str, str] = {}
        self.__commands: dict[str, str] = {}

    # region getter
    def get_value(self, key: str) -> str | None:
        if key not in self.__data:
            return None
        return self.__data[key]

    def get_commands(self) -> dict[str, str]:
        return self.__commands.copy()

    def get_command(self, key: str) -> str:
        return self.__commands[key]

    # endregion

    def __ini__(self) -> str:
        contents = [super().__ini__()]
        for content in self.get_lines():
            if isinstance(content, CommandWrapper):
                key = content.get_key()
                contents.append(f"run = {self.get_command(key)}")
            elif isinstance(content, DataWrapper):
                key = content.get_key()
                contents.append(f"{key} = {self.get_value(key)}")
            elif isinstance(content, Content):
                contents.append(content.__ini__())

        return "\n".join(contents)

    def __dict__(self):
        data = []
        scope = {}
        isScopeEmpty = True
        for content in self.get_lines():
            assert isinstance(content, Content), "content is not Allowed Instance"
            if not isinstance(content, KeyContentWrapper):
                if not isScopeEmpty:
                    isScopeEmpty = True
                    data.append(scope)
                    scope = {}
                data.append(content.__dict__())
                continue
            isScopeEmpty = False
            key = content.get_key()
            if isinstance(content, CommandWrapper):
                scope[key] = self.get_command(key)
            elif isinstance(content, DataWrapper):
                scope[key] = self.get_value(key)
            else:
                raise NotImplementedError()

        if not isScopeEmpty:
            data.append(scope)
        return {"__name": f"({self.__class__.__name__}){self.get_name()}", "data": data}

    def __str__(self, indent=None):
        return json.dumps(self.__dict__(), indent=indent)

    def add_content(self, content: Content) -> bool:
        if not isinstance(content, DataContent):
            self._add_line(content)
            return True
        key = content.get_key()
        match key:
            case "run":
                self.__add_command(content.get_value())
            case _:
                self.__add_data(key, content.get_value())
        return True

    def __add_data(self, key: str, value: str):
        self.__data[key] = value
        self._add_line(DataWrapper(key))

    def __add_command(self, command: str):
        key = f"_run_{len(self.__commands)}"
        self._add_line(CommandWrapper(key))
        self.__commands[key] = command


class ResourceSection(SectionBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__type = None
        self.__format = None
        self.__filename = None
        pass

    def __ini__(self) -> str:
        content = [super().__ini__()]
        if self.__type is not None:
            content.append(f"type = {self.__type}")
        if self.__format is not None:
            content.append(f"format = {self.__format}")
        if self.__filename is not None:
            content.append(f"filename = {self.__filename}")
        return "\n".join(content)

    def __dict__(self):
        data = {}
        if (type := self.__type) is not None:
            data["type"] = type
        if (format := self.__format) is not None:
            data["format"] = format
        if (filename := self.__filename) is not None:
            data["filename"] = filename
        return {"__name": f"(Section){self.get_name()}", "data": data}

    def add_content(self, content: DataContent) -> bool:
        key = content.get_key()
        value = content.get_value()
        match key:
            case "type":
                self.__type = value
            case "format":
                self.__format = value
            case "filename":
                self.__filename = value
            case _:
                return False
        return True
