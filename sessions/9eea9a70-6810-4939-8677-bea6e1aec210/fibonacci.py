def fibonacci_sequence(n):
    """
    计算斐波那契数列的前n项
    
    参数:
        n (int): 要计算的项数
    
    返回:
        list: 包含前n项斐波那契数的列表
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    # 初始化前两项
    fib_sequence = [0, 1]
    
    # 计算后续项
    for i in range(2, n):
        next_fib = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_fib)
    
    return fib_sequence

def print_fibonacci_10():
    """
    打印斐波那契数列的前10项
    """
    result = fibonacci_sequence(10)
    print("斐波那契数列的前10项:")
    for i, num in enumerate(result):
        print(f"第{i+1}项: {num}")
    
    return result

# 主程序
if __name__ == "__main__":
    # 计算并显示前10项
    fib_10 = print_fibonacci_10()
    
    # 也可以直接打印列表
    print(f"\n完整列表: {fib_10}")
