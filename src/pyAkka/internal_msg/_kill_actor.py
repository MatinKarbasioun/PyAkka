from typing import NamedTuple

from Common.ActorModel.PyAkka import ActorRefWrapper


class KillActorMessage(NamedTuple):
    actor_ref: ActorRefWrapper


