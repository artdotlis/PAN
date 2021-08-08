# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import final

from rewowr.public.errors.custom_errors import KnownError


class KnownErrorPanReWoWr(KnownError):
    pass


@final
class JsonDictConError(KnownErrorPanReWoWr):
    pass


@final
class CheckWriterNetTrainTestError(KnownErrorPanReWoWr):
    pass


@final
class ReaderJsonError(KnownErrorPanReWoWr):
    pass


@final
class CheckReaderJsonError(KnownErrorPanReWoWr):
    pass


@final
class WorkerCheckNetError(KnownErrorPanReWoWr):
    pass


@final
class WriterNetTrainTestError(KnownErrorPanReWoWr):
    pass


@final
class WorkerTestNetError(KnownErrorPanReWoWr):
    pass


@final
class WorkerTrainNetError(KnownErrorPanReWoWr):
    pass


@final
class WorkerCreateNetStructureError(KnownErrorPanReWoWr):
    pass


@final
class CheckWorkerCreateNetStructureError(KnownErrorPanReWoWr):
    pass


@final
class CheckWorkerCheckNetError(KnownErrorPanReWoWr):
    pass
