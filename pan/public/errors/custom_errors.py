# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import final

from rewowr.public.errors.custom_errors import KnownError


class KnownErrorPubPan(KnownError):
    pass


@final
class CheckConfigContainerError(KnownErrorPubPan):
    pass


@final
class ANNTreeIdError(KnownErrorPubPan):
    pass


@final
class TestNNStatsElementError(KnownErrorPubPan):
    pass


@final
class TrainNNStatsElementError(KnownErrorPubPan):
    pass


@final
class LoadingNetSavableError(KnownErrorPubPan):
    pass


@final
class NetConnectionWrError(KnownErrorPubPan):
    pass


@final
class PubNetInterfaceError(KnownErrorPubPan):
    pass
