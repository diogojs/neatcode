class Solution:
    @staticmethod
    def naiveMerge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        First implementation.

        Time complexity: O(m+n)
        Space complexity: O(m+n)
        """
        aux = []
        i = 0
        j = 0
        while i < m or j < n:
            a = nums1[i] if i < m else float('inf')
            b = nums2[j] if j < n else float('inf')
            if a <= b:
                aux.append(a)
                i += 1
            else:
                aux.append(b)
                j += 1
        nums1.clear()
        nums1.extend(aux)

    @staticmethod
    def merge(nums1: list[int], m: int, nums2: list[int], n: int) -> None:
        """
        Do not return anything, modify nums1 in-place instead.

        Time complexity: O(m+n)
        Space complexity: O(1)
        """
        i = 1
        j = 1
        for x in range(1,m+n+1):
            if j > n:
                break
            a = nums1[m-i]
            b = nums2[-j]
            if i <= m and a > b:
                nums1[-x] = a
                i += 1
            else:
                nums1[-x] = b
                j += 1

