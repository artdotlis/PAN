# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Dict, final
from dataclasses import dataclass

from pan.public.errors.custom_errors import NetConnectionWrError


@final
class NetConnectionWr:

    def __init__(self, connection_name: str, frame_work: str, /) -> None:
        super().__init__()
        self.__connection_name = connection_name
        self.__frame_work = frame_work

    @staticmethod
    def parse_dict_id(frame_work: str, con_name: str, /) -> str:
        if frame_work and con_name:
            return f"X{frame_work}x{con_name}X"
        return ""

    @property
    def dict_id(self) -> str:
        return self.parse_dict_id(self.framework, self.__connection_name)

    @property
    def framework(self) -> str:
        return self.__frame_work

    def check_if_fitting(self, connection: 'NetConnectionWr', /) -> None:
        if not self.dict_id:
            raise NetConnectionWrError("No connection expected!")
        if connection.dict_id != self.dict_id:
            raise NetConnectionWrError(f"Expected type {self.dict_id}, got {connection.dict_id}!")

    def __str__(self) -> str:
        return f"Con: {self.dict_id if self.dict_id else 'empty'}"


@final
@dataclass
class NetConnectionDict:
    framework: str
    con_dict: Dict[str, NetConnectionWr]
