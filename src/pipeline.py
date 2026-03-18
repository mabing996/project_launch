from this import d
import uuid

from src.info_extractor import extract_info
from src.project_classes import Company

from src.doc_generate import generate_project_report,generate_project_notification,generate_project_acceptance_report
import os
import sys

# 获取当前文件的上一级路径
cur_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Solver:
    def __init__(self):
        self.sessions = {}
        pass

    def text_preprocess(self, text: str) -> str:
        random_id = uuid.uuid4().hex[:6]
        project_data = extract_info(text)
        project_data.session_id = random_id
        # 将解析结果保存到sessions字典中
        self.sessions[random_id] = project_data
        return random_id
    
    def get_project_data(self, session_id: str) -> dict:
        """
        根据session ID获取保存的项目数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            保存的项目数据字典
        """
        return self.sessions.get(session_id, {"error": "会话ID不存在"})



import json
from src.project_classes import Company, Project

def pipeline(project_data_dict):
    """
    读取project_data.json文件并还原project_data
    
    Returns:
        还原后的Company对象
    """

    # 读取project_data.json文件
    # with open("/Users/swh/project_launch/project_data.json", "r", encoding="utf-8") as f:
    #     project_data_dict = json.load(f)
    
    # 创建Company对象
    company = Company(
        name=project_data_dict.get("name", ""),
        industry=project_data_dict.get("industry", ""),
        location=project_data_dict.get("location", ""),
        established_year=project_data_dict.get("established_year", 0),
        description=project_data_dict.get("description", ""),
        core_technologies=project_data_dict.get("core_technologies", []),
        patents=project_data_dict.get("patents", []),
        session_id=project_data_dict.get("session_id", "")
    )
    
    # 创建Project对象并添加到Company的projects列表中
    for project_dict in project_data_dict.get("projects", []):
        project = Project(
            name=project_dict.get("name", ""),
            project_id=project_dict.get("project_id", ""),
            company=company,
            start_date=project_dict.get("start_date", ""),
            end_date=project_dict.get("end_date", ""),
            field=project_dict.get("field", ""),
            intellectual_property=project_dict.get("intellectual_property", ""),
            patent_info=project_dict.get("patent_info", ""),
            background=project_dict.get("background", ""),
            objectives=project_dict.get("objectives", []),
            expected_benefits=project_dict.get("expected_benefits", []),
            challenges=project_dict.get("challenges", []),
            budget=project_dict.get("budget", ""),
            team_members=project_dict.get("team_members", [])
        )
        company.projects.append(project)
        
    

    ## 生成立项报告
    # project_reports = []
    # for project in company.projects:
    #     doc_path = process_one_project(project)
    #     project_reports.append(doc_path)
    return _pipeline(company)


def _pipeline(company):
    import multiprocessing
    
    # 使用多进程并行处理项目
    project_reports = []
    with multiprocessing.Pool() as pool:
        project_reports = pool.map(process_one_project, company.projects)

    return project_reports


