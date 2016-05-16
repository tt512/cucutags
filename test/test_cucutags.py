# -*- coding: utf-8 -*-  IGNORE:C0111
from __future__ import absolute_import, print_function, unicode_literals

import logging
import os.path
import unittest

import cucutags


class TestCucutags(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.datadir = os.path.join(os.path.dirname(__file__), "data")
        self.session = cucutags.Session(self.datadir)
        logging.debug("session = %s", self.session)

    def test_init_session(self):
        """Just initialize Session from data in the data
        subdirectory."""
        # We cannot use assertIsInstance because of 2.6 compatibility
        self.assertTrue(isinstance(self.session, cucutags.Session))

    def test_generate_tags(self):
        """Generate tags and compare with expected result."""
        tags = [tuple(x[1:]) for x in
                self.session.generate_tags(self.datadir)]
        expected = [(u'common_steps/app.py', 59),
                    (u'common_steps/gmenu.py', 12),
                    (u'common_steps/gmenu.py', 34),
                    (u'common_steps/app.py', 66),
                    (u'common_steps/app.py', 59),
                    (u'common_steps/gmenu.py', 12),
                    (u'common_steps/gmenu.py', 34),
                    (u'common_steps/app.py', 59),
                    (u'common_steps/app.py', 17),
                    (u'common_steps/app.py', 42),
                    (u'common_steps/app.py', 66),
                    (u'features/steps/tutorial.py', 3),
                    (u'features/steps/tutorial.py', 7),
                    (u'features/steps/tutorial.py', 11)]
        self.assertEqual(tags, expected)

    def test_find_step(self):
        step = self.session.get_step(u"Make sure that Empathy is running")
        filename = os.path.relpath(step[0], os.path.dirname(__file__))
        self.assertEqual([filename, step[1]],
                         ["data/common_steps/app.py", 59])
