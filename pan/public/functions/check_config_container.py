# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import TypeVar, Dict, final, Final
from dataclasses import dataclass

from pan.public.interfaces.config_constants import NetDictLibraryType, \
    CheckCreateNetElem
from pan.public.interfaces.net_connection import NetConnectionDict, \
    NetConnectionWr
from pan.public.interfaces.net_plotter_interface import NetXYPlotter
from pan.public.errors.custom_errors import CheckConfigContainerError

_CheckType: Final = TypeVar('_CheckType', NetDictLibraryType, NetConnectionDict)


def _check_framework(container_elem: _CheckType, dict_key: str, /) -> None:
    if not dict_key:
        raise CheckConfigContainerError("Framework is an empty string!")
    if dict_key != container_elem.framework:
        raise CheckConfigContainerError(
            f"Expected framework {dict_key} got {container_elem.framework}"
        )


_CheckDictType: Final = TypeVar('_CheckDictType', NetConnectionWr, CheckCreateNetElem)


def _check_dict_id(framework: str, dict_key: str, cont: _CheckDictType, /) -> None:
    if not dict_key:
        raise CheckConfigContainerError("NetID is an empty string!")
    if dict_key != cont.dict_id:
        raise CheckConfigContainerError(
            f"Expected dict_id {dict_key} got {cont.dict_id}"
        )
    if framework != cont.framework:
        raise CheckConfigContainerError(
            f"Expected framework {framework} got {cont.framework}"
        )


@final
@dataclass
class ConfigContainer:
    # The key in both dicts represents the framework name
    net_container: Dict[str, NetDictLibraryType]
    connection_container: Dict[str, NetConnectionDict]
    plotter: NetXYPlotter


def check_config_container(container: ConfigContainer, /) -> None:
    for dict_key, elem_con in container.connection_container.items():
        _check_framework(elem_con, dict_key)
        for inter_key, inter_val_con in elem_con.con_dict.items():
            _check_dict_id(dict_key, inter_key, inter_val_con)
    for dict_key, elem_net in container.net_container.items():
        _check_framework(elem_net, dict_key)
        for inter_key, inter_val_net in elem_net.net_dict.items():
            _check_dict_id(dict_key, inter_key, inter_val_net)

    if not isinstance(container.plotter, NetXYPlotter):
        CheckConfigContainerError(
            f"Expected plotter to be {NetXYPlotter.__name__} got {type(container.plotter).__name__}"
        )
