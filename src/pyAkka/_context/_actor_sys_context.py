import copy
import threading
from typing import Dict, Type, TypeVar, TYPE_CHECKING

from pykka import ActorDeadError

from .._reg import ActorRegistry

from .. import SupervisionHandler, Directive
from .._ref import ActorRef
from pykka import ActorRef as pActorRef
from ...PyAkka import ActorRefWrapper, ActorSysRef, SupervisionStrategy

T = TypeVar('T')

if TYPE_CHECKING:
    from ...PyAkka import BaseActor

    _Actor = Type[BaseActor]


class ActorSysContext:
    def __init__(self, actor_ref: ActorSysRef, actor_reg: ActorRegistry, actor_killer: pActorRef):
        self.__actor_ref: ActorSysRef = actor_ref
        self.__actor_reg = actor_reg
        self.__killer = actor_killer
        self.__children: Dict[str, ActorRefWrapper] = {}
        self.__context_lock = threading.RLock()

    def generate_actor(self, actor_class: '_Actor',
                       supervision=SupervisionStrategy(strategy=Directive.Stop,
                                                       maxNumOfRetries=3,
                                                       supervisionHandler=SupervisionHandler()),
                       *args, **kwargs) -> ActorRef:

        if not self.__actor_ref.actor_stop_acquired.is_set():
            actor_ref_wrapper = actor_class.start(supervisor=self.__actor_ref,
                                                  supervision_strategy=supervision,
                                                  killer=self.__killer,
                                                  actor_reg=self.__actor_reg,
                                                  *args, **kwargs)
            actor_ref = actor_ref_wrapper.generate_actor_ref()

            self.__add_actor(actor_ref)
            self.__add_child(actor_ref_wrapper)

            return actor_ref

    def subordinate_failure_handler(self, actor_ref_wrap: ActorRefWrapper):

        actor_ref = self.__actor_reg.get(actor_ref_wrap.actor_urn)

        match actor_ref_wrap.supervision.strategy:
            case Directive.Stop:
                stop_result = actor_ref_wrap.stop()

                if stop_result:
                    self.__remove_actor(actor_ref.actor_urn)

            case Directive.Restart:
                actor_ref_wrap.stop()
                new_actor_ref_wrap = self.__reset_actor(actor_ref_wrap) if actor_ref_wrap.is_restart_validate else None
                actor_ref.update(new_actor_ref_wrap)

            case Directive.Resume:
                actor_ref_wrap.resume()

    def broadcast(self, message):
        any(actor.tell(message) for actor in self.__children.values())

    def remove_subordinate(self, actor_urn: str):
        self.__remove_child(actor_urn)
        self.__remove_actor(actor_urn)

    def stop_subordinates(self):
        _stopped_processed = copy.copy(self.__children)

        for actor in _stopped_processed.values():
            actor.stop()

    def __add_actor(self, actor_ref: ActorRef):
        self.__actor_reg.add_or_update(actor_ref)

    def __remove_child(self, actor_urn: str):
        with self.__context_lock:
            self.__children.pop(actor_urn, None)

    def __remove_actor(self, actor_urn: str):
        self.__actor_reg.remove(actor_urn)

    def __add_child(self, child_actor_ref: ActorRefWrapper):
        with self.__context_lock:
            self.__children.update({child_actor_ref.actor_urn: child_actor_ref})

    def __reset_actor(self, actor_ref: ActorRefWrapper):
        actor = actor_ref.actor_class.start(supervisor=self.__actor_ref,
                                            supervision_strategy=actor_ref.supervision,
                                            actor_reg=self.__actor_reg,
                                            *actor_ref.prop.args, **actor_ref.prop.kwargs)
        return actor

    @property
    def is_empty(self):
        return not bool(self.__children)

    @property
    def children(self):
        return self.__children

