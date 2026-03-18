"""
公司和项目类定义
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Company:
    """
    公司信息类
    """
    name: str  # 公司名称
    industry: str = ""  # 所属行业
    location: str = ""  # 公司地点
    established_year: int = 0  # 成立年份
    description: str = ""  # 公司描述
    core_technologies: List[str] = field(default_factory=list)  # 核心技术
    patents: List[str] = field(default_factory=list)  # 专利情况
    projects: List['Project'] = field(default_factory=list)  # 公司的研发项目
    session_id: str = ""  # 会话ID


@dataclass
class Project:
    """
    项目信息类
    """
    name: str  # 项目名称
    project_id: str  # 项目编号
    company: Company  # 所属公司
    start_date: str  # 开始日期
    end_date: str  # 结束日期
    field: str  # 项目领域
    intellectual_property: str = ""  # 应用知识产权
    patent_info: str = ""  # 专利详细信息
    background: str = ""  # 项目背景
    objectives: List[str] = field(default_factory=list)  # 项目目标
    expected_benefits: List[str] = field(default_factory=list)  # 预期效益
    challenges: List[str] = field(default_factory=list)  # 面临挑战
    budget: str = ""  # 项目预算
    team_members: List[str] = field(default_factory=list)  # 项目团队成员
    
    def generate_project_report(self) -> str:
        """
        生成项目立项报告
        
        Returns:
            项目立项报告文本
        """
        report = f"# {self.name} 立项报告\n\n"
        
        # 公司信息
        report += f"## 公司信息\n"
        report += f"- 公司名称：{self.company.name}\n"
        report += f"- 所属行业：{self.company.industry}\n"
        report += f"- 公司地点：{self.company.location}\n"
        report += f"- 成立年份：{self.company.established_year}\n"
        report += f"- 公司描述：{self.company.description}\n"
        
        if self.company.core_technologies:
            report += f"- 核心技术：{', '.join(self.company.core_technologies)}\n"
        
        if self.company.patents:
            report += f"- 专利情况：{', '.join(self.company.patents)}\n"
        
        # 项目基本信息
        report += f"\n## 项目基本信息\n"
        report += f"- 项目编号：{self.project_id}\n"
        report += f"- 项目名称：{self.name}\n"
        report += f"- 项目领域：{self.field}\n"
        report += f"- 项目周期：{self.start_date} 至 {self.end_date}\n"
        report += f"- 项目预算：{self.budget}\n"
        
        if self.team_members:
            report += f"- 项目团队：{', '.join(self.team_members)}\n"
        
        # 项目背景
        report += f"\n## 项目背景\n"
        report += f"{self.background}\n"
        
        # 项目目标
        report += f"\n## 项目目标\n"
        for i, objective in enumerate(self.objectives, 1):
            report += f"{i}. {objective}\n"
        
        # 预期效益
        report += f"\n## 预期效益\n"
        for i, benefit in enumerate(self.expected_benefits, 1):
            report += f"{i}. {benefit}\n"
        
        # 面临挑战
        report += f"\n## 面临挑战\n"
        for i, challenge in enumerate(self.challenges, 1):
            report += f"{i}. {challenge}\n"
        
        return report
