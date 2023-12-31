from contents.line import Content, PlainText


class DataContent(Content):
    def __init__(self, key: str, value: str) -> None:
        self.__key = key
        self.__value = value

    def get_value(self):
        return self.__value

    def get_key(self):
        return self.__key


class ContentFactory:
    @staticmethod
    def getContent(line: str) -> Content:
        assign_idx = line.find("=")

        if assign_idx == -1:
            return PlainText(line)

        key = line[:assign_idx].strip()
        value = line[assign_idx + 1 :].strip()
        content = DataContent(key, value)
        return content
