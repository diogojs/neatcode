import pytest

from remove_duplicate import Solution

# helper to easily test both implementations without changing the tests
pytestmark = pytest.mark.parametrize(
    "method",
    [Solution.naiveRemoveDuplicates, Solution.removeDuplicates]
)


def test_case1(method):
    nums = [1,1,2]

    k = method(nums)

    expected_nums = [1,2]
    assert k == len(expected_nums)
    assert nums[:k] == expected_nums


def test_case2(method):
    nums = [0,0,1,1,1,2,2,3,3,4]

    k = method(nums)

    expected_nums = [0,1,2,3,4]
    assert k == len(expected_nums)
    assert nums[:k] == expected_nums


def test_case3(method):
    nums = [2]

    k = method(nums)

    expected_nums = [2]
    assert k == len(expected_nums)
    assert nums[:k] == expected_nums

