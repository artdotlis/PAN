# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import os
from pathlib import Path
from typing import Dict, Tuple

from pan.public.constants.net_tree_id_constants import ANNTreeIdType, ann_tree_id_short_file_name
from pan.public.constants.train_net_stats_constants import \
    TrainNNPlotterStatDictSeriesType, check_info_consistency
from pan.public.interfaces.net_plotter_interface import NetXYPlotter
from pan.pan_library.pan_implementations.errors.custom_errors import CheckPlotWriteError

from rewowr.public.functions.path_functions import create_dirs_rec


def _filter_data(data: Dict[str, TrainNNPlotterStatDictSeriesType],
                 filter_d: Dict[str, bool], /) -> Dict[str, TrainNNPlotterStatDictSeriesType]:
    return {
        pl_key: pl_data
        for pl_key, pl_data in data.items() if filter_d.get(pl_key, False)
    }


def _check_data_info(data: Dict[str, TrainNNPlotterStatDictSeriesType], /) \
        -> Tuple[Dict[str, bool], Dict[str, bool]]:
    info_last = None
    plot_dict: Dict[str, bool] = {}
    write_dict: Dict[str, bool] = {}
    for train_key, train_el in data.items():
        plot_d = None
        write_d = None
        for info_p in train_el.data_elem_dict.values():
            if plot_d is None:
                plot_d = info_p.plot_data
            elif plot_d != info_p.plot_data:
                raise CheckPlotWriteError("Different plot settings detected!")
            if write_d is None:
                write_d = info_p.write_data
            elif write_d != info_p.write_data:
                raise CheckPlotWriteError("Different write settings detected!")
            if info_last is None:
                info_last = info_p.info
            else:
                check_info_consistency(info_last, info_p.info)
        plot_dict[train_key] = False if plot_d is None else plot_d
        write_dict[train_key] = False if write_d is None else write_d
    return plot_dict, write_dict


def net_xy_plotter(data: Dict[str, TrainNNPlotterStatDictSeriesType],
                   id_file: ANNTreeIdType, working_path: Path,
                   hyper_params: str, plotter: NetXYPlotter, /) -> None:
    dir_name = f"{str(working_path)}{os.sep}{id_file.file_name}{os.sep}"
    dir_name += f"{os.sep.join(id_file.id_list)}"
    create_dirs_rec(Path(dir_name))
    name = id_file.id_merged_str
    if len(name) > 100:
        name = ann_tree_id_short_file_name(name)
    file_name = f"{dir_name}{os.sep}{name}"
    plot_dict, write_dict = _check_data_info(data)
    plottable_data = plotter.create_plottable_data(_filter_data(data, plot_dict))
    writable_data = plotter.create_writable_data(_filter_data(data, write_dict))
    plotter.plot_data(file_name, plottable_data)
    plotter.write_data(file_name, writable_data, hyper_params)


def net_xy_plotter_dump(data: Dict[str, TrainNNPlotterStatDictSeriesType], file_name: str,
                        dump_folder: Path, plotter: NetXYPlotter, /) -> None:
    name = file_name
    if len(name) > 100:
        name = ann_tree_id_short_file_name(name)
    create_dirs_rec(Path(dump_folder))
    file_name = f"{dump_folder}{os.sep}{name}"
    plot_dict, write_dict = _check_data_info(data)
    pl_data = plotter.create_plottable_dump_data(_filter_data(data, plot_dict))
    wr_data = plotter.create_writable_dump_data(_filter_data(data, write_dict))
    plotter.dump_plot(file_name, pl_data)
    plotter.dump_data(file_name, wr_data, "")
