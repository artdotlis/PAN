# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import os

from pathlib import Path
from typing import Dict

from pan.public.functions.check_config_container import ConfigContainer
from pan.pan_library.pan_rewowr.config_implementation.container_config import container_config
from pan.pan_library.pan_rewowr.config_implementation.re_wr_config import re_wr_config
from pan.pan_library.pan_rewowr.config_implementation.work_config import work_config
from pan.pan_library.pan_implementations.check_functions.check_rewowr_container_config import \
    check_rewowr_container_config
from rewowr.public.constants.check_constants import FactoryWorkerArgs
from rewowr.public.constants.config_constants import ReWrWoInterfaceDict
from rewowr.public.errors.custom_errors import KnownError
from rewowr.public.functions.factory_worker_structure import factory_worker
from rewowr.public.functions.path_functions import check_dir_path, create_dirs_rec


def ann_builder(config_container: ConfigContainer,
                directory_logs: Path, conf_file: Dict, /) -> None:
    try:
        check_rewowr_container_config(config_container)

        directory_log = check_dir_path(f"{str(directory_logs)}{os.sep}log")
        create_dirs_rec(directory_log)

        _ = list(factory_worker(
            FactoryWorkerArgs(
                conf_file=conf_file,
                working_dir_log=directory_log,
                step_name="BuildingANN"
            ),
            ReWrWoInterfaceDict(
                work_dict=work_config(
                    config_container.net_container, config_container.connection_container
                ),
                re_wr_dict=re_wr_config(config_container.plotter)
            ),
            container_config()
        ))
    except KnownError as known_error:
        print(f"This error should only appear if your implementations is faulty!\n{known_error}")
    except Exception as unknown:
        print("An implementation error occurred!")
        raise unknown
