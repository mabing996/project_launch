"""
加载和查看保存的项目数据
"""

import json

# 加载保存的项目数据
try:
    with open("project_data.json", "r", encoding="utf-8") as f:
        project_data_dict = json.load(f)
    
    print("项目数据加载成功！")
    print(f"公司名称: {project_data_dict['name']}")
    print(f"项目数量: {len(project_data_dict['projects'])}")
    
    for i, project in enumerate(project_data_dict['projects'], 1):
        print(f"\n项目{i}:")
        print(f"  项目序号: {project['project_id']}")
        print(f"  项目名称: {project['name']}")
        print(f"  项目领域: {project['field']}")
        print(f"  应用知识产权: {project['intellectual_property']}")
        print(f"  专利详细信息: {project['patent_info']}")
        print(f"  开始时间: {project['start_date']}")
        print(f"  结束时间: {project['end_date']}")
        
except FileNotFoundError:
    print("错误: 未找到 project_data.json 文件")
except Exception as e:
    print(f"错误: {str(e)}")
