from typing import List

import numpy as np
import matplotlib.pylab as plt
from matplotlib import cm
from matplotlib.figure import Figure

from cvpy.base.CASServerMode import CASServerMode
from cvpy.base.Statistic import Statistic


class CASThreadTunerResults(object):
    '''
    This is a class for results in CAS thread optimization tool.
    '''

    def __init__(self, cas_server_mode: CASServerMode = None,
                 controller_thread_range: range = None,
                 worker_thread_range: range = None,
                 objective_measure: Statistic = None,
                 controller_optimal_thread_count: int = None,
                 worker_optimal_thread_count: int = None,
                 mean_exec_times: List[List[int]] = None,
                 median_exec_times: List[List[int]] = None,
                 minimum_exec_times: List[List[int]] = None,
                 maximum_exec_times: List[List[int]] = None,
                 stdev_exec_times: List[List[int]] = None):

        '''
        Constructor for CASThreadTunerResults class
        :param cas_server_mode: CAS server architecture
        :param controller_thread_range: range of threads on controller node
        :param worker_thread_range: range of threads on worker node
        :param objective_measure: objective measure for performance over given iterations
        :param controller_optimal_thread_count: optimal thread count on controller node
        :param worker_optimal_thread_count: optimal thread count on worker node
        :param mean_exec_times: mean of recorded execution times over specified iterations
        :param median_exec_times: median of recorded execution times over specified iterations
        :param minimum_exec_times: minimum of recorded execution times over specified iterations
        :param maximum_exec_times: maximum of recorded execution times over specified iterations
        :param stdev_exec_times: standard deviation of recorded execution times over specified iterations
        '''

        self._cas_server_mode = cas_server_mode
        self._controller_thread_range = controller_thread_range
        self._worker_thread_range = worker_thread_range
        self._objective_measure = objective_measure
        self._controller_optimal_thread_count = controller_optimal_thread_count
        self._worker_optimal_thread_count = worker_optimal_thread_count
        self._mean_exec_times = mean_exec_times
        self._median_exec_times = median_exec_times
        self._minimum_exec_times = minimum_exec_times
        self._maximum_exec_times = maximum_exec_times
        self._stdev_exec_times = stdev_exec_times

    @property
    def cas_server_mode(self) -> CASServerMode:
        return self._cas_server_mode

    @cas_server_mode.setter
    def cas_server_mode(self, cas_server_mode) -> None:
        self._cas_server_mode = cas_server_mode

    @property
    def controller_thread_range(self) -> range:
        return self._controller_thread_range

    @controller_thread_range.setter
    def controller_thread_range(self, controller_thread_range) -> None:
        self._controller_thread_range = controller_thread_range

    @property
    def worker_thread_range(self) -> range:
        return self._worker_thread_range

    @worker_thread_range.setter
    def worker_thread_range(self, worker_thread_range) -> None:
        self._worker_thread_range = worker_thread_range

    @property
    def objective_measure(self) -> Statistic:
        return self._objective_measure

    @objective_measure.setter
    def objective_measure(self, objective_measure) -> None:
        self._objective_measure = objective_measure

    @property
    def controller_optimal_thread_count(self) -> int:
        return self._controller_optimal_thread_count

    @controller_optimal_thread_count.setter
    def controller_optimal_thread_count(self, controller_optimal_thread_count) -> None:
        self._controller_optimal_thread_count = controller_optimal_thread_count

    @property
    def worker_optimal_thread_count(self) -> int:
        return self._worker_optimal_thread_count

    @worker_optimal_thread_count.setter
    def worker_optimal_thread_count(self, worker_optimal_thread_count) -> None:
        self._worker_optimal_thread_count = worker_optimal_thread_count

    @property
    def mean_exec_times(self) -> List[List[int]]:
        return self._mean_exec_times

    @mean_exec_times.setter
    def mean_exec_times(self, mean_exec_times) -> None:
        self._mean_exec_times = mean_exec_times

    @property
    def median_exec_times(self) -> List[List[int]]:
        return self._median_exec_times

    @median_exec_times.setter
    def median_exec_times(self, median_exec_times) -> None:
        self._median_exec_times = median_exec_times

    @property
    def minimum_exec_times(self) -> List[List[int]]:
        return self._minimum_exec_times

    @minimum_exec_times.setter
    def minimum_exec_times(self, minimum_exec_times) -> None:
        self._minimum_exec_times = minimum_exec_times

    @property
    def maximum_exec_times(self) -> List[List[int]]:
        return self._maximum_exec_times

    @maximum_exec_times.setter
    def maximum_exec_times(self, maximum_exec_times) -> None:
        self._maximum_exec_times = maximum_exec_times

    @property
    def stdev_exec_times(self) -> List[List[int]]:
        return self._stdev_exec_times

    @stdev_exec_times.setter
    def stdev_exec_times(self, stdev_exec_times) -> None:
        self._sd_exec_times = stdev_exec_times

    def plot_exec_times(self, fig_width: float, fig_height: float) -> Figure:
        '''
        Plots performance for given CAS thread tuner results.

        Returns
        -------
        :class: 'matplotlib.figure.Figure'

        '''
        if self.objective_measure == Statistic.MEAN:
            opt_array = self.mean_exec_times
        elif self.objective_measure == Statistic.MEDIAN:
            opt_array = self.median_exec_times
        elif self.objective_measure == Statistic.MINIMUM:
            opt_array = self.minimum_exec_times
        elif self.objective_measure == Statistic.MAXIMUM:
            opt_array = self.maximum_exec_times
        else:
            opt_array = self.stdev_exec_times

        if self.cas_server_mode == CASServerMode.SMP:
            # Line plot
            fig = plt.figure(figsize=(fig_width, fig_height))
            x = list(self.controller_thread_range)
            y = opt_array
            plt.xlabel('Controller Thread Count')
            plt.ylabel('Runtime (sec)')
            plt.title('Performance of loadImages in SMP')
            plt.plot(x, y)
            return fig

        else:
            # Surface plot
            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            fig.set_figheight(fig_height)
            fig.set_figwidth(fig_width)
            x, y = np.meshgrid(self.controller_thread_range, self.worker_thread_range)
            surf = ax.plot_surface(x, y, np.transpose(opt_array), cmap=cm.coolwarm, linewidth=0, antialiased=False)
            fig.colorbar(surf, shrink=0.5, aspect=5)
            ax.set_xlabel('Controller Thread Count')
            ax.set_ylabel('Worker Thread Count')
            ax.set_zlabel('Runtime (sec)')
            ax.set_title('Performance of loadImages in MPP')
            return fig
