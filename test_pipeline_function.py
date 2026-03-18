"""
测试pipeline函数，验证其能否正确读取project_data.json文件并还原project_data
"""

from src.pipeline import pipeline

# 调用pipeline函数
project_data = pipeline()

# 验证结果
if project_data:
    print("项目数据还原成功！")
    print(f"公司名称: {project_data.name}")
    print(f"项目数量: {len(project_data.projects)}")
    
    for i, project in enumerate(project_data.projects, 1):
        print(f"\n项目{i}:")
        print(f"  项目序号: {project.project_id}")
        print(f"  项目名称: {project.name}")
        print(f"  项目领域: {project.field}")
        print(f"  应用知识产权: {project.intellectual_property}")
        print(f"  专利详细信息: {project.patent_info}")
        print(f"  开始时间: {project.start_date}")
        print(f"  结束时间: {project.end_date}")
else:
    print("项目数据还原失败！")
