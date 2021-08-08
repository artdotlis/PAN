# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import multiprocessing

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, final

from pan.pan_library.pan_interfaces.gen_constants.file_names import TTSubStrPre
from pan.public.interfaces.net_plotter_interface import NetXYPlotter
from pan.pan_library.pan_rewowr.re_wr_implementation.reader_json import ReaderJson
from pan.pan_library.pan_rewowr.errors.custom_errors import CheckWriterNetTrainTestError, \
    CheckReaderJsonError
from pan.pan_library.pan_rewowr.re_wr_implementation.writer_net_plotter import WriterNetTrainTest
from rewowr.public.functions.check_re_wr_wo_arguments import check_param_names, check_parse_type
from rewowr.public.functions.path_functions import check_dir_path
from rewowr.public.interfaces.re_wr_interface import ReWrInterface
from rewowr.public.interfaces.rewrwo_checker_interface import ReWrWoDictElem, ExtraArgsReWrWo, \
    ContainerDict


def _path_str(arg_path: str, /) -> Path:
    return Path(arg_path)


@final
class _CheckWriterNetTrainTest(ReWrWoDictElem[ReWrInterface]):
    def __init__(self, plotter: NetXYPlotter, /) -> None:
        super().__init__()
        self.__plotter: NetXYPlotter = plotter

    def check_args_func(self, ctx: multiprocessing.context.SpawnContext,
                        cont_dict: ContainerDict,
                        extra_args: ExtraArgsReWrWo, /) -> WriterNetTrainTest:
        param_name = ["working_path", "dump_size", "keep_dump"]
        check_param_names(extra_args.arguments, param_name)
        working_path: Path = check_dir_path(
            f"{check_parse_type(extra_args.arguments[param_name[0]], _path_str)}"
            + f"{os.sep}{TTSubStrPre.OUTPUT.value}"
            + f"{datetime.now().strftime('%d_%m_%Y__%H_%M_%S')}"
        )
        if working_path.exists():
            raise CheckWriterNetTrainTestError(
                f"The param working_path {working_path} already exists!"
            )
        dump_max = 0
        if extra_args.arguments[param_name[1]] != 'F':
            puffer = check_parse_type(extra_args.arguments[param_name[1]], int)
            dump_max = puffer if puffer > dump_max else dump_max

        keep_dump = False
        if dump_max > 0 and extra_args.arguments[param_name[2]] == 'T':
            keep_dump = True

        return WriterNetTrainTest(working_path, dump_max, keep_dump, self.__plotter)

    def check_numbers(self, worker_in_cnt: int, worker_out_cnt: int, workable_cnt: int, /) \
            -> Tuple[bool, str]:
        if workable_cnt != 1:
            return False, "Workable_cnt can not be smaller or higher than 1!"
        if worker_in_cnt < 0:
            return False, "Worker_in_cnt can not be smaller than 0!"
        if worker_out_cnt < 1:
            return False, "Worker_out_cnt should be at least 1!"
        return True, ""


@final
class _CheckReaderJson(ReWrWoDictElem[ReWrInterface]):

    def check_numbers(self, worker_in_cnt: int, worker_out_cnt: int, workable_cnt: int, /) \
            -> Tuple[bool, str]:
        if workable_cnt != 1:
            return False, "Workable_cnt should be 1!"
        if worker_in_cnt != 1:
            return False, "Worker_in_cnt should be 1!"
        if worker_out_cnt < 0:
            return False, "Worker_out_cnt can not be smaller than 0!"
        return True, ""

    def check_args_func(self, ctx: multiprocessing.context.SpawnContext,
                        cont_dict: ContainerDict, extra_args: ExtraArgsReWrWo, /) -> ReaderJson:
        param_name = "directory_in"
        check_param_names(extra_args.arguments, [param_name])
        directory_in: Path = check_parse_type(extra_args.arguments[param_name], _path_str)
        if not (directory_in.is_absolute() and directory_in.is_dir()):
            raise CheckReaderJsonError(
                f"The param working_path got {directory_in} [an absolute path to a directory]!"
            )
        return ReaderJson(ctx, directory_in)


def re_wr_config(plotter: NetXYPlotter, /) -> Dict[str, ReWrWoDictElem[ReWrInterface]]:
    local_re_wr_dict: Dict[str, ReWrWoDictElem[ReWrInterface]] = {
        "WriterNetTrainTest": _CheckWriterNetTrainTest(plotter),
        "ReaderJson": _CheckReaderJson()
    }
    return local_re_wr_dict
