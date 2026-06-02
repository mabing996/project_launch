


from src.pipeline import Solver, pipeline
import json



with open("./project_data.json", "r", encoding="utf-8") as f:
    project_data_dict = json.load(f)
res = pipeline(project_data_dict=project_data_dict)
print(res)





