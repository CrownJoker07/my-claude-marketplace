#!/usr/bin/env python3
"""
收集Git提交数据并生成JSON报告

Usage:
    python collect_commits.py --since 2024-01-01 --until 2024-01-07 --output commits.json
    python collect_commits.py --output commits.json  # 默认使用本周时间范围
"""

import argparse
import json
import re
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict


def get_default_week_range():
    """获取本周的时间范围（周一到周日）"""
    today = datetime.now()
    # 获取本周一（weekday() 返回 0-6，0是周一）
    monday = today - timedelta(days=today.weekday())
    # 获取本周日
    sunday = monday + timedelta(days=6)
    return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')


def run_git_command(args):
    """运行Git命令并返回输出"""
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode != 0:
            print(f"Git命令错误: {result.stderr}")
            return None
        return result.stdout
    except Exception as e:
        print(f"运行Git命令时出错: {e}")
        return None


def parse_commit_type(message):
    """解析提交类型（feat/fix/docs等）"""
    patterns = [
        r'^(feat|feature)[(:\s]',
        r'^(fix|bugfix)[(:\s]',
        r'^(docs|doc)[(:\s]',
        r'^(refactor)[(:\s]',
        r'^(test|tests)[(:\s]',
        r'^(chore)[(:\s]',
        r'^(style)[(:\s]',
        r'^(perf|performance)[(:\s]',
        r'^(build)[(:\s]',
        r'^(ci)[(:\s]',
        r'^(revert)[(:\s]',
    ]

    message_lower = message.lower()
    for pattern in patterns:
        match = re.match(pattern, message_lower)
        if match:
            commit_type = match.group(1)
            # 统一类型名称
            if commit_type in ['feature']:
                commit_type = 'feat'
            elif commit_type in ['doc']:
                commit_type = 'docs'
            elif commit_type in ['bugfix']:
                commit_type = 'fix'
            elif commit_type in ['performance']:
                commit_type = 'perf'
            return commit_type

    return 'other'


def get_commit_stats(commit_hash):
    """获取单个提交的统计信息（文件变更、新增、删除行数）"""
    # 获取文件变更统计
    output = run_git_command([
        'show', '--stat', '--format=', commit_hash
    ])

    if not output:
        return 0, 0, 0

    files_changed = 0
    insertions = 0
    deletions = 0

    lines = output.strip().split('\n')
    for line in lines:
        # 匹配 " X files changed, X insertions(+), X deletions(-)" 格式
        match = re.search(r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?', line)
        if match:
            files_changed = int(match.group(1))
            insertions = int(match.group(2)) if match.group(2) else 0
            deletions = int(match.group(3)) if match.group(3) else 0
            break

    return files_changed, insertions, deletions


def get_commits(since, until):
    """获取指定时间范围内的所有提交"""
    # 使用 git log 获取提交信息
    # 格式: hash|author|date|subject
    format_str = '%H|%an|%ad|%s'
    output = run_git_command([
        'log',
        f'--since={since} 00:00:00',
        f'--until={until} 23:59:59',
        f'--pretty=format:{format_str}',
        '--date=short'
    ])

    if not output:
        return []

    commits = []
    for line in output.strip().split('\n'):
        if '|' not in line:
            continue

        parts = line.split('|', 3)
        if len(parts) != 4:
            continue

        commit_hash, author, date, subject = parts

        # 获取统计信息
        files_changed, insertions, deletions = get_commit_stats(commit_hash)

        commits.append({
            'hash': commit_hash[:7],
            'full_hash': commit_hash,
            'author': author,
            'date': date,
            'message': subject,
            'type': parse_commit_type(subject),
            'files_changed': files_changed,
            'insertions': insertions,
            'deletions': deletions
        })

    return commits


def group_commits_by_author(commits):
    """按作者分组提交"""
    authors = defaultdict(lambda: {
        'commits': [],
        'stats': {
            'total_commits': 0,
            'files_changed': 0,
            'insertions': 0,
            'deletions': 0
        },
        'commit_types': defaultdict(int)
    })

    for commit in commits:
        author = commit['author']
        authors[author]['commits'].append(commit)
        authors[author]['stats']['total_commits'] += 1
        authors[author]['stats']['files_changed'] += commit['files_changed']
        authors[author]['stats']['insertions'] += commit['insertions']
        authors[author]['stats']['deletions'] += commit['deletions']
        authors[author]['commit_types'][commit['type']] += 1

    # 将 defaultdict 转换为普通 dict 以便 JSON 序列化
    result = {}
    for author, data in authors.items():
        result[author] = {
            'commits': data['commits'],
            'stats': data['stats'],
            'commit_types': dict(data['commit_types'])
        }

    return result


def calculate_overall_stats(authors_data):
    """计算总体统计信息"""
    total_commits = 0
    total_insertions = 0
    total_deletions = 0
    total_files_changed = 0

    for author_data in authors_data.values():
        stats = author_data['stats']
        total_commits += stats['total_commits']
        total_insertions += stats['insertions']
        total_deletions += stats['deletions']
        total_files_changed += stats['files_changed']

    return {
        'total_commits': total_commits,
        'active_contributors': len(authors_data),
        'total_insertions': total_insertions,
        'total_deletions': total_deletions,
        'total_files_changed': total_files_changed
    }


def main():
    parser = argparse.ArgumentParser(
        description='收集Git提交数据并生成JSON报告'
    )
    parser.add_argument(
        '--since',
        help='开始日期 (YYYY-MM-DD)，默认本周一'
    )
    parser.add_argument(
        '--until',
        help='结束日期 (YYYY-MM-DD)，默认本周日'
    )
    parser.add_argument(
        '--output',
        default='commits.json',
        help='输出JSON文件路径 (默认: commits.json)'
    )

    args = parser.parse_args()

    # 确定时间范围
    if args.since and args.until:
        since = args.since
        until = args.until
    else:
        default_since, default_until = get_default_week_range()
        since = args.since or default_since
        until = args.until or default_until

    print(f"收集提交数据: {since} ~ {until}")

    # 获取提交数据
    commits = get_commits(since, until)

    if not commits:
        print("未找到提交记录")
        # 创建空报告
        report = {
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

        # 生成报告
        report = {
            'period': {'since': since, 'until': until},
            'authors': authors_data,
            'overall_stats': overall_stats
        }

        print(f"贡献者数量: {overall_stats['active_contributors']}")
        print(f"总提交数: {overall_stats['total_commits']}")
        print(f"新增代码: +{overall_stats['total_insertions']} 行")
        print(f"删除代码: -{overall_stats['total_deletions']} 行")

    # 保存JSON文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"报告已保存到: {args.output}")


if __name__ == '__main__':
    main()
