#!/usr/bin/env python3
"""
将Git提交JSON数据转换为Markdown格式周报

Usage:
    python generate_report.py --input commits.json --output weekly-report.md
"""

import argparse
import json
from datetime import datetime


def load_commits_data(filepath):
    """加载提交数据JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_summary(authors_data):
    """生成工作概览总结"""
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
        type_desc = ', '.join([f"{t}({c})" for t, c in main_types])

        summary_parts.append(f"- **{author}**: {commits_count}次提交 ({type_desc})")

    return '\n'.join(summary_parts)


def generate_commit_type_distribution(commit_types):
    """生成提交类型分布的Markdown表格"""
    if not commit_types:
        return "暂无提交类型数据。"

    # 类型名称映射
    type_names = {
        'feat': '新功能 (feat)',
        'fix': '修复 (fix)',
        'docs': '文档 (docs)',
        'refactor': '重构 (refactor)',
        'test': '测试 (test)',
        'chore': '杂项 (chore)',
        'style': '样式 (style)',
        'perf': '性能 (perf)',
        'build': '构建 (build)',
        'ci': 'CI/CD (ci)',
        'revert': '回滚 (revert)',
        'other': '其他 (other)'
    }

    lines = []
    sorted_types = sorted(commit_types.items(), key=lambda x: x[1], reverse=True)
    for commit_type, count in sorted_types:
        type_name = type_names.get(commit_type, commit_type)
        lines.append(f"- {type_name}: {count}")

    return '\n'.join(lines)


def generate_commit_table(commits):
    """生成提交详情表格"""
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
    """生成单个作者的周报章节"""
    stats = data['stats']
    commits = data['commits']
    commit_types = data['commit_types']

    # 提交类型分布
    type_dist = generate_commit_type_distribution(commit_types)

    # 提交详情表格
    commit_table = generate_commit_table(commits)

    # 生成工作概览（基于提交信息自动总结）
    commit_messages = [c['message'] for c in commits]
    work_summary = summarize_work(commit_messages)

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


def summarize_work(commit_messages):
    """基于提交信息生成工作总结"""
    if not commit_messages:
        return "暂无工作记录。"

    # 按类型分组
    feat_msgs = []
    fix_msgs = []
    docs_msgs = []
    refactor_msgs = []
    other_msgs = []

    for msg in commit_messages:
        msg_lower = msg.lower()
        if any(msg_lower.startswith(p) for p in ['feat', 'feature']):
            feat_msgs.append(msg)
        elif any(msg_lower.startswith(p) for p in ['fix', 'bugfix']):
            fix_msgs.append(msg)
        elif any(msg_lower.startswith(p) for p in ['docs', 'doc']):
            docs_msgs.append(msg)
        elif msg_lower.startswith('refactor'):
            refactor_msgs.append(msg)
        else:
            other_msgs.append(msg)

    summary_parts = []

    if feat_msgs:
        summary_parts.append(f"- **新功能开发**: 完成了 {len(feat_msgs)} 个功能相关的提交")
    if fix_msgs:
        summary_parts.append(f"- **问题修复**: 修复了 {len(fix_msgs)} 个问题")
    if docs_msgs:
        summary_parts.append(f"- **文档更新**: 进行了 {len(docs_msgs)} 次文档相关的更新")
    if refactor_msgs:
        summary_parts.append(f"- **代码重构**: 进行了 {len(refactor_msgs)} 次代码重构")
    if other_msgs:
        summary_parts.append(f"- **其他工作**: {len(other_msgs)} 次其他类型的提交")

    return '\n'.join(summary_parts) if summary_parts else "进行了常规开发工作。"


def generate_markdown_report(data):
    """生成完整的Markdown格式周报"""
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


def main():
    parser = argparse.ArgumentParser(
        description='将Git提交JSON数据转换为Markdown格式周报'
    )
    parser.add_argument(
        '--input',
        default='commits.json',
        help='输入JSON文件路径 (默认: commits.json)'
    )
    parser.add_argument(
        '--output',
        default='weekly-report.md',
        help='输出Markdown文件路径 (默认: weekly-report.md)'
    )

    args = parser.parse_args()

    print(f"读取提交数据: {args.input}")

    try:
        data = load_commits_data(args.input)
    except FileNotFoundError:
        print(f"错误: 找不到文件 {args.input}")
        return 1
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败 - {e}")
        return 1

    print("生成Markdown报告...")
    report = generate_markdown_report(data)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"周报已保存到: {args.output}")

    return 0


if __name__ == '__main__':
    exit(main())
