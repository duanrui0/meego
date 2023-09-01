# -*- coding:utf-8 -*-
"""
作者：duanRui
日期：2023年09月02日
"""


def bubble_sort(arr):
    n = len(arr)

    for i in range(n):
        # 每次遍历将最大的元素冒泡到末尾
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

    return arr
if __name__ == '__main__':

    print (bubble_sort([3,3534,6546,123,123,123,123,2]))