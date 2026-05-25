def retry_with_backoff(max_retries=5, initial_delay=1):
    """
    创建一个带重试机制的lambda函数
    
    参数:
        max_retries: 最大重试次数，默认5次
        initial_delay: 初始延迟时间（秒），默认1秒
    
    返回:
        一个lambda函数，可以包装其他函数实现重试
    """
    def retry_decorator(func):
        def wrapper(*args, **kwargs):
            import time
            retry_count = 0
            delay = initial_delay
            
            while retry_count < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise Exception(f"函数执行失败，已重试{max_retries}次，最后错误: {str(e)}")
                    
                    print(f"第{retry_count}次重试，等待{delay}秒后重试...")
                    time.sleep(delay)
                    delay *= 2  # 指数退避策略
            
            return None
        
        return wrapper
    
    return retry_decorator


# 使用示例
if __name__ == "__main__":
    # 创建一个带重试机制的lambda函数
    risky_operation = retry_with_backoff(max_retries=5)(lambda x: 1 / x if x != 0 else 1/0)
    
    # 测试成功的调用
    try:
        result = risky_operation(10)
        print(f"执行成功，结果: {result}")
    except Exception as e:
        print(f"执行失败: {e}")
    
    # 测试会失败的调用
    try:
        result = risky_operation(0)
        print(f"执行成功，结果: {result}")
    except Exception as e:
        print(f"执行失败: {e}")
    
    # 使用装饰器的方式
    @retry_with_backoff(max_retries=3)
    def save_file(content, filepath):
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"文件保存成功: {filepath}")
    
    # 测试保存文件
    try:
        save_file("测试内容", "/tmp/test_file.txt")
    except Exception as e:
        print(f"保存文件失败: {e}")
