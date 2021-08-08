# -*- coding: utf-8 -*-
""".. moduleauthor:: Artur Lissin"""
import abc
from typing import TypeVar, Generic, Dict, Final

from pan.public.constants.train_net_stats_constants import \
    TrainNNPlotterStatDictSeriesType

_PlottableDataType: Final = TypeVar('_PlottableDataType')
_WritableDataType: Final = TypeVar('_WritableDataType')


class NetXYPlotter(Generic[_PlottableDataType, _WritableDataType], abc.ABC):
    @abc.abstractmethod
    def create_plottable_data(self, data_series: Dict[str, TrainNNPlotterStatDictSeriesType], /) \
            -> _PlottableDataType:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def create_writable_data(self, data_series: Dict[str, TrainNNPlotterStatDictSeriesType], /) \
            -> _WritableDataType:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def plot_data(self, file_name: str, data: _PlottableDataType, /) -> None:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def write_data(self, file_name: str, data: _WritableDataType, extra_str: str, /) -> None:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def create_plottable_dump_data(self,
                                   data_series: Dict[str, TrainNNPlotterStatDictSeriesType], /) \
            -> _PlottableDataType:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def create_writable_dump_data(self,
                                  data_series: Dict[str, TrainNNPlotterStatDictSeriesType], /) \
            -> _WritableDataType:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def dump_plot(self, file_name: str, data: _PlottableDataType, /) -> None:
        raise NotImplementedError("Interface!")

    @abc.abstractmethod
    def dump_data(self, file_name: str, data: _WritableDataType, extra_str: str, /) -> None:
        raise NotImplementedError("Interface!")
