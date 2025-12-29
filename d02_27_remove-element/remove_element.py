'''
Given an integer array nums and an integer val, remove all occurrences of val in nums in-place.
The order of the elements may be changed.
Then return the number of elements in nums which are not equal to val.

Consider the number of elements in nums which are not equal to val be k, to get accepted, you need to do the following things:
- Change the array nums such that the first k elements of nums contain the elements which are not equal to val.
    The remaining elements of nums are not important as well as the size of nums.
- Return k.
'''

class Solution:
    @staticmethod
    def naiveRemoveElement(nums: list[int], val: int) -> int:
        """
        First implementation.

        Time complexity: O(N²)
        Space complexity: O(1)
        """
        lenght = len(nums)
        k = 0
        for x in range(lenght):
            if nums[x] == val:
                for i in range(x+1, lenght):
                    if nums[i] != val:
                        nums[x], nums[i] = nums[i], nums[x]  # swap
                        break
                else:
                    break  # there is no more valid number (the rest of the array is all equal to val)
            k += 1
        
        return k

    @staticmethod
    def removeElement(nums: list[int], val: int) -> int:
        """
        Remove all occurrences of val in nums (in-place)

        Time complexity: O(N)
        Space complexity: O(N)
        """
        target_indexes = []
        k = 0
        for i, v in enumerate(nums):
            if v == val:
                target_indexes.append(i)
            else:
                k += 1
                if target_indexes:
                    target_index = target_indexes.pop(0)
                    nums[target_index] = v
                    nums[i] = val
                    target_indexes.append(i)

        return k
