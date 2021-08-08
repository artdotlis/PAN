# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import final

from pan.public.constants.test_net_stats_constants import \
    TestNNStatsElementType
from pan.public.constants.train_net_stats_constants import \
    TrainNNStatsElementType
from pan.pan_library.pan_interfaces.net_interfaces.net_interface import ANNTreeStructureTrainWr, \
    ANNStructureTestWr
from pan.pan_library.pan_interfaces.gen_constants.net_savable_constants import SavableNetType
from rewowr.public.container.container_simple_generic import SimpleGenericContainer


@final
class NeuralNetSaveCon(SimpleGenericContainer[SavableNetType]):
    pass


@final
class TrainNNStatsCon(SimpleGenericContainer[TrainNNStatsElementType]):
    pass


@final
class TestNNStatsCon(SimpleGenericContainer[TestNNStatsElementType]):
    pass


@final
class NeuralNetStructureTrainCon(SimpleGenericContainer[ANNTreeStructureTrainWr]):
    pass


@final
class NeuralNetStructureTestCon(SimpleGenericContainer[ANNStructureTestWr]):
    pass
