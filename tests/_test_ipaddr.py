import contextlib
import operator
import pickle
import re
import sys
import unittest
import weakref

import ipaddress


class NetworkTestCase_v4(BaseTestCase, NetmaskTestMixin_v4):
    factory = ipaddress.IPv4Network

    def test_supernet_of(self):
        # containee left of container
        self.assertFalse(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.1.0/24')))
        # containee inside container
        self.assertFalse(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.0.0/24')))
        # containee right of container
        self.assertFalse(
            self.factory('10.0.0.0/30').supernet_of(
                self.factory('10.0.1.0/24')))
        # containee larger than container
        self.assertTrue(
            self.factory('10.0.0.0/24').supernet_of(
                self.factory('10.0.0.0/30')))

    def test_same_type_equality(self):
        for obj in self.objects:
            self.assertEqual(obj, obj)
            self.assertTrue(obj <= obj)
            self.assertTrue(obj >= obj)

    def test_same_type_ordering(self):
        for lhs, rhs in (
            (self.v4addr, self.v4addr2),
            (self.v4net, self.v4net2),
            (self.v4intf, self.v4intf2),
            (self.v6addr, self.v6addr2),
            (self.v6net, self.v6net2),
            (self.v6intf, self.v6intf2),
        ):
            self.assertNotEqual(lhs, rhs)
            self.assertTrue(lhs < rhs)
            self.assertTrue(lhs <= rhs)
            self.assertTrue(rhs > lhs)
            self.assertTrue(rhs >= lhs)
            self.assertFalse(lhs > rhs)
            self.assertFalse(rhs < lhs)
            self.assertFalse(lhs >= rhs)
            self.assertFalse(rhs <= lhs)
