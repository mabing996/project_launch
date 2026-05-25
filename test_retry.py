#!/usr/bin/env python3
"""
测试retry_with_backoff函数的功能
"""

from docx_helper import texts
from src.retry_utils import retry_with_backoff
import time

def test_successful_operation():
    """测试成功的操作"""
    print("\n=== 测试1: 成功的操作 ===")
    
    @retry_with_backoff(max_retries=3)
    def divide_numbers(a, b):
        return a / b
    
    try:
        result = divide_numbers(10, 2)
        print(f"✓ 执行成功，结果: {result}")
    except Exception as e:
        print(f"✗ 执行失败: {e}")

def test_failing_operation():
    """测试会失败的操作"""
    print("\n=== 测试2: 会失败的操作 ===")
    
    @retry_with_backoff(max_retries=3, initial_delay=0.5)
    def divide_by_zero():
        return 1 / 0
    
    try:
        result = divide_by_zero()
        print(f"✓ 执行成功，结果: {result}")
    except Exception as e:
        print(f"✗ 执行失败（预期行为）: {e}")

def test_intermittent_failure():
    """测试间歇性失败"""
    print("\n=== 测试3: 间歇性失败（第2次成功） ===")
    
    call_count = [0]
    
    @retry_with_backoff(max_retries=5, initial_delay=0.5)
    def sometimes_fail():
        call_count[0] += 1
        print(f"  第{call_count[0]}次调用...")
        if call_count[0] < 2:
            raise Exception("模拟临时错误")
        return "成功！"
    
    try:
        result = sometimes_fail()
        print(f"✓ 执行成功，结果: {result}")
    except Exception as e:
        print(f"✗ 执行失败: {e}")

def test_lambda_usage():
    """测试lambda函数的使用"""
    print("\n=== 测试4: 使用lambda函数 ===")
    
    # 创建一个带重试的lambda函数
    risky_calculation = retry_with_backoff(max_retries=3)(lambda x: 1 / x if x != 0 else 1/0)
    
    # 测试成功的调用
    try:
        result = risky_calculation(10)
        print(f"✓ Lambda执行成功，结果: {result}")
    except Exception as e:
        print(f"✗ Lambda执行失败: {e}")
    
    # 测试会失败的调用
    try:
        result = risky_calculation(0)
        print(f"✓ Lambda执行成功，结果: {result}")
    except Exception as e:
        print(f"✗ Lambda执行失败（预期行为）: {e}")

def test_file_operations():
    """测试文件操作的重试"""
    print("\n=== 测试5: 文件操作 ===")
    
    import os
    import tempfile
    
    @retry_with_backoff(max_retries=3, initial_delay=0.5)
    def write_to_file(content, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"文件已保存: {filepath}"
    
    # 创建临时文件路径
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_file.txt")
    
    try:
        result = write_to_file("测试内容", temp_file)
        print(f"✓ {result}")
        
        # 验证文件内容
        with open(temp_file, 'r') as f:
            content = f.read()
            print(f"✓ 文件内容验证: {content}")
    except Exception as e:
        print(f"✗ 文件操作失败: {e}")
    finally:
        # 清理临时文件
        try:
            os.remove(temp_file)
            os.rmdir(temp_dir)
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("开始测试retry_with_backoff函数")
    print("=" * 60)
    text = """
    ```json
{
    "公司名称": "上海舜斯新材料科技有限公司",
    "研发项目": [
        {
            "项目序号": "RD02",
            "项目名称": "无磕碰与粘连的高精准铝制品的研发",
            "应用知识产权": "一种铝锭搬运装置ZL202222939332.9\n一种防粘连铝板存放装置ZL202320901205.1",
            "项目时间": "2022.1-2022.12",
            "领域": "新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术",
            "研发费用建议分配比例": "42%"
        },
        {
            "项目序号": "RD03",
            "项目名称": "抗静电水性环氧树脂涂料的制备与应用研发",
            "应用知识产权": "一种抗静电环氧树脂涂料的制备方法ZL201910985915.5\n水性环氧乳液制备管理系统2024SR0196400",
            "项目时间": "2022.1-2022.12",
            "领域": "新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术",
            "研发费用建议分配比例": "35%"
        },
        {
            "项目序号": "RD04",
            "项目名称": "基于高精度金属加工工艺的铝制品的研发",
            "应用知识产权": "一种金属加工工作台ZL202320855804.4\n一种金属制品加工定位模具ZL202320677793.5\n一种铝膜生产用裁切机ZL202320835407.0",
            "项目时间": "2023.1-2023.12",
            "领域": "新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术",
            "研发费用建议分配比例": "38%"
        }
    ]
}
```
"""
    import json
    text
    print(1)
    test_successful_operation()
    test_failing_operation()
    test_intermittent_failure()
    test_lambda_usage()
    test_file_operations()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
