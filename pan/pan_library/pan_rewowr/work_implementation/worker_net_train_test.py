# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import AsyncIterable, Tuple, Optional, Callable, Dict, Type, Union, Iterable, List, \
    final, Final

from dataclasses import dataclass

from pan.public.interfaces.pub_net_interface import NetSavable
from pan.public.constants.net_tree_id_constants import create_ann_tree_id, ANNTreeIdType
from pan.public.constants.test_net_stats_constants import \
    TestNNStatsElementType
from pan.public.constants.train_net_stats_constants import \
    TrainNNStatsElementType
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNTreeStructureTrain, \
    net_interface_save_net
from pan.pan_library.pan_rewowr.container.neural_net_container import TestNNStatsCon, \
    TrainNNStatsCon, NeuralNetSaveCon, NeuralNetStructureTrainCon, NeuralNetStructureTestCon
from pan.pan_library.pan_rewowr.errors.custom_errors import WorkerTrainNetError, WorkerTestNetError
from pan.pan_library.pan_interfaces.gen_constants.net_savable_constants import SavableNetType, \
    create_train_net_savable
from rewowr.public.constants.rewowr_worker_constants import WorkerTypeParam, PoolLoopCont, \
    DataContainer
from rewowr.public.interfaces.container_interface import ContainerInterface
from rewowr.public.interfaces.logger_interface import SyncStdoutInterface
from rewowr.public.interfaces.work_interface import WorkInterface

_OutTypeAlias: Final = Union[
    Optional[TestNNStatsElementType],
    Optional[TrainNNStatsElementType],
    Optional[SavableNetType]
]


@final
@dataclass
class _TrainerNetTypes:
    test: Optional[TestNNStatsElementType]
    train: Optional[TrainNNStatsElementType]
    save: Optional[SavableNetType]

    def get_erg(self, index: int, /) -> _OutTypeAlias:
        return [
            self.test,
            self.train,
            self.save
        ][index]


@final
@dataclass
class _TrainTestSave:
    train: bool = False
    test: bool = False
    save: bool = False


def _create_savable(savable_data: NetSavable, id_local: ANNTreeIdType,
                    save: bool, /) -> Optional[_TrainerNetTypes]:
    if not save:
        return None
    net_bytes = net_interface_save_net(savable_data)
    if net_bytes:
        return _TrainerNetTypes(None, None, create_train_net_savable(id_local, net_bytes))
    return None


def _rec_init(tt_list: List[bool], tree_node: ANNTreeStructureTrain,
              sync_out: SyncStdoutInterface, /) -> None:
    index = len(tt_list)
    tt_list.append(True)
    for child_node in tree_node.children:
        _rec_init(tt_list, child_node, sync_out)

    tt_list[index] = tree_node.node_data.init_net(
        tuple(child.node_data for child in tree_node.children),
        sync_out
    )


def _rec_init_rep(parent: bool, tt_list: List[bool], c_index: int,
                  tree_node: ANNTreeStructureTrain, /) -> None:
    next_id = c_index + 1
    if not parent:
        tt_list[c_index] = False
    for child_node in tree_node.children:
        _rec_init_rep(tt_list[c_index], tt_list, next_id, child_node)


@final
@dataclass
class _FileNameList:
    tt_list: List[bool]
    file_name: str
    index: int


def _rec_training(tt_value: bool, data: _FileNameList, tree_node: ANNTreeStructureTrain,
                  train_test_save: _TrainTestSave, sync_out: SyncStdoutInterface, /) \
        -> Iterable[_TrainerNetTypes]:
    tt_value_children = data.tt_list[data.index]
    data.index = data.index + 1
    for child_node in tree_node.children:
        yield from _rec_training(tt_value_children, data, child_node, train_test_save, sync_out)
    if tt_value:
        tree_node.node_data.prepare_data(sync_out)
        if train_test_save.train:
            for train_erg in tree_node.node_data.train_net(
                    create_ann_tree_id(tree_node.net_tree_id, data.file_name), sync_out
            ):
                yield _TrainerNetTypes(None, train_erg, None)
                saved_net = _create_savable(
                    tree_node.node_data.get_savable_data(),
                    create_ann_tree_id(tree_node.net_tree_id, data.file_name),
                    train_test_save.save and train_erg.dump_net
                )
                if saved_net is not None:
                    yield saved_net

        if train_test_save.test:
            test_data = tree_node.node_data.test_net(
                create_ann_tree_id(tree_node.net_tree_id, data.file_name),
                sync_out
            )
            for test_data_elem in test_data:
                yield _TrainerNetTypes(test_data_elem, None, None)

        tree_node.node_data.finalize()
        saved_net = _create_savable(
            tree_node.node_data.get_savable_data(),
            create_ann_tree_id(tree_node.net_tree_id, data.file_name),
            train_test_save.save
        )
        if saved_net is not None:
            yield saved_net


def _error(_: _TrainTestSave, /) -> int:
    raise WorkerTrainNetError("WorkerTrainNet does not support the wanted container type!")


def _set_train(train_test_save: _TrainTestSave, /) -> int:
    train_test_save.train = True
    return 1


def _set_test(train_test_save: _TrainTestSave, /) -> int:
    train_test_save.test = True
    return 0


def _set_save(train_test_save: _TrainTestSave, /) -> int:
    train_test_save.save = True
    return 2


