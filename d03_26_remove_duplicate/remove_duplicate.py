'''
Given an integer array `nums` sorted in non-decreasing order, remove the duplicates in-place such that each unique element appears only once.
The relative order of the elements should be kept the same.

Consider the number of unique elements in `nums` to be `k`. After removing duplicates, return the number of unique elements `k`.

The first `k` elements of `nums` should contain the unique numbers in sorted order. The remaining elements beyond index `k - 1` can be ignored.
'''

class Solution:
    @staticmethod
    def naiveRemoveDuplicates(nums: list[int]) -> int:
        """
        Remove all duplicates in nums (in-place). Returns the number of unique elements.

        First implementation, using auxiliary sets.

        Time complexity: O(N)
        Space complexity: O(N)
        """
        k = 0
        uniques = set()
        duplicates = set()

        for i, value in enumerate(nums):
            if value not in uniques:
                uniques.add(value)
                k += 1
                if duplicates:
                    available_index = duplicates.pop()
                    nums[available_index] = value
                    duplicates.add(i)
            else:
                duplicates.add(i)

        return k

    @staticmethod
    def removeDuplicates(nums: list[int]) -> int:
        """
        Remove all duplicates in nums (in-place). Returns the number of unique elements.

        As the array is already sorted, we can use just a "pointer" to the latest unique element, then iterate through the array
        comparing with the latest unique and update the pointer if we have a new unique value.

        Time complexity: O(N)
        Space complexity: O(1)
        """
        k = 0
        for value in nums:
            if value != nums[k]:
                k += 1
                nums[k] = value

        return k + 1
