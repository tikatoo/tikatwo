from typing import Callable, Mapping, Type

from .module import MessageHandler, Module
from .counter import Counter


mapping: Mapping[str, Type[Module]] = {
    'Counter': Counter
}
