import sys
import os
from unittest import TestCase
from pecan.testing import reset_global_config


class PecanTestCase(TestCase):

    def setUp(self):
        self.addCleanup(reset_global_config)
