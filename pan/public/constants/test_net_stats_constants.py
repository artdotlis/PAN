# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import List, NewType, final, Final
from dataclasses import dataclass

from pan.public.errors.custom_errors import TestNNStatsElementError
from pan.public.constants.net_tree_id_constants import ANNTreeIdType


@final
@dataclass
class _TestNNStatsElement:
    id_file: ANNTreeIdType
    data: List[str]
    file_end: str


TestNNStatsElementType: Final = NewType('TestNNStatsElementType', _TestNNStatsElement)


def create_test_net_stats(id_local: ANNTreeIdType, data: List[str], file_end: str, /) \
        -> TestNNStatsElementType:
    if not data:
        raise TestNNStatsElementError("Data can not be empty!")
    return TestNNStatsElementType(_TestNNStatsElement(
        id_file=id_local,
        data=data,
        file_end=file_end
    ))
