# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import time
from typing import Tuple, Dict, List, Final

from pan.pan_library.pan_interfaces.gen_constants.file_names import TTSubStrPre
from pan.public.interfaces.net_connection import NetConnectionDict
from pan.public.interfaces.config_constants import CheckCreateNetElem, \
    ExtraArgsNet, NetDictLibraryType
from pan.pan_library.pan_rewowr.container.dict_json import JsonDictCon
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetStructureTestCon
from pan.pan_library.pan_implementations.check_functions.check_train_test_structure_dict import \
    parse_test_structure_dict
from pan.pan_library.pan_implementations.factories.factory_net_interface import \
    factory_net_dict_test
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNStructureTest, \
    ANNStructureTestWr
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import NetDef
from pan.pan_library.pan_implementations.errors.custom_errors import FactoryTestStructureError
from rewowr.public.functions.check_extra_args_dict import check_extra_args_dict
from rewowr.public.functions.syncout_dep_functions import logger_print_con
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface

_MODULE_NAME: Final[str] = "factory_test_structure"


def _create_test_nets(net_creator: Dict[str, CheckCreateNetElem],
                      net_def: Dict[str, NetDef], /) -> List[ANNStructureTest]:
    erg_list = []
    for def_key, def_elem in net_def.items():
        extra_args = def_elem.net_args
        check_extra_args_dict(extra_args)
        node_elem = net_creator[def_key].check_args_func(
            ExtraArgsNet(arguments=extra_args)
        )
        erg_list.append(ANNStructureTest(
            f"{TTSubStrPre.TEST.value}{def_key}", f"{net_creator[def_key].dict_id}", node_elem
        ))

    return erg_list


def _create_test_cont(test_net: ANNStructureTest, file_name: str, /) -> NeuralNetStructureTestCon:
    if not file_name:
        raise FactoryTestStructureError("Give filename is empty!")
    erg: NeuralNetStructureTestCon = NeuralNetStructureTestCon()
    erg.set_data(ANNStructureTestWr(
        structure=test_net,
        file_name=file_name
    ))
    return erg


def factory_test_structure(data_container: JsonDictCon, sync_out: SyncStdoutInterface,
                           config_container_net: Dict[str, NetDictLibraryType],
                           _: Dict[str, NetConnectionDict], /) \
        -> Tuple[NeuralNetStructureTestCon, ...]:
    started_id = time.time()
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Starting creating the structure for testing!",
        0.0,
        False
    )

    test_structure = parse_test_structure_dict(data_container.get_data().structure)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished analysing input dict!",
        33.3,
        False
    )

    net_def_dict: Dict[str, CheckCreateNetElem] = factory_net_dict_test(
        test_structure.net_definitions, sync_out, config_container_net
    )
    test_nets = _create_test_nets(net_def_dict, test_structure.net_definitions)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating ANNStructureTest list!",
        66.6,
        False
    )
    tuple_erg = tuple(
        _create_test_cont(net_elem, data_container.get_data().structure_id)
        for net_elem in test_nets
    )
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating NeuralNetStructureTestCon containers!",
        100.0,
        True
    )
    return tuple_erg
