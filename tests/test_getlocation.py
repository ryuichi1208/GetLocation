import os
import pytest
import re
import sys

from pytest import ExitCode
from .. import getlocation

class TestGetlocation(object):
    def test_check_args_validate(self):
        assert getlocation.check_args_validate([0, "1"]) == (True, 1)
        assert getlocation.check_args_validate([0, "99"]) == (True, 99)
        assert getlocation.check_args_validate([0, "0"]) == (False, 0)
        assert getlocation.check_args_validate([0, "a"]) == (False, 0)
        assert getlocation.check_args_validate([0, "100"]) == (False, 0)
        assert getlocation.check_args_validate([0, "10", "20"]) == (False, 0)

    def test_main(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            getlocation.main(["args"])
        assert pytest_wrapped_e.type == SystemExit

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            getlocation.main(["args", "argv[0]"])
        assert pytest_wrapped_e.type == SystemExit

        with pytest.raises(SystemExit) as pytest_wrapped_e:
            getlocation.main(["args", "argv[0]", "argv[1]"])
        assert pytest_wrapped_e.type == SystemExit

    def test_print_pretty_json(self):
        assert getlocation.print_pretty_json({"aaa":"bbb"}) == None
        assert getlocation.print_pretty_json({"aaa":"bbb"}) == None
        assert getlocation.print_pretty_json({111:222}) == None
        assert getlocation.print_pretty_json({111:"bbb"}) == None
