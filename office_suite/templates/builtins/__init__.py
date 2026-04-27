"""内置模板注册

自动导入所有内置模板模块，触发注册。
"""

from . import (
    work_report,
    project_proposal,
    annual_report,
    product_launch,
    weekly_meeting,
    training_course,
    business_plan,
    resume,
    academic_defense,
    marketing_plan,
    quarterly_review,
    startup_pitch,
)

__all__ = [
    "work_report",
    "project_proposal",
    "annual_report",
    "product_launch",
    "weekly_meeting",
    "training_course",
    "business_plan",
    "resume",
    "academic_defense",
    "marketing_plan",
    "quarterly_review",
    "startup_pitch",
]
