#!/usr/bin/env python

#  Copyright Contributors to the OpenCue Project
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Tests for the outline.cfg spec_version
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import unittest

from xml.etree import ElementTree as Et

import outline
import outline.modules.shell


class SpecVersiondTest(unittest.TestCase):
    def _makeSpec(self):
        # Ensure to reset current
        outline.Outline.current = None
        ol = outline.Outline(name="spec_version_test")
        layer = outline.modules.shell.Shell("test_layer", command=["/bin/ls"])
        layer.set_arg("timeout", 420)
        layer.set_arg("timeout_llu", 4200)
        ol.add_layer(layer)
        l = outline.cuerun.OutlineLauncher(ol)
        l.set_flag("priority", 42)
        return Et.fromstring(l.serialize())

    def test_1_9(self):
        outline.config.set("outline", "spec_version", "1.9")
        root = self._makeSpec()
        self.assertIsNone(root.find("job/layers/layer/timeout"))
        self.assertIsNone(root.find("job/layers/layer/timeout_llu"))
        self.assertIsNone(root.find("job/priority"))

    def test_1_10(self):
        outline.config.set("outline", "spec_version", "1.10")
        root = self._makeSpec()
        self.assertEqual(root.find("job/layers/layer/timeout").text, "420")
        self.assertEqual(root.find("job/layers/layer/timeout_llu").text, "4200")
        self.assertIsNone(root.find("job/priority"))

    def test_1_11(self):
        outline.config.set("outline", "spec_version", "1.11")
        root = self._makeSpec()
        self.assertEqual(root.find("job/layers/layer/timeout").text, "420")
        self.assertEqual(root.find("job/layers/layer/timeout_llu").text, "4200")
        self.assertEqual(root.find("job/priority").text, "42")

    def _makeGpuSpec(self, **gpu_args):
        ol = outline.Outline(name="spec_version_test")
        layer = outline.modules.shell.Shell("test_layer", command=["/bin/ls"])
        for name, value in gpu_args.items():
            layer.set_arg(name, value)
        ol.add_layer(layer)
        l = outline.cuerun.OutlineLauncher(ol)
        return Et.fromstring(l.serialize())

    def test_gpu_1_11(self):
        outline.config.set("outline", "spec_version", "1.11")
        root = self._makeGpuSpec(gpus=4, gpu_memory=8 * 1024 * 1024)
        self.assertIsNone(root.find("job/layers/layer/gpus"))
        self.assertIsNone(root.find("job/layers/layer/gpu_memory"))

    def test_gpu_1_12(self):
        outline.config.set("outline", "spec_version", "1.12")
        root = self._makeGpuSpec(gpus=4, gpu_memory=8 * 1024 * 1024)
        self.assertEqual(root.find("job/layers/layer/gpus").text, "4")
        self.assertEqual(root.find("job/layers/layer/gpu_memory").text, "8388608")

    def test_a_layer_that_sets_only_gpu_memory_asks_for_no_gpus(self):
        outline.config.set("outline", "spec_version", "1.12")
        root = self._makeGpuSpec(gpu_memory="9g")
        self.assertEqual(root.find("job/layers/layer/gpus").text, "0")

    def test_a_layer_that_sets_only_gpus_reserves_the_default_gpu_memory(self):
        outline.config.set("outline", "spec_version", "1.12")
        root = self._makeGpuSpec(gpus=2)
        self.assertEqual(root.find("job/layers/layer/gpu_memory").text, "1g")

    def test_a_layer_that_sets_no_gpu_args_has_no_gpu_elements(self):
        outline.config.set("outline", "spec_version", "1.12")
        root = self._makeGpuSpec()
        self.assertEqual(
            [root.find("job/layers/layer/gpus"), root.find("job/layers/layer/gpu_memory")],
            [None, None])

    def test_gpu_memory_only_below_1_12_has_no_gpu_elements(self):
        outline.config.set("outline", "spec_version", "1.11")
        root = self._makeGpuSpec(gpu_memory="9g")
        self.assertEqual(
            [root.find("job/layers/layer/gpus"), root.find("job/layers/layer/gpu_memory")],
            [None, None])

    def _makeMaxCoresGpusSpec(self):
        ol = outline.Outline(name="override_max_cores_and_gpus", maxcores=8, maxgpus=7)
        layer = outline.modules.shell.Shell("test_layer", command=["/bin/ls"])
        ol.add_layer(layer)
        l = outline.cuerun.OutlineLauncher(ol)
        return Et.fromstring(l.serialize())

    def test_max_cores_gpus_1_12(self):
        outline.config.set("outline", "spec_version", "1.12")
        root = self._makeMaxCoresGpusSpec()
        self.assertIsNone(root.find("job/maxcores"))
        self.assertIsNone(root.find("job/maxgpus"))

    def test_max_cores_gpus_1_13(self):
        outline.config.set("outline", "spec_version", "1.13")
        root = self._makeMaxCoresGpusSpec()
        self.assertEqual(root.find("job/maxcores").text, "8")
        self.assertEqual(root.find("job/maxgpus").text, "7")
