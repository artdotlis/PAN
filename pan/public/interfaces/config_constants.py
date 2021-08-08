# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import abc
from typing import Dict, Type, final
from dataclasses import dataclass

from pan.public.interfaces.pub_net_interface import NodeANNDataElemInterface


@final
@dataclass
class ExtraArgsNet:
    arguments: Dict[str, str]


class CheckCreateNetElem(abc.ABC):
    @abc.abstractmethod
    def check_args_func(self, extra_args: ExtraArgsNet, /) -> NodeANNDataElemInterface:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def dict_id(self) -> str:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def framework(self) -> str:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def net_type(self) -> Type[NodeANNDataElemInterface]:
        raise NotImplementedError("Interface!")


@final
@dataclass
class NetDictLibraryType:
    framework: str
    net_dict: Dict[str, CheckCreateNetElem]
