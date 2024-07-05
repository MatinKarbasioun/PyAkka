from typing import Type, Any, TYPE_CHECKING
from abc import abstractmethod
import pykka


if TYPE_CHECKING:
    from ...PyAkka import BaseActor, ActorSystem

    _Actor = Type[BaseActor]
    _ActorSys = Type[ActorSystem]


class IActorRef:

    @abstractmethod
    def tell(self, message):
        raise NotImplementedError

    @abstractmethod
    def ask(self, message, block=True, timeout=None):
        raise NotImplementedError

    @abstractmethod
    def stop(self, block=True, timeout=None):
        raise NotImplementedError

    @abstractmethod
    def broadcast(self, message: Any):
        raise NotImplementedError

    @abstractmethod
    def proxy(self) -> pykka.ActorProxy:
        raise NotImplementedError

    @abstractmethod
    def is_stop_set(self):
        raise NotImplementedError


class IActorRefWrapper:

    @abstractmethod
    def tell(self, message):
        raise NotImplementedError

    @abstractmethod
    def ask(self, message, block=True, timeout=None):
        raise NotImplementedError

    @abstractmethod
    def stop(self, block=True, timeout=None):
        raise NotImplementedError

    @abstractmethod
    def broadcast(self, message: Any):
        raise NotImplementedError

    @abstractmethod
    def proxy(self) -> pykka.ActorProxy:
        raise NotImplementedError

    @abstractmethod
    def is_stop_set(self):
        raise NotImplementedError
