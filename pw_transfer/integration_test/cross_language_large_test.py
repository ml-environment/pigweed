#!/usr/bin/env python3
# Copyright 2022 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""Cross-language pw_transfer tests that take tens of minutes to run.

Usage:

   bazel run pw_transfer/integration_test:cross_language_large_test

Command-line arguments must be provided after a double-dash:

   bazel run pw_transfer/integration_test:cross_language_large_test -- \
       --server-port 3304

Which tests to run can be specified as command-line arguments:

  bazel run pw_transfer/integration_test:cross_language_large_test -- \
      LargeTransferIntegrationTest.test_3mb_write_dropped_data_1_java

"""

from parameterized import parameterized
import random

from google.protobuf import text_format

import test_fixture
from test_fixture import (TransferConfig, TransferIntegrationTest,
                          TransferIntegrationTestHarness)
from pigweed.pw_transfer.integration_test import config_pb2


# TODO(b/232805936): Extend tests to use different resource IDs and do multiple
# reads/writes.
class LargeTransferIntegrationTest(TransferIntegrationTest):
    # Each set of transfer tests uses a different client/server port pair to
    # allow tests to be run in parallel.
    HARNESS_CONFIG = TransferIntegrationTestHarness.Config(server_port=3306,
                                                           client_port=3307)

    @parameterized.expand([
        ("cpp"),
        ("java"),
        ("python"),
    ])
    def test_3mb_write_dropped_data(self, client_type):
        server_config = config_pb2.ServerConfig(
            chunk_size_bytes=216,
            pending_bytes=32 * 1024,
            chunk_timeout_seconds=5,
            transfer_service_retries=4,
            extend_window_divisor=32,
        )
        client_config = config_pb2.ClientConfig(
            max_retries=5,
            initial_chunk_timeout_ms=10000,
            chunk_timeout_ms=4000,
        )
        proxy_config = text_format.Parse(
            """
            client_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_dropper: {rate: 0.01, seed: 1649963713563718435} }
            ]

            server_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_dropper: {rate: 0.01, seed: 1649963713563718436} }
        ]""", config_pb2.ProxyConfig())

        payload = random.Random(1649963713563718437).randbytes(3 * 1024 * 1024)
        resource_id = 12
        config = TransferConfig(server_config, client_config, proxy_config)
        self.do_single_write(client_type, config, resource_id, payload)

    @parameterized.expand([
        ("cpp"),
        ("java"),
        ("python"),
    ])
    def test_3mb_write_reordered_data(self, client_type):
        server_config = config_pb2.ServerConfig(
            chunk_size_bytes=216,
            pending_bytes=32 * 1024,
            chunk_timeout_seconds=5,
            transfer_service_retries=4,
            extend_window_divisor=32,
        )
        client_config = config_pb2.ClientConfig(
            max_retries=5,
            initial_chunk_timeout_ms=10000,
            chunk_timeout_ms=4000,
        )
        proxy_config = text_format.Parse(
            """
            client_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_transposer: {rate: 0.005, timeout: 0.5, seed: 1649963713563718435} }
            ]

            server_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_transposer: {rate: 0.005, timeout: 0.5, seed: 1649963713563718435} }
        ]""", config_pb2.ProxyConfig())

        payload = random.Random(1649963713563718437).randbytes(3 * 1024 * 1024)
        resource_id = 12
        config = TransferConfig(server_config, client_config, proxy_config)
        self.do_single_write(client_type, config, resource_id, payload)

    @parameterized.expand([
        ("cpp"),
        # TODO(b/250976246): This test runs indefinitely (>24 hrs) when using
        # the java client, so it is disabled for now until the issue is
        # diagnosed.
        # ("java"),
        ("python"),
    ])
    def test_3mb_read_dropped_data(self, client_type):
        server_config = config_pb2.ServerConfig(
            chunk_size_bytes=216,
            pending_bytes=32 * 1024,
            chunk_timeout_seconds=5,
            transfer_service_retries=4,
            extend_window_divisor=32,
        )
        client_config = config_pb2.ClientConfig(
            max_retries=5,
            initial_chunk_timeout_ms=10000,
            chunk_timeout_ms=4000,
        )
        proxy_config = text_format.Parse(
            """
            client_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_dropper: {rate: 0.01, seed: 1649963713563718435} }
            ]

            server_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_dropper: {rate: 0.01, seed: 1649963713563718436} }
        ]""", config_pb2.ProxyConfig())

        payload = random.Random(1649963713563718437).randbytes(3 * 1024 * 1024)
        resource_id = 12
        config = TransferConfig(server_config, client_config, proxy_config)
        self.do_single_read(client_type, config, resource_id, payload)

    @parameterized.expand([
        ("cpp"),
        ("java"),
        ("python"),
    ])
    def test_3mb_read_reordered_data(self, client_type):
        server_config = config_pb2.ServerConfig(
            chunk_size_bytes=216,
            pending_bytes=32 * 1024,
            chunk_timeout_seconds=5,
            transfer_service_retries=4,
            extend_window_divisor=32,
        )
        client_config = config_pb2.ClientConfig(
            max_retries=5,
            initial_chunk_timeout_ms=10000,
            chunk_timeout_ms=4000,
        )
        proxy_config = text_format.Parse(
            """
            client_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_transposer: {rate: 0.005, timeout: 0.5, seed: 1649963713563718435} }
            ]

            server_filter_stack: [
                { rate_limiter: {rate: 50000} },
                { hdlc_packetizer: {} },
                { data_transposer: {rate: 0.005, timeout: 0.5, seed: 1649963713563718435} }
        ]""", config_pb2.ProxyConfig())

        payload = random.Random(1649963713563718437).randbytes(3 * 1024 * 1024)
        resource_id = 12
        config = TransferConfig(server_config, client_config, proxy_config)
        self.do_single_read(client_type, config, resource_id, payload)


if __name__ == '__main__':
    test_fixture.run_tests_for(LargeTransferIntegrationTest)
