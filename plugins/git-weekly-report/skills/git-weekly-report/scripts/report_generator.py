#!/usr/bin/env python3
"""
报告生成模块

将Git提交数据转换为Markdown格式周报。
"""

from .content_analyzer import generate_work_summary, TYPE_NAMES


def generate_summary(authors_data):
    """
    生成团队工作摘要

    Args:
        authors_data: 按作者分组的数据

    Returns:
        str: Markdown格式的摘要
    """
    if not authors_data:
        return "本周暂无提交记录。"

    # 按提交数量排序
    sorted_authors = sorted(
        authors_data.items(),
        key=lambda x: x[1]['stats']['total_commits'],
        reverse=True
    )

    summary_parts = []
    for author, data in sorted_authors:
        commits_count = data['stats']['total_commits']
        commit_types = data['commit_types']

        # 找出主要的提交类型
        main_types = sorted(commit_types.items(), key=lambda x: x[1], reverse=True)[:3]
        type_desc = ', '.join([f"{TYPE_NAMES.get(t, t)}({c})" for t, c in main_types])

        summary_parts.append(f"- **{author}**: {commits_count}次提交 ({type_desc})")

    return '\n'.join(summary_parts)


def generate_commit_type_distribution(commit_types):
    """
    生成提交类型分布的Markdown列表

    Args:
        commit_types: 提交类型统计

    Returns:
        str: Markdown格式的类型分布
    """
    if not commit_types:
        return "暂无提交类型数据。"

    lines = []
    sorted_types = sorted(commit_types.items(), key=lambda x: x[1], reverse=True)
    for commit_type, count in sorted_types:
        type_name = TYPE_NAMES.get(commit_type, commit_type)
        lines.append(f"- {type_name}: {count}")

    return '\n'.join(lines)


def generate_commit_table(commits):
    """
    生成提交详情表格

    Args:
        commits: 提交列表

    Returns:
        str: Markdown格式的表格
    """
    if not commits:
        return "暂无提交记录。"

    # 按时间排序
    sorted_commits = sorted(commits, key=lambda x: x['date'])

    lines = [
        "| 日期 | 类型 | 提交信息 | 文件变更 | 代码变更 |",
        "|------|------|----------|----------|----------|"
    ]

    for commit in sorted_commits:
        date = commit['date']
        commit_type = commit['type']
        message = commit['message']
        # 截断过长的消息
        if len(message) > 50:
            message = message[:47] + '...'
        # 转义管道符
        message = message.replace('|', '\\|')

        files = f"{commit['files_changed']} files"
        changes = f"+{commit['insertions']}/-{commit['deletions']}"

        lines.append(f"| {date} | {commit_type} | {message} | {files} | {changes} |")

    return '\n'.join(lines)


def generate_author_section(author, data):
    """
    生成单个作者的周报章节

    Args:
        author: 作者名称（保持原样）
        data: 作者数据

    Returns:
        str: Markdown格式的章节
    """
    stats = data['stats']
    commits = data['commits']
    commit_types = data['commit_types']

    # 提交类型分布
    type_dist = generate_commit_type_distribution(commit_types)

    # 提交详情表格
    commit_table = generate_commit_table(commits)

    # 生成工作概览（基于提交信息智能总结）
    # 使用 content_analyzer 生成基于内容的描述
    work_summary = generate_work_summary(commits)

    section = f"""## {author}

### 工作概览
{work_summary}

### 提交统计
- **提交数**: {stats['total_commits']}
- **修改文件**: {stats['files_changed']} 个
- **新增代码**: +{stats['insertions']} 行
- **删除代码**: -{stats['deletions']} 行

### 提交类型分布
{type_dist}

### 提交详情
{commit_table}

---

"""
    return section


def generate_markdown_report(data):
    """
    生成完整的Markdown格式周报

    Args:
        data: 包含 period, authors, overall_stats 的数据字典

    Returns:
        str: Markdown格式的完整报告
    """
    period = data['period']
    authors = data['authors']
    overall_stats = data['overall_stats']

    since = period['since']
    until = period['until']

    # 生成总体统计
    overall_section = f"""# Git 周报 ({since} ~ {until})

## 总体统计

- **总提交数**: {overall_stats['total_commits']}
- **活跃贡献者**: {overall_stats['active_contributors']} 人
- **新增代码**: +{overall_stats['total_insertions']} 行
- **删除代码**: -{overall_stats['total_deletions']} 行
- **修改文件**: {overall_stats['total_files_changed']} 个

## 团队工作摘要

{generate_summary(authors)}

---

"""

    # 生成每个作者的详细报告
    author_sections = []
    if authors:
        # 按提交数量排序
        sorted_authors = sorted(
            authors.items(),
            key=lambda x: x[1]['stats']['total_commits'],
            reverse=True
        )

        for author, author_data in sorted_authors:
            author_sections.append(generate_author_section(author, author_data))
    else:
        author_sections.append("## 详细记录\n\n本周暂无提交记录。\n")

    return overall_section + '\n'.join(author_sections)
