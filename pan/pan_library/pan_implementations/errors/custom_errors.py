# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import final

from rewowr.public.errors.custom_errors import KnownError


class KnownErrorPanImplementations(KnownError):
    pass


@final
class CheckNetConnectivityError(KnownErrorPanImplementations):
    pass


@final
class CheckTrainStructureError(KnownErrorPanImplementations):
    pass


@final
class CheckReWoWrContainerConfigError(KnownErrorPanImplementations):
    pass


@final
class CheckNetDefCompletenessError(KnownErrorPanImplementations):
    pass


@final
class CheckNetInterfaceError(KnownErrorPanImplementations):
    pass


@final
class CheckPlotWriteError(KnownErrorPanImplementations):
    pass


@final
class FactoryTestStructureError(KnownErrorPanImplementations):
    pass


@final
class FactoryTrainStructureError(KnownErrorPanImplementations):
    pass
