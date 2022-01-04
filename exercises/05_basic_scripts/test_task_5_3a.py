from functools import wraps
from importlib import reload
import sys
import pytest


# Checking that the test is called via pytest ... and not python ...
from _pytest.assertion.rewrite import AssertionRewritingHook

if not isinstance(__loader__, AssertionRewritingHook):
    print(f"Tests should be called using this expression:\npytest {__file__}\n\n")


def count_calls(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        __tracebackhide__ = True
        wrapper.total_calls += 1
        result = func(*args, **kwargs)
        return result

    wrapper.total_calls = 0
    return wrapper


@count_calls
def monkey_input_access(prompt):
    __tracebackhide__ = True
    if monkey_input_access.total_calls == 1:
        return "access"
    elif monkey_input_access.total_calls == 2:
        return "Gi0/3"
    elif monkey_input_access.total_calls == 3:
        if "vlan number" in prompt.lower():
            return "55"
        else:
            pytest.fail(
                "For access ports, the vlan request should be like this:"
                "Enter VLAN number:"
            )


@count_calls
def monkey_input_trunk(prompt):
    __tracebackhide__ = True
    if monkey_input_trunk.total_calls == 1:
        return "trunk"
    elif monkey_input_trunk.total_calls == 2:
        return "Gi0/2"
    elif monkey_input_trunk.total_calls == 3:
        if "allowed vlans" in prompt.lower():
            return "10,11,12"
        else:
            pytest.fail(
                "For trunk ports, the vlan request should be like this:"
                "Enter the allowed VLANs:"
            )


def test_task_access(capsys, monkeypatch):
    """
    Task check for access
    """
    monkeypatch.setattr("builtins.input", monkey_input_access)
    import task_5_3a

    out, err = capsys.readouterr()
    correct_stdout = (
        "interface Gi0/3\n"
        "switchport mode access\n"
        "switchport access vlan 55\n"
        "switchport nonegotiate\n"
        "spanning-tree portfast\n"
        "spanning-tree bpduguard enable"
    )

    assert (
        out
    ), "Nothing is printed to stdout. It is necessary not only to get the correct result, but also to print it to the stdout using print"
    assert correct_stdout == out.strip(), "Wrong output is printed to stdout"


def test_task_trunk(capsys, monkeypatch):
    """
    Task check for trunk
    """
    monkeypatch.setattr("builtins.input", monkey_input_trunk)
    if sys.modules.get("task_5_3a"):
        reload(sys.modules["task_5_3a"])
    import task_5_3a

    out, err = capsys.readouterr()
    correct_stdout = (
        "interface Gi0/2\n"
        "switchport trunk encapsulation dot1q\n"
        "switchport mode trunk\n"
        "switchport trunk allowed vlan 10,11,12"
    )
    assert (
        out
    ), "Nothing is printed to stdout. It is necessary not only to get the correct result, but also to print it to the stdout using print"
    assert correct_stdout == out.strip(), "Wrong output is printed to stdout"
