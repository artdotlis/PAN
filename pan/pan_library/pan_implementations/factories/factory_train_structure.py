# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import time
from typing import Dict, Optional, Tuple, Final

from pan.pan_library.pan_interfaces.gen_constants.file_names import TTSubStrPre
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetStructureTrainCon
from pan.pan_library.pan_rewowr.container.dict_json import JsonDictCon
from pan.pan_library.pan_implementations.check_functions.check_train_test_structure_dict import \
    parse_train_structure_dict
from pan.pan_library.pan_implementations.factories.factory_net_interface import \
    factory_net_dict_train
from pan.pan_library.pan_implementations.check_functions.check_net_definitions_completness import \
    check_net_definitions_completeness
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNTreeStructureTrain, \
    ANNTreeStructureTrainWr
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import \
    NetElementStructure, NetTreeStructure, NetDef
from pan.pan_library.pan_implementations.check_functions.check_net_connections import \
    check_connectivity
from pan.pan_library.pan_implementations.errors.custom_errors import FactoryTrainStructureError
from pan.public.interfaces.config_constants import CheckCreateNetElem, \
    ExtraArgsNet, NetDictLibraryType
from pan.public.interfaces.net_connection import NetConnectionDict
from rewowr.public.functions.check_extra_args_dict import check_extra_args_dict
from rewowr.public.functions.syncout_dep_functions import logger_print_con
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface

_MODULE_NAME: Final[str] = "factory_train_structure"


def _rec_tree_creation(parent: Optional[ANNTreeStructureTrain], tree_structure: NetTreeStructure,
                       net_creator: Dict[str, CheckCreateNetElem], net_def: Dict[str, NetDef],
                       child_id: int, /) -> ANNTreeStructureTrain:
    extra_args = net_def[tree_structure.net_id].net_args
    check_extra_args_dict(extra_args)
    node_elem = net_creator[tree_structure.net_id].check_args_func(
        ExtraArgsNet(arguments=extra_args)
    )
    add_name: str = TTSubStrPre.ROOT.value if parent is None else TTSubStrPre.NODE.value
    current_node = ANNTreeStructureTrain(
        f"{add_name}{tree_structure.net_id}_{child_id}",
        f"{net_creator[tree_structure.net_id].dict_id}",
        parent, node_elem
    )
    list_of_children = tuple(
        _rec_tree_creation(current_node, child_node, net_creator, net_def, child_id)
        for child_id, child_node in enumerate(tree_structure.children)
    )
    current_node.children = list_of_children
    return current_node


def _create_train_tree(net_creator: Dict[str, CheckCreateNetElem],
                       net_structure: NetElementStructure, /) -> ANNTreeStructureTrain:
    tree_root = net_structure.tree_root
    return _rec_tree_creation(None, tree_root, net_creator, net_structure.net_definitions, 0)


def factory_train_structure(data_container: JsonDictCon, sync_out: SyncStdoutInterface,
                            config_container_net: Dict[str, NetDictLibraryType],
                            config_container_con: Dict[str, NetConnectionDict], /) \
        -> Tuple[NeuralNetStructureTrainCon]:
    started_id = time.time()
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Starting creating the structure for training!",
        0.0,
        False
    )

    train_structure = parse_train_structure_dict(data_container.get_data().structure)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished analysing input dict!",
        25.0,
        False
    )

    check_net_definitions_completeness(train_structure)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished checking net definition for completeness!",
        50.0,
        False
    )

    root_id = train_structure.tree_root.net_id
    root_framework = train_structure.net_definitions[root_id].net_framework
    net_def_dict: Dict[str, CheckCreateNetElem] = factory_net_dict_train(
        train_structure.net_definitions, root_framework, sync_out, config_container_net
    )
    tree_data = _create_train_tree(net_def_dict, train_structure)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating ANNTreeStructureTrain structure!",
        75.0,
        False
    )
    check_connectivity(root_framework, tree_data, config_container_con)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating a NeuralNetStructureTrainCon container!",
        100.0,
        True
    )
    file_name = data_container.get_data().structure_id
    if not file_name:
        raise FactoryTrainStructureError("Give filename is empty!")
    erg: NeuralNetStructureTrainCon = NeuralNetStructureTrainCon()
    erg.set_data(ANNTreeStructureTrainWr(
        structure=tree_data,
        file_name=file_name
    ))
    tuple_erg = (erg,)
    return tuple_erg
