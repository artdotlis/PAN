# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import AsyncIterable, Tuple, Type, Dict, Callable, Union, TypeVar, Generic, Final, final

from pan.pan_library.pan_rewowr.container.dict_json import JsonDictCon
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetStructureTrainCon, \
    NeuralNetStructureTestCon
from pan.pan_library.pan_implementations.factories.factory_train_structure import \
    factory_train_structure
from pan.pan_library.pan_rewowr.errors.custom_errors import WorkerCreateNetStructureError
from pan.pan_library.pan_implementations.factories.factory_test_structure import \
    factory_test_structure
from pan.public.interfaces.config_constants import NetDictLibraryType
from pan.public.interfaces.net_connection import NetConnectionDict
from rewowr.public.constants.rewowr_worker_constants import DataContainer, PoolLoopCont, \
    WorkerTypeParam
from rewowr.public.interfaces.container_interface import ContainerInterface
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface
from rewowr.public.interfaces.work_interface import WorkInterface


_FunPT: Final = Union[
    JsonDictCon, SyncStdoutInterface, Dict[str, NetDictLibraryType], Dict[str, NetConnectionDict]
]
_CallableT: Final = Callable[
    [JsonDictCon, SyncStdoutInterface, Dict[str, NetDictLibraryType],
     Dict[str, NetConnectionDict]], Tuple[ContainerInterface, ...]
]


def _error_net_structure(*_: _FunPT) -> Tuple[ContainerInterface, ...]:
    raise WorkerCreateNetStructureError("Container type is not defined in this worker")


_SwitchContType: Final[Dict[Type[ContainerInterface], _CallableT]] = {
    NeuralNetStructureTestCon: factory_test_structure,
    NeuralNetStructureTrainCon: factory_train_structure
}

_NetStructureType: Final = TypeVar(
    '_NetStructureType',
    NeuralNetStructureTestCon, NeuralNetStructureTrainCon
)


@final
class WorkerCreateNetStructure(Generic[_NetStructureType], WorkInterface):

    def __init__(self, container_proto: Type[_NetStructureType],
                 config_container_net: Dict[str, NetDictLibraryType],
                 config_container_con: Dict[str, NetConnectionDict], /) -> None:
        super().__init__()
        self.__container_proto: Type[_NetStructureType] = container_proto
        self.__config_container_net = config_container_net
        self.__config_container_con = config_container_con

    # Can block event queue

    def get_connection_in(self) -> Tuple[Type[JsonDictCon]]:
        erg = (JsonDictCon,)
        return erg

    def get_connection_out(self) -> Tuple[Type[_NetStructureType]]:
        erg = (self.__container_proto,)
        return erg

    def on_close(self, sync_out: SyncStdoutInterface, /) -> None:
        pass

    async def work(self, sync_out: SyncStdoutInterface, data_container: DataContainer,
                   container_types: WorkerTypeParam, pool_loop: PoolLoopCont, /) \
            -> AsyncIterable[DataContainer]:
        if len(container_types.cont_out) != 1:
            raise WorkerCreateNetStructureError(
                f"Expected exactly one type got {len(container_types.cont_out)}"
            )

        for data_key, data_tuple in enumerate(data_container):
            if data_key >= len(container_types.cont_in):
                raise WorkerCreateNetStructureError("Wrong type!")
            for tuple_elem in data_tuple:
                if not isinstance(tuple_elem, JsonDictCon):
                    raise WorkerCreateNetStructureError("Wrong type!")
                erg = (_SwitchContType.get(
                    container_types.cont_out[0], _error_net_structure
                )(tuple_elem, sync_out, self.__config_container_net, self.__config_container_con),)
                yield erg
