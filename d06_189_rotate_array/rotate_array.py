'''
Given an integer array `nums`, rotate the array to the right by `k` steps, where k is non-negative.

Follow up:
- Try to come up with as many solutions as you can. There are at least three different ways to solve this problem.
- Could you do it in-place with O(1) extra space?
'''


class Solution:
    @staticmethod
    def naiveRotate(nums: list[int], k: int) -> None:
        """
        Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

        Time complexity: O(N)
        Space complexity: O(N)
        """
        for i, v in enumerate(nums.copy()):
            nums[(i+k) % len(nums)] = v
    
    @staticmethod
    def rotate(nums: list[int], k: int) -> None:
        """
        Time complexity: O(N)
        Space complexity: O(1)
        """
        nums[:] = nums[-k % len(nums):] + nums[:-k % len(nums)]
    
    @staticmethod
    def rotateOptimized(nums: list[int], k: int) -> None:
        """
        Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

        Time complexity: O(N)
        Space complexity: O(1)
        """
        # [1,2,3,4,5,6,7]
        if k == 0 or len(nums) <= 1:
            return

        i = 0
        displaced = nums[i]
        iterations = 0
        while i != len(nums) - k and iterations < len(nums):
            new_pos = (i+k) % len(nums)
            displaced, nums[new_pos] = nums[new_pos], displaced
            i = new_pos
            iterations += 1
        
        new_pos = (i+k) % len(nums)
        nums[new_pos] = displaced

        if k > 1 and len(nums) / k == len(nums) // k:
            i = 1
            displaced = nums[i]
            iterations = 0

            if (i+k) % len(nums) == new_pos:
                return
            
            while i != len(nums) - k + 1 and iterations < len(nums):
                new_pos = (i+k) % len(nums)
                displaced, nums[new_pos] = nums[new_pos], displaced
                i = new_pos
                iterations += 1
            
            new_pos = (i+k) % len(nums)
            nums[new_pos] = displaced
