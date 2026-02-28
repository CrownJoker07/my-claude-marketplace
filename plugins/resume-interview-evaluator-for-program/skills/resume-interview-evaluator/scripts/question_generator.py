#!/usr/bin/env python3
"""
面试问题生成器模块

功能：
    1. 加载各维度面试题库
    2. 根据技能熟练度选择问题难度
    3. 随机选择指定数量的问题
    4. 生成针对性问题列表

使用方法:
    from question_generator import QuestionGenerator, SkillProficiency

    generator = QuestionGenerator()
    questions = generator.generate_for_candidate(skills, projects, analysis)
"""

import os
import re
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass


class SkillProficiency(Enum):
    """技能熟练度等级"""
    BEGINNER = "了解"      # 初级
    INTERMEDIATE = "熟练"  # 中级
    ADVANCED = "精通"      # 高级


@dataclass
class Question:
    """面试问题数据结构"""
    content: str
    difficulty: str
    dimension: str
    is_project_related: bool = False


class QuestionBank:
    """单个维度的题库"""

    def __init__(self, dimension: str, file_path: str):
        self.dimension = dimension
        self.file_path = file_path
        self.questions = {
            "初级": [],
            "中级": [],
            "高级": [],
            "项目深挖": []
        }
        self._loaded = False

    def load(self) -> bool:
        """加载题库文件"""
        if self._loaded:
            return True

        if not os.path.exists(self.file_path):
            return False

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析题库结构
            current_section = None
            current_question = ""

            for line in content.split('\n'):
                line = line.strip()

                # 检测章节标题
                if line.startswith('## 初级') or '了解' in line:
                    if current_question and current_section:
                        self._add_question(current_section, current_question)
                    current_section = "初级"
                    current_question = ""
                elif line.startswith('## 中级') or '熟练' in line:
                    if current_question and current_section:
                        self._add_question(current_section, current_question)
                    current_section = "中级"
                    current_question = ""
                elif line.startswith('## 高级') or '精通' in line:
                    if current_question and current_section:
                        self._add_question(current_section, current_question)
                    current_section = "高级"
                    current_question = ""
                elif line.startswith('## 项目深挖'):
                    if current_question and current_section:
                        self._add_question(current_section, current_question)
                    current_section = "项目深挖"
                    current_question = ""
                elif line.startswith('#') or not line:
                    # 跳过其他标题和空行
                    continue
                elif current_section and re.match(r'^\d+\.', line):
                    # 保存上一个问题
                    if current_question:
                        self._add_question(current_section, current_question)
                    # 开始新问题（去除序号）
                    current_question = re.sub(r'^\d+\.\s*', '', line)
                elif current_section and current_question:
                    # 继续当前问题
                    current_question += " " + line

            # 保存最后一个问题
            if current_question and current_section:
                self._add_question(current_section, current_question)

            self._loaded = True
            return True

        except Exception as e:
            print(f"加载题库 {self.dimension} 失败: {e}")
            return False

    def _add_question(self, section: str, content: str):
        """添加问题到对应章节"""
        content = content.strip()
        if len(content) < 10:  # 过滤太短的内容
            return

        is_project = section == "项目深挖"
        question = Question(
            content=content,
            difficulty=section,
            dimension=self.dimension,
            is_project_related=is_project
        )
        self.questions[section].append(question)

    def get_questions(self, difficulty: Optional[str] = None,
                     count: int = 0,
                     exclude_ids: Optional[Set[int]] = None) -> List[Question]:
        """
        获取问题列表

        Args:
            difficulty: 难度级别，None表示获取所有
            count: 获取数量，0表示获取全部
            exclude_ids: 要排除的问题索引集合
        """
        if not self._loaded:
            self.load()

        result = []
        exclude_ids = exclude_ids or set()

        if difficulty and difficulty in self.questions:
            # 获取指定难度
            available = [(i, q) for i, q in enumerate(self.questions[difficulty])
                        if i not in exclude_ids]
            if count > 0 and len(available) > count:
                selected = random.sample(available, count)
            else:
                selected = available
            result = [q for _, q in selected]
        else:
            # 获取所有难度
            for diff, questions in self.questions.items():
                if diff == "项目深挖":
                    continue
                available = [(i, q) for i, q in enumerate(questions)
                            if i not in exclude_ids]
                result.extend([q for _, q in available])

        if count > 0 and len(result) > count:
            result = random.sample(result, count)

        return result

    def get_by_proficiency(self, proficiency: SkillProficiency,
                          project_tech_stack: List[str] = None) -> List[Question]:
        """
        根据熟练度获取问题

        Args:
            proficiency: 技能熟练度
            project_tech_stack: 项目技术栈，用于选择项目深挖问题
        """
        if not self._loaded:
            self.load()

        result = []

        # 根据熟练度选择难度
        if proficiency == SkillProficiency.BEGINNER:
            # 初级：主要问初级问题，少量中级
            result.extend(self.get_questions("初级", 3))
            result.extend(self.get_questions("中级", 1))
        elif proficiency == SkillProficiency.INTERMEDIATE:
            # 中级：混合初中级，少量高级
            result.extend(self.get_questions("初级", 1))
            result.extend(self.get_questions("中级", 3))
            result.extend(self.get_questions("高级", 1))
        elif proficiency == SkillProficiency.ADVANCED:
            # 高级：主要问中高级，深挖项目
            result.extend(self.get_questions("中级", 1))
            result.extend(self.get_questions("高级", 3))
            result.extend(self.get_questions("项目深挖", 2))

        return result


