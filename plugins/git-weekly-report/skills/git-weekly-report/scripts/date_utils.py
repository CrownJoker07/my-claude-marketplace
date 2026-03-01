#!/usr/bin/env python3
"""
日期工具模块

提供周报日期计算功能，支持本周、上周等时间范围计算。
"""

from datetime import datetime, timedelta


def get_default_week_range(reference_date=None):
    """
    获取本周的时间范围（周一到周日）

    Args:
        reference_date: 参考日期，默认为今天

    Returns:
        tuple: (周一日期, 周日日期) 格式为 'YYYY-MM-DD'
    """
    if reference_date is None:
        reference_date = datetime.now()

    # 获取本周一（weekday() 返回 0-6，0是周一）
    monday = reference_date - timedelta(days=reference_date.weekday())
    # 获取本周日
    sunday = monday + timedelta(days=6)

    return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')


def get_last_week_range(reference_date=None):
    """
    获取上周的时间范围（上周一到上周日）

    Args:
        reference_date: 参考日期，默认为今天

    Returns:
        tuple: (上周一日期, 上周日日期) 格式为 'YYYY-MM-DD'
    """
    if reference_date is None:
        reference_date = datetime.now()

    # 获取本周一
    this_monday = reference_date - timedelta(days=reference_date.weekday())
    # 上周一 = 本周一 - 7天
    last_monday = this_monday - timedelta(days=7)
    # 上周日 = 本周一 - 1天
    last_sunday = this_monday - timedelta(days=1)

    return last_monday.strftime('%Y-%m-%d'), last_sunday.strftime('%Y-%m-%d')


def parse_date(date_string):
    """
    解析日期字符串为 datetime 对象

    Args:
        date_string: 日期字符串，格式为 'YYYY-MM-DD'

    Returns:
        datetime: 解析后的日期对象

    Raises:
        ValueError: 日期格式无效
    """
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError as e:
        raise ValueError(f"日期格式无效: {date_string}，期望格式: YYYY-MM-DD") from e


def format_date(date_obj):
    """
    将 datetime 对象格式化为字符串

    Args:
        date_obj: datetime 对象

    Returns:
        str: 格式化后的日期字符串 'YYYY-MM-DD'
    """
    return date_obj.strftime('%Y-%m-%d')
