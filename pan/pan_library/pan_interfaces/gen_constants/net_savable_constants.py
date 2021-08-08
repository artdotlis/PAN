# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import NewType, final, Final

from dataclasses import dataclass

from pan.public.constants.net_tree_id_constants import ANNTreeIdType
from pan.pan_library.pan_interfaces.errors.custom_errors import SavableNetError


@final
@dataclass
class _SavableNet:
    id_file: ANNTreeIdType
    ann: bytes


SavableNetType: Final = NewType('SavableNetType', _SavableNet)


def create_train_net_savable(id_local: ANNTreeIdType, ann: bytes, /) -> SavableNetType:
    if not ann:
        raise SavableNetError("Data can not be empty!")
    return SavableNetType(_SavableNet(
        id_file=id_local,
        ann=ann
    ))
