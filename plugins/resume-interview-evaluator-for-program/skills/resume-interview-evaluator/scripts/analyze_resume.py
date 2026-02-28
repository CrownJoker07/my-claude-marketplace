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
            project_name = name_match.group(1).strip()
        else:
            # 方式2：取项目文本的第一行作为项目名（如果不是分隔符）
            first_line = proj_text.strip().split('\n')[0].strip()
            # 过滤掉纯数字、分隔符等无意义内容
            if first_line and len(first_line) > 2 and len(first_line) < 50:
                # 去除常见的列表标记（如 "1. ", "- ", "◆ " 等）
                cleaned_name = re.sub(r'^[\d\s\.\-\◆\●\*\[\(]+', '', first_line)
                if cleaned_name and len(cleaned_name) > 2:
                    project_name = cleaned_name

        project = {
            'name': project_name or f'项目{i+1}',
            'type': '',
            'role': '',
            'description': proj_text.strip()[:500],
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

        # 提取个人贡献
        personal_contribution = extract_personal_contribution(proj_text)

        # 提取项目详细信息
        project_details = extract_project_details(proj_text)
        project['project_scale'] = project_details.get('project_scale', '')
        project['development_time'] = project_details.get('development_time', '')
        project['team_size'] = project_details.get('team_size', '')
        project['core_systems'] = project_details.get('core_systems', [])
        project['tech_highlights'] = tech_highlights
        project['personal_contribution'] = personal_contribution

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


def extract_tech_highlights(proj_text: str, tech_stack: List[str]) -> List[str]:
    """
    提取技术亮点
    - 识别"实现了/开发了/设计了/优化了"等关键词
    - 提取性能数据（提升X%、降低X毫秒）
    - 识别创新点（自定义、自研、独创）
    """
    highlights = []

    # 技术实现关键词
    implementation_patterns = [
        r'(?:实现了|开发了|设计了|搭建了|完成了|构建了)([^，。\n]{5,100})',
        r'(?:基于|使用|采用)([^，。\n]{3,50})(?:实现了|开发了|完成了)([^，。\n]{5,80})',
        r'(?:独立|负责|主导)([^，。\n]{5,100})',
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


def extract_personal_contribution(proj_text: str) -> List[str]:
    """
    提取个人贡献
    - 识别"负责/主导/独立/参与"等职责描述
    - 提取第一人称描述
    - 识别具体成果数据
    """
    contributions = []

    # 职责描述模式
    responsibility_patterns = [
        r'(?:负责|主导|独立|带领|参与|协助|配合)([^，。\n]{5,100})',
        r'(?:我|本人)(?:负责|主导|独立|参与|完成|实现)([^，。\n]{5,100})',
        r'(?:担任|作为)([^，。\n]{3,20})(?:负责|主导|参与)([^，。\n]{5,80})',
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

    # 分析技能熟练度
    all_skills = []
    all_skills.extend([(s, '编程语言') for s in skills['languages']])
    all_skills.extend([(s, '游戏引擎') for s in skills['engines']])
    all_skills.extend([(s, '专业技能') for s in skills['professional']])
    all_skills.extend([(s, '工具') for s in skills['tools']])

    for skill, category in all_skills:
        level = '了解'
        evidence = '简历提及'

        # 根据项目数量判断熟练度
        related_projects = sum(1 for p in projects if skill in str(p))
        if related_projects >= 2:
            level = '精通'
            evidence = f'{related_projects}个项目经验'
        elif related_projects == 1:
            level = '熟练'
            evidence = '1个项目经验'
        elif len(projects) > 0:
            level = '了解'
            evidence = '简历提及'

        analysis['skill_levels'].append({
            'skill': skill,
            'category': category,
            'level': level,
            'evidence': evidence
        })

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

    # 技能熟练度评估
    lines.append("### 技能熟练度评估")
    lines.append("")
    lines.append("| 技能 | 熟练度 | 证据来源 |")
    lines.append("|------|--------|----------|")

    for item in analysis['skill_levels'][:15]:  # 最多显示15个
        lines.append(f"| {item['skill']} | {item['level']} | {item['evidence']} |")
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
            lines.append(f"- **核心系统**: {', '.join(project['core_systems'])}")

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
        if not project.get('role'):
            risks.append('职责描述不清晰')
        if len(desc) < 100:
            risks.append('项目描述过于简单')
        if not tech_highlights:
            risks.append('缺少技术亮点描述')
        if not contributions:
            risks.append('缺少个人贡献说明')
        if risks:
            lines.append(f"- **风险点**: {'; '.join(risks)}")

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
    """生成面试问题清单"""
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
    lines.append(f"- **建议时长**: 30-35分钟")
    lines.append("")

    # 阶段1: 自我介绍
    lines.append("## 阶段1: 自我介绍 (2分钟)")
    lines.append("- [ ] 请简单介绍一下自己")
    lines.append("- [ ] 为什么来面试这个岗位？")
    lines.append("- [ ] 为什么选择我们公司/项目组？")
    lines.append("")

    # 阶段2: 项目经历深挖
    lines.append("## 阶段2: 项目经历深挖 (20分钟)")
    lines.append("")

    for i, project in enumerate(projects[:3], 1):
        lines.append(f"### 项目{i}: {project['name']}")
        lines.append("")

        # 架构问题
        lines.append("**架构与设计**:")
        lines.append(f"- [ ] 请介绍一下《{project['name']}》的整体架构")
        lines.append(f"- [ ] 你在项目中担任{project['role'] or '什么角色'}？团队规模？")
        lines.append(f"- [ ] 项目的核心玩法是什么？技术挑战在哪里？")
        lines.append("")

        # 技术细节问题（基于技术栈）
        if project['tech_stack']:
            lines.append("**技术细节**:")
            for tech in project['tech_stack'][:3]:
                if tech == 'Unity':
                    lines.append(f"- [ ] [{tech}] 项目中使用了Unity的哪些系统？")
                    lines.append(f"- [ ] [{tech}] 资源管理是如何做的？")
                elif tech == 'Wwise':
                    lines.append(f"- [ ] [{tech}] Wwise与Unity音频系统的区别？")
                elif tech == '行为树':
                    lines.append(f"- [ ] [{tech}] AI的行为树是如何设计的？")
                else:
                    lines.append(f"- [ ] [{tech}] 如何使用{tech}解决具体问题？")
            lines.append("")

        # 挑战与解决
        lines.append("**挑战与解决**:")
        lines.append("- [ ] 项目中遇到的最大技术挑战是什么？如何解决的？")
        lines.append("- [ ] 如果重新设计这个项目，会做哪些改进？")
        lines.append("- [ ] 如何保证代码质量和可维护性？")
        lines.append("")

    # 阶段3: 基础能力考察
    lines.append("## 阶段3: 基础能力考察 (5分钟)")
    lines.append("")

    # 根据技能生成针对性问题
    if 'C#' in str(skills['languages']):
        lines.append("### C#基础")
        lines.append("- [ ] 值类型和引用类型的区别？什么是装箱拆箱？")
        lines.append("- [ ] 什么是GC？如何避免GC Alloc？")
        lines.append("- [ ] 委托和事件的区别？")
        lines.append("")

    if 'Unity' in str(skills['engines']):
        lines.append("### Unity专项")
        lines.append("- [ ] Unity生命周期函数的执行顺序？")
        lines.append("- [ ] MonoBehaviour的原理？")
        lines.append("- [ ] Resources.Load和Addressable的区别？")
        lines.append("")

    if 'C++' in str(skills['languages']):
        lines.append("### C++基础")
        lines.append("- [ ] 指针和引用的区别？")
        lines.append("- [ ] 什么是内存泄漏？如何避免？")
        lines.append("- [ ] 虚函数的作用？")
        lines.append("")

    # 薄弱环节验证
    lines.append("### 薄弱环节验证")
    for risk in analysis['risks'][:3]:
        # 从风险点生成验证问题
        if 'C++' in risk:
            lines.append("- [ ] C++中智能指针有哪些类型？各有什么特点？")
        elif 'Unity' in risk and 'C#' in risk:
            lines.append("- [ ] 请写一个简单的Unity脚本示例")
        elif '架构' in risk or '设计模式' in risk:
            lines.append("- [ ] 项目中使用了哪些设计模式？单例模式的优缺点？")
        elif '网络' in risk:
            lines.append("- [ ] TCP和UDP的区别？游戏中如何选择？")
        else:
            lines.append(f"- [ ] 请详细说明：{risk.replace('需验证', '').replace('需确认', '')}")
    lines.append("")

    # 通用问题
    lines.append("### 通用必问题")
    lines.append("- [ ] 解释A*寻路算法的原理")
    lines.append("- [ ] 如何实现一个对象池？有什么好处？")
    lines.append("")

    # 阶段4: 非技术素质
    lines.append("## 阶段4: 非技术素质 (2分钟)")
    lines.append("- [ ] 项目与他人合作有没有遇到过矛盾？如何处理？")
    lines.append("- [ ] 合理安排需求的情况下，没做完的需求会如何处理？")
    lines.append("- [ ] 工作过程中遇到不懂的问题会如何解决？")
    lines.append("")

    # 阶段5: 候选人提问
    lines.append("## 阶段5: 候选人提问 (3分钟)")
    lines.append("- [ ] 给候选人提问机会")
    lines.append("- **候选人问题**: ___")
    lines.append("")

    # 评分记录表
    lines.append("## 评分记录表")
    lines.append("")
    lines.append("| 维度 | 权重 | 得分 | 备注 |")
    lines.append("|------|------|------|------|")
    lines.append("| 技术能力 | 35% | ___ | Unity/C#/架构 |")
    lines.append("| 项目经验 | 25% | ___ | 项目深度/复杂度 |")
    lines.append("| 算法基础 | 15% | ___ | 数据结构/算法 |")
    lines.append("| 团队协作 | 10% | ___ | 沟通/协作意识 |")
    lines.append("| 发展潜力 | 10% | ___ | 学习能力/视野 |")
    lines.append("| 文化匹配 | 5% | ___ | 价值观/态度 |")
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
