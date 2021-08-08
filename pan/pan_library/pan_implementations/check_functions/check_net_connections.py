# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Tuple, Dict, Iterable

from pan.pan_library.pan_implementations.errors.custom_errors import CheckNetConnectivityError
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNTreeStructureTrain
from pan.public.interfaces.net_connection import NetConnectionWr, NetConnectionDict


def _check_if_nets_fit(parent_out: Tuple[NetConnectionWr, ...],
                       children_in: Tuple[NetConnectionWr, ...], /) -> None:
    if not parent_out and children_in:
        raise CheckNetConnectivityError("Parent net does not expect to have children!")

    if len(parent_out) != len(children_in):
        raise CheckNetConnectivityError(f"Missing connections: p {parent_out} ch {children_in}!")

    for net_index, net_elem in enumerate(parent_out):
        net_elem.check_if_fitting(children_in[net_index])


def _check_keys_connection_container(con_con: Dict[str, NetConnectionWr],
                                     tuple_to_check: Iterable[str], /) -> None:
    for key_name in tuple_to_check:
        if key_name not in con_con:
            raise CheckNetConnectivityError(
                f"Could not find {key_name} connection in the connection dict!"
            )


def _rec_fitting_check(con_con: Dict[str, NetConnectionWr],
                       tree_elem: ANNTreeStructureTrain, /) -> None:
    parent_out: Tuple[NetConnectionWr, ...] = tree_elem.node_data.connection_out
    children_in: Tuple[NetConnectionWr, ...] = tuple(
        child_elem.node_data.connection_in
        for child_elem in tree_elem.children
    )
    _check_if_nets_fit(parent_out, children_in)
    _check_keys_connection_container(con_con, (elem.dict_id for elem in parent_out))
    _check_keys_connection_container(con_con, (elem.dict_id for elem in children_in))
    for child_node in tree_elem.children:
        _rec_fitting_check(con_con, child_node)


def check_connectivity(framework: str, tree_root: ANNTreeStructureTrain,
                       config_container_con: Dict[str, NetConnectionDict], /) -> None:
    if framework not in config_container_con:
        raise CheckNetConnectivityError(
            f"Could not find {framework} framework in connection-container!"
        )
    if tree_root.parent is not None:
        raise CheckNetConnectivityError("Tree root should not have any parents!")

    _rec_fitting_check(config_container_con[framework].con_dict, tree_root)
