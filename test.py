


from src.pipeline import Solver, pipeline
import json
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python test.py <json_path>")
    sys.exit(1)

json_path = sys.argv[1]

if not os.path.exists(json_path):
    print(f"错误: 未找到文件 {json_path}")
    sys.exit(1)

print(f"开始处理文件: {json_path}")

with open(json_path, "r", encoding="utf-8") as f:
    project_data_dict = json.load(f)
res = pipeline(project_data_dict=project_data_dict)
print(res)





