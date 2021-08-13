# -*- coding: utf-8 -*-
"""This module provides a procedure to read JSON files.

.. moduleauthor:: Artur Lissin
"""
import multiprocessing
from multiprocessing import current_process, synchronize

import json
import os
import random
import time

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Type, TypeVar, Callable, Union, final, Final

from pan.pan_library.pan_rewowr.errors.custom_errors import ReaderJsonError
from pan.pan_library.pan_interfaces.gen_constants.file_names import TTSubStrPre, CONF_NAME_REGEX, \
    CONF_NAME_PATTERN
from pan.pan_library.pan_rewowr.container.dict_json import JsonDictCon, ContValue

from rewowr.public.extra_types.custom_types import CustomProcessValueWrapper
from rewowr.public.constants.rewowr_worker_constants import DataContainer, PoolLoopCont, \
    ContainerTypes
from rewowr.public.functions.decorator_functions import remove_all_args
from rewowr.public.functions.path_functions import check_absolute_path, get_file_path_pattern, \
    create_dirs_rec
from rewowr.public.container.container_no_connection import NoConnectionContainer
from rewowr.public.interfaces.re_wr_interface import ReWrInterface


def _check_lock(file_dir: Path, /) -> bool:
    locks = list(file_dir.glob("*.lock"))
    if not locks:
        pid = current_process().pid
        if isinstance(pid, int):
            lock_name = file_dir.joinpath(f"{pid}.lock")
            lock_name.touch()
            all_locks = list(file_dir.glob("*.lock"))
            if len(all_locks) > 1:
                lock_name.unlink()
                time.sleep(random.random())
                _check_lock(file_dir)
            return True
    return False


_AppendType: Final = TypeVar('_AppendType', List, Dict)


def _append_to_list(erg_list: List[JsonDictCon], id_num: int,
                    loaded_dict: _AppendType, loaded_dict_name: str, /) -> None:
    if isinstance(loaded_dict, dict):
        empty_venn: JsonDictCon = JsonDictCon()
        empty_venn.set_data(ContValue(
            structure_id=f"{loaded_dict_name}_num_{id_num}",
            structure=loaded_dict
        ))
        erg_list.append(empty_venn)


@final
@dataclass
class _ReadMethodCon:
    file_dir: str
    erg_list: List[JsonDictCon]
    json_containers: List[Tuple[str, Union[Dict, List]]]


def _fix_conf_name(name: str, /) -> str:
    name_search = CONF_NAME_PATTERN.search(name)
    if name_search is None:
        raise ReaderJsonError("Could not find the given pattern in str!")
    return name_search.group(1)


def _read_method(process_lock: synchronize.RLock, running: CustomProcessValueWrapper[int],
                 directory_in: Tuple[Path, List[str]], /) \
        -> Callable[[], Tuple[JsonDictCon, ...]]:
    def read_method_inner() -> Tuple[JsonDictCon, ...]:
        erg_value: Tuple[JsonDictCon, ...] = tuple()
        receivable = -1
        with process_lock:
            if running.value > 0:
                running.value -= 1
                receivable = running.value
        if receivable >= 0:
            cont = _ReadMethodCon(
                file_dir=str(directory_in[0].joinpath(directory_in[1][receivable])),
                erg_list=[],
                json_containers=[]
            )
            if _check_lock(Path(cont.file_dir)):
                for file_name in Path(cont.file_dir).glob(CONF_NAME_REGEX):
                    json_file = check_absolute_path(str(file_name.absolute()))
                    dir_fi_path = get_file_path_pattern().search(str(json_file))
                    if dir_fi_path is not None and dir_fi_path.group(1) is not None:
                        with json_file.open('r') as json_fh:
                            cont.json_containers.append(
                                (json_file.with_suffix('').name, json.load(json_fh))
                            )

            for name, loaded_dict in cont.json_containers:
                if isinstance(loaded_dict, list):
                    for list_index, list_dict in enumerate(loaded_dict):
                        _append_to_list(
                            cont.erg_list, list_index, list_dict,
                            f"{TTSubStrPre.FOREST.value}{directory_in[1][receivable]}#"
                            + f"{_fix_conf_name(name)}"
                        )
                else:
                    _append_to_list(
                        cont.erg_list, 0, loaded_dict,
                        f"{TTSubStrPre.FOREST.value}{directory_in[1][receivable]}#"
                        + f"{_fix_conf_name(name)}"
                    )
            erg_value = tuple(cont.erg_list)

        return erg_value

    return read_method_inner


