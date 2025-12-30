import pytest

from majority_element import Solution

# helper to easily test both implementations without changing the tests
pytestmark = pytest.mark.parametrize(
    "method",
    [Solution.majorityElement, Solution.majorityElementOptimized]
)


def test_case1(method):
    nums = [3,2,3]

    k = method(nums)

    assert k == 3


def test_case2(method):
    nums = [2,2,1,1,1,2,2]

    k = method(nums)

    assert k == 2


def test_case3(method):
    nums =  [6,6,6,6,7,4,4,6,3]

    k = method(nums)

    assert k == 6

    