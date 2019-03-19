from typing import Callable, Mapping, Type

from .module import MessageHandler, Module
from .callresponse import CallResponse


mapping: Mapping[str, Type[Module]] = {
    'CallResponse': CallResponse
}
