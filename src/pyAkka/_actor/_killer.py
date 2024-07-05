from typing import Any

from pykka import ThreadingActor, ActorDeadError

from Common.ActorModel.PyAkka import ActorRefWrapper
from Common.ActorModel.PyAkka.internal_msg import KillActorMessage, ActorStopCommand


class Killer(ThreadingActor):
    def __init__(self):
        super(Killer, self).__init__()

    def on_receive(self, message: Any) -> Any:
        if isinstance(message, KillActorMessage):
            return self.__kill_child(message.actor_ref)

    def __kill_child(self, child_actor: ActorRefWrapper):
        stop_actor = True

        if child_actor.is_alive():
            stop_actor = self.__stop_child(child_actor)
            child_actor.actor_thread.join()
        return stop_actor

    @classmethod
    def __stop_child(cls, actor: ActorRefWrapper, timeout=None):
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
