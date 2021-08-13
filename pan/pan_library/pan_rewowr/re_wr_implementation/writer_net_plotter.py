# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from dataclasses import dataclass
from typing import Dict, Type, Callable, Union, Tuple, Final, final
from pathlib import Path

from pan.public.interfaces.net_plotter_interface import NetXYPlotter
from pan.public.constants.train_net_stats_constants import \
    TrainNNPlotterStatDictSeriesType, TrainNNStatsElementType, create_ann_train_stats_blank
from pan.pan_library.pan_implementations.plot_functions.ann_plot_functions import net_xy_plotter, \
    net_xy_plotter_dump
from pan.pan_library.pan_implementations.write_to_file_functions.ann_write_functions import \
    net_test_writer, net_save_to_file
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetSaveCon, \
    TrainNNStatsCon, TestNNStatsCon
from pan.pan_library.pan_rewowr.errors.custom_errors import WriterNetTrainTestError
from rewowr.public.constants.rewowr_worker_constants import DataContainer, ContainerTypes, \
    PoolLoopCont
from rewowr.public.container.container_no_connection import NoConnectionContainer
from rewowr.public.functions.path_functions import remove_dir_rec, create_dirs_rec
from rewowr.public.interfaces.container_interface import ContainerInterface
from rewowr.public.interfaces.re_wr_interface import ReWrInterface

_DictNetStats: Final = Dict[str, Dict[str, TrainNNPlotterStatDictSeriesType]]
_DUMP_FOLDER_NAME: Final[str] = "dump_out"


def _check_if_complete(data_series: Dict[str, TrainNNPlotterStatDictSeriesType], /) -> bool:
    finished = True
    for data in data_series.values():
        if data.last_index < 1 and data.last_glob:
            raise WriterNetTrainTestError(f"The last index {data.last_index} is smaller than 1!")
        checked_ser = True
        if not data.checked and data.last_glob:
            for key_index in range(0, data.last_index + 1):
                if key_index not in data.data_elem_dict:
                    finished = False
                    checked_ser = False
            data.checked = checked_ser
        elif finished:
            finished = data.checked and data.last_glob

    return finished


def _save_nets(data: Tuple[ContainerInterface, ...], working_path: Path,
               _1: _DictNetStats, _2: bool, _3: NetXYPlotter, /) -> None:
    for data_elem in data:
        if not isinstance(data_elem, NeuralNetSaveCon):
            raise WriterNetTrainTestError(
                f"The given Type {type(data_elem).__name__} is not {NeuralNetSaveCon.__name__}!"
            )
        net_save_to_file(data_elem.get_data(), working_path)


def _save_test_data(data: Tuple[ContainerInterface, ...], working_path: Path,
                    _1: _DictNetStats, _2: bool, _3: NetXYPlotter, /) -> None:
    for data_elem in data:
        if not isinstance(data_elem, TestNNStatsCon):
            raise WriterNetTrainTestError(
                f"The given Type {type(data_elem).__name__} is not {TestNNStatsCon.__name__}!"
            )
        net_test_writer(data_elem.get_data(), working_path)


def _add_to_data(data: Tuple[ContainerInterface, ...], working_path: Path,
                 net_stats_dict: _DictNetStats, dump: bool, plotter: NetXYPlotter, /) -> None:
    for data_elem in data:
        if not isinstance(data_elem, TrainNNStatsCon):
            raise WriterNetTrainTestError(
                f"The given Type {type(data_elem).__name__} "
                + f"is not {TrainNNStatsCon.__name__}!"
            )
        elem_to_add: TrainNNStatsElementType = data_elem.get_data()
        if elem_to_add.write_data or elem_to_add.plot_data:
            dict_elem: TrainNNPlotterStatDictSeriesType = net_stats_dict.setdefault(
                elem_to_add.info.id_file.id_merged_str, {}
            ).setdefault(
                elem_to_add.info.name_series,
                create_ann_train_stats_blank()
            )
            if elem_to_add.package_pos in dict_elem.data_elem_dict:
                raise WriterNetTrainTestError(
                    f"The Key {elem_to_add.package_pos}"
                    + f" already exists for the id {elem_to_add.info.id_file.id_merged_str}"
                    + f" and the series {elem_to_add.info.name_series}"
                )
            dict_elem.data_elem_dict[elem_to_add.package_pos] = elem_to_add
            if elem_to_add.last:
                dict_elem.last_glob = True
                dict_elem.last_index = elem_to_add.package_pos

            if _check_if_complete(net_stats_dict[elem_to_add.info.id_file.id_merged_str]):
                net_xy_plotter(
                    net_stats_dict[elem_to_add.info.id_file.id_merged_str],
                    elem_to_add.info.id_file, working_path, elem_to_add.hyper_param,
                    plotter
                )
                del net_stats_dict[elem_to_add.info.id_file.id_merged_str]
    if dump:
        for key_index, plot_elem in net_stats_dict.items():
            net_xy_plotter_dump(
                plot_elem, key_index, working_path.joinpath(_DUMP_FOLDER_NAME), plotter
            )


