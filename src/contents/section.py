from abc import ABCMeta, abstractmethod
import json
from contents.content import DataContent
from contents.line import Line, Type, LineWrapper, Comment


class SectionBase(Line, metaclass=ABCMeta):
    def __init__(self, name: str):
        self.__lines: list[LineWrapper] = []
        self.__name: str = name

    # region getter
    def get_name(self) -> str:
        return self.__name

    def get_lines(self) -> list[LineWrapper]:
        return self.__lines

    # endregion

    @abstractmethod
    def add_content(self, content: Line) -> bool:
        raise NotImplementedError()

    def add_line(self, line: str | Line, lineType=Type.Line):
        self.__lines.append(LineWrapper(line, lineType))

    def add_comment(self, comment: str):
        self.add_line(Comment(comment), Type.Line)

    def __ini__(self) -> str:
        return f"\n[{self.get_name()}]"


class Section(SectionBase):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.__data: dict[str, str] = {}
        self.__commands: list[str] = []

    # region getter
    def get_value(self, key: str) -> str | None:
        if key not in self.__data:
            return None
        return self.__data[key]

    def get_commands(self) -> list[str]:
        return self.__commands.copy()

    def get_command(self, key: str) -> str:
        idx = key.split("_")[-1]
        return self.__commands[int(idx)]

    # endregion

    def __ini__(self) -> str:
        content = [super().__ini__()]
        for lineWrapper in self.get_lines():
            line = lineWrapper.line
            if isinstance(line, Line):
                content.append(line.__ini__())
                continue
            if lineWrapper.type == Type.Data:
                content.append(f"{line} = {self.get_value(line)}")
            elif lineWrapper.type == Type.Command:
                content.append(f"run = {self.get_command(line)}")
        return "\n".join(content)

    def __dict__(self):
        data = []
        scope = {}
        isScopeEmpty = True
        for lineWrapper in self.get_lines():
            line = lineWrapper.line
            if isinstance(line, Line):
                if not isScopeEmpty:
                    isScopeEmpty = True
                    data.append(scope)
                    scope = {}
                data.append(line.__dict__())
                continue
            # case str
            value = self.get_value(line)
            if value is None:
                value = self.get_command(line)
            scope[line] = value
            isScopeEmpty = False
        if not isScopeEmpty:
            data.append(scope)
        return {"__name": f"({self.__class__.__name__}){self.get_name()}", "data": data}

    def __str__(self, indent=None):
        return json.dumps(self.__dict__(), indent=indent)

    def add_content(self, content: Line) -> bool:
        if not isinstance(content, DataContent):
            self.add_line(content)
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
        self.add_line(key, Type.Data)

    def __add_command(self, command: str):
        self.add_line(f"run_{len(self.__commands)}", Type.Command)
        self.__commands.append(command)


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


class BranchSection(Section):
    def __init__(self, parentName: str):
        super().__init__(parentName + "_branch")

    def __ini__(self) -> str:
        content = [f"if states"]
        for lineWrapper in self.get_lines():
            line = lineWrapper.line
            if isinstance(line, Line):
                content.append(line.__ini__())
                continue
            if lineWrapper.type == Type.Data:
                content.append(f"{line} = {self.get_value(line)}")
            elif lineWrapper.type == Type.Command:
                content.append(f"run = {self.get_command(line)}")
        return "\n".join(content) + "\nendif"


class SectionFactory:
    @staticmethod
    def getSections(line: str) -> list[SectionBase]:
        sections: list[SectionBase] = []
        if line[0] != "[":
            return sections
        section_names = line.split("[")[1:]
        for name in section_names:
            name = name.split("]")[0].strip()
            section = SectionFactory.getSection(name)
            sections.append(section)
        return sections

    @staticmethod
    def getSection(name: str) -> SectionBase:
        if name.startswith("Resource"):
            return ResourceSection(name)
        else:
            return Section(name)
