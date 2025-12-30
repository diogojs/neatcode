'''
Given an integer array `nums` sorted in non-decreasing order, remove some duplicates in-place such that each unique element appears at most twice.
The relative order of the elements should be kept the same.

Consider the number of unique/twin elements in `nums` to be `k`. After removing extra duplicates, return the number of elements `k`.

The first `k` elements of `nums` should contain the valid numbers in sorted order. The remaining elements beyond index `k - 1` can be ignored.

Do NOT allocate extra space for another array. You must do this by modifying the input array in-place with O(1) extra memory.
'''

class Solution:
    @staticmethod
    def removeDuplicates(nums: list[int]) -> int:
        """
        Remove some duplicates in nums (in-place), such that each element appears at most twice. The relative order of the elements is kept the same.

        As the array is already sorted, we can use just a "pointer" to the latest unique element (and a flag to know if it has a second appearance), then iterate through the array
        comparing with the latest unique and update the pointer if we have a new unique value.

        Time complexity: O(N)
        Space complexity: O(1)
        """
        k = 0
        duplicates = False

        for value in nums[1:]:
            if value != nums[k]:
                k += 2 if duplicates else 1
                nums[k] = value
                duplicates = False
            else:
                duplicates = True
                nums[k+1] = value

        if duplicates:  # last value was duplicate but we didn't fall into the first if, so we need to manually add it
            k += 1
            nums[k] = value

        return k + 1
