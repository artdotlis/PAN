# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import pickle as rick
from typing import Type

from pan.public.errors.custom_errors import LoadingNetSavableError
from pan.public.interfaces.pub_net_interface import NetSavable, NodeANNDataElemInterface


def net_interface_load_net(container_class: Type[NodeANNDataElemInterface], byte_data: bytes, /) \
        -> NetSavable:
    try:
        loaded_data = rick.loads(byte_data)
    except Exception as ex:
        raise LoadingNetSavableError(f"Data load error occurred:\n {ex}")

    if not isinstance(loaded_data, NetSavable):
        raise LoadingNetSavableError(f"Loaded data has the wrong type: {type(loaded_data)}")

    if loaded_data.node_type != container_class:
        raise LoadingNetSavableError(
            f"Loaded data has the wrong net type: \ngot {type(loaded_data.node_type)}"
            + f"\nexpected {container_class}"
        )
    loaded_data.prepare_ann_load()
    return loaded_data
