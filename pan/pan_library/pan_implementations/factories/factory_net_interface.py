# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import time
from typing import Dict, Final

from pan.public.interfaces.config_constants import CheckCreateNetElem, NetDictLibraryType
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import NetDef
from pan.pan_library.pan_implementations.check_functions.check_net_interface import \
    create_net_interface_check_dict
from pan.pan_library.pan_implementations.check_functions.check_net_definitions_completness import \
    check_net_def_framework
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface
from rewowr.public.functions.syncout_dep_functions import logger_print_con

_MODULE_NAME: Final[str] = "factory_net_interface"


def factory_net_dict_train(net_def: Dict[str, NetDef], framework_name: str,
                           sync_out: SyncStdoutInterface,
                           config_container_net: Dict[str, NetDictLibraryType], /) \
        -> Dict[str, CheckCreateNetElem]:
    started_id = time.time()
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Starting to create the CheckCreateNetElem dict for training!",
        0.0,
        False
    )
    check_net_def_framework(framework_name, net_def)
    erg_dict = create_net_interface_check_dict(net_def, config_container_net)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating CheckCreateNetElem dict!",
        100.0,
        True
    )
    return erg_dict


def factory_net_dict_test(net_def: Dict[str, NetDef], sync_out: SyncStdoutInterface,
                          config_container_net: Dict[str, NetDictLibraryType], /) \
        -> Dict[str, CheckCreateNetElem]:
    started_id = time.time()
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Starting to create the CheckCreateNetElem dict for training!",
        0.0,
        False
    )
    erg_dict = create_net_interface_check_dict(net_def, config_container_net)
    logger_print_con(
        sync_out,
        f"{_MODULE_NAME}{started_id}",
        "Finished creating CheckCreateNetElem dict!",
        100.0,
        True
    )
    return erg_dict