class QuestionGenerator:
    """面试问题生成器"""

    # 技能到题库维度的映射
    SKILL_DIMENSION_MAP = {
        # 编程语言
        'C#': 'csharp',
        'C++': 'cpp',
        'Python': None,
        'Lua': None,
        'JavaScript': None,
        'TypeScript': None,
        'Java': None,
        'Go': None,

        # 游戏引擎
        'Unity': 'unity',
        'Unreal Engine': 'cpp',
        'Godot': None,
        'Cocos': None,

        # 专业技能映射
        'ECS': 'unity',
        'DOTS': 'unity',
        'Shader': 'graphics',
        'HLSL': 'graphics',
        'GLSL': 'graphics',
        'AI': 'ai',
        '行为树': 'ai',
        '状态机': 'ai',
        '寻路': 'ai',
        'Navigation': 'ai',
        'NavMesh': 'ai',
        'A*': 'datastructure',
        '网络': 'network',
        '网络同步': 'network',
        '帧同步': 'network',
        '状态同步': 'network',
        '热更新': 'optimization',
        'AssetBundle': 'unity',
        'Addressable': 'unity',
        'UI': 'ui',
        'UGUI': 'ui',
        'FairyGUI': 'ui',
        '物理': 'unity',
        'Physics': 'unity',
        '碰撞检测': 'unity',
        '性能优化': 'optimization',
        '内存优化': 'optimization',
        'Draw Call': 'optimization',
        'XLua': 'unity',
        'ToLua': 'unity',
        'SLua': 'unity',
        '设计模式': 'designpattern',
        '架构设计': 'designpattern',
        'MVC': 'designpattern',
        'MVP': 'designpattern',
        'MVVM': 'designpattern',
        '多线程': 'optimization',
        '异步编程': 'csharp',
        'UniTask': 'unity',
        'async/await': 'csharp',
        'Git': 'general',
        'SVN': 'general',
        '版本控制': 'general',
    }

    def __init__(self, questions_dir: Optional[str] = None):
        """
        初始化问题生成器

        Args:
            questions_dir: 题库目录路径，默认为脚本所在目录的questions子目录
        """
        if questions_dir is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            questions_dir = os.path.join(os.path.dirname(script_dir), 'questions')

        self.questions_dir = questions_dir
        self.banks: Dict[str, QuestionBank] = {}
        self._load_all_banks()

    def _load_all_banks(self):
        """加载所有题库"""
        bank_files = {
            'unity': 'unity.md',
            'csharp': 'csharp.md',
            'cpp': 'cpp.md',
            'datastructure': 'datastructure.md',
            'designpattern': 'designpattern.md',
            'network': 'network.md',
            'graphics': 'graphics.md',
            'optimization': 'optimization.md',
            'ai': 'ai.md',
            'ui': 'ui.md',
            'general': 'general.md',
        }

        for dimension, filename in bank_files.items():
            file_path = os.path.join(self.questions_dir, filename)
            bank = QuestionBank(dimension, file_path)
            if bank.load():
                self.banks[dimension] = bank

    def _map_skill_to_dimension(self, skill: str) -> Optional[str]:
        """将技能映射到题库维度"""
        # 直接匹配
        if skill in self.SKILL_DIMENSION_MAP:
            return self.SKILL_DIMENSION_MAP[skill]

        # 模糊匹配
        for key, dimension in self.SKILL_DIMENSION_MAP.items():
            if key.lower() in skill.lower() or skill.lower() in key.lower():
                return dimension

        return None

    def _determine_proficiency(self, skill: str, skill_data: Dict,
                               project_count: int = 0) -> SkillProficiency:
        """
        确定技能熟练度

        基于：
        1. 明确标注的熟练度
        2. 项目使用经验数量
        3. 技能深度描述
        """
        # 检查是否有明确标注
        if 'proficiency' in skill_data:
            prof = skill_data['proficiency']
            if isinstance(prof, str):
                if prof in ['精通', '专家']:
                    return SkillProficiency.ADVANCED
                elif prof in ['熟练', '掌握']:
                    return SkillProficiency.INTERMEDIATE
                elif prof in ['了解', '入门']:
                    return SkillProficiency.BEGINNER

        # 基于项目数量判断
        if project_count >= 3:
            return SkillProficiency.ADVANCED
        elif project_count >= 1:
            return SkillProficiency.INTERMEDIATE

        # 默认中级
        return SkillProficiency.INTERMEDIATE

    def generate_for_candidate(self, skills: Dict, projects: List[Dict],
                              analysis: Dict) -> Dict[str, List[Question]]:
        """
        为候选人生成面试问题

        Args:
            skills: 技能信息 {'languages': [], 'engines': [], 'professional': [], 'tools': []}
            projects: 项目经历列表
            analysis: 分析报告（包含风险点等）

        Returns:
            按维度分类的问题字典
        """
        result = {
            'skills': {},      # 技能维度问题
            'projects': [],    # 项目深挖问题
            'weakness': [],    # 薄弱环节问题
            'general': [],     # 通用问题
        }

        # 统计技能在项目中的使用情况
        skill_project_count = self._count_skill_in_projects(skills, projects)

        # 为每个技能生成问题
        processed_dimensions = set()

        # 处理编程语言
        for lang in skills.get('languages', []):
            dimension = self._map_skill_to_dimension(lang)
            if dimension and dimension not in processed_dimensions:
                prof = self._determine_proficiency(
                    lang, {},
                    skill_project_count.get(lang, 0)
                )
                questions = self._get_questions_for_skill(dimension, prof, projects)
                if questions:
                    result['skills'][lang] = {
                        'proficiency': prof.value,
                        'project_count': skill_project_count.get(lang, 0),
                        'questions': questions
                    }
                    processed_dimensions.add(dimension)

        # 处理游戏引擎
        for engine in skills.get('engines', []):
            dimension = self._map_skill_to_dimension(engine)
            if dimension and dimension not in processed_dimensions:
                prof = self._determine_proficiency(
                    engine, {},
                    skill_project_count.get(engine, 0)
                )
                questions = self._get_questions_for_skill(dimension, prof, projects)
                if questions:
                    result['skills'][engine] = {
                        'proficiency': prof.value,
                        'project_count': skill_project_count.get(engine, 0),
                        'questions': questions
                    }
                    processed_dimensions.add(dimension)

        # 处理专业技能
        for prof_skill in skills.get('professional', []):
            dimension = self._map_skill_to_dimension(prof_skill)
            if dimension and dimension not in processed_dimensions:
                prof = self._determine_proficiency(
                    prof_skill, {},
                    skill_project_count.get(prof_skill, 0)
                )
                questions = self._get_questions_for_skill(dimension, prof, projects)
                if questions:
                    result['skills'][prof_skill] = {
                        'proficiency': prof.value,
                        'project_count': skill_project_count.get(prof_skill, 0),
                        'questions': questions
                    }
                    processed_dimensions.add(dimension)

        # 生成项目深挖问题
        result['projects'] = self._generate_project_questions(projects)

        # 生成薄弱环节验证问题
        result['weakness'] = self._generate_weakness_questions(analysis.get('risks', []))

        # 添加通用问题
        if 'general' in self.banks:
            result['general'] = self.banks['general'].get_questions(count=5)

        return result

    def _count_skill_in_projects(self, skills: Dict, projects: List[Dict]) -> Dict[str, int]:
        """统计技能在项目中的使用次数"""
        count = {}

        all_skills = (
            skills.get('languages', []) +
            skills.get('engines', []) +
            skills.get('professional', [])
        )

        for skill in all_skills:
            count[skill] = 0
            for project in projects:
                tech_stack = project.get('tech_stack', [])
                description = project.get('description', '')
                if skill in tech_stack or skill in description:
                    count[skill] += 1

        return count

    def _get_questions_for_skill(self, dimension: str,
                                  proficiency: SkillProficiency,
                                  projects: List[Dict]) -> List[Question]:
        """为特定技能获取问题"""
        if dimension not in self.banks:
            return []

        bank = self.banks[dimension]

        # 获取该维度相关的项目技术栈
        project_techs = []
        for project in projects:
            tech_stack = project.get('tech_stack', [])
            project_techs.extend(tech_stack)

        return bank.get_by_proficiency(proficiency, project_techs)

    def _generate_project_questions(self, projects: List[Dict]) -> List[Dict]:
        """生成项目深挖问题"""
        project_questions = []

        for project in projects[:3]:  # 最多3个项目
            questions = []

            # 基于技术栈的问题
            tech_stack = project.get('tech_stack', [])
            for tech in tech_stack[:3]:
                dimension = self._map_skill_to_dimension(tech)
                if dimension and dimension in self.banks:
                    bank = self.banks[dimension]
                    qs = bank.get_questions("项目深挖", 1)
                    questions.extend(qs)

            # 通用项目问题
            if 'general' in self.banks:
                qs = self.banks['general'].get_questions(count=2)
                questions.extend(qs)

            project_questions.append({
                'name': project.get('name', '未命名项目'),
                'tech_stack': tech_stack,
                'role': project.get('role', ''),
                'questions': questions
            })

        return project_questions

    def _generate_weakness_questions(self, risks: List[str]) -> List[Question]:
        """基于风险点生成验证问题"""
        weakness_questions = []

        for risk in risks[:3]:
            # 根据风险类型匹配题库
            if 'C++' in risk and 'cpp' in self.banks:
                qs = self.banks['cpp'].get_questions("中级", 1)
                weakness_questions.extend(qs)
            elif 'Unity' in risk and 'unity' in self.banks:
                qs = self.banks['unity'].get_questions("中级", 1)
                weakness_questions.extend(qs)
            elif '设计模式' in risk or '架构' in risk:
                if 'designpattern' in self.banks:
                    qs = self.banks['designpattern'].get_questions("中级", 1)
                    weakness_questions.extend(qs)
            elif '网络' in risk and 'network' in self.banks:
                qs = self.banks['network'].get_questions("中级", 1)
                weakness_questions.extend(qs)
            elif '算法' in risk or '数据结构' in risk:
                if 'datastructure' in self.banks:
                    qs = self.banks['datastructure'].get_questions("中级", 1)
                    weakness_questions.extend(qs)
            elif '渲染' in risk or 'Shader' in risk:
                if 'graphics' in self.banks:
                    qs = self.banks['graphics'].get_questions("中级", 1)
                    weakness_questions.extend(qs)

        return weakness_questions

    def format_questions_markdown(self, question_data: Dict[str, any]) -> str:
        """将问题数据格式化为Markdown"""
        lines = []

        # 技能维度问题
        if question_data.get('skills'):
            lines.append("## 技能维度考察")
            lines.append("")

            for skill_name, skill_info in question_data['skills'].items():
                prof = skill_info.get('proficiency', '熟练')
                proj_count = skill_info.get('project_count', 0)
                questions = skill_info.get('questions', [])

                if not questions:
                    continue

                lines.append(f"### {skill_name} ({prof} - {proj_count}个项目)")
                lines.append("")

                # 按难度分组
                by_difficulty = {"初级": [], "中级": [], "高级": [], "项目深挖": []}
                for q in questions:
                    if q.difficulty in by_difficulty:
                        by_difficulty[q.difficulty].append(q)

                for diff, qs in by_difficulty.items():
                    if not qs:
                        continue

                    if diff == "项目深挖":
                        lines.append(f"**项目相关问题** (选1-2个):")
                    else:
                        lines.append(f"**{diff}问题** (选{min(len(qs), 2)}个):")

                    for i, q in enumerate(qs[:3], 1):  # 每类最多显示3个
                        lines.append(f"- [ ] {q.content}")
                    lines.append("")

        # 项目深挖
        if question_data.get('projects'):
            lines.append("## 项目深挖")
            lines.append("")

            for project in question_data['projects']:
                proj_name = project.get('name', '未命名项目')
                tech_stack = project.get('tech_stack', [])
                role = project.get('role', '')
                questions = project.get('questions', [])

                lines.append(f"### {proj_name}")
                if tech_stack:
                    lines.append(f"**技术栈**: {', '.join(tech_stack)}")
                if role:
                    lines.append(f"**角色**: {role}")
                lines.append("")

                for q in questions[:4]:  # 每个项目最多4个问题
                    lines.append(f"- [ ] {q.content}")
                lines.append("")

        # 薄弱环节验证
        if question_data.get('weakness'):
            lines.append("## 薄弱环节验证")
            lines.append("")

            for q in question_data['weakness'][:3]:
                lines.append(f"- [ ] [{q.dimension}] {q.content}")
            lines.append("")

        # 通用问题
        if question_data.get('general'):
            lines.append("## 通用问题")
            lines.append("")

            for q in question_data['general'][:3]:
                lines.append(f"- [ ] {q.content}")
            lines.append("")

        return "\n".join(lines)


# 便捷函数
def generate_question_list(skills: Dict, projects: List[Dict],
                          analysis: Dict) -> str:
    """
    快速生成面试问题清单（Markdown格式）

    Args:
        skills: 技能信息
        projects: 项目经历
        analysis: 分析报告

    Returns:
        Markdown格式的问题清单
    """
    generator = QuestionGenerator()
    question_data = generator.generate_for_candidate(skills, projects, analysis)
    return generator.format_questions_markdown(question_data)
