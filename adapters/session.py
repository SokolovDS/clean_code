import abc


class AbstractSession(abc.ABC):
    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError


class FakeSession(AbstractSession):
    committed = False

    def commit(self):
        self.committed = True
