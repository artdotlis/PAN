# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from enum import Enum
from typing import Type, Dict, List

from pan.pan_library.pan_implementations.errors.custom_errors import CheckTrainStructureError
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import \
    NetElementStructure, NetElementStructureKeys, NetDefKeys, NetTreeStructureKeys, \
    NetTreeStructure, NetDef, NetElemStructureTest, NetElemStructureTestKeys


def _check_inner_parts(keys_enum: Type[Enum], dict_to_check: Dict, /) -> None:
    for enum_elem in keys_enum:
        if enum_elem.value.index not in dict_to_check:
            raise CheckTrainStructureError(f"The key {enum_elem.value.index} is missing!")
        if not isinstance(dict_to_check[enum_elem.value.index], enum_elem.value.type):
            raise CheckTrainStructureError(
                f"The {enum_elem.value.index} element is not a {enum_elem.value.type}!"
            )


def _rec_inner_check_net_tree(dict_to_check: Dict, /) -> None:
    _check_inner_parts(NetTreeStructureKeys, dict_to_check)
    for list_rec in dict_to_check[NetTreeStructureKeys.children.value.index]:
        _rec_inner_check_net_tree(list_rec)


def _create_dict_container_net_def(given_dict: Dict, /) -> Dict[str, NetDef]:
    dict_puf = {}
    for key_dict, dict_value in given_dict.items():
        kwargs_loc = {
            enum_elem.name: dict_value[enum_elem.value.index]
            for enum_elem in NetDefKeys
        }
        dict_puf[key_dict] = NetDef(**kwargs_loc)

    return dict_puf


def _rec_container_tree(given_tree: List[Dict], /) -> List[NetTreeStructure]:
    if not given_tree:
        return []
    return [
        NetTreeStructure(
            net_id=tree_node[NetTreeStructureKeys.net_id.value.index],
            children=_rec_container_tree(tree_node[NetTreeStructureKeys.children.value.index])
        )
        for tree_node in given_tree
    ]


def _create_dict_container_tree(given_tree: Dict, /) -> NetTreeStructure:
    return NetTreeStructure(
        net_id=given_tree[NetTreeStructureKeys.net_id.value.index],
        children=_rec_container_tree(given_tree[NetTreeStructureKeys.children.value.index])
    )


def parse_train_structure_dict(json_container: Dict, /) -> NetElementStructure:
    _check_inner_parts(NetElementStructureKeys, json_container)

    if not isinstance(json_container[NetElementStructureKeys.net_definitions.value.index], dict):
        raise CheckTrainStructureError(
            f"The {NetElementStructureKeys.net_definitions.value.index} element is not a dictionary"
            + f" but {type(json_container[NetElementStructureKeys.tree_root.value.index])}!"
        )

    for dict_elem in json_container[NetElementStructureKeys.net_definitions.value.index].values():
        _check_inner_parts(NetDefKeys, dict_elem)

    if not isinstance(json_container[NetElementStructureKeys.tree_root.value.index], dict):
        raise CheckTrainStructureError(
            f"The {NetElementStructureKeys.tree_root.value.index} element is not a dictionary"
            + f" but {type(json_container[NetElementStructureKeys.tree_root.value.index])}!"
        )
    _rec_inner_check_net_tree(json_container[NetElementStructureKeys.tree_root.value.index])

    return NetElementStructure(
        net_definitions=_create_dict_container_net_def(
            json_container[NetElementStructureKeys.net_definitions.value.index]
        ),
        tree_root=_create_dict_container_tree(
            json_container[NetElementStructureKeys.tree_root.value.index]
        )
    )


def parse_test_structure_dict(json_container: Dict, /) -> NetElemStructureTest:
    _check_inner_parts(NetElemStructureTestKeys, json_container)

    for dict_elem in json_container[NetElemStructureTestKeys.net_definitions.value.index].values():
        _check_inner_parts(NetDefKeys, dict_elem)

    return NetElemStructureTest(
        net_definitions=_create_dict_container_net_def(
            json_container[NetElemStructureTestKeys.net_definitions.value.index]
        )
    )
