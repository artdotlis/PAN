# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import copy

from typing import List, NewType, Final, final

from pan.public.errors.custom_errors import ANNTreeIdError

_TREE_SEP: Final[str] = '_x_'


def ann_tree_id_short_file_name(ann_tree_id_str: str, /) -> str:
    split_tree = ann_tree_id_str.split(_TREE_SEP)
    return f"{len(split_tree)}_{split_tree[-1]}"


@final
class _ANNTreeId:
    def __init__(self, id_list: List[str], file_name: str, /) -> None:
        super().__init__()
        self.__id_list = id_list
        self.__file_name = file_name
        self.__mod = ""

    @property
    def id_list(self) -> List[str]:
        return self.__id_list

    @property
    def file_name(self) -> str:
        return self.__file_name

    @property
    def mod_str(self) -> str:
        return self.__mod

    def add_modifier(self, mod: str, /) -> None:
        if self.__mod:
            self.__mod = f"{self.__mod}X{mod}"
        else:
            self.__mod = f"{mod}"

    @property
    def id_merged_str(self) -> str:
        id_merged_str = _TREE_SEP.join(self.id_list)
        if self.file_name:
            id_merged_str += f"_{self.file_name}"
        if self.mod_str:
            id_merged_str += f"_{self.mod_str}"
        return id_merged_str


ANNTreeIdType: Final = NewType('ANNTreeIdType', _ANNTreeId)


def create_ann_tree_id_empty(id_list_local: List[str], /) -> ANNTreeIdType:
    if not id_list_local:
        raise ANNTreeIdError("The parameter id_list_local can not be empty!")
    return ANNTreeIdType(_ANNTreeId(copy.deepcopy(id_list_local), ""))


def create_ann_tree_id(id_list_local: List[str], file_name: str, /) -> ANNTreeIdType:
    if not (id_list_local and file_name):
        raise ANNTreeIdError("The parameter id_list_local and the file name can not be empty!")
    return ANNTreeIdType(_ANNTreeId(copy.deepcopy(id_list_local), file_name))
