import threading

from .._ref import ActorRef


class ActorRegistry:
    def __init__(self):
        self.__actors: dict[str, ActorRef] = {}
        self.__rLock = threading.RLock()

    def add_or_update(self, actor_ref: ActorRef):
        with self.__rLock:
            self.__actors.update({actor_ref.actor_urn: actor_ref})

    def remove(self, actor_urn: str):
        with self.__rLock:
            self.__actors.pop(actor_urn, None)

    def get(self, actor_urn: str) -> ActorRef:
        _actor_ref = self.__actors.get(actor_urn, None)
        return _actor_ref

    def get_all(self) -> list[ActorRef]:
        return list(self.__actors.values())
