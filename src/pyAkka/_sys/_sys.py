import logging
import threading
from types import TracebackType
from typing import Type, Any

import pykka

from .._actor._killer import Killer
from .._reg import ActorRegistry as actorRegistry
from pykka import ActorRegistry, ActorDeadError

from .._actor import BaseActor
from .._context import ActorSysContext
from .._ref import ActorSysRef
from ..internal_msg import ActorStopCommand

logger = logging.getLogger("pykka")

_Actor = Type[BaseActor]


class ActorSystem(pykka.ThreadingActor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor_inbox = self._create_actor_inbox()
        self.actor_stopped = threading.Event()
        self.__actor_registry = actorRegistry()
        self.__thread = None
        self.actor_ref: ActorSysRef = ActorSysRef(actor=self)
        self.__killer = Killer.start()
        self.__context = ActorSysContext(self.actor_ref, self.__actor_registry, actor_killer=self.__killer)

    @property
    def context(self) -> ActorSysContext:
        return self.__context

    @classmethod
    def start(cls,
              *args,
              **kwargs) -> ActorSysRef:
        obj = cls(*args, **kwargs)

        assert obj.actor_ref is not None, (
            "Actor.__init__() have not been called. "
            "Did you forget to call super() in your override?"
        )
        ActorRegistry.register(obj.actor_ref)
        logger.debug(f"Starting {obj}")
        obj.start_loop()
        return obj.actor_ref

    def on_failure(
            self,
            exception_type: type[BaseException],
            exception_value: BaseException,
            traceback: TracebackType,
    ) -> None:
        logger.error(f'exception occurred with type{exception_type!r} and value {exception_value!r}')
        logger.error(f'traceback {traceback!r}')
        self.context.stop_subordinates()

    def start_loop(self):
        self._start_actor_loop()

    def on_stop(self) -> None:
        self.__killer.stop(block=True)
        logger.info('Actor System Stopped')
        print('Actor Sys Stopped')

    @classmethod
    def __stop_child(cls, actor, timeout=None):
        ask_future = actor.ask(ActorStopCommand(), block=False)

        def _stop_result_converter(timeout):
            try:
                ask_future.get(timeout=timeout)
                return True
            except ActorDeadError:
                return False

        converted_future = ask_future.__class__()
        converted_future.set_get_hook(_stop_result_converter)
        return converted_future.get(timeout=timeout)

    @property
    def thread(self):
        return self.__thread
