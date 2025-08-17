def calculate_sum_1_to_10():
    """
    计算1到10的和
    返回值：整数，表示1到10的总和
    """
    total = 0
    for i in range(1, 11):
        total += i
    return total

# 另一种更简洁的实现方式
def calculate_sum_1_to_10_simple():
    """
    使用内置sum函数计算1到10的和
    返回值：整数，表示1到10的总和
    """
    return sum(range(1, 11))

# 使用数学公式的实现方式
def calculate_sum_1_to_10_formula():
    """
    使用等差数列求和公式：n*(n+1)/2
    返回值：整数，表示1到10的总和
    """
    n = 10
    return n * (n + 1) // 2

# 测试函数
if __name__ == "__main__":
    print("方法1 - 循环求和:", calculate_sum_1_to_10())
    print("方法2 - sum函数:", calculate_sum_1_to_10_simple())
    print("方法3 - 数学公式:", calculate_sum_1_to_10_formula())
