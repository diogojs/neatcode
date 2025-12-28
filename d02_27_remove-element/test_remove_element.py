import pytest

from remove_element import Solution

# helper to easily test both implementations without changing the tests
pytestmark = pytest.mark.parametrize(
    "method",
    [Solution.naiveRemoveElement]#, Solution.naiveRemoveElement]
)


def test_case1(method):
    nums = [3,2,2,3]
    val = 3

    k = method(nums, val)

    expected_nums = [2,2]
    sorted_nums = sorted(nums[:k])
    assert k == len(expected_nums)
    assert sorted_nums == expected_nums


def test_case2(method):
    nums = [0,1,2,2,3,0,4,2]
    val = 2

    k = method(nums, val)

    expected_nums = [0,0,1,3,4]
    sorted_nums = sorted(nums[:k])
    assert k == len(expected_nums)
    assert sorted_nums == expected_nums


def test_case3(method):
    nums = [2]
    val = 3

    k = method(nums, val)

    expected_nums = [2]
    sorted_nums = sorted(nums[:k])
    assert k == len(expected_nums)
    assert sorted_nums == expected_nums



def test_case4(method):
    nums = []
    val = 0

    k = method(nums, val)

    expected_nums = []
    sorted_nums = sorted(nums[:k])
    assert k == len(expected_nums)
    assert sorted_nums == expected_nums