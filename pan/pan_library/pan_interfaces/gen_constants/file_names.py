# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import re
from enum import Enum
from typing import final, Final, Pattern

CONF_NAME_REGEX: Final[str] = "*_net_conf.json"
CONF_NAME_PATTERN: Final[Pattern[str]] = re.compile(r'(.*)_net_conf')


@final
class TTSubStrPre(Enum):
    OUTPUT = "output_"
    FOREST = "forest_"
    ROOT = "root_"
    NODE = "node_"
    TEST = "test_"
