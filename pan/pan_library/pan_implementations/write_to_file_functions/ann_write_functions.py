# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import os
from pathlib import Path

from pan.public.constants.test_net_stats_constants import \
    TestNNStatsElementType
from pan.pan_library.pan_interfaces.gen_constants.net_savable_constants import SavableNetType
from pan.public.constants.net_tree_id_constants import ann_tree_id_short_file_name
from rewowr.public.functions.path_functions import create_dirs_rec


def net_test_writer(data_cont: TestNNStatsElementType, working_path: Path, /) -> None:
    dir_name = f"{str(working_path)}{os.sep}{data_cont.id_file.file_name}{os.sep}"
    dir_name += f"{os.sep.join(data_cont.id_file.id_list)}"
    create_dirs_rec(Path(dir_name))
    name = data_cont.id_file.id_merged_str
    if len(name) > 100:
        name = ann_tree_id_short_file_name(name)
    file_name = Path(f"{dir_name}{os.sep}{name}_test.{data_cont.file_end}")
    with file_name.open('a') as data_handler:
        data_to_write = "\n".join(data_cont.data)
        if data_to_write:
            data_to_write += "\n"
        data_handler.write(data_to_write)


def net_save_to_file(net_to_save: SavableNetType, working_path: Path, /) -> None:
    dir_name = f"{str(working_path)}{os.sep}{net_to_save.id_file.file_name}{os.sep}"
    dir_name += f"{os.sep.join(net_to_save.id_file.id_list)}"
    create_dirs_rec(Path(dir_name))
    name = net_to_save.id_file.id_merged_str
    if len(name) > 100:
        name = ann_tree_id_short_file_name(name)
    file_name = Path(f"{dir_name}{os.sep}{name}_saved.ann")
    if file_name.exists() and file_name.is_file():
        file_name.unlink()
    with file_name.open('wb') as data_handler:
        data_handler.write(net_to_save.ann)
