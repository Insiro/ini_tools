from __future__ import annotations
import os
from contents.content import ContentFactory
from contents.line import Type, Content, Comment
from contents.section import (
    BranchSection,
    ResourceSection,
    SectionBase,
    Section,
    SectionFactory,
)


class GiIni(Section):
    sections: dict[str, SectionBase] = {}
    __varaibles: list[str] = []

    def add_varaible(self, name: str):
        self.__varaibles.append(name)

    def save(self, file_name: str):
        file = open(file_name, "w")
        for wrapper in self.get_lines():
            line = wrapper.line
            if isinstance(line, Content):
                print(line.__ini__(), file=file)
                continue
            match wrapper.type:
                case Type.Command:
                    print(f"run = {self.get_command(line)}", file=file)
                case Type.Data:
                    print(f"{line} = {self.get_value(line)}")

    def add_content(self, content: Content) -> bool:
        assert isinstance(
            content, Comment | Section | ResourceSection
        ), "File Scope only Allow Section and Comment"
        if isinstance(content, Section):
            name = content.get_name()
            self.sections[name] = content
        super()._add_line(content)
        return True

    # def add_resource(self, resource: str):
    #     self.add_data("filename", resource)


class GiLoader:
    __stack: list[GiIni | SectionBase] = []
    __current: GiIni | SectionBase
    __ini: GiIni

    def __engage_scope(self, scope: SectionBase, clear=False):
        if clear:
            self.__current = self.__ini
            self.__stack = []
        self.__stack.append(self.__current)
        self.__current = scope

    def __close_scope(self):
        pass

    def __parse_line(self, line_str: str):
        line = line_str.strip()
        items = line.split(";")

        # region commant block handling
        if len(items) > 1:
            item = ";".join(items[1:])
            self.__current.add_comment(item)
        # endregion

        item = items[0]
        if len(item) == 0:
            return

        # get sections
        if item[0] == "[":
            sections = SectionFactory.getSections(item)
            for section in sections:
                self.__ini.add_content(section)
                self.__engage_scope(section, True)
            return
        # line handling

        # region conditional branch handling TODO: process if states
        if item.startswith("if"):
            branch = BranchSection(self.__current.get_name())  # TODO: save conditions
            self.__current.add_content(branch)
            self.__engage_scope(branch)
            return
        if item.startswith("else"):
            return
        if item == "endif":
            self.__close_scope()
            return
        # endregion

        # region remeber global variables # TODO : check rember var is required?
        if item.startswith("global"):
            variables = item.split("$")[1:]
            for var in variables:
                var = var.strip()
                name = var.split(" ")[0]
                self.__ini.add_varaible(name)
            return
        # endregion
        content = ContentFactory.getContent(line)
        self.__current.add_content(content)

    def load_ini(self, file: str) -> GiIni:
        assert os.path.isfile(file), "wrong input file"

        ini = GiIni(file)
        self.__ini = ini
        self.__current = ini
        self.__stack = []
        lines = open(file).readlines()

        for line_str in lines:
            self.__parse_line(line_str)

        # clean up data
        self.__stack = []

        return ini
