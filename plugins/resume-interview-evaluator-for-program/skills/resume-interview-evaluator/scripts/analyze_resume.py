#!/usr/bin/env python3
"""
简历自动分析脚本

功能：
    1. 从 PDF 简历中提取文本
    2. 解析关键信息（姓名、岗位、技能、项目等）
    3. 生成技能评估报告
    4. 生成定制化面试问题清单

使用方法:
    # 基本用法
    python3 analyze_resume.py /path/to/resume.pdf

    # 指定输出目录
    python3 analyze_resume.py /path/to/resume.pdf -o ./output

    # 指定候选人姓名（如PDF中无法识别）
    python3 analyze_resume.py /path/to/resume.pdf --name "张三"

输出:
    - 技能评估报告_{姓名}_{日期}.md
    - 面试问题清单_{姓名}_{日期}.md
"""

import argparse
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def extract_pdf_text(pdf_path: str) -> str:
    """
    从 PDF 文件中提取文本

    优先使用 pdfplumber（效果更好），如未安装则使用 PyPDF2
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")

    # 首先尝试使用 pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            if text.strip():
                return text
    except ImportError:
        pass

    # 回退到 PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    except ImportError:
        raise ImportError(
            "请安装 pdfplumber 或 PyPDF2:\n"
            "  pip install pdfplumber\n"
            "  或\n"
            "  pip install PyPDF2"
        )


def parse_resume(text: str) -> Dict:
    """
    解析简历文本，提取关键信息

    返回结构化数据：
    {
        'name': str,
        'position': str,
        'experience_years': str,
        'education': str,
        'skills': {
            'languages': List[str],
            'engines': List[str],
            'professional': List[str],
            'tools': List[str]
        },
        'projects': List[Dict],
        'work_experience': List[str]
    }
    """
    lines = text.split('\n')

    result = {
        'name': '',
        'position': '',
        'experience_years': '',
        'education': '',
        'skills': {
            'languages': [],
            'engines': [],
            'professional': [],
            'tools': []
        },
        'projects': [],
        'work_experience': []
    }

    # 提取姓名（常见格式：姓名、名字在开头位置）
    result['name'] = extract_name(text, lines)

    # 提取期望岗位
    result['position'] = extract_position(text)

    # 提取工作年限
    result['experience_years'] = extract_experience_years(text)

    # 提取教育背景
    result['education'] = extract_education(text)

    # 提取技能信息
    result['skills'] = extract_skills(text)

    # 提取项目经历
    result['projects'] = extract_projects(text)

    # 提取工作经历
    result['work_experience'] = extract_work_experience(text)

    return result


def extract_name(text: str, lines: List[str]) -> str:
    """提取姓名"""
    # 尝试匹配常见的姓名标识
    patterns = [
        r'姓\s*名[：:]\s*([^\n\s]+)',
        r'Name[：:]\s*([^\n\s]+)',
        r'^\s*([^\n\s]{2,4})\s*的?简历',
        r'([^\n\s]{2,4})\s*个人简历',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # 过滤掉常见的非姓名词汇
            if name and name not in ['简历', '个人', '我的']:
                return name

    # 尝试从第一行提取（通常是姓名）
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line) <= 10:
            return first_line

    return '未知'


def extract_position(text: str) -> str:
    """提取期望岗位"""
    patterns = [
        r'期望职位[：:]\s*([^\n]+)',
        r'应聘职位[：:]\s*([^\n]+)',
        r'目标职位[：:]\s*([^\n]+)',
        r'求职意向[：:]\s*([^\n]+)',
        r'期望岗位[：:]\s*([^\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # 从文本中推断岗位类型
    if 'Unity' in text or 'unity' in text:
        return 'Unity游戏开发工程师'
    elif 'Unreal' in text or 'UE' in text or '虚幻' in text:
        return 'UE4/UE5游戏开发工程师'
    elif '游戏' in text and ('开发' in text or '程序' in text):
        return '游戏开发工程师'

    return '游戏开发工程师'


def extract_experience_years(text: str) -> str:
    """提取工作年限"""
    patterns = [
        r'(\d+)\s*年\s*(?:工作|开发)?经验',
        r'工作年限[：:]\s*(\d+)\s*年',
        r'(\d+)\s*年以上?(?:相关)?经验',
        r'(应届|校招|实习生?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            years = match.group(1)
            if years in ['应届', '校招', '实习', '实习生']:
                return '应届生/实习'
            return f"{years}年"

    return '未知'


def extract_education(text: str) -> str:
    """提取教育背景"""
    # 匹配学校名称
    school_patterns = [
        r'([^\n]+大学)',
        r'([^\n]+学院)',
        r'毕业院校[：:]\s*([^\n]+)',
        r'学历[：:]\s*([^\n]+)',
    ]

    for pattern in school_patterns:
        match = re.search(pattern, text)
        if match:
            school = match.group(1).strip()
            # 检查是否有学历信息
            degree_match = re.search(r'(本科|硕士|博士|专科|大专|研究生)', text)
            if degree_match:
                return f"{school} {degree_match.group(1)}"
            return school

    return ''


def extract_skills(text: str) -> Dict[str, List[str]]:
    """提取技能信息"""
    skills = {
        'languages': [],
        'engines': [],
        'professional': [],
        'tools': []
    }

    # 编程语言
    lang_keywords = {
        'C#': ['C#', 'CSharp', 'csharp'],
        'C++': ['C++', 'CPP', 'cpp'],
        'Python': ['Python', 'python'],
        'Lua': ['Lua', 'lua'],
        'JavaScript': ['JavaScript', 'JS', 'js'],
        'TypeScript': ['TypeScript', 'TS', 'ts'],
        'Java': ['Java', 'java'],
        'Go': ['Go', 'Golang', 'golang'],
    }

    for lang, keywords in lang_keywords.items():
        for kw in keywords:
            if kw in text:
                if lang not in skills['languages']:
                    skills['languages'].append(lang)
                break

    # 游戏引擎
    engine_keywords = {
        'Unity': ['Unity', 'unity', 'Unity3D', 'U3D'],
        'Unreal Engine': ['Unreal', 'UE4', 'UE5', '虚幻引擎', '虚幻'],
        'Godot': ['Godot', 'godot'],
        'Cocos': ['Cocos', 'cocos', 'Cocos2d', 'Cocos Creator'],
    }

    for engine, keywords in engine_keywords.items():
        for kw in keywords:
            if kw in text:
                if engine not in skills['engines']:
                    skills['engines'].append(engine)
                break

    # 专业技能
    prof_keywords = [
        'ECS', 'DOTS', 'Job System',
        'Shader', 'HLSL', 'GLSL', 'ShaderLab',
        'AI', '行为树', '状态机', 'FSM',
        '寻路', 'Navigation', 'NavMesh', 'A*',
        '网络', '网络同步', '帧同步', '状态同步',
        '热更新', 'AssetBundle', 'Addressable',
        'UI', 'UGUI', 'FairyGUI',
        '物理', 'Physics', '碰撞检测',
        '性能优化', '内存优化', 'Draw Call',
        'Lua', 'XLua', 'ToLua', 'SLua',
        '设计模式', '架构设计', 'MVC', 'MVP', 'MVVM',
        '多线程', '异步编程', 'UniTask', 'async/await',
        '版本控制', 'Git', 'SVN'
    ]

    for kw in prof_keywords:
        if kw in text and kw not in skills['professional']:
            skills['professional'].append(kw)

    # 工具
    tool_keywords = [
        'Visual Studio', 'VS Code', 'Rider',
        'Git', 'SVN', 'Perforce',
        'Jenkins', 'CI/CD',
        'Jira', 'Confluence', 'Trello',
        'Profiler', 'Frame Debugger',
        'Blender', 'Maya', '3ds Max',
        'Photoshop', 'PS',
        'Wwise', 'FMOD', 'Audio',
        'Spine', 'Live2D'
    ]

    for kw in tool_keywords:
        if kw in text and kw not in skills['tools']:
            skills['tools'].append(kw)

    return skills


def _is_valid_project_name(name: str) -> bool:
    """
    验证是否为有效的项目名称

    规则：
    1. 长度在3-30字符之间
    2. 不能包含明显的描述性词语
    3. 不能是完整的句子（不能包含过多标点或连接词）
    4. 不能是纯数字或特殊字符
    """
    if not name or len(name) < 3 or len(name) > 30:
        return False

    # 过滤包含明显描述性关键词的
    desc_keywords = [
        '参与', '负责', '开发', '设计', '实现', '完成', '使用', '通过',
        '积累', '团队协作', '项目经验', '工作经验', '主要职责',
        '技术栈', '项目描述', '项目职责', '项目介绍'
    ]

    for keyword in desc_keywords:
        if keyword in name:
            return False

    # 过滤包含过多标点符号的（可能是句子）
    if name.count('，') + name.count('。') + name.count('；') > 1:
        return False

    # 过滤包含连接词的（可能是句子）
    if '，' in name or '。' in name or '；' in name:
        return False

    # 过滤纯数字或纯特殊字符
    if re.match(r'^[\d\s\-\_\.]+$', name):
        return False

    return True


def extract_projects(text: str) -> List[Dict]:
    """提取项目经历"""
    projects = []

    # 项目分割模式
    project_patterns = [
        r'(?:项目经历|项目经验|Projects?)[：:\s]*\n?(.+?)(?=工作经历|教育背景|个人技能|$)',
    ]

    project_text = ""
    for pattern in project_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            project_text = match.group(1)
            break

    if not project_text:
        # 尝试直接找项目关键词
        project_text = text

    # 尝试识别单个项目（按常见分隔符分割）
    project_splits = re.split(r'\n(?=项目\d+[：:]|【|◆|●|\d+\.)', project_text)

    for i, proj_text in enumerate(project_splits[:5]):  # 最多取5个项目
        if len(proj_text.strip()) < 20:
            continue

        # 尝试多种方式提取项目名称
        project_name = None

        # 方式1：匹配 "项目名称：XXX"、"项目名：XXX"、《XXX》、【XXX】格式
        name_match = re.search(r'(?:项目名称[：:]\s*|项目名[：:]\s*|Project\s*Name[：:]\s*|《|【)([^\n【】》]+)', proj_text, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
            # 过滤：项目名通常较短（<30字符），且不应是完整句子
            if _is_valid_project_name(candidate):
                project_name = candidate

        # 方式2：取项目文本的第一行作为项目名（如果不是分隔符）
        if not project_name:
            first_line = proj_text.strip().split('\n')[0].strip()
            # 去除常见的列表标记（如 "1. ", "- ", "◆ " 等）
            cleaned_name = re.sub(r'^[\d\s\.\-\◆\●\*\[\(]+', '', first_line)
            if _is_valid_project_name(cleaned_name):
                project_name = cleaned_name

        # 方式3：查找引号内的名称
        if not project_name:
            quote_match = re.search(r'["\']([^"\'\n]{3,30})["\']', proj_text)
            if quote_match:
                candidate = quote_match.group(1).strip()
                if _is_valid_project_name(candidate):
                    project_name = candidate

        # 使用智能描述提取
        meaningful_desc = extract_meaningful_description(proj_text)

        project = {
            'name': project_name or f'项目{i+1}',
            'type': '',
            'role': '',
            'description': meaningful_desc,
            'tech_stack': []
        }

        # 提取项目类型
        if any(kw in proj_text for kw in ['2D', '横版', '平台']):
            project['type'] = '2D横版/平台'
        elif any(kw in proj_text for kw in ['3D', '三维']):
            project['type'] = '3D游戏'
        elif any(kw in proj_text for kw in ['FPS', '射击', '第一人称']):
            project['type'] = 'FPS射击'
        elif any(kw in proj_text for kw in ['RPG', '角色扮演']):
            project['type'] = 'RPG'
        elif any(kw in proj_text for kw in ['对战', 'PVP', 'MOBA']):
            project['type'] = '网络对战'
        else:
            project['type'] = '游戏项目'

        # 提取角色
        role_patterns = [
            r'(?:职责|角色|担任)[：:]\s*([^\n]+)',
            r'(主程序|客户端|服务器|独立开发|程序|策划|美术)',
        ]
        for pattern in role_patterns:
            role_match = re.search(pattern, proj_text)
            if role_match:
                project['role'] = role_match.group(1).strip()
                break

        # 提取技术栈
        tech_keywords = ['Unity', 'Unreal', 'UE4', 'UE5', 'C#', 'C++', 'Lua', 'Wwise', '行为树', 'ECS']
        for tech in tech_keywords:
            if tech in proj_text:
                project['tech_stack'].append(tech)

        # 提取技术亮点
        tech_highlights = extract_tech_highlights(proj_text, project['tech_stack'])

        # 提取个人贡献（传入角色信息用于推断）
        personal_contribution = extract_personal_contribution(proj_text, project['role'])

        # 提取项目详细信息
        project_details = extract_project_details(proj_text)
        project['project_scale'] = project_details.get('project_scale', '')
        project['development_time'] = project_details.get('development_time', '')
        project['team_size'] = project_details.get('team_size', '')
        project['core_systems'] = project_details.get('core_systems', [])
        project['tech_highlights'] = tech_highlights
        project['personal_contribution'] = personal_contribution

        # 如果核心系统为空，尝试基于上下文推断
        if not project['core_systems']:
            inferred_systems = infer_core_systems_by_context(proj_text, project['role'], project['tech_stack'])
            if inferred_systems:
                project['core_systems'] = inferred_systems
                project['inferred_core_systems'] = True  # 标记为推断的

        # 分析项目复杂度
        complexity_result = analyze_project_complexity(project)
        project['complexity_score'] = complexity_result['score']
        project['complexity_level'] = complexity_result['level']
        project['complexity_reason'] = complexity_result['reason']

        projects.append(project)

    return projects


def extract_project_details(proj_text: str) -> Dict:
    """
    提取项目详细信息
    - 开发周期、团队规模
    - 核心系统（战斗系统、AI系统、网络同步、UI系统等）
    - 项目规模指标
    """
    details = {
        'project_scale': '',
        'development_time': '',
        'team_size': '',
        'core_systems': []
    }

    # 提取开发周期
    time_patterns = [
        r'(?:开发周期|项目周期|时间)[：:]\s*([^\n]+)',
        r'(\d{4}[\.\-/]\d{1,2})\s*[-~至]\s*(\d{4}[\.\-/]\d{1,2}|至今)',
        r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*[-~至]\s*(\d{4})\s*年\s*(\d{1,2})\s*月',
        r'(\d{4}\.\d{1,2})\s*-\s*(\d{4}\.\d{1,2}|至今)',
    ]
    for pattern in time_patterns:
        time_match = re.search(pattern, proj_text)
        if time_match:
            details['development_time'] = time_match.group(0).strip()
            break

    # 提取团队规模
    team_patterns = [
        r'(?:团队规模|团队人数|团队)[：:]\s*(\d+)\s*人',
        r'团队\s*(\d+)\s*人',
        r'(\d+)\s*人团队',
        r'(?:团队|项目组)(?:规模)?[：:]?\s*(\d+)[\s人]',
    ]
    for pattern in team_patterns:
        team_match = re.search(pattern, proj_text)
        if team_match:
            details['team_size'] = team_match.group(1) + '人'
            break

    # 提取核心系统
    system_keywords = {
        '战斗系统': ['战斗系统', '战斗', '技能系统', '连招', '打击感'],
        'AI系统': ['AI系统', '行为树', '状态机', '寻路', 'Navigation', 'NPC行为'],
        '网络同步': ['网络同步', '帧同步', '状态同步', '服务器', '联机', '多人'],
        'UI系统': ['UI系统', '界面', 'UGUI', 'FairyGUI', 'UI框架'],
        '资源管理': ['资源管理', 'AssetBundle', 'Addressable', '热更新', '资源加载'],
        '物理系统': ['物理系统', '碰撞检测', '刚体', 'Physics'],
        '渲染系统': ['渲染', 'Shader', '后处理', '光照', '材质'],
        '音频系统': ['音频', '音效', 'Wwise', 'FMOD', '声音'],
        '动画系统': ['动画', 'Animation', 'Animator', '动作', '骨骼'],
        '剧情系统': ['剧情', '对话系统', '任务系统', '叙事'],
        '经济系统': ['经济系统', '商城', '充值', '货币'],
    }
    for system, keywords in system_keywords.items():
        if any(kw in proj_text for kw in keywords):
            details['core_systems'].append(system)

    # 提取项目规模
    scale_indicators = []
    if '日活' in proj_text or 'DAU' in proj_text or '用户' in proj_text:
        scale_match = re.search(r'(?:日活|DAU|用户)[：:]?\s*([\d\w]+)', proj_text)
        if scale_match:
            scale_indicators.append(f"用户规模: {scale_match.group(1)}")
    if any(kw in proj_text for kw in ['同时在线', '并发']):
        scale_match = re.search(r'(?:同时在线|并发)[：:]?\s*([\d\w]+)', proj_text)
        if scale_match:
            scale_indicators.append(f"并发: {scale_match.group(1)}")

    if scale_indicators:
        details['project_scale'] = '，'.join(scale_indicators)

    return details


def infer_contribution_by_role(role: str) -> List[str]:
    """根据角色推断可能的贡献"""
    role_contributions = {
        '客户端': [
            '参与游戏客户端功能开发',
            '负责Gameplay系统实现',
            '参与UI交互逻辑开发',
            '协助资源管理与加载优化',
        ],
        '服务器': [
            '参与服务器后端开发',
            '负责网络同步逻辑实现',
            '参与数据存储方案设计',
        ],
        '主程序': [
            '主导项目技术架构设计',
            '负责核心系统开发',
            '指导团队成员开发',
        ],
        '独立开发': [
            '独立完成项目全部开发工作',
            '负责技术选型与架构设计',
            '完成 gameplay、UI、系统等模块',
        ],
    }
    return role_contributions.get(role, [])


def infer_core_systems_by_context(proj_text: str, role: str, tech_stack: List[str]) -> List[str]:
    """基于上下文推断可能的核心系统"""
    inferred_systems = []

    # 基于技术栈推断
    if any(tech in proj_text for tech in ['Unity', 'unity']):
        inferred_systems.extend(['资源管理', 'UI系统', '动画系统'])
    if any(tech in proj_text for tech in ['Wwise', 'wwise']):
        inferred_systems.append('音频系统')
    if 'ECS' in str(tech_stack):
        inferred_systems.append('ECS架构系统')

    # 基于角色推断
    role_systems = {
        '客户端': ['游戏玩法系统', 'UI系统', '资源管理'],
        '服务器': ['网络同步', '数据存储', '服务器架构'],
        '主程序': ['架构设计', '核心系统', '技术框架'],
    }
    if role in role_systems:
        inferred_systems.extend(role_systems[role])

    # 基于文本关键词推断
    if any(kw in proj_text for kw in ['游戏', '玩法', '操作', '战斗', '技能']):
        inferred_systems.append('游戏玩法系统')
    if any(kw in proj_text for kw in ['工作室', '团队', '协作', 'Git', 'SVN']):
        inferred_systems.append('版本控制协作')
    if any(kw in proj_text for kw in ['网络', '联机', '多人', '同步']):
        inferred_systems.append('网络同步系统')

    return list(set(inferred_systems))


def clean_extracted_text(text: str) -> Tuple[str, bool]:
    """
    清洗提取的文本，检测并处理乱码

    返回: (清洗后的文本, 是否包含乱码)
    """
    if not text:
        return "", False

    # 1. 检测异常字符比例
    # 定义正常中文字符、英文字母、数字、常用标点
    # 使用正则表达式定义正常字符范围（中文字符、英文字母、数字、常用标点）
    # 使用字符类避免过多转义，[\x5b\x5d] 代表 [ 和 ]
    normal_chars = re.compile('[\u4e00-\u9fa5a-zA-Z0-9\s，。、；：""''（）【】——/\\%@#&*()_+,.:;!?<>\x5b\x5d{}-]')

    total_chars = len(text)
    if total_chars == 0:
        return "", False

    normal_count = len(normal_chars.findall(text))
    abnormal_ratio = 1 - (normal_count / total_chars)

    # 如果异常字符比例超过30%，认为是乱码
    has_garbage = abnormal_ratio > 0.30

    # 2. 过滤无意义的控制字符和乱码模式
    # 移除常见乱码模式（如单个字母+符号的随机组合）
    cleaned = text

    # 移除孤立的外文字母（可能是PDF提取的乱码）
    # 保留成词的字母，移除随机单字母
    cleaned = re.sub(r'(?<![a-zA-Z])[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ](?![a-zA-Z])', '', cleaned)

    # 移除过多的连续特殊字符
    cleaned = re.sub(r'[^\w\u4e00-\u9fa5]{4,}', ' ', cleaned)

    # 3. 检测混合编码痕迹（如UTF-8误读为Latin-1的特征）
    garbage_patterns = [
        r'[\x00-\x08\x0b-\x0c\x0e-\x1f]',  # 控制字符
        r'Ã[\u00a0-\u00bf]',  # UTF-8误读为Latin-1的常见模式
        r'Â[\u00a0-\u00bf]',
        r'ï¿½',  # 替换字符
    ]

    for pattern in garbage_patterns:
        if re.search(pattern, cleaned):
            has_garbage = True
            cleaned = re.sub(pattern, '', cleaned)

    # 4. 清理多余空白
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned, has_garbage


def extract_meaningful_description(proj_text: str) -> str:
    """提取有意义的项目描述，带乱码检测"""
    # 1. 尝试找到"项目描述"、"项目介绍"等标签后的内容
    desc_patterns = [
        r'(?:项目描述|项目介绍|项目简介|描述)[：:]\s*([^\n]+(?:\n(?!(?:职责|角色|技术|成果|担任))[^\n]+)*)',
        r'(?:项目背景|背景)[：:]\s*([^\n]+)',
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, proj_text)
        if match:
            desc = match.group(1).strip()[:500]
            cleaned, has_garbage = clean_extracted_text(desc)
            if has_garbage and len(cleaned) < 20:
                # 如果清洗后内容太少，继续尝试其他段落
                continue
            return cleaned if cleaned else desc

    # 2. 如果没有匹配，取非列表标记的第一段有意义文字
    lines = proj_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        # 过滤列表标记和过短/过长的行
        if len(line) > 30 and len(line) < 300:
            if not re.match(r'^[-•◆●\d\s\.\[\(]', line):
                cleaned, has_garbage = clean_extracted_text(line)
                if not has_garbage or len(cleaned) > 20:
                    return cleaned[:500] if cleaned else line[:500]

    # 3. 兜底：返回前500字符（经过清洗）
    cleaned, has_garbage = clean_extracted_text(proj_text.strip()[:500])
    if has_garbage and len(cleaned) < 20:
        return "[文本提取异常，建议查看原始简历]"
    return cleaned if cleaned else proj_text.strip()[:500]


def extract_tech_highlights(proj_text: str, tech_stack: List[str]) -> List[str]:
    """
    提取技术亮点
    - 识别"实现了/开发了/设计了/优化了"等关键词
    - 提取性能数据（提升X%、降低X毫秒）
    - 识别创新点（自定义、自研、独创）
    """
    highlights = []

    # 技术实现关键词 - 扩展匹配模式
    implementation_patterns = [
        # 原有模式
        r'(?:实现了|开发了|设计了|搭建了|完成了|构建了)([^，。\n]{5,100})',
        # 新增模式 - 注意这里需要匹配"完成了"而不是"完成"，以避免匹配"完成"开头的词组
        r'(?:完成了|参与到|制作出|编写出|重构了|封装了|集成了|部署了)([^，。\n]{5,100})',
        r'(?:使用|运用|应用|借助|通过)([^，。\n]{3,50})(?:完成|实现|开发|制作|做到)([^，。\n]{5,80})',
        r'(?:解决|处理|克服|应对)了?([^，。\n]{5,100})(?:问题|困难|挑战|bug|Bug)',
        r'(?:优化|改进|完善|提升)了?([^，。\n]{5,100})',
        r'(?:独立|负责|主导)完成?了?([^，。\n]{5,100})',
    ]

    for pattern in implementation_patterns:
        matches = re.findall(pattern, proj_text)
        for match in matches:
            if isinstance(match, tuple):
                highlight = ''.join(match).strip()
            else:
                highlight = match.strip()
            if len(highlight) > 10 and len(highlight) < 150:
                # 过滤掉非技术描述
                if any(tech in highlight for tech in tech_stack + ['系统', '框架', '优化', '性能', '算法']):
                    highlights.append(highlight)

    # 提取性能优化数据
    perf_patterns = [
        r'(?:性能|效率|帧率|内存|加载)[^，。\n]*(?:提升|提高|优化|降低|减少)[^，。\n]*(?:\d+%?|\d+ms?|\d+秒?|X+倍?)',
        r'(?:提升|提高|优化|降低|减少)[^，。\n]*(?:\d+%?|\d+ms?|\d+秒?|X+倍?)[^，。\n]*(?:性能|效率|帧率|内存|加载)',
        r'(?:帧率|FPS)[^，。\n]*(?:提升|达到)[^，。\n]*\d+',
        r'(?:Draw ?Call|DC)[^，。\n]*(?:减少|降低|优化)[^，。\n]*\d+',
    ]
    for pattern in perf_patterns:
        perf_matches = re.findall(pattern, proj_text, re.IGNORECASE)
        for match in perf_matches:
            highlight = match.strip()
            if highlight and highlight not in highlights:
                highlights.append(f"性能优化: {highlight}")

    # 提取创新点
    innovation_keywords = ['自定义', '自研', '独创', '自主研发', '从零搭建', '架构设计']
    for keyword in innovation_keywords:
        pattern = rf'{keyword}([^，。\n]{{5,80}})'
        matches = re.findall(pattern, proj_text)
        for match in matches:
            highlight = f"{keyword}{match.strip()}"
            if highlight not in highlights:
                highlights.append(highlight)

    # 去重并限制数量
    unique_highlights = []
    for h in highlights:
        h_clean = re.sub(r'\s+', '', h)
        if not any(re.sub(r'\s+', '', existing) == h_clean for existing in unique_highlights):
            unique_highlights.append(h)

    return unique_highlights[:6]  # 最多返回6个亮点


def extract_personal_contribution(proj_text: str, role: str = '') -> List[str]:
    """
    提取个人贡献
    - 识别"负责/主导/独立/参与"等职责描述
    - 提取第一人称描述
    - 识别具体成果数据
    - 新增：基于角色的推断
    """
    contributions = []

    # 职责描述模式 - 扩展模式
    responsibility_patterns = [
        # 原有模式
        r'(?:负责|主导|独立|带领|参与|协助|配合)了?([^，。：\n]{5,100})',
        r'(?:我|本人)(?:负责|主导|独立|参与|完成|实现)了?([^，。：\n]{5,100})',
        r'(?:担任|作为)([^，。：\n]{3,20})(?:负责|主导|参与)了?([^，。：\n]{5,80})',
        # 新增模式 - 匹配更自然的描述
        r'(?:参与|协作|配合)了?([^，。：\n]{5,100})',
        r'(?:学习|掌握|熟悉|了解)了?([^，。：\n]{5,60})(?:技术|工具|技能|框架)',
        r'(?:积累|沉淀|总结)了?([^，。：\n]{5,80})(?:经验|能力|知识)',
    ]

    for pattern in responsibility_patterns:
        matches = re.findall(pattern, proj_text)
        for match in matches:
            if isinstance(match, tuple):
                contribution = ''.join(match).strip()
            else:
                contribution = match.strip()
            if len(contribution) > 5 and len(contribution) < 120:
                contributions.append(contribution)

    # 提取具体成果（包含数字）
    achievement_patterns = [
        r'(?:完成|实现|交付|上线)[^，。\n]*(?:\d+)[^，。\n]*(?:个|项|套|版|功能|模块|系统)',
        r'(?:优化|改进)[^，。\n]*(?:\d+)[^，。\n]*(?:处|个|项|问题|Bug)',
        r'(?:节约|节省|减少)[^，。\n]*(?:\d+)[^，。\n]*(?:时间|成本|人力|资源)',
    ]
    for pattern in achievement_patterns:
        matches = re.findall(pattern, proj_text)
        for match in matches:
            if match.strip() and match.strip() not in contributions:
                contributions.append(match.strip())

    # 去重
    unique_contributions = []
    for c in contributions:
        c_clean = re.sub(r'\s+', '', c)
        if not any(re.sub(r'\s+', '', existing) == c_clean for existing in unique_contributions):
            unique_contributions.append(c)

    # 如果规则提取不到内容，尝试基于角色推断
    if not unique_contributions and role:
        inferred = infer_contribution_by_role(role)
        if inferred:
            # 添加推断标记
            unique_contributions = [f"[基于角色推断] {c}" for c in inferred[:2]]

    return unique_contributions[:5]  # 最多返回5个贡献点


def analyze_project_complexity(project: Dict) -> Dict:
    """
    基于多维度评估项目复杂度
    - 技术栈丰富度 (20%)
    - 系统复杂度 (25%)
    - 项目规模 (20%)
    - 技术亮点 (20%)
    - 描述完整度 (15%)
    返回复杂度等级和评估理由
    """
    score = 0
    reasons = []

    # 1. 技术栈丰富度 (最高20分)
    tech_count = len(project.get('tech_stack', []))
    if tech_count >= 5:
        score += 20
        reasons.append('技术栈丰富')
    elif tech_count >= 3:
        score += 15
        reasons.append('技术栈较丰富')
    elif tech_count >= 1:
        score += 8
    else:
        reasons.append('技术栈单一')

    # 2. 系统复杂度 (最高25分)
    core_systems = project.get('core_systems', [])
    system_count = len(core_systems)
    if system_count >= 4:
        score += 25
        reasons.append(f'涉及{system_count}个核心系统')
    elif system_count >= 2:
        score += 18
        reasons.append(f'涉及{system_count}个核心系统')
    elif system_count >= 1:
        score += 10
    else:
        reasons.append('未明确核心系统')

    # 3. 项目规模 (最高20分)
    scale_score = 0
    team_size = project.get('team_size', '')
    if team_size:
        team_num = re.search(r'(\d+)', team_size)
        if team_num:
            num = int(team_num.group(1))
            if num >= 10:
                scale_score = 20
                reasons.append('团队规模较大')
            elif num >= 5:
                scale_score = 15
            elif num >= 3:
                scale_score = 10
            else:
                scale_score = 5

    dev_time = project.get('development_time', '')
    if dev_time and ('年' in dev_time or re.search(r'\d+\s*个月', dev_time)):
        if scale_score < 15:
            scale_score = 15
        if '开发周期长' not in reasons:
            reasons.append('开发周期较长')

    score += scale_score

    # 4. 技术亮点 (最高20分)
    highlights = project.get('tech_highlights', [])
    highlight_count = len(highlights)
    if highlight_count >= 4:
        score += 20
        reasons.append('技术亮点突出')
    elif highlight_count >= 2:
        score += 15
        reasons.append('有技术亮点')
    elif highlight_count >= 1:
        score += 8
    else:
        reasons.append('缺少技术亮点描述')

    # 5. 描述完整度 (最高15分)
    desc_len = len(project.get('description', ''))
    if desc_len >= 400:
        score += 15
    elif desc_len >= 200:
        score += 10
        if desc_len < 300:
            reasons.append('项目描述可更详细')
    elif desc_len >= 100:
        score += 5
        reasons.append('项目描述较简单')
    else:
        score += 2
        reasons.append('项目描述过于简单')

    # 确定复杂度等级
    if score >= 75:
        level = '高'
    elif score >= 50:
        level = '中等'
    elif score >= 30:
        level = '一般'
    else:
        level = '入门'

    # 生成评估理由
    if reasons:
        reason_text = '，'.join(reasons[:3])  # 最多显示3个理由
    else:
        reason_text = '项目信息完整度一般'

    return {
        'score': min(score, 100),
        'level': level,
        'reason': reason_text
    }


def extract_work_experience(text: str) -> List[str]:
    """提取工作经历"""
    experiences = []

    patterns = [
        r'(?:工作经历|工作经验|Work Experience)[：:\s]*\n?(.+?)(?=项目经历|教育背景|个人技能|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            exp_text = match.group(1).strip()
            # 简单按行分割
            lines = [line.strip() for line in exp_text.split('\n') if line.strip()]
            return lines[:5]  # 最多5条

    return experiences


def analyze_skills(parsed_data: Dict) -> Dict:
    """
    分析技能熟练度和风险点

    返回分析结果：
    {
        'skill_levels': List[Dict],
        'advantages': List[str],
        'risks': List[str],
        'recommendation_level': str,
        'overall_assessment': str,
        'suitable_positions': List[str]
    }
    """
    analysis = {
        'skill_levels': [],
        'advantages': [],
        'risks': [],
        'recommendation_level': 'B',
        'overall_assessment': '',
        'suitable_positions': []
    }

    skills = parsed_data['skills']
    projects = parsed_data['projects']

    # 分析技能熟练度 - 使用字典去重，确保同一技能只保留一条记录
    # 优先级：编程语言 > 游戏引擎 > 专业技能 > 工具
    skill_records = {}  # skill_name -> {category, level, evidence, priority}

    # 按优先级顺序处理，优先级高的先处理
    category_priority = {
        '编程语言': 1,
        '游戏引擎': 2,
        '专业技能': 3,
        '工具': 4
    }

    all_skills = []
    all_skills.extend([(s, '编程语言') for s in skills['languages']])
    all_skills.extend([(s, '游戏引擎') for s in skills['engines']])
    all_skills.extend([(s, '专业技能') for s in skills['professional']])
    all_skills.extend([(s, '工具') for s in skills['tools']])

    for skill, category in all_skills:
        # 跳过空技能名
        if not skill:
            continue

        # 标准化技能名（用于去重比较）
        skill_normalized = skill.lower().strip()

        level = '了解'
        evidence = '简历提及'

        # 根据项目数量判断熟练度
        related_projects = sum(1 for p in projects if skill in str(p))
        if related_projects >= 2:
            level = '精通'
            evidence = f'{related_projects}个项目'
        elif related_projects == 1:
            level = '熟练'
            evidence = '1个项目'
        elif len(projects) > 0:
            level = '了解'
            evidence = '简历提及'

        # 如果技能已存在，根据优先级和熟练度决定是否更新
        if skill_normalized in skill_records:
            existing = skill_records[skill_normalized]
            current_priority = category_priority.get(category, 99)
            existing_priority = category_priority.get(existing['category'], 99)

            # 优先级相同时，保留熟练度更高的
            if current_priority == existing_priority:
                level_priority = {'精通': 3, '熟练': 2, '了解': 1}
                if level_priority.get(level, 0) > level_priority.get(existing['level'], 0):
                    skill_records[skill_normalized] = {
                        'skill': skill,
                        'category': category,
                        'level': level,
                        'evidence': evidence,
                        'priority': current_priority
                    }
            # 优先级更高时，替换
            elif current_priority < existing_priority:
                skill_records[skill_normalized] = {
                    'skill': skill,
                    'category': category,
                    'level': level,
                    'evidence': evidence,
                    'priority': current_priority
                }
        else:
            # 新技能，直接添加
            skill_records[skill_normalized] = {
                'skill': skill,
                'category': category,
                'level': level,
                'evidence': evidence,
                'priority': category_priority.get(category, 99)
            }

    # 转换为列表并按类别分组排序
    analysis['skill_levels'] = [
        {k: v for k, v in record.items() if k != 'priority'}
        for record in skill_records.values()
    ]

    # 生成优势亮点
    advantages = []

    # 引擎经验
    if 'Unity' in skills['engines']:
        advantages.append('具备Unity引擎开发经验')
    if 'Unreal Engine' in skills['engines']:
        advantages.append('具备Unreal Engine开发经验')

    # 编程语言
    if 'C#' in skills['languages'] and 'C++' in skills['languages']:
        advantages.append('同时掌握C#和C++，语言基础扎实')

    # 项目经验
    if len(projects) >= 2:
        advantages.append(f'有{len(projects)}个项目经历，项目经验丰富')

    # 特殊技能
    advanced_skills = ['ECS', 'Shader', '网络', 'AI', '性能优化']
    for skill in advanced_skills:
        if any(skill in s for s in skills['professional']):
            advantages.append(f'具备{skill}相关经验')
            break

    if not advantages:
        advantages.append('基础技能符合岗位要求')

    analysis['advantages'] = advantages

    # 生成风险点
    risks = []

    # 检查技能组合是否合理
    if 'Unity' in str(skills['engines']) and 'C#' not in str(skills['languages']):
        risks.append('Unity经验但未见C#技能，需验证实际使用程度')

    if 'Unreal Engine' in str(skills['engines']) and 'C++' not in str(skills['languages']):
        risks.append('Unreal经验但未见C++技能，需确认使用版本和深度')

    # 项目描述简单
    if projects:
        avg_desc_len = sum(len(p['description']) for p in projects) / len(projects)
        if avg_desc_len < 100:
            risks.append('项目描述较为简单，需深入了解项目细节和技术难点')

    # 缺少核心技术
    if not any(kw in str(skills['professional']) for kw in ['设计模式', '架构']):
        risks.append('未见架构/设计模式相关经验，需验证代码组织能力')

    if not risks:
        risks.append('需进一步面试验证技术深度')

    analysis['risks'] = risks

    # 推荐等级
    if len(projects) >= 3 and len(skills['languages']) >= 2:
        analysis['recommendation_level'] = 'A'
        analysis['overall_assessment'] = '项目经验丰富，技术栈全面，强烈推荐'
    elif len(projects) >= 2:
        analysis['recommendation_level'] = 'B'
        analysis['overall_assessment'] = '项目经验良好，具备岗位所需基础能力'
    elif len(projects) >= 1:
        analysis['recommendation_level'] = 'C'
        analysis['overall_assessment'] = '项目经验有限，需谨慎评估实际能力'
    else:
        analysis['recommendation_level'] = 'D'
        analysis['overall_assessment'] = '项目经验不足，建议了解学习能力和潜力'

    # 适合岗位
    if 'Unity' in str(skills['engines']):
        analysis['suitable_positions'].append('Unity游戏开发工程师')
    if 'Unreal Engine' in str(skills['engines']):
        analysis['suitable_positions'].append('UE4/UE5游戏开发工程师')
    if not analysis['suitable_positions']:
        analysis['suitable_positions'].append('游戏开发工程师')

    return analysis


def generate_skill_report(parsed_data: Dict, analysis: Dict, output_dir: str) -> str:
    """生成技能评估报告"""
    name = parsed_data['name']
    today = datetime.now().strftime('%Y%m%d')

    lines = []
    lines.append(f"# 候选人技能评估报告 - {name}")
    lines.append("")

    # 基本信息
    lines.append("## 基本信息")
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append(f"| 姓名 | {name} |")
    lines.append(f"| 期望岗位 | {parsed_data['position']} |")
    lines.append(f"| 工作年限 | {parsed_data['experience_years']} |")
    lines.append(f"| 毕业院校 | {parsed_data['education'] or '未识别'} |")
    lines.append("")

    # 技能概览
    lines.append("## 技能概览")
    lines.append("")

    skills = parsed_data['skills']

    lines.append("### 技术栈")
    lines.append("")
    if skills['languages']:
        lines.append(f"- **编程语言**: {', '.join(skills['languages'])}")
    if skills['engines']:
        lines.append(f"- **游戏引擎**: {', '.join(skills['engines'])}")
    if skills['professional']:
        prof_str = ', '.join(skills['professional'][:10])  # 最多显示10个
        lines.append(f"- **专业技能**: {prof_str}")
    if skills['tools']:
        tools_str = ', '.join(skills['tools'][:8])  # 最多显示8个
        lines.append(f"- **工具**: {tools_str}")
    lines.append("")

    # 技能熟练度评估 - 按类别分组的简洁列表格式
    lines.append("### 技能熟练度评估")
    lines.append("")

    # 按类别分组
    category_order = ['编程语言', '游戏引擎', '专业技能', '工具']
    skills_by_category = {}
    for item in analysis['skill_levels']:
        cat = item['category']
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(item)

    # 按优先级顺序输出各分类
    for category in category_order:
        if category in skills_by_category:
            items = skills_by_category[category]
            # 按熟练度排序：精通 > 熟练 > 了解
            level_order = {'精通': 0, '熟练': 1, '了解': 2}
            items.sort(key=lambda x: (level_order.get(x['level'], 3), x['skill']))

            lines.append(f"**{category}**")
            for item in items[:10]:  # 每类最多显示10个
                lines.append(f"- {item['skill']} - {item['level']}（{item['evidence']}）")
            lines.append("")

    # 项目经历分析
    lines.append("## 项目经历分析")
    lines.append("")

    for i, project in enumerate(parsed_data['projects'][:3], 1):  # 最多3个项目
        lines.append(f"### 项目{i}: {project['name']}")
        lines.append(f"- **项目类型**: {project.get('type', '游戏项目')}")
        lines.append(f"- **担任角色**: {project.get('role') or '未明确'}")

        # 团队规模和开发周期
        if project.get('team_size'):
            lines.append(f"- **团队规模**: {project['team_size']}")
        if project.get('development_time'):
            lines.append(f"- **开发周期**: {project['development_time']}")

        # 项目规模
        if project.get('project_scale'):
            lines.append(f"- **项目规模**: {project['project_scale']}")

        lines.append("")

        # 项目描述（截取前200字符）
        desc = project.get('description', '')
        if desc:
            desc_short = desc[:200] + '...' if len(desc) > 200 else desc
            lines.append(f"**项目描述**: {desc_short}")
            lines.append("")

        # 技术栈
        if project.get('tech_stack'):
            lines.append(f"- **技术栈**: {', '.join(project['tech_stack'])}")

        # 核心系统
        if project.get('core_systems'):
            systems_str = ', '.join(project['core_systems'])
            if project.get('inferred_core_systems'):
                lines.append(f"- **核心系统**（推断）: {systems_str}")
            else:
                lines.append(f"- **核心系统**: {systems_str}")

        lines.append("")

        # 技术亮点
        tech_highlights = project.get('tech_highlights', [])
        if tech_highlights:
            lines.append("**技术亮点**:")
            for highlight in tech_highlights[:4]:  # 最多显示4个亮点
                lines.append(f"  - {highlight}")
            lines.append("")

        # 个人贡献
        contributions = project.get('personal_contribution', [])
        if contributions:
            lines.append("**个人贡献**:")
            for contrib in contributions[:3]:  # 最多显示3个贡献点
                lines.append(f"  - {contrib}")
            lines.append("")

        # 复杂度评估
        complexity_level = project.get('complexity_level', '未知')
        complexity_reason = project.get('complexity_reason', '')
        lines.append(f"- **复杂度评估**: {complexity_level}")
        if complexity_reason:
            lines.append(f"- **评估理由**: {complexity_reason}")

        # 风险点
        risks = []
        follow_up_questions = []

        if not project.get('role'):
            risks.append('职责描述不清晰，建议追问具体分工')
            follow_up_questions.append('你在项目中具体担任什么角色？负责哪些模块？')

        if len(desc) < 100:
            risks.append('项目描述较简单，建议深入了解技术细节')
            follow_up_questions.append('请详细描述项目的技术架构和实现方案')

        if not tech_highlights:
            risks.append('未明确技术亮点，建议询问遇到的技术难点和解决方案')
            follow_up_questions.append('项目开发中遇到过哪些技术挑战？如何解决的？')

        if not contributions:
            risks.append('个人贡献不突出，建议追问具体负责的工作内容')
            follow_up_questions.append('在这个项目中你具体完成了哪些工作？')

        if project.get('inferred_core_systems'):
            risks.append('核心系统未明确，建议核实实际参与的系统')

        if risks:
            lines.append(f"- **风险点**: {'; '.join(risks)}")

        # 添加建议追问问题
        if follow_up_questions and not tech_highlights:
            lines.append("- **建议追问**:")
            for q in follow_up_questions[:2]:
                lines.append(f"  - {q}")

        lines.append("")

    # 优势亮点
    lines.append("## 优势亮点")
    lines.append("")
    for i, adv in enumerate(analysis['advantages'], 1):
        lines.append(f"{i}. {adv}")
    lines.append("")

    # 风险点
    lines.append("## 风险点/待验证")
    lines.append("")
    for i, risk in enumerate(analysis['risks'], 1):
        lines.append(f"{i}. {risk}")
    lines.append("")

    # 综合评价
    lines.append("## 综合评价")
    lines.append("")
    lines.append(f"- **推荐等级**: {analysis['recommendation_level']}级")
    lines.append(f"- **总体评价**: {analysis['overall_assessment']}")
    lines.append(f"- **适合岗位**: {', '.join(analysis['suitable_positions'])}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*报告由简历自动分析系统生成*")
    lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    content = "\n".join(lines)

    # 保存文件
    filename = f"技能评估报告_{name}_{today}.md"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def generate_question_list(parsed_data: Dict, analysis: Dict, output_dir: str) -> str:
    """
    生成面试问题清单

    使用新的问题生成器，根据候选人技能智能选择问题
    """
    name = parsed_data['name']
    today = datetime.now().strftime('%Y%m%d')
    skills = parsed_data['skills']
    projects = parsed_data['projects']

    lines = []
    lines.append(f"# 面试问题清单 - {name}")
    lines.append("")

    # 面试概览
    lines.append("## 面试概览")
    lines.append(f"- **候选人**: {name}")
    lines.append(f"- **岗位**: {parsed_data['position']}")
    lines.append(f"- **建议时长**: 根据问题数量动态调整")
    lines.append("")

    # 候选人技能摘要
    lines.append("### 候选人技能摘要")
    if skills.get('languages'):
        lines.append(f"- **编程语言**: {', '.join(skills['languages'])}")
    if skills.get('engines'):
        lines.append(f"- **游戏引擎**: {', '.join(skills['engines'])}")
    if skills.get('professional'):
        lines.append(f"- **专业技能**: {', '.join(skills['professional'][:8])}")
    lines.append("")

    # 使用新的问题生成器生成问题
    try:
        # 动态导入以避免循环依赖
        import importlib.util
        script_dir = os.path.dirname(os.path.abspath(__file__))
        generator_path = os.path.join(script_dir, 'question_generator.py')

        spec = importlib.util.spec_from_file_location("question_generator", generator_path)
        question_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(question_generator)

        # 创建生成器并生成问题
        generator = question_generator.QuestionGenerator()
        question_data = generator.generate_for_candidate(skills, projects, analysis)

        # 添加技能维度问题
        if question_data.get('skills'):
            lines.append("## 技能维度考察")
            lines.append("")
            lines.append("*根据候选人技能标签匹配的问题维度，按熟练度选择问题难度*")
            lines.append("")

            for skill_name, skill_info in question_data['skills'].items():
                prof = skill_info.get('proficiency', '熟练')
                proj_count = skill_info.get('project_count', 0)
                questions = skill_info.get('questions', [])

                if not questions:
                    continue

                lines.append(f"### {skill_name} ({prof} - {proj_count}个项目)")
                lines.append("")

                # 按难度分组显示
                by_difficulty = {"初级": [], "中级": [], "高级": [], "项目深挖": []}
                for q in questions:
                    if q.difficulty in by_difficulty:
                        by_difficulty[q.difficulty].append(q)

                # 显示各类问题
                for diff in ["初级", "中级", "高级"]:
                    qs = by_difficulty[diff]
                    if not qs:
                        continue

                    lines.append(f"**{diff}问题** (选择{min(len(qs), 2)}个提问):")
                    for i, q in enumerate(qs[:3], 1):
                        lines.append(f"- [ ] {q.content}")
                    lines.append("")

                # 项目深挖问题
                if by_difficulty["项目深挖"]:
                    lines.append(f"**项目深挖** (针对{skill_name}在项目中使用):")
                    for q in by_difficulty["项目深挖"][:2]:
                        lines.append(f"- [ ] {q.content}")
                    lines.append("")

        # 添加项目深挖问题
        if question_data.get('projects'):
            lines.append("## 项目深挖")
            lines.append("")
            lines.append("*针对具体项目经历的技术追问*")
            lines.append("")

            for project in question_data['projects']:
                proj_name = project.get('name', '未命名项目')
                tech_stack = project.get('tech_stack', [])
                role = project.get('role', '')
                questions = project.get('questions', [])

                lines.append(f"### {proj_name}")
                if tech_stack:
                    lines.append(f"**技术栈**: {', '.join(tech_stack[:5])}")
                if role:
                    lines.append(f"**角色**: {role}")
                lines.append("")

                # 通用项目问题
                lines.append("**架构与设计**:")
                lines.append(f"- [ ] 请介绍一下《{proj_name}》的整体架构设计")
                lines.append(f"- [ ] 你在项目中担任{role or '什么角色'}？团队规模如何？")
                lines.append(f"- [ ] 项目的技术亮点是什么？最大的技术挑战在哪里？")
                lines.append("")

                # 技术栈相关问题
                if tech_stack:
                    lines.append("**技术细节追问**:")
                    for tech in tech_stack[:3]:
                        lines.append(f"- [ ] [{tech}] 项目中具体如何使用{tech}？遇到过什么问题？")
                    lines.append("")

                lines.append("**挑战与解决**:")
                lines.append("- [ ] 项目中遇到的最大技术挑战是什么？如何解决的？")
                lines.append("- [ ] 如果重新设计这个项目，会做哪些改进？")
                lines.append("- [ ] 如何保证代码质量和可维护性？")
                lines.append("")

        # 添加薄弱环节验证问题
        if question_data.get('weakness') and analysis.get('risks'):
            lines.append("## 薄弱环节验证")
            lines.append("")
            lines.append("*基于简历分析发现的风险点进行针对性验证*")
            lines.append("")

            for i, risk in enumerate(analysis['risks'][:3], 1):
                lines.append(f"**风险点{i}**: {risk}")
                lines.append("")

            lines.append("**验证问题**:")
            for q in question_data['weakness'][:5]:
                lines.append(f"- [ ] [{q.dimension}] {q.content}")
            lines.append("")

        # 添加通用问题
        if question_data.get('general'):
            lines.append("## 通用问题")
            lines.append("")
            lines.append("**软技能与项目经验**:")
            for q in question_data['general'][:5]:
                lines.append(f"- [ ] {q.content}")
            lines.append("")

    except Exception as e:
        # 如果新生成器失败，使用简单的备选方案
        lines.append("## 技能考察")
        lines.append("")
        lines.append(f"*问题生成模块加载失败 ({e})，使用备选问题*")
        lines.append("")

        if 'C#' in str(skills.get('languages', [])):
            lines.append("### C#基础")
            lines.append("- [ ] 值类型和引用类型的区别？什么是装箱拆箱？")
            lines.append("- [ ] 什么是GC？如何避免GC Alloc？")
            lines.append("")

        if 'Unity' in str(skills.get('engines', [])):
            lines.append("### Unity专项")
            lines.append("- [ ] Unity生命周期函数的执行顺序？")
            lines.append("- [ ] 项目中是如何进行资源管理的？")
            lines.append("")

        if 'C++' in str(skills.get('languages', [])):
            lines.append("### C++基础")
            lines.append("- [ ] 指针和引用的区别？")
            lines.append("- [ ] 什么是内存泄漏？如何避免？")
            lines.append("")

        # 项目问题
        lines.append("## 项目深挖")
        lines.append("")
        for i, project in enumerate(projects[:3], 1):
            lines.append(f"### 项目{i}: {project.get('name', '未命名')}")
            lines.append(f"- [ ] 请介绍项目架构和技术选型")
            lines.append(f"- [ ] 项目中遇到的最大挑战是什么？")
            lines.append("")

    # 面试流程指引
    lines.append("---")
    lines.append("")
    lines.append("## 面试流程建议")
    lines.append("")
    lines.append("| 阶段 | 时间 | 内容 |")
    lines.append("|------|------|------|")
    lines.append("| 自我介绍 | 2-3分钟 | 候选人背景了解 |")
    lines.append("| 技能考察 | 15-20分钟 | 按技能维度提问 |")
    lines.append("| 项目深挖 | 10-15分钟 | 针对具体项目追问 |")
    lines.append("| 薄弱验证 | 5分钟 | 验证风险点 |")
    lines.append("| 候选人提问 | 3-5分钟 | 回答候选人问题 |")
    lines.append("")

    # 评分记录表
    lines.append("## 评分记录表")
    lines.append("")
    lines.append("| 维度 | 权重 | 得分 | 备注 |")
    lines.append("|------|------|------|------|")
    lines.append("| 技术深度 | 30% | ___ | 技能掌握程度 |")
    lines.append("| 项目经验 | 25% | ___ | 项目复杂度/贡献 |")
    lines.append("| 问题解决 | 20% | ___ | 分析和解决问题能力 |")
    lines.append("| 基础知识 | 15% | ___ | 数据结构/算法/设计模式 |")
    lines.append("| 沟通协作 | 10% | ___ | 表达/团队协作意识 |")
    lines.append("| **总分** | **100%** | ___ | |")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"*面试问题清单由简历自动分析系统生成*")
    lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    content = "\n".join(lines)

    # 保存文件
    filename = f"面试问题清单_{name}_{today}.md"
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='从PDF简历自动生成技能评估报告和面试问题清单',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python3 analyze_resume.py /path/to/resume.pdf

  # 指定输出目录
  python3 analyze_resume.py /path/to/resume.pdf -o ./reports

  # 指定候选人姓名
  python3 analyze_resume.py /path/to/resume.pdf --name "张三"
        """
    )

    parser.add_argument('pdf_path', help='PDF简历文件路径')
    parser.add_argument('-o', '--output-dir', help='输出目录（默认为PDF所在目录）')
    parser.add_argument('--name', help='候选人姓名（如PDF中无法自动识别）')

    args = parser.parse_args()

    print("=" * 60)
    print("  简历自动分析系统")
    print("=" * 60)
    print()

    # 步骤1: 提取PDF文本
    print("📄 正在提取PDF文本...")
    try:
        text = extract_pdf_text(args.pdf_path)
        print(f"   ✓ 成功提取 {len(text)} 字符")
    except Exception as e:
        print(f"   ✗ 错误: {e}")
        sys.exit(1)

    # 步骤2: 解析简历信息
    print("\n🔍 正在解析简历信息...")
    parsed_data = parse_resume(text)

    # 如果指定了姓名，覆盖自动识别的
    if args.name:
        parsed_data['name'] = args.name

    print(f"   ✓ 姓名: {parsed_data['name']}")
    print(f"   ✓ 期望岗位: {parsed_data['position']}")
    print(f"   ✓ 工作年限: {parsed_data['experience_years']}")
    print(f"   ✓ 编程语言: {', '.join(parsed_data['skills']['languages']) or '未识别'}")
    print(f"   ✓ 游戏引擎: {', '.join(parsed_data['skills']['engines']) or '未识别'}")
    print(f"   ✓ 项目数量: {len(parsed_data['projects'])}")

    # 步骤3: 分析技能
    print("\n📊 正在分析技能熟练度...")
    analysis = analyze_skills(parsed_data)
    print(f"   ✓ 识别技能: {len(analysis['skill_levels'])} 项")
    print(f"   ✓ 推荐等级: {analysis['recommendation_level']}级")

    # 始终使用 PDF 所在目录作为输出目录
    output_dir = os.path.dirname(os.path.abspath(args.pdf_path))

    # 步骤4: 生成技能评估报告
    print("\n📝 正在生成技能评估报告...")
    report_path = generate_skill_report(parsed_data, analysis, output_dir)
    print(f"   ✓ 报告已保存: {report_path}")

    # 步骤5: 生成面试问题清单
    print("\n📋 正在生成面试问题清单...")
    question_path = generate_question_list(parsed_data, analysis, output_dir)
    print(f"   ✓ 清单已保存: {question_path}")

    # 完成
    print("\n" + "=" * 60)
    print("  分析完成！")
    print("=" * 60)
    print(f"\n📁 生成的文件:")
    print(f"   1. {report_path}")
    print(f"   2. {question_path}")
    print()


if __name__ == "__main__":
    main()
