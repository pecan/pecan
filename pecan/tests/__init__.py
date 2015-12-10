import sys
import os
if sys.version_info < (2, 7):
    from unittest2 import TestCase  # pragma: nocover
else:
    from unittest import TestCase  # pragma: nocover
from pecan.testing import reset_global_config


class PecanTestCase(TestCase):

    def setUp(self):
        self.addCleanup(reset_global_config)
