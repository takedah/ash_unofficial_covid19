from abc import ABCMeta, abstractmethod


class Factory(metaclass=ABCMeta):
    def create(self, **row):
        item = self._create_item(**row)
        self._register_item(item)
        return item

    @abstractmethod
    def _create_item(self, **row):
        pass

    @abstractmethod
    def _register_item(self, item):
        pass
