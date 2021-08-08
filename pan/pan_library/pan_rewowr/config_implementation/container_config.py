# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
from typing import Final

from pan.pan_library.pan_rewowr.container.dict_json import JsonDictCon
from pan.pan_library.pan_rewowr.container.neural_net_container import NeuralNetSaveCon, \
    NeuralNetStructureTrainCon, NeuralNetStructureTestCon, TrainNNStatsCon, TestNNStatsCon
from rewowr.public.interfaces.rewrwo_checker_interface import ContainerDict

_LocalContDict: Final[ContainerDict] = ContainerDict(
    container_dict={
        "NeuralNetSaveCon": NeuralNetSaveCon,
        "NeuralNetStructureTrainCon": NeuralNetStructureTrainCon,
        "NeuralNetStructureTestCon": NeuralNetStructureTestCon,
        "TrainNNStatsCon": TrainNNStatsCon,
        "TestNNStatsCon": TestNNStatsCon,
        "JsonDictCon": JsonDictCon
    }
)


def container_config() -> ContainerDict:
    return _LocalContDict
