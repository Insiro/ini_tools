from contents.line import Content


class KeyContentWrapper(Content):
    def __init__(self, key) -> None:
        self.__key = key

    def get_key(self):
        return self.__key


class CommandWrapper(KeyContentWrapper):
    pass


class DataWrapper(KeyContentWrapper):
    pass
