# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from enum import Enum
from typing import Dict, List, Type, final
from dataclasses import dataclass


@final
@dataclass
class _EnumIndexType:
    index: str
    type: Type


@final
@dataclass
class NetDef:
    net_framework: str
    net_interface: str
    net_args: Dict[str, str]


@final
class NetDefKeys(Enum):
    net_framework = _EnumIndexType("NetFramework", str)
    net_interface = _EnumIndexType("NetInterface", str)
    net_args = _EnumIndexType("NetArgs", dict)


@final
@dataclass
class NetTreeStructure:
    net_id: str
    children: List['NetTreeStructure']


@final
class NetTreeStructureKeys(Enum):
    net_id = _EnumIndexType("NetID", str)
    children = _EnumIndexType("Children", list)


@final
@dataclass
class NetElementStructure:
    net_definitions: Dict[str, NetDef]
    tree_root: NetTreeStructure


@final
class NetElementStructureKeys(Enum):
    net_definitions = _EnumIndexType("NetDef", dict)
    tree_root = _EnumIndexType("Root", dict)


@final
@dataclass
class NetElemStructureTest:
    net_definitions: Dict[str, NetDef]


@final
class NetElemStructureTestKeys(Enum):
    net_definitions = _EnumIndexType("NetDef", dict)
