#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' CAS thread optimization tool '''

from typing import Callable
import numpy as np

from swat.cas import CAS

from cvpy.base.CASServerMode import CASServerMode
from cvpy.base.Statistic import Statistic
from cvpy.base.CASThreadTunerResults import CASThreadTunerResults


class CASThreadTuner(object):

    @staticmethod
    def tune_thread_count(action_function: Callable[[CAS, np.ndarray, np.ndarray], float],
                          setup_function: Callable[[], CAS],
                          teardown_function: Callable[[CAS], None],
                          iterations: int = 5,
                          controller_thread_range: range = range(4, 65, 4),
                          worker_thread_range: range = range(4, 65, 4),
                          objective_measure: Statistic = Statistic.MEAN) -> CASThreadTunerResults:
        '''
        Compute the optimal thread count for a given image action.

        Parameters
        ----------
        action_function : :class:'function'
            Specifies a user-defined function that calls an image action.
        setup_function : :class:'function'
            Specifies a user defined function to set up CAS environment
        teardown_function : :class:'function'
            Specifies a user defined function to terminate the CAS session.
        iterations : :class:'int'
            Specifies the number of iterations to call action_function for each combination of threads.
        controller_thread_range : :class:'range'
            Specifies the range of threads on controller node.
        worker_thread_range : :class:'range'
            Specifies the range of threads on each worker node.
        objective_measure : :class:'enum.EnumMeta'
            Specifies the objective measure for performance over the given iterations - mean, median, minimum, maximum, stdev.

        Returns
        -------
        :class: '__main__.CASThreadTunerResults'

        '''

        # Setup function
        s = setup_function()

        # SMP
        if s.serverstatus()['server']['nodes'].values[0] == 1:
            mode = CASServerMode.SMP

            # Loop over controller thread range
            perf_array = np.zeros((len(Statistic), len(controller_thread_range)))
            for c_thread_idx, c_thread_count in enumerate(controller_thread_range):

                perf_record = np.zeros(iterations)
                # Loop over given number of iterations
                for iteration in range(iterations):
                    perf = action_function(s, c_thread_count, c_thread_count)
                    perf_record[iteration] = perf

                # perf_array stores the performance statistic
                perf_array[Statistic.MEAN.value, c_thread_idx] = round(float(np.mean(perf_record)), 4)
                perf_array[Statistic.MEDIAN.value, c_thread_idx] = round(float(np.median(perf_record)), 4)
                perf_array[Statistic.MINIMUM.value, c_thread_idx] = round(float(np.amin(perf_record)), 4)
                perf_array[Statistic.MAXIMUM.value, c_thread_idx] = round(float(np.amax(perf_record)), 4)
                perf_array[Statistic.STDEV.value, c_thread_idx] = round(float(np.std(perf_record)), 4)

        else:
            mode = CASServerMode.MPP

            # Loop over controller thread range
            perf_array = np.zeros((len(Statistic), len(controller_thread_range), len(worker_thread_range)))
            for c_thread_idx, c_thread_count in enumerate(controller_thread_range):

                # Loop over worker thread range
                for w_thread_idx, w_thread_count in enumerate(worker_thread_range):

                    perf_record = np.zeros(iterations)
                    # Loop over given number of iterations
                    for iteration in range(iterations):
                        perf = action_function(s, c_thread_count, w_thread_count)
                        perf_record[iteration] = perf

                    # perf_array stores the performance statistic
                    perf_array[Statistic.MEAN.value, c_thread_idx, w_thread_idx] = round(float(np.mean(perf_record)), 4)
                    perf_array[Statistic.MEDIAN.value, c_thread_idx, w_thread_idx] = round(
                        float(np.median(perf_record)), 4)
                    perf_array[Statistic.MINIMUM.value, c_thread_idx, w_thread_idx] = round(float(np.amin(perf_record)),
                                                                                            4)
                    perf_array[Statistic.MAXIMUM.value, c_thread_idx, w_thread_idx] = round(float(np.amax(perf_record)),
                                                                                            4)
                    perf_array[Statistic.STDEV.value, c_thread_idx, w_thread_idx] = round(float(np.std(perf_record)), 4)

        # Teardown function
        teardown_function(s)

        opt_array = perf_array[objective_measure.value]
        opt_index = np.unravel_index(np.argmin(opt_array, axis=None), opt_array.shape)

        worker_optimal_count = None
        if mode == CASServerMode.MPP:
            worker_optimal_count = worker_thread_range[opt_index[1]]

        # Return results
        return CASThreadTunerResults(cas_server_mode=mode,
                                     controller_thread_range=controller_thread_range,
                                     worker_thread_range=worker_thread_range,
                                     objective_measure=objective_measure,
                                     controller_optimal_thread_count=controller_thread_range[opt_index[0]],
                                     worker_optimal_thread_count=worker_optimal_count,
                                     mean_exec_times=perf_array[Statistic.MEAN.value],
                                     median_exec_times=perf_array[Statistic.MEDIAN.value],
                                     minimum_exec_times=perf_array[Statistic.MINIMUM.value],
                                     maximum_exec_times=perf_array[Statistic.MAXIMUM.value],
                                     stdev_exec_times=perf_array[Statistic.STDEV.value]
                                     )
