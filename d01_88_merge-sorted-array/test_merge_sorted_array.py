import pytest

from merge_sorted_array import Solution

# helper to easily test both implementations without changing the tests
pytestmark = pytest.mark.parametrize(
    "method",
    [Solution.merge, Solution.naiveMerge]
)


def test_case1(method):
    nums1 = [1,2,3,0,0,0]
    m = 3
    nums2 = [2,5,6]
    n = 3

    method(nums1, m, nums2, n)
    assert nums1 == [1,2,2,3,5,6]


def test_case2(method):
    nums1 = [1]
    m = 1
    nums2 = []
    n = 0

    method(nums1, m, nums2, n)
    assert nums1 == [1]


def test_case3(method):
    nums1 = [0]
    m = 0
    nums2 = [1]
    n = 1

    method(nums1, m, nums2, n)
    assert nums1 == [1]


def test_case4(method):
    nums1 = [2, 0]
    m = 1
    nums2 = [1]
    n = 1

    method(nums1, m, nums2, n)
    assert nums1 == [1,2]


def test_case5(method):
    nums1 = [0,0,0,0,0]
    m = 0
    nums2 = [1,2,3,4,5]
    n = 5

    method(nums1, m, nums2, n)
    assert nums1 == [1,2,3,4,5]

