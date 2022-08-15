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

import sys
import unittest

import numpy as np
import xmlrunner

from swat import CAS

from cvpy.base.CASServerMode import CASServerMode
from cvpy.base.Statistic import Statistic
from cvpy.utils.CASThreadTuner import CASThreadTuner


class TestCASThreadTuner(unittest.TestCase):
    CAS_HOST = None
    CAS_PORT = None
    USERNAME = None
    PASSWORD = None
    DATAPATH = None

    @staticmethod
    def set_up() -> CAS:
        s = CAS(TestCASThreadTuner.CAS_HOST, TestCASThreadTuner.CAS_PORT, TestCASThreadTuner.USERNAME,
                TestCASThreadTuner.PASSWORD)

        s.loadactionset('image')

        s.addcaslib(name='dlib',
                    activeOnAdd=False,
                    path=TestCASThreadTuner.DATAPATH,
                    datasource='PATH',
                    subdirectories=True)

        return s

    @staticmethod
    def tear_down(s) -> None:
        s.close()

    @staticmethod
    def load_images(s: CAS, c_threads: np.ndarray, w_threads: np.ndarray) -> float:
        image_table = s.CASTable('image_table', replace=True)

        response = s.image.loadImages(path='images',
                                      casout=image_table,
                                      caslib='dlib',
                                      nControllerThreads=c_threads,
                                      nThreads=w_threads)

        return response.performance.elapsed_time

    def test_casthreadtuner_all_parameters_specified(self):

        tuner_results = CASThreadTuner.tune_thread_count(action_function=TestCASThreadTuner.load_images,
                                                         setup_function=TestCASThreadTuner.set_up,
                                                         teardown_function=TestCASThreadTuner.tear_down,
                                                         iterations=2, controller_thread_range=range(16, 65, 16),
                                                         worker_thread_range=range(32, 65, 32),
                                                         objective_measure=Statistic.MEDIAN)

        self.assertTrue(tuner_results._cas_server_mode == CASServerMode.SMP or
                        tuner_results._cas_server_mode == CASServerMode.MPP)
        self.assertEqual(tuner_results._controller_thread_range, range(16, 65, 16))
        self.assertEqual(tuner_results._objective_measure, Statistic.MEDIAN)
        self.assertIsNotNone(tuner_results.controller_optimal_thread_count)
        self.assertIsNotNone(tuner_results._mean_exec_times)
        self.assertIsNotNone(tuner_results._median_exec_times)
        self.assertIsNotNone(tuner_results._minimum_exec_times)
        self.assertIsNotNone(tuner_results._maximum_exec_times)
        self.assertIsNotNone(tuner_results._stdev_exec_times)

        if tuner_results._cas_server_mode == CASServerMode.MPP:
            self.assertEqual(tuner_results._worker_thread_range, range(32, 65, 32))
            self.assertIsNotNone(tuner_results._worker_optimal_thread_count)

        fig = tuner_results.plot_exec_times(fig_width=5, fig_height=5)
        self.assertIsNotNone(fig)

    def test_casthreadtuner_optional_parameters_not_specified(self):

        tuner_results = CASThreadTuner.tune_thread_count(action_function=self.load_images, setup_function=self.set_up,
                                                         teardown_function=self.tear_down)

        self.assertTrue(tuner_results._cas_server_mode == CASServerMode.SMP or
                        tuner_results._cas_server_mode == CASServerMode.MPP)
        self.assertEqual(tuner_results._controller_thread_range, range(4, 65, 4))
        self.assertEqual(tuner_results._objective_measure, Statistic.MEAN)
        self.assertTrue(tuner_results.controller_optimal_thread_count)
        self.assertIsNotNone(tuner_results._mean_exec_times)
        self.assertIsNotNone(tuner_results._median_exec_times)
        self.assertIsNotNone(tuner_results._minimum_exec_times)
        self.assertIsNotNone(tuner_results._maximum_exec_times)
        self.assertIsNotNone(tuner_results._stdev_exec_times)

        if tuner_results._cas_server_mode == CASServerMode.MPP:
            self.assertEqual(tuner_results._worker_thread_range, range(4, 65, 4))
            self.assertIsNotNone(tuner_results._worker_optimal_thread_count)

        fig = tuner_results.plot_exec_times()
        self.assertIsNotNone(fig)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestCASThreadTuner.CAS_HOST = sys.argv.pop(1)
        TestCASThreadTuner.CAS_PORT = sys.argv.pop(1)
        TestCASThreadTuner.USERNAME = sys.argv.pop(1)
        TestCASThreadTuner.PASSWORD = sys.argv.pop(1)
        TestCASThreadTuner.DATAPATH = sys.argv.pop(1)

    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='test-reports'),
        failfast=False, buffer=False, catchbreak=False
    )