@final
@dataclass
class _WriteThreadCon:
    cont_class: Type[ContainerInterface]
    data: Tuple[ContainerInterface, ...]
    net_stats_dict: _DictNetStats
    working_path: Path
    dump: bool
    net_plotter: NetXYPlotter


def _thread_write(args: _WriteThreadCon, /) -> Callable[[], None]:
    def _error(*_: Union[Tuple[ContainerInterface, ...], Path, _DictNetStats, bool, NetXYPlotter]) \
            -> None:
        raise WriterNetTrainTestError(f"The given Type {args.cont_class.__name__} is not defined!")

    switch: Dict[
        Type[ContainerInterface],
        Callable[[Tuple[ContainerInterface, ...], Path, _DictNetStats, bool, NetXYPlotter], None]
    ] = {
        TrainNNStatsCon: _add_to_data,
        NeuralNetSaveCon: _save_nets,
        TestNNStatsCon: _save_test_data
    }

    def thread_write_inner() -> None:
        switch.get(args.cont_class, _error)(
            args.data, args.working_path, args.net_stats_dict, args.dump, args.net_plotter
        )

    return thread_write_inner


_TypeCon: Final = Tuple[Type[TrainNNStatsCon], Type[NeuralNetSaveCon], Type[TestNNStatsCon]]


@final
class WriterNetTrainTest(ReWrInterface):

    def __init__(self, working_path: Path, dump_max: int, keep_dump: bool,
                 net_plotter: NetXYPlotter, /) -> None:
        super().__init__()
        self.__working_path: Path = working_path
        create_dirs_rec(self.__working_path)
        self.__net_stats_dict: _DictNetStats = {}  # IS NOT PROCESS SENSITIVE
        self.__dump_counter = 0  # IS NOT PROCESS SENSITIVE
        self.__dump_max = dump_max
        self.__keep_dump = keep_dump
        self.__net_plotter = net_plotter

    def get_connection_read(self) -> Tuple[Type[NoConnectionContainer]]:
        erg = (NoConnectionContainer,)
        return erg

    def get_connection_write(self) -> _TypeCon:
        erg = (TrainNNStatsCon, NeuralNetSaveCon, TestNNStatsCon)
        return erg

    def get_blockable(self) -> bool:
        return False

    def wr_on_close(self) -> None:
        if self.__net_stats_dict:
            print(
                f"Not all data was savable: {len(self.__net_stats_dict)}\n{self.__net_stats_dict}"
            )
        if not self.__keep_dump:
            remove_dir_rec(str(self.__working_path.joinpath(_DUMP_FOLDER_NAME)))

    def on_error(self) -> None:
        if not self.__keep_dump:
            remove_dir_rec(str(self.__working_path))

    async def read(self, container_types: ContainerTypes, pool_loop: PoolLoopCont, /) \
            -> DataContainer:
        raise NotImplementedError("Not implemented")

    async def write(self, data_container: DataContainer,
                    container_types: ContainerTypes, pool_loop: PoolLoopCont, /) -> bool:
        for cont_index, cont_data in enumerate(data_container):
            if self.__dump_max != 0:
                for tuple_elem in cont_data:
                    if isinstance(tuple_elem, TrainNNStatsCon):
                        self.__dump_counter += 1
            if cont_data:
                _thread_write(_WriteThreadCon(
                    cont_class=container_types[cont_index],
                    data=cont_data,
                    net_stats_dict=self.__net_stats_dict,
                    working_path=self.__working_path,
                    dump=self.__dump_max != 0 and self.__dump_counter >= self.__dump_max,
                    net_plotter=self.__net_plotter
                ))()
            if self.__dump_counter >= self.__dump_max:
                self.__dump_counter = 0

        return False

    async def running(self, pool_loop: PoolLoopCont, provider_cnt: int, /) -> bool:
        raise NotImplementedError("Not implemented")
