import pytest

from rotate_array import Solution

# helper to easily test both implementations without changing the tests
pytestmark = pytest.mark.parametrize(
    "method",
    [Solution.naiveRotate, Solution.rotate, Solution.rotateOptimized]
)


def test_case1(method):
    nums = [1,2,3,4,5,6,7]
    k = 3

    method(nums, k)

    expected = [5,6,7,1,2,3,4]
    assert nums == expected


def test_case2(method):
    nums = [-1,-100,3,99]
    k = 2

    method(nums, k)

    expected = [3,99,-1,-100]
    assert nums == expected


def test_case3(method):
    nums = [1]
    k = 0

    method(nums, k)

    expected = [1]
    assert nums == expected


def test_case4(method):
    nums = [1, 2]
    k = 1

    method(nums, k)

    expected = [2, 1]
    assert nums == expected


def test_case5(method):
    nums = [1,2,3]
    k = 1

    method(nums, k)

    expected = [3, 1, 2]
    assert nums == expected


def test_case6(method):
    nums = [1,2,3,4,5,6]
    k = 3

    method(nums, k)

    expected = [4,5,6,1,2,3]
    assert nums == expected


def test_case7(method):
    nums = [1,2]
    k = 7

    method(nums, k)

    expected = [2, 1]
    assert nums == expected

