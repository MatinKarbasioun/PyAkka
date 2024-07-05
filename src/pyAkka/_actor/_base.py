import logging
import queue
import threading
from types import TracebackType

from .._reg import ActorRegistry as actorReg
import pykka
from pykka import ActorRegistry, ThreadingFuture, ActorRef
from pykka import messages
from typing import Union

from .. import ActorSysRef
from ..internal_msg import ActorStopCommand
from ...PyAkka import ActorRefWrapper, Directive, SupervisionStrategy, ActorProp, Context

logger = logging.getLogger("pykka")


class BaseActor(pykka.Actor):
    supervisor: Union[ActorRefWrapper, ActorSysRef] = None
    killer = None
    actor_reg: actorReg
    supervision: SupervisionStrategy = None
    use_daemon_thread = False
    actor_prop = ActorProp(args=(), kwargs={})

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__thread = None
        self.actor_stopped = threading.Event()
        self.__use_daemon_thread = False
        self.actor_ref: ActorRefWrapper = self.__generate_actor_ref(self.actor_prop)

        self.__context = Context(actor_reg=self.actor_reg,
                                 actor_killer=self.killer,
                                 parent=self.supervisor,
                                 parent_context=self.supervisor.context,
                                 actor_ref=self.actor_ref)

    @property
    def context(self):
        return self.__context

    @classmethod
    def start(cls,
              supervisor,
              supervision_strategy: SupervisionStrategy,
              killer: ActorRef,
              actor_reg: actorReg,
              *args,
              **kwargs) -> ActorRefWrapper:
        cls.supervisor = supervisor
        cls.supervision = supervision_strategy
        cls.killer = killer
        cls.actor_reg = actor_reg
        cls.actor_prop = ActorProp(kwargs=kwargs, args=args)
        obj = cls(*args, **kwargs)

        assert obj.actor_ref is not None, (
            "Actor.__init__() have not been called. "
            "Did you forget to call super() in your override?"
        )
        ActorRegistry.register(obj.actor_ref)
        logger.debug(f"Starting {obj}")
        obj.start_loop()
        return obj.actor_ref

    def on_stop(self) -> None:
        self.supervision.supervisionHandler.on_stop(self.actor_ref)
        print(f"on stopped of actor {self} called")

    def on_failure(
            self,
            exception_type: type[BaseException],
            exception_value: BaseException,
            traceback: TracebackType,
    ) -> None:

        print('on failure call')
        self.supervision.supervisionHandler.on_failure(self.actor_ref, exception_type, exception_value, traceback)
        logger.error(f'exception occurred with type{exception_type!r} and value {exception_value!r}')
        logger.error(f'traceback {traceback!r}')
        self.__context.failure_handle()

    def _handle_failure(self, exception_type, exception_value, traceback):
        """Logs unexpected failures, unregisters and stops the actor."""
        logger.error(
            f"Unhandled exception in {self}:",
            exc_info=(exception_type, exception_value, traceback),
        )
        print('handle failure call')
        match self.actor_ref.supervision.strategy:
            case Directive.Stop:
                ActorRegistry.unregister(self.actor_ref)
                self.actor_stopped.set()

            case Directive.Restart:
                self.actor_stopped.set()

            case Directive.Resume:
                pass

    def _handle_receive(self, message):
        """Handles messages sent to the actor."""
        if isinstance(message, ActorStopCommand):
            self._stop()
        if isinstance(message, messages.ProxyCall):
            callee = self._get_attribute_from_path(message.attr_path)
            return callee(*message.args, **message.kwargs)
        if isinstance(message, messages.ProxyGetAttr):
            attr = self._get_attribute_from_path(message.attr_path)
            return attr
        if isinstance(message, messages.ProxySetAttr):
            parent_attr = self._get_attribute_from_path(message.attr_path[:-1])
            attr_name = message.attr_path[-1]
            return setattr(parent_attr, attr_name, message.value)
        return self.on_receive(message)

    @staticmethod
    def _create_actor_inbox():
        return queue.Queue()

    @staticmethod
    def _create_future():
        return ThreadingFuture()

    def start_loop(self):
        self._start_actor_loop()

    def _start_actor_loop(self):
        self.__thread = threading.Thread(target=self._actor_loop)
        self.__thread.name = self.__thread.name.replace("Thread", self.__class__.__name__)
        self.__thread.daemon = self.__use_daemon_thread
        self.__thread.start()

    @property
    def thread(self):
        return self.__thread

    def __generate_actor_ref(self, actor_prop):
        return ActorRefWrapper(actor=self,
                               supervisor=self.supervisor,
                               supervision_strategy=self.supervision,
                               actor_prop=actor_prop)
