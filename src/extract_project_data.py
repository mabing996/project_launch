"""
提取科研项目立项报告书数据
支持处理多个文件，以字典格式存储，每个字段是数组
"""

import re
from pathlib import Path
from typing import List, Dict, Any


def parse_project_file(file_path: str) -> Dict[str, Any]:
    """
    解析单个项目文件，提取结构化数据
    
    Args:
        file_path: 文件路径
        
    Returns:
        解析后的项目数据字典
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析文本，去除行号和空白
    texts = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 去除行号前缀（如 "1. " 或 "10. "）
        match = re.match(r'^\d+\.\s*(.*)$', line)
        if match:
            content = match.group(1).strip()
            if content:
                texts.append(content)
        else:
            texts.append(line)
    
    # 严格按照t.txt结构提取数据
    project_data = {
        "立项报告书": {
            "项目背景": [],
            "项目目标": [],
            "预期效益": [],
            "面临的挑战": []
        },
        "项目立项通知": {
            "各部门": "",
            "项目信息": [],
            "工作要求": []
        },
        "项目验收报告": {
            "项目概况": [],
            "项目目标与完成情况": [],
            "核心技术点": [],
            "创新点": [],
            "验收内容": [],
            "验收结论": []
        }
    }
    
    # 解析各个部分
    section = ""
    sub_section = ""
    
    for text in texts:
        # 识别章节
        if text == "一、项目背景":
            section = "项目背景"
            sub_section = ""
        elif text == "二、项目目标":
            section = "项目目标"
            sub_section = ""
        elif text == "三、预期效益与挑战":
            section = "预期效益与挑战"
            sub_section = ""
        elif text == "（一）预期效益":
            sub_section = "预期效益"
        elif text == "（二）面临的挑战":
            sub_section = "面临的挑战"
        elif text == "项目立项通知":
            section = "项目立项通知"
            sub_section = ""
        elif text == "各部门：":
            sub_section = "各部门"
        elif text == "一、项目信息":
            sub_section = "项目信息"
        elif text == "二、工作要求":
            sub_section = "工作要求"
        elif text == "项目验收报告":
            section = "项目验收报告"
            sub_section = ""
        elif text == "一、项目概况":
            sub_section = "项目概况"
        elif text == "二、项目目标与完成情况":
            sub_section = "项目目标与完成情况"
        elif text == "三、项目核心技术点与创新点":
            sub_section = "核心技术点与创新点"
        elif text == "1. 核心技术点":
            sub_section = "核心技术点"
        elif text == "2. 创新点":
            sub_section = "创新点"
        elif text == "五、项目验收情况":
            sub_section = "验收情况"
        elif text == "（一）验收内容":
            sub_section = "验收内容"
        elif text == "（二）验收结论":
            sub_section = "验收结论"
        
        # 填充内容
        elif section == "项目背景" and text and text != "一、项目背景":
            project_data["立项报告书"]["项目背景"].append(text)
        elif section == "项目目标" and text and text != "二、项目目标":
            project_data["立项报告书"]["项目目标"].append(text)
        elif section == "预期效益与挑战":
            if sub_section == "预期效益" and text and text != "（一）预期效益":
                project_data["立项报告书"]["预期效益"].append(text)
            elif sub_section == "面临的挑战" and text and text != "（二）面临的挑战":
                project_data["立项报告书"]["面临的挑战"].append(text)
        elif section == "项目立项通知":
            if sub_section == "各部门" and text and text != "各部门：":
                project_data["项目立项通知"]["各部门"] = text
            elif sub_section == "项目信息" and text and text != "一、项目信息":
                project_data["项目立项通知"]["项目信息"].append(text)
            elif sub_section == "工作要求" and text and text != "二、工作要求":
                project_data["项目立项通知"]["工作要求"].append(text)
        elif section == "项目验收报告":
            if sub_section == "项目概况" and text and text != "一、项目概况":
                project_data["项目验收报告"]["项目概况"].append(text)
            elif sub_section == "项目目标与完成情况" and text and text != "二、项目目标与完成情况":
                project_data["项目验收报告"]["项目目标与完成情况"].append(text)
            elif sub_section == "核心技术点" and text and text != "1. 核心技术点":
                project_data["项目验收报告"]["核心技术点"].append(text)
            elif sub_section == "创新点" and text and text != "2. 创新点":
                project_data["项目验收报告"]["创新点"].append(text)
            elif sub_section == "验收内容" and text and text != "（一）验收内容":
                project_data["项目验收报告"]["验收内容"].append(text)
            elif sub_section == "验收结论" and text and text != "（二）验收结论":
                project_data["项目验收报告"]["验收结论"].append(text)
    
    return project_data

def is_company_name(text: str) -> bool:
    """判断文本是否为公司名称"""
    if not text or len(text) < 5:
        return False
    
    exclude_keywords = [
        "项目", "报告", "通知", "部门", "管理", "研发", "技术", "材料", "产品",
        "一、", "二、", "三、", "（一）", "（二）", "（三）", "1.", "2.",
        "立项编号", "发文日期", "项目名称", "项目团队", "项目周期", "项目预算",
        "验收", "概况", "目标", "效益", "挑战", "要求", "结论", "统计"
    ]
    
    for keyword in exclude_keywords:
        if keyword in text:
            return False
    
    company_suffixes = [
        "有限公司", "股份有限公司", "科技有限公司", "新材料科技有限公司",
        "集团", "公司", "企业", "厂", "实业", "发展"
    ]
    
    for suffix in company_suffixes:
        if text.endswith(suffix) or suffix in text:
            return True
    
    if len(text) >= 6 and not any(keyword in text for keyword in exclude_keywords):
        return True
    
    return False

def is_year(text: str) -> bool:
    """判断文本是否为年份格式"""
    if not text:
        return False
    
    year_pattern = r'^\d{4}年$'
    if re.match(year_pattern, text):
        return True
    
    date_pattern = r'^\d{4}年\d{1,2}月\d{1,2}日$'
    if re.match(date_pattern, text):
        return True
    
    return False

def extract_projects_data(file_paths: List[str]) -> Dict[str, Any]:
    """
    提取多个项目文件的数据，以字典格式存储，每个字段是数组
    
    Args:
        file_paths: 文件路径列表
        
    Returns:
        包含所有项目数据的字典，每个字段是数组
    """
    all_projects = []
    
    for file_path in file_paths:
        try:
            project_data = parse_project_file(file_path)
            all_projects.append(project_data)
            print(f"成功解析: {file_path}")
        except Exception as e:
            print(f"解析失败 {file_path}: {e}")
    
    # 严格按照t.txt结构转换为每个字段是数组的格式
    result = {
        "立项报告书": {
            "项目背景": [],
            "项目目标": [],
            "预期效益": [],
            "面临的挑战": []
        },
        "项目立项通知": {
            "各部门": [],
            "项目信息": [],
            "工作要求": []
        },
        "项目验收报告": {
            "项目概况": [],
            "项目目标与完成情况": [],
            "核心技术点": [],
            "创新点": [],
            "验收内容": [],
            "验收结论": []
        }
    }
    
    # 填充数据
    for project in all_projects:
        # 立项报告书
        result["立项报告书"]["项目背景"].append(project["立项报告书"]["项目背景"])
        result["立项报告书"]["项目目标"].append(project["立项报告书"]["项目目标"])
        result["立项报告书"]["预期效益"].append(project["立项报告书"]["预期效益"])
        result["立项报告书"]["面临的挑战"].append(project["立项报告书"]["面临的挑战"])
        
        # 项目立项通知
        result["项目立项通知"]["各部门"].append(project["项目立项通知"]["各部门"])
        result["项目立项通知"]["项目信息"].append(project["项目立项通知"]["项目信息"])
        result["项目立项通知"]["工作要求"].append(project["项目立项通知"]["工作要求"])
        
        # 项目验收报告
        result["项目验收报告"]["项目概况"].append(project["项目验收报告"]["项目概况"])
        result["项目验收报告"]["项目目标与完成情况"].append(project["项目验收报告"]["项目目标与完成情况"])
        result["项目验收报告"]["核心技术点"].append(project["项目验收报告"]["核心技术点"])
        result["项目验收报告"]["创新点"].append(project["项目验收报告"]["创新点"])
        result["项目验收报告"]["验收内容"].append(project["项目验收报告"]["验收内容"])
        result["项目验收报告"]["验收结论"].append(project["项目验收报告"]["验收结论"])
    
    return result


# 测试函数
if __name__ == "__main__":
    # 要处理的文件路径
    file_paths = [
        '/Users/swh/project_launch/assets/texts/RD01高精度受热均匀的高纯度铝制品的研发.txt',
        '/Users/swh/project_launch/assets/texts/RD02无磕碰与粘连的高精准铝制品的研发.txt'
    ]
    
    try:
        print("开始提取项目数据...")
        result = extract_projects_data(file_paths)
        
        print("\n" + "=" * 60)
        print("提取结果:")
        print("=" * 60)
        
        # 打印立项报告书摘要
        print("\n立项报告书 (摘要):")
        for i, background in enumerate(result["立项报告书"]["项目背景"]):
            print(f"项目 {i+1} 背景长度: {len(background)} 段")
            print(f"项目 {i+1} 目标长度: {len(result['立项报告书']['项目目标'][i])} 条")
            print(f"项目 {i+1} 预期效益长度: {len(result['立项报告书']['预期效益'][i])} 条")
            print(f"项目 {i+1} 面临的挑战长度: {len(result['立项报告书']['面临的挑战'][i])} 条")
        
        # 打印项目立项通知
        print("\n项目立项通知:")
        for i, dept in enumerate(result["项目立项通知"]["各部门"]):
            print(f"项目 {i+1} 各部门: {dept}")
            print(f"项目 {i+1} 项目信息长度: {len(result['项目立项通知']['项目信息'][i])} 条")
            print(f"项目 {i+1} 工作要求长度: {len(result['项目立项通知']['工作要求'][i])} 条")
        
        # 打印项目验收报告摘要
        print("\n项目验收报告 (摘要):")
        for i, overview in enumerate(result["项目验收报告"]["项目概况"]):
            print(f"项目 {i+1} 概况长度: {len(overview)} 段")
            print(f"项目 {i+1} 核心技术点: {len(result['项目验收报告']['核心技术点'][i])} 个")
            print(f"项目 {i+1} 创新点: {len(result['项目验收报告']['创新点'][i])} 个")
            print(f"项目 {i+1} 验收内容: {len(result['项目验收报告']['验收内容'][i])} 条")
            print(f"项目 {i+1} 验收结论: {len(result['项目验收报告']['验收结论'][i])} 条")
        
        print("\n" + "=" * 60)
        print("提取完成！")
        print("=" * 60)
        
        # 可以将结果保存为 JSON 文件
        import json
        with open('/Users/swh/project_launch/project_data.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("\n数据已保存到 project_data.json")
        
    except Exception as e:
        import traceback
        print(f"错误: {e}")
        traceback.print_exc()
