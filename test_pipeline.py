"""
测试pipeline.py中的text_preprocess方法
"""

from src.pipeline import Solver

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
	RD03	抗静电水性环氧树脂涂料的制备与应用研发	"一种抗静电环氧树脂涂料的制备方法ZL201910985915.5
水性环氧乳液制备管理系统2024SR0196400"	2022.1-2022.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	35%
	RD04	基于高精度金属加工工艺的铝制品的研发	"一种金属加工工作台ZL202320855804.4
一种金属制品加工定位模具ZL202320677793.5
一种铝膜生产用裁切机ZL202320835407.0"	2023.1-2023.12	新材料--金属材料--铝、铜、镁、钛合金清洁生产与深加工技术	38%
"""

# 创建Solver实例
solver = Solver()

# 测试text_preprocess方法
session_id = solver.text_preprocess(test_text)
print(f"生成的会话ID：{session_id}")

# 测试get_project_data方法
project_data = solver.get_project_data(session_id)

# 打印结果
print("\n从sessions中获取的解析结果：")
if isinstance(project_data, dict) and "error" in project_data:
    print(f"错误：{project_data['error']}")
else:
    print(f"公司名称：{project_data.name}")
    print(f"会话ID：{project_data.session_id}")
    print(f"项目数量：{len(project_data.projects)}")
    
    for i, project in enumerate(project_data.projects, 1):
        print(f"\n项目{i}：")
        print(f"  项目序号：{project.project_id}")
        print(f"  项目名称：{project.name}")
        print(f"  项目领域：{project.field}")
        print(f"  开始时间：{project.start_date}")
        print(f"  结束时间：{project.end_date}")
        print(f"  应用知识产权：{project.intellectual_property}")

# 验证结果格式
print("\n验证结果：")
if isinstance(project_data, dict) and "error" in project_data:
    print(f"✗ 解析失败：{project_data['error']}")
else:
    print(f"✓ 解析成功，返回Company实例")
    print(f"✓ 公司名称：{project_data.name}")
    print(f"✓ 包含{len(project_data.projects)}个项目")
    if project_data.projects:
        print("✓ 项目列表不为空")

# 测试不存在的会话ID
print("\n测试不存在的会话ID：")
non_existent_data = solver.get_project_data("non_existent")
print(non_existent_data)
