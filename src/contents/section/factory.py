from contents.section.section import ResourceSection, Section, SectionBase


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
