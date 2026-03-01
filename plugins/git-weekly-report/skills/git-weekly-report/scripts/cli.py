#!/usr/bin/env python3
"""
Git 周报插件命令行入口

统一CLI入口，支持生成本周/上周周报或自定义时间范围。

Usage:
    python -m skills.git-weekly-report.scripts.cli --this-week
    python -m skills.git-weekly-report.scripts.cli --last-week
    python -m skills.git-weekly-report.scripts.cli --since 2024-01-01 --until 2024-01-07
    python -m skills.git-weekly-report.scripts.cli --output my-report.md
"""

import argparse
import json
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from skills.git-weekly-report.scripts.date_utils import get_default_week_range, get_last_week_range
from skills.git-weekly-report.scripts.git_collector import get_commits, group_commits_by_author, calculate_overall_stats
from skills.git-weekly-report.scripts.report_generator import generate_markdown_report


def main():
    parser = argparse.ArgumentParser(
        description='Git 周报生成工具 - 自动生成Git仓库的Markdown格式周报',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成本周周报（默认）
  python -m skills.git-weekly-report.scripts.cli

  # 生成上周周报
  python -m skills.git-weekly-report.scripts.cli --last-week

  # 自定义时间范围
  python -m skills.git-weekly-report.scripts.cli --since 2024-01-01 --until 2024-01-07

  # 指定输出文件
  python -m skills.git-weekly-report.scripts.cli --output my-report.md
        """
    )

    # 时间范围选项（互斥）
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument(
        '--this-week',
        action='store_true',
        help='生成本周周报（周一到周日，默认）'
    )
    time_group.add_argument(
        '--last-week',
        action='store_true',
        help='生成上周周报'
    )

    # 自定义日期
    parser.add_argument(
        '--since',
        help='开始日期 (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--until',
        help='结束日期 (YYYY-MM-DD)'
    )

    # 输出选项
    parser.add_argument(
        '--output',
        '-o',
        default='weekly-report.md',
        help='输出Markdown文件路径 (默认: weekly-report.md)'
    )
    parser.add_argument(
        '--json-output',
        help='同时输出JSON格式数据到指定文件'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='显示详细输出'
    )

    args = parser.parse_args()

    # 确定时间范围
    if args.last_week:
        since, until = get_last_week_range()
        if args.verbose:
            print(f"时间范围: 上周 ({since} ~ {until})")
    elif args.since and args.until:
        since, until = args.since, args.until
        if args.verbose:
            print(f"时间范围: 自定义 ({since} ~ {until})")
    else:
        # 默认本周
        since, until = get_default_week_range()
        if args.verbose or not args.this_week:
            print(f"时间范围: 本周 ({since} ~ {until})")

    print(f"收集提交数据: {since} ~ {until}")

    # 获取提交数据
    commits = get_commits(since, until)

    if not commits:
        print("未找到提交记录")
        # 创建空报告
        report_data = {
            'period': {'since': since, 'until': until},
            'authors': {},
            'overall_stats': {
                'total_commits': 0,
                'active_contributors': 0,
                'total_insertions': 0,
                'total_deletions': 0,
                'total_files_changed': 0
            }
        }
    else:
        print(f"找到 {len(commits)} 条提交记录")

        # 按作者分组
        authors_data = group_commits_by_author(commits)

        # 计算总体统计
        overall_stats = calculate_overall_stats(authors_data)

        # 生成报告数据
        report_data = {
            'period': {'since': since, 'until': until},
            'authors': authors_data,
            'overall_stats': overall_stats
        }

        print(f"贡献者数量: {overall_stats['active_contributors']}")
        print(f"总提交数: {overall_stats['total_commits']}")
        print(f"新增代码: +{overall_stats['total_insertions']} 行")
        print(f"删除代码: -{overall_stats['total_deletions']} 行")

    # 生成Markdown报告
    print("生成Markdown报告...")
    report = generate_markdown_report(report_data)

    # 保存Markdown文件
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"周报已保存到: {args.output}")

    # 可选：保存JSON文件
    if args.json_output:
        with open(args.json_output, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存到: {args.json_output}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
