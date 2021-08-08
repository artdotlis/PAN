# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Dict

from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import \
    NetElementStructure, NetTreeStructure
from pan.pan_library.pan_implementations.errors.custom_errors import CheckNetDefCompletenessError
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import NetDef


def _check_recursively(net_def: Dict[str, NetDef], net_elem: NetTreeStructure, /) -> None:
    if net_elem.net_id not in net_def:
        raise CheckNetDefCompletenessError(f"Could not find the id {net_elem.net_id}")
    for child in net_elem.children:
        _check_recursively(net_def, child)


def check_net_definitions_completeness(structure: NetElementStructure, /) -> None:
    _check_recursively(structure.net_definitions, structure.tree_root)


def check_net_def_framework(framework: str, net_def: Dict[str, NetDef], /) -> None:
    for net_id, net_elem in net_def.items():
        if net_elem.net_framework != framework:
            raise CheckNetDefCompletenessError(
                f"Net structure required framework {framework} "
                + f"got framework {net_elem.net_framework} in {net_id}!"
            )
