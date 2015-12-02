# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#

import asyncio
import functools
import inspect
import unittest

__all__ = (
    'MetaAioTestCase',
    'TestCase',
)


def run_in_loop(coro):
    @functools.wraps(coro)
    def wrapper(testcase, *args, **kwargs):
        future = asyncio.wait_for(coro(testcase, *args, **kwargs),
                                  timeout=getattr(testcase, 'timeout', 5))
        return testcase.loop.run_until_complete(future)
    return wrapper


class MetaAioTestCase(type):

    def __new__(cls, name, bases, attrs):
        for key, obj in attrs.items():
            if key.startswith('test_'):
                if inspect.iscoroutinefunction(obj):
                    attrs[key] = run_in_loop(obj)
                else:
                    attrs[key] = obj
        return super().__new__(cls, name, bases, attrs)


class TestCase(unittest.TestCase, metaclass=MetaAioTestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def future(self, result=..., exception=...):
        future = asyncio.Future(loop=self.loop)
        if result is not ...:
            future.set_result(result)  # pragma: no cover
        if exception is not ...:
            future.set_exception(exception)
        return future
