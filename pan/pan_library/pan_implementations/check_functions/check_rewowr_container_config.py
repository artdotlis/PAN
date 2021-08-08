# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Dict

from pan.pan_library.pan_rewowr.config_implementation.container_config import container_config
from pan.pan_library.pan_rewowr.config_implementation.re_wr_config import re_wr_config
from pan.pan_library.pan_rewowr.config_implementation.work_config import work_config
from pan.pan_library.pan_implementations.errors.custom_errors import CheckReWoWrContainerConfigError
from pan.public.functions.check_config_container import ConfigContainer
from rewowr.public.interfaces.container_interface_config import \
    get_rewowr_container_interface_config
from rewowr.public.interfaces.re_wr_interface_config import get_rewowr_re_wr_interface_config
from rewowr.public.interfaces.work_interface_config import get_rewowr_work_interface_config


def _compare_dict(local_dict: Dict, rewowr_dict: Dict, /) -> None:
    for key_name in local_dict.keys():
        if key_name in rewowr_dict:
            raise CheckReWoWrContainerConfigError(
                f"The key {key_name} was found in the ReWoWr dictionary!"
            )


def check_rewowr_container_config(config: ConfigContainer, /) -> None:
    _compare_dict(
        work_config(config.net_container, config.connection_container),
        get_rewowr_work_interface_config()
    )
    _compare_dict(re_wr_config(config.plotter), get_rewowr_re_wr_interface_config())
    _compare_dict(
        container_config().container_dict, get_rewowr_container_interface_config().container_dict
    )
