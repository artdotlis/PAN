# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import List, NewType, Dict, final, Optional, Callable, Final
from dataclasses import dataclass

from pan.public.errors.custom_errors import TrainNNStatsElementError
from pan.public.constants.net_tree_id_constants import ANNTreeIdType


@final
@dataclass
class TrainNNStatsElemInfo:
    id_file: ANNTreeIdType
    name_series: str
    type_series: str
    name_sub_series: str
    type_sub_series: str
    x_label: str
    y_label: str
    title: str
    subtitle: str


@final
@dataclass
class _TrainNNStatsElement:
    info: TrainNNStatsElemInfo
    x_cords: List[float]
    y_cords: List[float]
    last: bool
    package_pos: int  # starts from 0 to N+
    dump_net: bool
    hyper_param: str
    plot_data: bool
    write_data: bool


@final
@dataclass
class TrainNNStatsElementFiller:
    last: bool
    dump: bool
    hyper_param: str
    plot_data: bool
    write_data: bool


TrainNNStatsElementType: Final = NewType('TrainNNStatsElementType', _TrainNNStatsElement)


TrainReturnFiller: Final = Callable[
    [TrainNNStatsElemInfo, List[float], List[float], TrainNNStatsElementFiller],
    TrainNNStatsElementType
]


def check_info_consistency(info_f: TrainNNStatsElemInfo, info: TrainNNStatsElemInfo, /) -> None:
    if info_f.id_file.id_merged_str != info.id_file.id_merged_str:
        raise TrainNNStatsElementError(
            f"ID: {info_f.id_file.id_merged_str} {info.id_file.id_merged_str}"
        )
    if info_f.x_label != info.x_label:
        raise TrainNNStatsElementError(f"Label x: {info_f.x_label} {info.x_label}")
    if info_f.y_label != info.y_label:
        raise TrainNNStatsElementError(f"Label y: {info_f.y_label} {info.y_label}")
    if info_f.type_series != info.type_series:
        raise TrainNNStatsElementError(f"Type: {info_f.type_series} {info.type_series}")
    if info_f.type_sub_series != info.type_sub_series:
        raise TrainNNStatsElementError(f"Subtype: {info_f.type_sub_series} {info.type_sub_series}")
    if info_f.title != info.title:
        raise TrainNNStatsElementError(f"Title: {info_f.title} {info.title}")
    if info_f.subtitle != info.subtitle:
        raise TrainNNStatsElementError(f"Subtitle: {info_f.subtitle} {info.subtitle}")


def create_train_net_stats_function() -> TrainReturnFiller:
    """
        Note:
                Here the _TrainNNStatsElement objects are not process sensitive! Thus their id must
                differ based on the process, so package_pos don't merge between processes.
    """
    index_cnt: int = 0
    last_local: bool = False
    info_last: Optional[str] = None

    def filler(info: TrainNNStatsElemInfo, x_cords: List[float], y_cords: List[float],
               extra_params: TrainNNStatsElementFiller) -> TrainNNStatsElementType:
        nonlocal last_local
        nonlocal index_cnt
        nonlocal info_last
        if info_last is None:
            info_last = info.id_file.id_merged_str
        elif info.id_file.id_merged_str != info_last:
            raise TrainNNStatsElementError(f"ID: {info_last} {info.id_file.id_merged_str}")
        if last_local:
            raise TrainNNStatsElementError(
                "The function create_train_net_stats_function was already closed!"
            )
        if not (y_cords and x_cords) and len(y_cords) != len(x_cords):
            raise TrainNNStatsElementError("Data can not be empty or have mismatched sizes!")
        erg = TrainNNStatsElementType(_TrainNNStatsElement(
            info=info,
            x_cords=x_cords,
            y_cords=y_cords,
            last=extra_params.last,
            package_pos=index_cnt,
            dump_net=extra_params.dump,
            hyper_param=extra_params.hyper_param,
            plot_data=extra_params.plot_data,
            write_data=extra_params.write_data
        ))
        index_cnt = index_cnt + 1
        last_local = extra_params.last
        return erg

    return filler


@final
@dataclass
class _TrainNNPlotterStatDictSeries:
    last_glob: bool
    last_index: int
    checked: bool
    data_elem_dict: Dict[int, TrainNNStatsElementType]


TrainNNPlotterStatDictSeriesType: Final = NewType(
    'TrainNNPlotterStatDictSeriesType', _TrainNNPlotterStatDictSeries
)


def create_ann_train_stats_blank() -> TrainNNPlotterStatDictSeriesType:
    return TrainNNPlotterStatDictSeriesType(_TrainNNPlotterStatDictSeries(
        last_glob=False,
        last_index=-1,
        checked=False,
        data_elem_dict={}
    ))
