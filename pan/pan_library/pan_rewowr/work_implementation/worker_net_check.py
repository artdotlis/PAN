# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Tuple, Type, Union, AsyncIterable, final, Final

from rewowr.public.constants.rewowr_worker_constants import DataContainer, WorkerTypeParam, \
    PoolLoopCont
from rewowr.public.container.empty_container import EmptyContainer
from rewowr.public.interfaces.container_interface import ContainerInterface
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface
from rewowr.public.interfaces.work_interface import WorkInterface

from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetStructureTrainCon, \
    NeuralNetStructureTestCon
from pan.pan_library.pan_rewowr.errors.custom_errors import WorkerCheckNetError
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNTreeStructureTrain

WorkerCheckTypes: Final = Tuple[Type[Union[NeuralNetStructureTestCon, NeuralNetStructureTrainCon]]]


def _rec_check(tree_node: ANNTreeStructureTrain, sync_out: SyncStdoutInterface, /) -> None:
    for child_node in tree_node.children:
        _rec_check(child_node, sync_out)

    tree_node.node_data.check_net(
        tuple(child.node_data for child in tree_node.children),
        sync_out
    )
    print(f"No child errors detected for {'/'.join(tree_node.net_tree_id)}")


async def _check_elem(data_elem: ContainerInterface, sync_out: SyncStdoutInterface, /) -> None:
    if isinstance(data_elem, NeuralNetStructureTrainCon):
        if data_elem.get_data().structure.parent is not None:
            raise WorkerCheckNetError("Received not root node!")
        _rec_check(data_elem.get_data().structure, sync_out)

    if isinstance(data_elem, NeuralNetStructureTestCon):
        data_elem.get_data().structure.node_data.check_net(tuple(), sync_out)

    if not isinstance(data_elem, (NeuralNetStructureTrainCon, NeuralNetStructureTestCon)):
        raise WorkerCheckNetError("Received wrong data type!")

    print(f"No root errors detected for {data_elem.get_data().structure.net_id}")


@final
class WorkerCheckNet(WorkInterface):

    def __init__(self, container_proto: WorkerCheckTypes, /) -> None:
        super().__init__()
        self.__container_proto: WorkerCheckTypes = container_proto

    # Can block event queue

    def get_connection_in(self) -> WorkerCheckTypes:
        return self.__container_proto

    def get_connection_out(self) -> Tuple[Type[EmptyContainer]]:
        erg = (EmptyContainer,)
        return erg

    def on_close(self, sync_out: SyncStdoutInterface, /) -> None:
        pass

    # Should not block event queue
    async def work(self, sync_out: SyncStdoutInterface, data_container: DataContainer,
                   container_types: WorkerTypeParam,
                   pool_loop: PoolLoopCont, /) -> AsyncIterable[DataContainer]:
        for tuple_index, tuple_elem in enumerate(data_container):
            if tuple_index >= 1 or tuple_index >= len(container_types.cont_in):
                raise WorkerCheckNetError("Wrong number container types received!")
            for data_elem in tuple_elem:
                await _check_elem(data_elem, sync_out)
            erg = ((EmptyContainer(),),)
            yield erg
