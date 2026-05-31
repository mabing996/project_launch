"""
生成立项报告的函数
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import call_llm
from src.prompt import PROJECT_REPORT_PROMPT, PROJECT_NOTIFICATION_PROMPT, PROJECT_ACCEPTANCE_PROMPT, REFERENCE_REPORT
from src.project_classes import Project


def generate_project_report(
    project: Project
) -> dict:
    """
    生成立项报告
    
    Args:
        project: 项目对象
        
    Returns:
        生成的立项报告结构化数据
    """
    # 构建prompt，强调专利成果
    # prompt = PROJECT_REPORT_PROMPT % (REFERENCE_REPORT,
    #                              project.company.name,
    #                              "", 
    #                              "", 
    #                              project.name, 
    #                              project.start_date,
    #                               project.end_date, 
    #                               "")
    # 在prompt中添加专利成果强调
    prompt = PROJECT_REPORT_PROMPT.replace("{company_name}", project.company.name)
    prompt = prompt.replace("{project_name}", project.name)
    prompt = prompt.replace("{core_technologies}", project.intellectual_property)
    prompt = prompt.replace("{example}", REFERENCE_REPORT)

    prompt = f"{prompt}\n\n特别注意：请在报告中重点体现项目的专利成果，包括以下专利详细信息：\n{project.patent_info}\n请重点突出专利成果的技术价值和创新点，但不要直接引用名字。"\
             f"内容不要包含专利名称或编号，也不准包含日期"\
             f"注意因果，专利成果是该项目的产出，所以你不能说‘根据公司现有技术’"\
             f"内容量与模版相当。双引号等符号要用中文符号。"
    # 调用LLM生成报告
    response = call_llm(prompt)
    
    # 解析响应为结构化数据
    import json
    try:
        response = response.strip(' `json').replace('\n', '')
        # result = json.loads(response)
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始响应
        structured_data = {"error": "解析失败", "original_response": response}
    
    return structured_data





def generate_project_notification(
    project: Project
) -> dict:
    """
    生成立项通知
    
    Args:
        project: 项目对象
        
    Returns:
        生成的立项通知结构化数据
    """
    project_team = project.team_members if project.team_members else []
    
    # 构建prompt，强调专利成果
    # prompt = PROJECT_NOTIFICATION_PROMPT % (project.company.name, project.name, "", ", ".join(project_team), project.start_date, project.end_date, "", "", project.project_id)

    prompt = PROJECT_NOTIFICATION_PROMPT.replace("{company_name}", project.company.name)
    prompt = prompt.replace("{project_name}", project.name)
    prompt = prompt.replace("{core_technologies}", project.intellectual_property)

    # 在prompt中添加专利成果强调
    prompt = f"{prompt}\n\n特别注意：该项目产出了如下知识产权成果，专利详细信息有：\n{project.patent_info}\n请重点突出专利成果的技术价值和创新点，但不要直接引用名字。"\
             f"内容不要包含专利名称或编号，也不准包含日期"\
             f"注意因果，专利成果是该项目的产出，所以你不能说‘根据公司现有技术’"\
             f"内容量与模版相当。双引号等符号要用中文符号。"
    
    # 调用LLM生成通知
    response = call_llm(prompt)
    
    # 解析响应为结构化数据
    import json
    try:
        response = response.strip(' `json').replace('\n', '')
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始响应
        structured_data = {"error": "解析失败", "original_response": response}
    
    return structured_data


def generate_project_acceptance_report(
    project: Project
) -> dict:
    """
    生成验收报告
    
    Args:
        project: 项目对象
        
    Returns:
        生成的验收报告结构化数据
    """
    core_technologies = []
    innovations = []
    acceptance_contents = []
    
    # 构建prompt，强调专利成果
    # prompt = PROJECT_ACCEPTANCE_PROMPT % (
    #     project.company.name, 
    #     project.name, 
    #     f"项目产出了{project.intellectual_property}等知识产权成果", 
    # )
    # 在prompt中添加专利成果强调
    prompt = PROJECT_ACCEPTANCE_PROMPT.replace("{company_name}", project.company.name)
    prompt = prompt.replace("{project_name}", project.name)
    prompt = prompt.replace("{core_technologies}", project.intellectual_property)

    # 在prompt中添加专利成果强调
    prompt = f"{prompt}\n\n特别注意：该项目产出了如下知识产权成果，专利详细信息有：\n{project.patent_info}\n请重点突出专利成果的技术价值和创新点，但不要直接引用名字。"\
             f"仅项目概况可以包含专利名称，其他部分不要包含专利名称或编号。内容不准包含日期"\
             f"注意因果，专利成果是该项目的产出，所以你不能说‘根据公司现有技术’"\
             f"此外，核心技术点要与立项报告的项目目标一一对应。"\
             f"立项报告的项目目标如下："\
             f'{project.report["项目目标"]}'\
             f"项目概况包含的知识产权成果需要带有编号"\
             f"内容量与模版相当。双引号等符号要用中文符号。"
    
    # 调用LLM生成验收报告
    response = call_llm(prompt)
    
    # 解析响应为结构化数据
    import json
    try:
        response = response.strip(' `json').replace('\n', '')
        structured_data = json.loads(response)
    except json.JSONDecodeError:
        # 如果解析失败，返回原始响应
        structured_data = {"error": "解析失败", "original_response": response}
    
    return structured_data


# 测试函数
if __name__ == "__main__":
    # 从project_data.json加载项目数据
    from src.pipeline import pipeline
    company = pipeline()
    
    if company and company.projects:
        # 选择第一个项目进行测试
        project = company.projects[0]
        
        print(f"使用项目：{project.name} 进行测试\n")
        
        # 测试生成立项报告
        print("=== 测试生成立项报告 ===")
        report = generate_project_report(project=project)
        
        # 保存报告
        import json
        with open("测试立项报告.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print("立项报告已生成并保存到：测试立项报告.json")
        print("\n报告内容预览：")
        print(json.dumps(report, ensure_ascii=False, indent=2)[:500] + "...")
        
        # 测试生成立项通知
        print("\n\n=== 测试生成立项通知 ===")
        notification = generate_project_notification(project=project)
        
        # 保存通知
        with open("测试立项通知.json", "w", encoding="utf-8") as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)
        
        print("立项通知已生成并保存到：测试立项通知.json")
        print("\n通知内容预览：")
        print(json.dumps(notification, ensure_ascii=False, indent=2)[:500] + "...")
        
        # 测试生成验收报告
        print("\n\n=== 测试生成验收报告 ===")
        acceptance = generate_project_acceptance_report(project=project)
        
        # 保存验收报告
        with open("测试验收报告.json", "w", encoding="utf-8") as f:
            json.dump(acceptance, f, ensure_ascii=False, indent=2)
        
        print("验收报告已生成并保存到：测试验收报告.json")
        print("\n验收报告内容预览：")
        print(json.dumps(acceptance, ensure_ascii=False, indent=2)[:500] + "...")
    else:
        print("无法加载项目数据，请确保project_data.json文件存在且格式正确")
