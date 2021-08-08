# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Optional, Type, Dict, final
import pickle as rick

from dataclasses import dataclass

from pan.pan_library.pan_rewowr.errors.custom_errors import JsonDictConError
from rewowr.public.interfaces.container_interface import ContainerInterface


@final
@dataclass
class ContValue:
    structure_id: str
    structure: Dict


@final
class JsonDictCon(ContainerInterface[ContValue]):

    def __init__(self) -> None:
        super().__init__()
        self.__json_dict: Optional[ContValue] = None

    def get_data(self) -> ContValue:
        if self.__json_dict is None:
            raise JsonDictConError('JsonDictCon is empty!')
        return self.__json_dict

    def set_data(self, value: ContValue, /) -> None:
        if not value:
            raise JsonDictConError('The given value is empty!')
        self.__json_dict = value

    def serialize(self) -> bytes:
        return rick.dumps(self.get_data(), protocol=rick.HIGHEST_PROTOCOL)

    @classmethod
    def deserialize(cls: Type['JsonDictCon'], data: bytes, /) -> 'JsonDictCon':
        puf = JsonDictCon()
        puf.set_data(rick.loads(data))
        return puf
