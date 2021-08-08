# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import final

from rewowr.public.errors.custom_errors import KnownError


class KnownErrorPanInterfaces(KnownError):
    pass


@final
class SavableNetError(KnownErrorPanInterfaces):
    pass


@final
class ANNTreeStructureTrainError(KnownErrorPanInterfaces):
    pass
