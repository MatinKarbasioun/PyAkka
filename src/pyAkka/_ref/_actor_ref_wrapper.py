import gc
import random
import threading
import time
import uuid
from typing import Type, Any, TYPE_CHECKING, Self

import pykka
from pykka import ActorRegistry

from .._ref import ActorRef

from Common.ActorModel.PyAkka._prop import ActorProp

if TYPE_CHECKING:
    from ...PyAkka import BaseActor, ActorSystem, SupervisionStrategy

    _Actor = Type[BaseActor]
    _ActorSys = Type[ActorSystem]


class ActorRefWrapper(pykka.ActorRef):

    def __init__(self,
                 actor: 'BaseActor',
                 supervisor: Self,
                 supervision_strategy: 'SupervisionStrategy',
                 actor_prop: ActorProp):
        super().__init__(actor)
        self._actor: 'BaseActor' = actor
        self.__supervision_strategy = supervision_strategy
        self.actor_class: _Actor = actor.__class__
        self.__supervisor = supervisor
        self.__actor_prop = actor_prop
        self.__actor_try_num = 0
        self.__actor_stop_acquired = threading.Event()
        self.__ref_lock = threading.RLock()
        self.__stop_response = False
        print(f'ActorRef {self} with ref', threading.current_thread().ident)

    def tell(self, message):
        super(ActorRefWrapper, self).tell(message)

    def ask(self, message, block=True, timeout=None):
        print(f'ask locked {message}')
        return super(ActorRefWrapper, self).ask(message, block, timeout)

    def stop(self, block=True, timeout=None):
        with self.__ref_lock:
            while not self._actor.context.parenting:
                if not self.__actor_stop_acquired.is_set():
                    print('stop locked')
                    self.__actor_stop_acquired.set()
                    self._actor.context.stop_subordinates()
                    self.__stop_response = self._actor.context.remove_myself()
                    return self.__stop_response

                return self.__actor_stop_acquired.is_set()

    def resume(self):
        self.actor_stopped.clear()
        ActorRegistry.register(self)

    def broadcast(self, message: Any):
        self._actor.context.broadcast(message)

    def proxy(self) -> pykka.ActorProxy:
        return super(ActorRefWrapper, self).proxy()

    @property
    def context(self):
        return self._actor.context

    @property
    def children(self):
        return self._actor.context.__children

    @property
    def supervision(self):
        return self.__supervision_strategy

    @property
    def prop(self):
        return self.__actor_prop

    @property
    def actor_stop_acquired(self):
        return self.__actor_stop_acquired

    @property
    def is_restart_validate(self):
        self.__actor_try_num += 1
        return self.__actor_try_num <= self.supervision.maxNumOfRetries

    @property
    def actor_thread(self) -> threading.Thread:
        return self._actor.thread

    def generate_actor_ref(self):
        return ActorRef(self)
