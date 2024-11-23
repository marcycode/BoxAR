from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def notify(self, observable, *args, **kwargs):
        pass
