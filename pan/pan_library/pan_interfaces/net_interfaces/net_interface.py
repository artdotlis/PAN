# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Iterable, Tuple, Optional, List, final
import pickle as rick

from dataclasses import dataclass

from pan.pan_library.pan_interfaces.errors.custom_errors import ANNTreeStructureTrainError
from pan.public.interfaces.pub_net_interface import NetSavable, NodeANNDataElemInterface


def net_interface_save_net(save_able_data: NetSavable, /) -> bytes:
    if not save_able_data.to_save:
        return b''
    saved_buffer = save_able_data.prepare_ann_save()
    erg = rick.dumps(save_able_data, protocol=rick.HIGHEST_PROTOCOL)
    save_able_data.ann_saved(saved_buffer)
    return erg


def rec_walk_ann_tree(ann_node: Optional['ANNTreeStructureTrain'], /) \
        -> Iterable['ANNTreeStructureTrain']:
    if ann_node is not None:
        yield ann_node
        yield from rec_walk_ann_tree(ann_node.parent)


@final
@dataclass
class ANNTreeStructureTrainWr:
    structure: 'ANNTreeStructureTrain'
    file_name: str


@final
class ANNTreeStructureTrain:
    def __init__(self, net_id: str, dict_id: str,
                 parent: Optional['ANNTreeStructureTrain'],
                 data_elem: NodeANNDataElemInterface, /) -> None:
        self.__net_id = net_id
        self.__parent: Optional['ANNTreeStructureTrain'] = parent
        self.__children: Tuple['ANNTreeStructureTrain', ...] = tuple()
        self.__data_elem: NodeANNDataElemInterface = data_elem
        self.__data_elem.set_node_name(f"{net_id} - {dict_id}")

    @property
    def net_id(self) -> str:
        return self.__net_id

    @property
    def net_tree_id(self) -> List[str]:
        tree_id_list = [node.net_id for node in rec_walk_ann_tree(self)]
        return tree_id_list[::-1]

    @property
    def node_data(self) -> NodeANNDataElemInterface:
        return self.__data_elem

    @property
    def parent(self) -> Optional['ANNTreeStructureTrain']:
        return self.__parent

    @property
    def children(self) -> Tuple['ANNTreeStructureTrain', ...]:
        return self.__children

    @children.setter
    def children(self, children: Tuple['ANNTreeStructureTrain', ...], /) -> None:
        if self.children:
            raise ANNTreeStructureTrainError(f"The children attribute was already set!")
        self.__children = children


@final
@dataclass
class ANNStructureTestWr:
    structure: 'ANNStructureTest'
    file_name: str


@final
class ANNStructureTest:
    def __init__(self, net_id: str, dict_id: str, data_elem: NodeANNDataElemInterface, /) -> None:
        self.__net_id = net_id
        self.__data_elem = data_elem
        self.__data_elem.set_node_name(f"{net_id} - {dict_id}")

    @property
    def net_id(self) -> str:
        return self.__net_id

    @property
    def net_tree_id(self) -> List[str]:
        return [self.net_id]

    @property
    def node_data(self) -> NodeANNDataElemInterface:
        return self.__data_elem