def process_one_project(project: Project) -> dict:
    """
    处理一个项目，生成项目报告
    
    Args:
        project: 项目对象
        
    Returns:
        项目报告结构化数据
    """
    project_report = generate_project_report(project)
    project_notification = generate_project_notification(project)
    project_acceptance_report = generate_project_acceptance_report(project)

    doc_template_path = './assets/索屿-专审材料/RD/高精准金型模具的研发.docx'

    from docx import Document
    doc = Document(doc_template_path)

    texts = [ para.text for para in doc.paragraphs]
    # for para in doc.paragraphs:
    #     if '项目名称' in para.text:
    #         para.text = para.text.replace('项目名称', project.name)
    ## 逐行替换
    # 替换项目名称
    # doc.paragraphs[4].text = doc.paragraphs[4].text.replace('高精准金型模具的研发', project.name)

    doc.paragraphs[4].runs[2].text = project.name
    # 替换企业名称
    # doc.paragraphs[5].text = doc.paragraphs[5].text.replace('上海索屿智能科技有限公司', project.company.name)
    doc.paragraphs[5].runs[2].text = project.company.name

    doc.paragraphs[6].runs[2].text = ''

    # 替换企业法人
    # doc.paragraphs[6].text = doc.paragraphs[6].text.replace('郑  涵', '')
    # 替换项目负责人
    # doc.paragraphs[7].text = doc.paragraphs[7].text.replace('汪永太', '')
    doc.paragraphs[7].runs[2].text = ''
    # 替换项目起止时间
    # doc.paragraphs[8].text = doc.paragraphs[8].text.replace('2024年01月至2024年12月', f'{project.start_date}至{project.end_date}')
    # 替换编制日期

    # doc.paragraphs[14].text = doc.paragraphs[14].text.replace('2024年01月04日', '')
    # # 替换立项通知中的项目名称
    # doc.paragraphs[54].text = doc.paragraphs[54].text.replace('高精准金型模具的研发', project.name)
    # # 替换立项通知中的项目负责人
    # doc.paragraphs[55].text = doc.paragraphs[55].text.replace('汪永太', '')
    # # 替换立项通知中的项目周期
    # doc.paragraphs[57].text = doc.paragraphs[57].text.replace('2024年01月04日至2024年12月31日', f'{project.start_date}至{project.end_date}')
    
    # 替换项目背景部分
    doc.paragraphs[21].text = project_report['项目背景']['国内背景']

    # 国际背景 
    # internation_bg = project_report['项目背景']['国际背景']
    # internation_bgs = internation_bg.split('；')
    # internation_bgs = [bg.strip() for bg in internation_bgs]

    doc.paragraphs[23].text = project_report['项目背景']['国际背景'][0]
    doc.paragraphs[24].text = project_report['项目背景']['国际背景'][1]
    doc.paragraphs[25].text = project_report['项目背景']['国际背景'][2]
    doc.paragraphs[26].text = project_report['项目背景']['国际背景'][3]





    doc.paragraphs[28].text = project_report['项目背景']['背景总结']
    
    # 替换项目目标部分
    # doc.paragraphs[29].text = '本项目聚焦于' + project.name + '的研发，重点突破相关关键技术，实现以下技术目标：'
    # for i, objective in enumerate(project_report['项目目标'], 30):
    #     doc.paragraphs[i].text = objective

    doc.paragraphs[30].text = project_report['项目目标'][0]
    doc.paragraphs[31].text = project_report['项目目标'][1]
    doc.paragraphs[32].text = project_report['项目目标'][2]
    doc.paragraphs[33].text = project_report['项目目标'][3]
    doc.paragraphs[34].text = project_report['项目目标'][4]
    


    # 替换预期效益与挑战部分
    doc.paragraphs[37].text = '经济效益：' + project_report['预期效益与挑战']['预期效益']['经济效益']
    doc.paragraphs[38].text = '社会效益：' + project_report['预期效益与挑战']['预期效益']['社会效益']
    doc.paragraphs[39].text = '技术效益：' + project_report['预期效益与挑战']['预期效益']['技术效益']
    
    doc.paragraphs[41].text = project_report['预期效益与挑战']['面临的挑战'][0]
    doc.paragraphs[42].text = project_report['预期效益与挑战']['面临的挑战'][1]
    doc.paragraphs[43].text = project_report['预期效益与挑战']['面临的挑战'][2]
    
    # for i, challenge in enumerate(project_report['预期效益与挑战']['面临的挑战'], 40):
    #     doc.paragraphs[i].text = challenge
    if project_report['预期效益与挑战']['项目预算'].startswith('项目预算'):
        doc.paragraphs[44].text = project_report['预期效益与挑战']['项目预算']
    else:
        doc.paragraphs[44].text = '项目预算：' + project_report['预期效益与挑战']['项目预算']
    
    doc.paragraphs[46].text = project.company.name

    # doc.paragraphs[46].text = 


    # 替换立项通知部分
    doc.paragraphs[50].text = project_notification['通知正文']
    doc.paragraphs[53].text = doc.paragraphs[53].text.replace('SOYU202403', '')

    doc.paragraphs[54].text = doc.paragraphs[54].text.replace('2024年01月04日', '')


    doc.paragraphs[55].text = '项目名称：' + project.name
    doc.paragraphs[56].text = '项目负责人：'
    # doc.paragraphs[56].text = '项目团队：' + ', '.join(project_notification['项目信息']['项目团队'])
    # doc.paragraphs[57].text = '项目周期：' + project_notification['项目信息']['项目周期']
    # doc.paragraphs[58].text = '项目预算：' + project_notification['项目信息']['项目预算']
    doc.paragraphs[57].text = '项目团队：'
    doc.paragraphs[58].text = '项目周期：'
    doc.paragraphs[59].text = '项目预算：' + project_notification['项目信息']['项目预算']


    doc.paragraphs[66].text = project.company.name

    # for i, requirement in enumerate(project_notification['工作要求'], 60):
    #     doc.paragraphs[i].text = requirement
    # doc.paragraphs[63].text = project_notification['结尾语']
    
    # 替换验收报告部分
    doc.paragraphs[70].text = project_acceptance_report['项目概况']
    doc.paragraphs[72].text = project_acceptance_report['项目目标与完成情况']
    for i, tech_point in enumerate(project_acceptance_report['项目核心技术点与创新点']['核心技术点'], 75):
        doc.paragraphs[i].text = tech_point
    for i, innovation in enumerate(project_acceptance_report['项目核心技术点与创新点']['创新点'], 80):
        doc.paragraphs[i].text = innovation
    for i, content in enumerate(project_acceptance_report['项目验收情况']['验收内容'], 87):
        doc.paragraphs[i].text = content
    doc.paragraphs[91].text = project_acceptance_report['项目验收情况']['验收结论']
    

    doc.paragraphs[93].text = project.company.name

    # 修改眉页
    # 访问文档的页眉
    header = doc.sections[0].header
    # 遍历页眉中的段落，替换公司名称
    for paragraph in header.paragraphs:
        if '上海索屿智能科技有限公司' in paragraph.text:
            paragraph.text = paragraph.text.replace('上海索屿智能科技有限公司', project.company.name)

    # 保存修改后的文档
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    # 保存到上一级的assets/docs目录下
    save_dir = os.path.join(cur_dir, 'assets', 'docs')
    # 确保目录存在
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f'{project.name}_{timestamp}.docx')
    doc.save(save_path)

    return project_report





    

    

    