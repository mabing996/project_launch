import os
from openai import OpenAI
from typing import Optional, List, Dict, Any


API_KEY='4b96aa7c-a15f-45f9-9ffb-4d453923c927'

def get_client() -> OpenAI:
    """
    初始化OpenAI客户端
    
    Returns:
        OpenAI客户端实例
    """
    api_key = API_KEY
    
    return OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key,
    )


def call_llm(
    prompt: str,
    # model: str = "doubao-seed-2-0-pro-260215",
    # model: str = "glm-4-7-251222",
    # model: str = "doubao-seed-1-8-251228",
    model = 'doubao-seed-2-0-mini-260428',
    messages: Optional[List[Dict[str, Any]]] = None
) -> Any:
    """
    调用大语言模型
    
    Args:
        prompt: 用户输入的提示文本
        model: 使用的模型名称，默认为doubao-seed-2-0-pro-260215
        messages: 可选的消息列表，如果不提供则使用prompt构建单轮对话
    
    Returns:
        模型响应对象
    """
    # 内部创建client
    # 使用蓝色输出LLM调用信息
    print(f'\033[34mcall_llm model: {model}, prompt: {prompt}\033[0m')
    client = get_client()
    
    if messages is None:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                ],
            }
        ]
    
    response = client.responses.create(
        model=model,
        input=messages
    )
    text = response.output_text

    print(f'\033[32mcall_llm model: {model}, text: {text}\033[0m')
    return text


def main():
    """
    主函数，演示如何使用LLM调用函数
    """
    response = call_llm("你好")
    print(response)


if __name__ == "__main__":
    main()
