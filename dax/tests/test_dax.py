from unittest import TestCase

import dax


class TestJoke(TestCase):
    def test_is_string(self):
        s = 'TEST_STRING';
        self.assertTrue(isinstance(s, str))
