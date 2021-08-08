# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import abc
from dataclasses import dataclass
from typing import TypeVar, Generic, Type, Tuple, Iterable, Union, final, Final

from pan.public.constants.net_tree_id_constants import ANNTreeIdType
from pan.public.constants.test_net_stats_constants import TestNNStatsElementType
from pan.public.constants.train_net_stats_constants import TrainNNStatsElementType
from pan.public.interfaces.net_connection import NetConnectionWr
from pan.public.errors.custom_errors import PubNetInterfaceError
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface

_AnnT: Final = TypeVar('_AnnT')
_AnnInt: Final = TypeVar('_AnnInt')
_AnnBuf: Final = TypeVar('_AnnBuf')
_InputT: Final = TypeVar('_InputT')


class NetSavInterface(Generic[_AnnT, _AnnInt, _AnnBuf, _InputT], abc.ABC):
    @property
    @abc.abstractmethod
    def get_net_com(self) -> _AnnT:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def get_net_lego(self) -> _AnnT:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def save(self) -> Tuple[bytes, Tuple[_AnnInt, ...], _AnnBuf]:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def save_complete(self, saved_net: Tuple[_AnnInt, ...], saved_buf: _AnnBuf, /) -> None:
        raise NotImplementedError("Interface!")

    @classmethod
    @abc.abstractmethod
    def load(cls, data: bytes, extra_args: _InputT, /) -> 'NetSavInterface':
        raise NotImplementedError("Interface!")


@final
@dataclass
class NetSavableArgs:
    node_id: str
    node_type: Type['NodeANNDataElemInterface']
    ann_type: Type[NetSavInterface]
    to_save: bool


@final
class NetSavable(Generic[_AnnT, _AnnInt, _AnnBuf, _InputT]):

    def __init__(self, ann: NetSavInterface[_AnnT, _AnnInt, _AnnBuf, _InputT],
                 args: NetSavableArgs, input_data: _InputT, /) -> None:
        super().__init__()
        self.__node_id = args.node_id
        self.__node_type = args.node_type
        self.__ann_obj: Union[bytes, NetSavInterface[_AnnT, _AnnInt, _AnnBuf, _InputT]] = ann
        self.__input_data: _InputT = input_data
        self.__to_save = args.to_save
        self.__ann_type = args.ann_type

    @property
    def node_id(self) -> str:
        return self.__node_id

    @property
    def to_save(self) -> bool:
        return self.__to_save

    @property
    def node_type(self) -> Type['NodeANNDataElemInterface']:
        return self.__node_type

    def prepare_ann_save(self) -> Tuple[NetSavInterface, Tuple[_AnnInt, ...], _AnnBuf]:
        if not isinstance(self.__ann_obj, NetSavInterface):
            raise PubNetInterfaceError('Net was already properly saved!')
        out_put = self.__ann_obj
        buff = self.__ann_obj.save()
        self.__ann_obj = buff[0]
        erg = (out_put, buff[1], buff[2])
        return erg

    def ann_saved(self, buffered: Tuple[NetSavInterface, Tuple[_AnnInt, ...], _AnnBuf], /) -> None:
        if not isinstance(self.__ann_obj, bytes):
            raise PubNetInterfaceError('Net was already properly loaded!')
        self.__ann_obj = buffered[0]
        self.__ann_obj.save_complete(buffered[1], buffered[2])

    def prepare_ann_load(self) -> None:
        if not isinstance(self.__ann_obj, bytes):
            raise PubNetInterfaceError('Net was already properly loaded!')
        self.__ann_obj = self.__ann_type.load(self.__ann_obj, self.__input_data)

    @property
    def ann_container(self) -> NetSavInterface[_AnnT, _AnnInt, _AnnBuf, _InputT]:
        if not isinstance(self.__ann_obj, NetSavInterface):
            raise PubNetInterfaceError('Net was not properly loaded!')
        return self.__ann_obj

    @property
    def input_data(self) -> _InputT:
        return self.__input_data


class NodeANNDataElemInterface(Generic[_AnnT, _AnnInt, _AnnBuf, _InputT], abc.ABC):
    # savable
    @abc.abstractmethod
    def get_savable_data(self) -> NetSavable[_AnnT, _AnnInt, _AnnBuf, _InputT]:
        raise NotImplementedError("Interface!")

    # not savable
    @abc.abstractmethod
    def get_node_name(self) -> str:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def set_node_name(self, name: str) -> None:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def connection_in(self) -> NetConnectionWr:
        raise NotImplementedError("Interface!")

    @property
    @abc.abstractmethod
    def connection_out(self) -> Tuple[NetConnectionWr, ...]:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def check_net(self, internal_nets: Tuple['NodeANNDataElemInterface', ...],
                  sync_out: SyncStdoutInterface, /) -> None:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def prepare_data(self, sync_out: SyncStdoutInterface, /) -> None:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def init_net(self, internal_nets: Tuple['NodeANNDataElemInterface', ...],
                 sync_out: SyncStdoutInterface, /) -> bool:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def train_net(self, id_file: ANNTreeIdType, sync_out: SyncStdoutInterface, /) \
            -> Iterable[TrainNNStatsElementType]:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def test_net(self, id_file: ANNTreeIdType, sync_out: SyncStdoutInterface, /) \
            -> Tuple[TestNNStatsElementType, ...]:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def finalize(self) -> None:
        raise NotImplementedError("Interface!")
