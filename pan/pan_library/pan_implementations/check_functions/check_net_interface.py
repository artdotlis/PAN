# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Dict

from pan.pan_library.pan_implementations.errors.custom_errors import CheckNetInterfaceError
from pan.pan_library.pan_interfaces.gen_constants.check_constants_train_test import NetDef
from pan.public.interfaces.config_constants import CheckCreateNetElem, NetDictLibraryType


def create_net_interface_check_dict(net_def: Dict[str, NetDef],
                                    config_con_net: Dict[str, NetDictLibraryType], /) \
        -> Dict[str, CheckCreateNetElem]:
    erg_dict = {}
    for key_id, dict_elem in net_def.items():
        if dict_elem.net_framework not in config_con_net:
            raise CheckNetInterfaceError(
                f"The framework {dict_elem.net_framework} from net {key_id} could not be found!"
            )
        frame_work_dict = config_con_net[dict_elem.net_framework]
        if dict_elem.net_interface not in frame_work_dict.net_dict:
            raise CheckNetInterfaceError(
                f"The interface {dict_elem.net_interface} from net {key_id} could not be found!"
            )
        erg_dict[key_id] = frame_work_dict.net_dict[dict_elem.net_interface]

    return erg_dict
