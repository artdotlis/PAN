# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import multiprocessing

import re
from typing import Dict, Pattern, Tuple, Type, Final, final

from pan.pan_library.pan_rewowr.work_implementation.worker_net_check import WorkerCheckNet
from pan.pan_library.pan_rewowr.work_implementation.worker_net_train_test import WorkerTrainNet, \
    WorkerTestNet
from pan.pan_library.pan_rewowr.work_implementation.worker_create_net_structure import \
    WorkerCreateNetStructure
from pan.pan_library.pan_rewowr.errors.custom_errors import CheckWorkerCreateNetStructureError, \
    CheckWorkerCheckNetError
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetStructureTestCon, \
    NeuralNetStructureTrainCon
from pan.public.interfaces.config_constants import NetDictLibraryType
from pan.public.interfaces.net_connection import NetConnectionDict
from rewowr.public.constants.config_constants import no_check_need_no_params
from rewowr.public.functions.check_container import check_container
from rewowr.public.functions.check_re_wr_wo_arguments import check_param_names, check_parse_type
from rewowr.public.interfaces.container_interface import ContainerInterface
from rewowr.public.interfaces.rewrwo_checker_interface import ReWrWoDictElem, ContainerDict, \
    ExtraArgsReWrWo
from rewowr.public.interfaces.work_interface import WorkInterface

_COMMA: Final[Pattern[str]] = re.compile(r',')


@final
class _CheckWorkerCreateNetStructure(ReWrWoDictElem[WorkInterface]):

    def __init__(self, config_container_net: Dict[str, NetDictLibraryType],
                 config_container_con: Dict[str, NetConnectionDict], /) -> None:
        super().__init__()
        self.__config_container_net = config_container_net
        self.__config_container_con = config_container_con

    def check_numbers(self, worker_in_cnt: int, worker_out_cnt: int,
                      workable_cnt: int, /) -> Tuple[bool, str]:
        if workable_cnt < 1:
            return False, "Workable_cnt can not be smaller than 1!"
        if worker_in_cnt < 0:
            return False, "Worker_in_cnt can not be smaller than 0!"
        if worker_out_cnt < 0:
            return False, "Worker_out_cnt can not be smaller than 0!"
        return True, ""

    def check_args_func(self, ctx: multiprocessing.context.SpawnContext,
                        cont_dict: ContainerDict,
                        extra_args: ExtraArgsReWrWo, /) -> WorkerCreateNetStructure:
        param_name = "container_proto"
        check_param_names(extra_args.arguments, [param_name])
        if not isinstance(extra_args.arguments[param_name], str):
            raise CheckWorkerCreateNetStructureError(f"Type of {param_name} must be str!")
        container_types_str = tuple(
            check_parse_type(extra_args.arguments[param_name], _COMMA.split)
        )
        container_proto = tuple(
            check_container(cont_type, cont_dict)
            for cont_type in container_types_str
        )
        if not (NeuralNetStructureTestCon in container_proto
                or NeuralNetStructureTrainCon in container_proto):
            raise CheckWorkerCreateNetStructureError(
                f"Worker accepts only NeuralNetStructureTestCon or NeuralNetStructureTrainCon!"
            )

        if len(container_proto) != 1:
            raise CheckWorkerCreateNetStructureError(
                "The worker WorkerCreateNetStructure accepts only one type!"
            )
        _switch: Dict[
            Type[ContainerInterface], WorkerCreateNetStructure
        ] = {
            NeuralNetStructureTrainCon: WorkerCreateNetStructure[NeuralNetStructureTrainCon](
                NeuralNetStructureTrainCon,
                self.__config_container_net, self.__config_container_con
            ),
            NeuralNetStructureTestCon: WorkerCreateNetStructure[NeuralNetStructureTestCon](
                NeuralNetStructureTestCon,
                self.__config_container_net, self.__config_container_con
            )
        }
        erg_worker = _switch.get(
            container_proto[0],
            WorkerCreateNetStructure[NeuralNetStructureTestCon](
                NeuralNetStructureTestCon,
                self.__config_container_net, self.__config_container_con
            )
        )
        return erg_worker


@final
class _CheckWorkerCheckNet(ReWrWoDictElem[WorkInterface]):

    def check_numbers(self, worker_in_cnt: int, worker_out_cnt: int,
                      workable_cnt: int, /) -> Tuple[bool, str]:
        if workable_cnt < 1:
            return False, "Workable_cnt can not be smaller than 1!"
        if worker_in_cnt < 0:
            return False, "Worker_in_cnt can not be smaller than 0!"
        if worker_out_cnt < 0:
            return False, "Worker_out_cnt can not be smaller than 0!"
        return True, ""

    def check_args_func(self, ctx: multiprocessing.context.SpawnContext,
                        cont_dict: ContainerDict,
                        extra_args: ExtraArgsReWrWo, /) -> WorkerCheckNet:
        param_name = "container_proto"
        check_param_names(extra_args.arguments, [param_name])
        if not isinstance(extra_args.arguments[param_name], str):
            raise CheckWorkerCheckNetError(f"Type of {param_name} must be str!")
        container_types_str = tuple(
            check_parse_type(extra_args.arguments[param_name], _COMMA.split)
        )
        if len(container_types_str) != 1:
            raise CheckWorkerCheckNetError(
                f"Expected one container type got {len(container_types_str)}!"
            )
        container_proto = check_container(container_types_str[0], cont_dict)
        if not issubclass(container_proto, (NeuralNetStructureTrainCon, NeuralNetStructureTestCon)):
            raise CheckWorkerCheckNetError(
                f"Expected {NeuralNetStructureTrainCon.__name__}"
                + f" or {NeuralNetStructureTestCon.__name__}"
                + f" got {container_proto.__name__}"
            )
        erg = (container_proto,)
        return WorkerCheckNet(erg)


def work_config(config_container_net: Dict[str, NetDictLibraryType],
                config_container_con: Dict[str, NetConnectionDict], /) \
        -> Dict[str, ReWrWoDictElem[WorkInterface]]:
    _local_wo_dict: Dict[str, ReWrWoDictElem[WorkInterface]] = {
        "WorkerCreateNetStructure": _CheckWorkerCreateNetStructure(
            config_container_net, config_container_con
        ),
        "WorkerTrainNet": no_check_need_no_params(WorkerTrainNet, 1, 0, 0),
        "WorkerTestNet": no_check_need_no_params(WorkerTestNet, 1, 0, 0),
        "WorkerCheckNet": _CheckWorkerCheckNet()
    }
    return _local_wo_dict
