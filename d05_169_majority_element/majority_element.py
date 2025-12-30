'''
Given an array `nums` of size `n`, return the majority element.

The majority element is the element that appears more than ⌊n / 2⌋ times.

You may assume that the majority element always exists in the array.

Follow-up: Could you solve the problem in linear time and in O(1) space?
'''

from collections import defaultdict


class Solution:
    @staticmethod
    def majorityElement(nums: list[int]) -> int:
        """
        Return the majority element (the element that appears more than n/2 times) in the given list of integers.

        Time complexity: O(N)
        Space complexity: O(N)
        """
        frequencies = defaultdict(int)
        length = len(nums)

        for num in nums:
            frequencies[num] += 1

            if frequencies[num] > length // 2:
                return num

        return -1  # This line should never be reached given the problem constraints
    
    @staticmethod
    def majorityElementOptimized(nums: list[int]) -> int:
        """
        Return the majority element (the element that appears more than n/2 times) in the given list of integers.

        Follow-up: Could you solve the problem in linear time and in O(1) space?

        Time complexity: O(N)
        Space complexity: O(1)
        """
        result = majority = 0
        
        for n in nums:
            if majority == 0:
                result = n
            
            majority += 1 if n == result else -1
        
        return result

