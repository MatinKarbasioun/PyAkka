from typing import Any, TYPE_CHECKING, Type

import pykka


from ._IActor_ref import IActorRef

if TYPE_CHECKING:
    from .._ref import ActorRefWrapper

    _ActorRef = ActorRefWrapper


class ActorRef(IActorRef):

    def __init__(self, actor_ref: 'ActorRefWrapper'):
        self.__actor_ref = actor_ref

    def tell(self, message):
        self.__actor_ref.tell(message)

    def ask(self, message, block=True, timeout=None):
        return self.__actor_ref.ask(message, block, timeout)

    def stop(self, block=True, timeout=None):
        stop_response = self.__actor_ref.stop(block, timeout)
        return stop_response

    def broadcast(self, message: Any):
        self.__actor_ref.broadcast(message)

    def proxy(self) -> pykka.ActorProxy:
        return self.__actor_ref.proxy()

    @property
    def actor_urn(self):
        return self.__actor_ref.actor_urn

    @property
    def is_stop_set(self):
        return self.__actor_ref.actor_stop_acquired

    def update(self, actor_ref_wrapper: 'ActorRefWrapper' = None):
        if actor_ref_wrapper:
            self.__actor_ref = actor_ref_wrapper
