#!/usr/bin/env python3
"""
内容分析器模块

分析Git提交信息，生成基于实际内容的工作描述。
禁止输出模板化计数描述（如"完成了X个功能"）。
"""

import re
from collections import defaultdict


# 提交类型中文映射
TYPE_NAMES = {
    'feat': '功能开发',
    'fix': '问题修复',
    'docs': '文档更新',
    'refactor': '代码重构',
    'test': '测试相关',
    'chore': '杂项工作',
    'style': '代码样式',
    'perf': '性能优化',
    'build': '构建相关',
    'ci': 'CI/CD',
    'revert': '代码回滚',
    'art': '美术资源',
    'other': '其他工作'
}


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


def extract_content(message):
    """
    提取提交信息中的内容部分（去除类型前缀）

    Args:
        message: 原始提交信息

    Returns:
        str: 内容描述
    """
    # 匹配常见的提交格式前缀
    patterns = [
        r'^(?:feat|feature|fix|bugfix|docs|doc|refactor|test|tests|chore|style|perf|performance|build|ci|revert|art|asset)[(:\s]+\s*',
        r'^\[.*?\]\s*',  # [type] 格式
    ]

    content = message
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    return content.strip()


def analyze_commits(commits):
    """
    分析提交列表，按类型分组并提取内容

    Args:
        commits: 提交列表，每个提交包含 'message' 和 'type' 字段

    Returns:
        dict: 按类型分组的分析结果
    """
    # 按类型分组
    grouped = defaultdict(list)

    for commit in commits:
        commit_type = commit.get('type', 'other')
        message = commit.get('message', '')
        content = extract_content(message)

        if content:
            grouped[commit_type].append({
                'hash': commit.get('hash', ''),
                'content': content,
                'full_message': message
            })

    return dict(grouped)


def generate_work_summary(commits):
    """
    生成工作概览总结

    禁止输出模板化计数描述（如"完成了X个功能"）。
    必须基于实际提交内容生成描述。

    Args:
        commits: 提交列表

    Returns:
        str: Markdown格式的工作总结
    """
    if not commits:
        return "暂无工作记录。"

    grouped = analyze_commits(commits)

    if not grouped:
        return "进行了常规开发工作。"

    summary_parts = []

    # 按优先级顺序输出不同类型
    priority_order = ['feat', 'fix', 'art', 'refactor', 'perf', 'docs', 'test', 'chore', 'style', 'build', 'ci', 'revert', 'other']

    for commit_type in priority_order:
        if commit_type not in grouped:
            continue

        items = grouped[commit_type]
        type_name = TYPE_NAMES.get(commit_type, commit_type)

        # 提取所有内容描述
        contents = [item['content'] for item in items if item['content']]

        if not contents:
            continue

        # 合并相似内容，去重
        unique_contents = merge_similar_contents(contents)

        # 生成描述
        if len(unique_contents) == 1:
            desc = unique_contents[0]
        else:
            # 多个相关内容，用分号连接
            desc = '；'.join(unique_contents[:5])  # 最多显示5条
            if len(unique_contents) > 5:
                desc += f'等 {len(unique_contents)} 项工作'

        summary_parts.append(f"- **{type_name}**：{desc}")

    return '\n'.join(summary_parts) if summary_parts else "进行了常规开发工作。"


def merge_similar_contents(contents):
    """
    合并相似的内容描述，去除重复

    Args:
        contents: 内容描述列表

    Returns:
        list: 去重后的内容列表
    """
    if not contents:
        return []

    # 简单的去重逻辑：去除完全重复和高度相似的
    seen = set()
    result = []

    for content in contents:
        # 标准化用于比较
        normalized = content.lower().replace(' ', '').replace('，', ',').replace('。', '.')

        # 检查是否已经存在相似内容
        is_similar = False
        for seen_item in seen:
            # 如果一条是另一条的前缀，或相似度很高
            if normalized in seen_item or seen_item in normalized:
                is_similar = True
                break
            # 计算简单相似度：共同子串长度
            if len(normalized) > 10 and len(seen_item) > 10:
                common = len(set(normalized) & set(seen_item))
                if common / max(len(normalized), len(seen_item)) > 0.8:
                    is_similar = True
                    break

        if not is_similar:
            seen.add(normalized)
            result.append(content)

    return result


def generate_type_description(commit_type, commits):
    """
    生成特定类型的详细描述

    Args:
        commit_type: 提交类型
        commits: 该类型的提交列表

    Returns:
        str: 详细描述
    """
    if not commits:
        return ""

    type_name = TYPE_NAMES.get(commit_type, commit_type)
    contents = [extract_content(c.get('message', '')) for c in commits]
    contents = [c for c in contents if c]

    if not contents:
        return f"**{type_name}**：进行了相关更新。"

    unique_contents = merge_similar_contents(contents)

    if len(unique_contents) == 1:
        return f"**{type_name}**：{unique_contents[0]}"
    else:
        desc = '；'.join(unique_contents[:3])
        return f"**{type_name}**：{desc}"
