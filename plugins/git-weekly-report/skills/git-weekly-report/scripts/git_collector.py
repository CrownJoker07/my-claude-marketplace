#!/usr/bin/env python3
"""
Git 数据收集模块

提供Git提交数据收集功能，包括提交信息、统计信息等。
"""

import re
import subprocess
from collections import defaultdict


def run_git_command(args):
    """
    运行Git命令并返回输出

    Args:
        args: Git命令参数列表

    Returns:
        str: 命令输出，失败返回None
    """
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
    """
    解析提交类型（feat/fix/docs等）

    Args:
        message: 提交信息

    Returns:
        str: 提交类型
    """
    patterns = [
        (r'^(feat|feature)[(:\s]', 'feat'),
        (r'^(fix|bugfix)[(:\s]', 'fix'),
        (r'^(docs|doc)[(:\s]', 'docs'),
        (r'^(refactor)[(:\s]', 'refactor'),
        (r'^(test|tests)[(:\s]', 'test'),
        (r'^(chore)[(:\s]', 'chore'),
        (r'^(style)[(:\s]', 'style'),
        (r'^(perf|performance)[(:\s]', 'perf'),
        (r'^(build)[(:\s]', 'build'),
        (r'^(ci)[(:\s]', 'ci'),
        (r'^(revert)[(:\s]', 'revert'),
        (r'^(art|asset)[(:\s]', 'art'),
    ]

    message_lower = message.lower()
    for pattern, commit_type in patterns:
        if re.match(pattern, message_lower):
            return commit_type

    return 'other'


def get_commit_stats(commit_hash):
    """
    获取单个提交的统计信息（文件变更、新增、删除行数）

    Args:
        commit_hash: 提交hash

    Returns:
        tuple: (文件变更数, 新增行数, 删除行数)
    """
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
        match = re.search(
            r'(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?',
            line
        )
        if match:
            files_changed = int(match.group(1))
            insertions = int(match.group(2)) if match.group(2) else 0
            deletions = int(match.group(3)) if match.group(3) else 0
            break

    return files_changed, insertions, deletions


def get_commits(since, until):
    """
    获取指定时间范围内的所有提交

    Args:
        since: 开始日期 (YYYY-MM-DD)
        until: 结束日期 (YYYY-MM-DD)

    Returns:
        list: 提交列表
    """
    # 使用 git log 获取提交信息
    # 格式: hash|author|date|subject
    # %an = author name (保持原样，不翻译)
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
            'author': author,  # 保持原样，不做任何翻译或修改
            'date': date,
            'message': subject,
            'type': parse_commit_type(subject),
            'files_changed': files_changed,
            'insertions': insertions,
            'deletions': deletions
        })

    return commits


def group_commits_by_author(commits):
    """
    按作者分组提交

    Args:
        commits: 提交列表

    Returns:
        dict: 按作者分组的提交数据
    """
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
    """
    计算总体统计信息

    Args:
        authors_data: 按作者分组的数据

    Returns:
        dict: 总体统计信息
    """
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
