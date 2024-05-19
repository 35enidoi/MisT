from abc import ABC, abstractmethod

__all__ = ["AbstractViewModel"]


class AbstractViewModel(ABC):
    theme: str

    @abstractmethod
    def recreate_before(self, _view) -> None:
        pass

    @abstractmethod
    def recreate_after(self) -> None:
        pass
