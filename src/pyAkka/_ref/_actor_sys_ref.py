import threading
from typing import Type, Any, TYPE_CHECKING

import pykka

from Common.ActorModel.PyAkka import SupervisionStrategy, Directive, SupervisionHandler

if TYPE_CHECKING:
    from Common.ActorModel.PyAkka import BaseActor, ActorSystem

    _Actor = Type[BaseActor]
    _ActorSys = Type[ActorSystem]


class ActorSysRef(pykka.ActorRef):
    def __init__(self,
                 actor: 'ActorSystem'):
        super().__init__(actor)
        self._actor: 'ActorSystem' = actor
        self.actor_class: '_ActorSys' = actor.__class__
        self.__actor_stop_acquired = threading.Event()

    def create_actor(self, actor_class: '_Actor',
                     supervision: SupervisionStrategy = SupervisionStrategy(strategy=Directive.Stop,
                                                                            maxNumOfRetries=3,
                                                                            supervisionHandler=SupervisionHandler()),
                     *args,
                     **kwargs):
        return self._actor.context.generate_actor(actor_class,
                                                  supervision,
                                                  *args,
                                                  **kwargs)

    def tell(self, message):
        super(ActorSysRef, self).tell(message)

    def ask(self, message, block=True, timeout=None):
        return super(ActorSysRef, self).ask(message, block, timeout)

    def broadcast(self, message: Any):
        self.context.broadcast(message)

    def stop_subordinates(self):
        if not self.__actor_stop_acquired.is_set():
            self.__actor_stop_acquired.set()
            self.context.stop_subordinates()

        return self.__actor_stop_acquired.is_set()

    def proxy(self) -> pykka.ActorProxy:
        return super(ActorSysRef, self).proxy()

    @property
    def context(self):
        return self._actor.context

    @property
    def actor_sys_thread(self):
        return self._actor.thread

    @property
    def actor_stop_acquired(self):
        return self.__actor_stop_acquired

    def terminate(self, block=True, timeout=None):
        is_full = True

        while is_full:
            self.stop_subordinates()
            is_full = not self.context.is_empty

        stop_response = super(ActorSysRef, self).stop(block, timeout)
        return stop_response