def _create_container_tuple(cont_type: Type[ContainerInterface],
                            index: int, test_train_save: _TrainerNetTypes, /) \
        -> Tuple[ContainerInterface, ...]:
    if test_train_save.get_erg(index) is None:
        return tuple()
    erg = (cont_type(),)
    erg[0].set_data(test_train_save.get_erg(index))
    return erg


_SwitchThreadType: Final = Dict[Type[ContainerInterface], Callable[[_TrainTestSave], int]]


async def _rec_thread_worker_elem(train_test_save: _TrainTestSave, switch: _SwitchThreadType,
                                  data_elem: ContainerInterface, container_types: WorkerTypeParam,
                                  sync_out: SyncStdoutInterface, /) \
        -> AsyncIterable[DataContainer]:
    if not isinstance(data_elem, NeuralNetStructureTrainCon) or \
            data_elem.get_data().structure.parent is not None:
        raise WorkerTrainNetError("Received wrong data type!")
    tt_list: List[bool] = []
    _rec_init(tt_list, data_elem.get_data().structure, sync_out)
    _rec_init_rep(True, tt_list, 0, data_elem.get_data().structure)
    for erg_nets in _rec_training(
            True,
            _FileNameList(
                tt_list=tt_list,
                file_name=data_elem.get_data().file_name,
                index=0
            ),
            data_elem.get_data().structure, train_test_save,
            sync_out
    ):
        if isinstance(erg_nets, _TrainerNetTypes):
            yield tuple(
                _create_container_tuple(
                    type_cont,
                    switch.get(type_cont, _error)(train_test_save),
                    erg_nets
                )
                for type_cont in container_types.cont_out
            )
        else:
            raise WorkerTrainNetError("Wrong data received!")


async def _rec_thread_worker(data_container: Tuple[ContainerInterface, ...],
                             container_types: WorkerTypeParam,
                             sync_out: SyncStdoutInterface, /) -> AsyncIterable[DataContainer]:
    train_test_save = _TrainTestSave()

    switch: _SwitchThreadType = {
        TestNNStatsCon: _set_test,
        TrainNNStatsCon: _set_train,
        NeuralNetSaveCon: _set_save
    }

    for type_cont in container_types.cont_out:
        switch.get(type_cont, _error)(train_test_save)

    for data_elem in data_container:
        async for erg in _rec_thread_worker_elem(
                train_test_save, switch, data_elem, container_types,
                sync_out
        ):
            yield erg


@final
class WorkerTrainNet(WorkInterface):

    # Can block event queue
    def get_connection_in(self) -> Tuple[Type[NeuralNetStructureTrainCon]]:
        erg = (NeuralNetStructureTrainCon,)
        return erg

    def get_connection_out(self) \
            -> Tuple[Type[TestNNStatsCon], Type[TrainNNStatsCon], Type[NeuralNetSaveCon]]:
        erg = (TestNNStatsCon, TrainNNStatsCon, NeuralNetSaveCon)
        return erg

    def on_close(self, sync_out: SyncStdoutInterface, /) -> None:
        pass

    # Should not block event queue
    async def work(self, sync_out: SyncStdoutInterface, data_container: DataContainer,
                   container_types: WorkerTypeParam, pool_loop: PoolLoopCont, /) \
            -> AsyncIterable[DataContainer]:
        for tuple_index, tuple_elem in enumerate(data_container):
            if tuple_index >= 1 or tuple_index >= len(container_types.cont_in):
                raise WorkerTrainNetError("Wrong number container types received!")
            async for work_erg in _rec_thread_worker(
                    tuple_elem, container_types, sync_out
            ):
                yield work_erg


@final
class WorkerTestNet(WorkInterface):

    # Can block event queue
    def get_connection_in(self) -> Tuple[Type[NeuralNetStructureTestCon]]:
        erg = (NeuralNetStructureTestCon,)
        return erg

    def get_connection_out(self) -> Tuple[Type[TestNNStatsCon]]:
        erg = (TestNNStatsCon,)
        return erg

    def on_close(self, sync_out: SyncStdoutInterface, /) -> None:
        pass

    # Should not block event queue
    async def work(self, sync_out: SyncStdoutInterface, data_container: DataContainer,
                   container_types: WorkerTypeParam, pool_loop: PoolLoopCont, /) \
            -> AsyncIterable[Tuple[Tuple[TestNNStatsCon, ...]]]:
        for tuple_key, tuple_elem in enumerate(data_container):
            if tuple_key >= len(container_types.cont_in):
                raise WorkerTestNetError("Wrong type number received!")
            for data_elem in tuple_elem:
                if not isinstance(data_elem, NeuralNetStructureTestCon):
                    raise WorkerTestNetError("Received wrong data type!")
                node = data_elem.get_data().structure
                file_name = data_elem.get_data().file_name
                node.node_data.init_net(tuple(), sync_out)
                node.node_data.prepare_data(sync_out)
                erg_temp = node.node_data.test_net(
                    create_ann_tree_id(node.net_tree_id, file_name),
                    sync_out
                )
                test_erg: Tuple[Tuple[TestNNStatsCon, ...]] = (
                    tuple(TestNNStatsCon() for _ in erg_temp),
                )
                for t_index, test_erg_e in enumerate(test_erg[0]):
                    test_erg_e.set_data(erg_temp[t_index])
                node.node_data.finalize()
                yield test_erg