def _check_run(process_lock: synchronize.RLock,
               running: CustomProcessValueWrapper[int], /) -> Callable[[], bool]:
    def check_run_inner() -> bool:
        with process_lock:
            return running.value > 0

    return check_run_inner


def _rm_files_rec(dir_name: Path, /) -> None:
    for file in dir_name.glob("*.lock"):
        Path(file).unlink()
    try:
        for next_dir in next(os.walk(str(dir_name)))[1]:
            _rm_files_rec(dir_name.joinpath(next_dir))
    except StopIteration:
        pass


def _rm_lock_file(process_lock: synchronize.RLock,
                  json_glob_lock: Tuple[Path, Path],
                  directory_in: Tuple[Path, List[str]], /) -> Callable[[], None]:
    def rm_lock_file_inner() -> None:
        with process_lock:
            if json_glob_lock[1].exists():
                json_glob_lock[1].unlink()
                dir_locks = list(json_glob_lock[0].glob("*.lock"))
                if not dir_locks:
                    json_glob_lock[0].rmdir()
                    _rm_files_rec(directory_in[0])
    return rm_lock_file_inner


@final
class ReaderJson(ReWrInterface):
    # Note: ReaderJson must be not-concurrently initialised
    def __init__(self, ctx: multiprocessing.context.SpawnContext, directory_in: Path, /) -> None:
        super().__init__()
        self.__directory_in: Tuple[Path, List[str]] = (
            directory_in, next(os.walk(str(directory_in)))[1]
        )
        json_lock_dir: Path = directory_in.joinpath("json_file_locks")
        create_dirs_rec(json_lock_dir)
        dir_locks = list(json_lock_dir.glob("*.lock"))
        self.__json_glob_lock = (
            json_lock_dir,
            json_lock_dir.joinpath(f"{len(dir_locks) + 1}.lock")
        )
        self.__json_glob_lock[1].touch()
        self.__process_lock = ctx.RLock()
        self.__running: CustomProcessValueWrapper[int] = CustomProcessValueWrapper[int](
            ctx, len(self.__directory_in[1])
        )

    def get_connection_read(self) -> Tuple[Type[JsonDictCon]]:
        erg = (JsonDictCon,)
        return erg

    def get_connection_write(self) -> Tuple[Type[NoConnectionContainer]]:
        erg = (NoConnectionContainer,)
        return erg

    def get_blockable(self) -> bool:
        return False

    def wr_on_close(self) -> None:
        raise NotImplementedError(f"{ReaderJson.__name__} should never be a provider!")

    def on_error(self) -> None:
        _rm_lock_file(self.__process_lock, self.__json_glob_lock, self.__directory_in)()

    async def read(self, container_types: ContainerTypes,
                   pool_loop: PoolLoopCont, /) -> Tuple[Tuple[JsonDictCon, ...]]:
        erg_value: Tuple[JsonDictCon, ...] = await pool_loop.loop.run_in_executor(
            pool_loop.th_exec, remove_all_args(_read_method(
                self.__process_lock, self.__running, self.__directory_in
            ))
        )
        erg_tuple = (erg_value,)
        return erg_tuple

    async def write(self, data_container: DataContainer, container_types: ContainerTypes,
                    pool_loop: PoolLoopCont, /) -> bool:
        raise NotImplementedError(f"{ReaderJson.__name__} should never be written to!")

    async def running(self, pool_loop: PoolLoopCont, provider_cnt: int, /) -> bool:
        running = await pool_loop.loop.run_in_executor(
            pool_loop.th_exec, remove_all_args(_check_run(
                self.__process_lock, self.__running
            ))
        )
        if not running:
            await pool_loop.loop.run_in_executor(
                pool_loop.th_exec, remove_all_args(_rm_lock_file(
                    self.__process_lock, self.__json_glob_lock, self.__directory_in
                ))
            )

        return running
