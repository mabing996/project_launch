"""
根据excel文本提取项目信息

文本示例

上海舜斯新材料科技有限公司					
高新技术产品	PS01	高精准铝制品	RD01、RD02、RD04、RD06、RD07			
	PS02	金属专用新型化学合成涂料	RD03、RD05、RD08			
研发项目	项目序号	项目名称	应用知识产权	项目时间	领域	研发费用建议分配比例
	RD01	高精度受热均匀的高纯度铝制品的研发	"一种用于金属热处理的高频感应加热设备ZL202123098145.4
一种铸造铝合金用导流管ZL202320853749.5"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	23%
	RD02	无磕碰与粘连的高精准铝制品的研发	"一种铝锭搬运装置ZL202222939332.9
一种防粘连铝板存放装置ZL202320901205.1"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	42%
	RD03	抗静电水性环氧树脂涂料的制备与应用研发	"一种抗静电环氧树脂涂料的制备方法ZL201910985915.5
水性环氧乳液制备管理系统2024SR0196400"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	35%
	RD04	基于高精度金属加工工艺的铝制品的研发	"一种金属加工工作台ZL202320855804.4
一种金属制品加工定位模具ZL202320677793.5
一种铝膜生产用裁切机ZL202320835407.0"	2023.1-2023.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	38%
	RD05	基于全自动精细研磨系统的化学合成涂料的研发	"分散机自动化运行控制系统2024SR1349350
乳液分散机智能研磨控制系统2023SR1520801
一种具有防护功能的全自动分散机ZL202222906160.5"	2023.1-2023.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	62%
	RD06	适用于高精准智能喷涂的铝制品表面处理技术研发	"铝卷智能喷涂控制系统2023SR0895277
有色金属冶炼温度调试系统2024SR1349390"	2024.1-2024.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	23%
	RD07	基于视觉识别有色金属压延表面缺陷检测的铝制品的研发	"有色金属压延生产缺陷检测系统2023SR1515942
基于视觉识别的铝板表面检测系统2023SR1521783"	2024.1-2024.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	42%
	RD08	基于智能控制搅拌系统的高性能化学合成涂料研发	"一种膨润土复合甲基丙烯酸聚合物高强度吸水剂及其制备方法ZL201910466194.7
智能混合搅拌树脂控制系统2024SR0200023
一种合成树脂用搅拌装置ZL202320490196.1
一种油漆生产中的油漆桶转运装置ZL202221656904.6"	2024.1-2024.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	35%

输出示例
{
    "公司名称": "xxx",
    "研发项目": [
        {
            "项目序号": "PS01",
            "项目名称": "高精准铝制品",
            "应用知识产权": 'xxx',
            "项目时间": "2022.1-2022.12",
            "领域": "新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术",
            "研发费用建议分配比例": "23%"
        },
        xxx
    ]
}

"""

import json
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import call_llm
from src.prompt import PROMPT
from src.project_classes import Company, Project


def extract_info(text: str) -> Company:
    """
    从文本中提取项目信息
    
    Args:
        text: Excel文本内容
        
    Returns:
        包含项目信息的Company类实例
    """
    # 构建完整的prompt
    full_prompt = PROMPT + text
    
    # 调用LLM
    response = call_llm(full_prompt)
    
    # 解析JSON响应
    try:
        response = response.strip(' `json').replace('\n', '')
        result = json.loads(response)
        
        # 创建Company实例
        company = Company(name=result.get("公司名称", ""))
        
        # 处理研发项目
        if "研发项目" in result:
            for project_data in result["研发项目"]:
                # 创建Project实例
                project = Project(
                    name=project_data.get("项目名称", ""),
                    project_id=project_data.get("项目序号", ""),
                    company=company,
                    start_date=project_data.get("项目时间", "").split("-")[0] if "-" in project_data.get("项目时间", "") else "",
                    end_date=project_data.get("项目时间", "").split("-")[1] if "-" in project_data.get("项目时间", "") else "",
                    field=project_data.get("领域", ""),
                    intellectual_property=project_data.get("应用知识产权", ""),
                )
                # 添加到公司的项目列表中
                company.projects.append(project)
        
        return company
    except json.JSONDecodeError as e:
        # 如果解析失败，返回一个包含错误信息的Company实例
        company = Company(name="")
        # 可以在这里添加错误信息到company的某个字段
        print(f"JSON解析错误: {str(e)}")
        return company


# 测试函数
if __name__ == "__main__":
    # 测试文本
    test_text = """
上海舜斯新材料科技有限公司                    
高新技术产品	PS01	高精准铝制品	RD01、RD02、RD04、RD06、RD07            
	PS02	金属专用新型化学合成涂料	RD03、RD05、RD08            
研发项目	项目序号	项目名称	应用知识产权	项目时间	领域	研发费用建议分配比例
	RD01	高精度受热均匀的高纯度铝制品的研发	"一种用于金属热处理的高频感应加热设备ZL202123098145.4
一种铸造铝合金用导流管ZL202320853749.5"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	23%
	RD02	无磕碰与粘连的高精准铝制品的研发	"一种铝锭搬运装置ZL202222939332.9
一种防粘连铝板存放装置ZL202320901205.1"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	42%
    """
    
    company = extract_info(test_text)
    print(f"公司名称：{company.name}")
    print(f"项目数量：{len(company.projects)}")
    
    for i, project in enumerate(company.projects, 1):
        print(f"\n项目{i}：")
        print(f"  项目序号：{project.project_id}")
        print(f"  项目名称：{project.name}")
        print(f"  项目领域：{project.field}")
        print(f"  开始时间：{project.start_date}")
        print(f"  结束时间：{project.end_date}")
