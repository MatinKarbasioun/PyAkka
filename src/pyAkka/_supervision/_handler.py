from types import TracebackType
from abc import abstractmethod
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from ...PyAkka import ActorRefWrapper

    _Ref = ActorRefWrapper


class SupervisionHandler:

    @abstractmethod
    def on_failure(self,
                   actor_ref: '_Ref',
                   exception_type: type[BaseException],
                   exception_value: BaseException,
                   traceback: TracebackType):
        pass

    @abstractmethod
    def on_stop(self, actor_ref: '_Ref'):
        pass
