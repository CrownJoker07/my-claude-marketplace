#!/usr/bin/env python3
"""
面试评估报告生成脚本

使用方法:
    # 交互模式（推荐）
    python3 generate_report.py

    # 快速模式
    python3 generate_report.py --name "候选人姓名" --position "岗位名称" --score 82

    # 完整参数模式
    python3 generate_report.py \
        --name "张三" \
        --position "Unity开发实习生" \
        --interviewer "李四" \
        --technical 85 \
        --project 80 \
        --algorithm 75 \
        --teamwork 80 \
        --potential 85 \
        --culture 80 \
        --highlights "技术扎实" "学习能力强" \
        --risks "经验较少" \
        --recommendation "建议录用" \
        --output-dir "./reports"
"""

import argparse
import os
import sys
from datetime import datetime


def get_level(total_score):
    """根据总分确定推荐等级"""
    if total_score >= 85:
        return "A级（强烈推荐）"
    elif total_score >= 70:
        return "B级（推荐）"
    elif total_score >= 60:
        return "C级（谨慎考虑）"
    else:
        return "D级（不推荐）"


def generate_project_questions(project_name, role, tech_stack):
    """
    根据项目信息生成针对性的面试问题
    """
    questions = []

    # 项目概述问题
    questions.append(f"**项目概述**：《{project_name}》")
    questions.append(f"- 你在项目中担任{role}，请介绍一下项目整体架构？")
    questions.append(f"- 团队规模？开发周期？你的具体职责？")
    questions.append("")

    # 根据技术栈生成问题
    if "Wwise" in tech_stack:
        questions.append("**音频系统**：")
        questions.append("- Wwise与Unity音频系统的核心区别？")
        questions.append("- 如何在代码中管理音频事件和状态？")
        questions.append("")

    if "战斗" in tech_stack or "技能" in tech_stack:
        questions.append("**战斗系统设计**：")
        questions.append("- 请描述技能系统的架构设计")
        questions.append("- 如何处理技能之间的打断、连携、Buff/Debuff关系？")
        questions.append("- 伤害计算是如何实现的？")
        questions.append("")

    if "AI" in tech_stack or "行为树" in tech_stack:
        questions.append("**AI系统设计**：")
        questions.append("- 行为树与状态机的适用场景对比？")
        questions.append("- A*寻路在项目中是如何实现的？如何优化性能？")
        questions.append("")

    if "地形" in tech_stack or "地图" in tech_stack:
        questions.append("**地形系统**：")
        questions.append("- 地形编辑工具是如何设计的？")
        questions.append("- 大地形是如何做性能优化的（分块、LOD等）？")
        questions.append("")

    if "特效" in tech_stack or "粒子" in tech_stack:
        questions.append("**特效系统**：")
        questions.append("- Unity原生粒子系统有哪些限制？如何优化？")
        questions.append("- 特效资源的管理和加载策略？")
        questions.append("")

    # 通用深度问题
    questions.append("**技术深度追问**：")
    questions.append("- 项目中遇到的最大技术挑战是什么？如何解决的？")
    questions.append("- 如果重新设计这个项目，你会做哪些改进？")
    questions.append("- 代码贡献率80%+是如何统计的？使用什么版本控制策略？")
    questions.append("")

    return "\n".join(questions)


def generate_capability_questions(tech_skills, weak_areas):
    """
    根据候选人能力生成有针对性的基础问题
    """
    questions = []

    # 根据技术强项提问
    if "UniTask" in tech_skills:
        questions.append("**异步编程**：")
        questions.append("- UniTask和Unity传统Coroutine的区别？")
        questions.append("- async/await的原理是什么？在什么场景下使用？")
        questions.append("")

    if "ECS" in tech_skills or "DOTS" in tech_skills:
        questions.append("**ECS架构**：")
        questions.append("- ECS相比传统OOP的优势？")
        questions.append("- 什么场景适合使用ECS？")
        questions.append("")

    if "Shader" in tech_skills:
        questions.append("**图形学基础**：")
        questions.append("- MVP矩阵分别代表什么？")
        questions.append("- 顶点着色器和片元着色器分别做什么？")
        questions.append("")

    # 针对薄弱环节的补充问题
    if weak_areas:
        questions.append("**薄弱环节补充考察**：")
        for area in weak_areas:
            if "C++" in area:
                questions.append("- C++中指针和引用的区别？")
                questions.append("- 什么是内存泄漏？如何避免？")
            elif "分布式" in area:
                questions.append("- 请具体说明简历中提到的'分布式系统'是如何实现的？")
            elif "Shader" in area:
                questions.append("- 了解ShaderLab的基本结构吗？")
            questions.append("")

    # 通用必问题
    questions.append("**必问基础问题**：")
    questions.append("- C#中值类型和引用类型的区别？什么是装箱拆箱？")
    questions.append("- 什么是GC？如何避免GC Alloc？")
    questions.append("- 项目中使用了哪些设计模式？单例模式的优缺点？")
    questions.append("- 解释A*寻路算法的原理")
    questions.append("- 如何实现一个对象池？有什么好处？")

    return "\n".join(questions)


def generate_report(name, position, interviewer, scores, highlights, risks, recommendation,
                    project_name=None, project_role=None, tech_stack=None, weak_areas=None,
                    output_dir=None):
    """
    生成结构化的面试评估报告

    Args:
        name: 候选人姓名
        position: 岗位名称
        interviewer: 面试官姓名
        scores: 字典，包含各维度得分
        highlights: 优势亮点列表
        risks: 风险点列表
        recommendation: 推荐意见
        project_name: 项目名称
        project_role: 项目角色
        tech_stack: 技术栈列表
        weak_areas: 薄弱环节列表
        output_dir: 输出目录（可选）

    Returns:
        生成的报告文件路径
    """

    # 计算总分（按权重）
    weights = {
        'technical': 0.35,
        'project': 0.25,
        'algorithm': 0.15,
        'teamwork': 0.10,
        'potential': 0.10,
        'culture': 0.05
    }

    total_score = sum(scores.get(k, 0) * weights.get(k, 0) for k in weights.keys())
    level = get_level(total_score)

    # 生成针对性问题
    project_questions = ""
    if project_name and tech_stack:
        project_questions = generate_project_questions(project_name, project_role or "主程序", tech_stack)

    capability_questions = generate_capability_questions(tech_stack or [], weak_areas or [])

    # 构建报告内容
    report_lines = []
    report_lines.append(f"# 面试评估报告 - {name}")
    report_lines.append("")
    report_lines.append("## 基本信息")
    report_lines.append("")
    report_lines.append("| 项目 | 内容 |")
    report_lines.append("|------|------|")
    report_lines.append(f"| 候选人 | {name} |")
    report_lines.append(f"| 岗位 | {position} |")
    report_lines.append(f"| 面试官 | {interviewer} |")
    report_lines.append(f"| 面试日期 | {datetime.now().strftime('%Y-%m-%d')} |")
    report_lines.append(f"| 报告生成时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    report_lines.append("")

    # 评分汇总
    report_lines.append("## 评分汇总")
    report_lines.append("")
    report_lines.append(f"### 总体评分：{total_score:.1f}/100")
    report_lines.append("")
    report_lines.append(f"### 推荐等级：{level}")
    report_lines.append("")
    report_lines.append("### 分项评分")
    report_lines.append("")
    report_lines.append("| 评估维度 | 权重 | 得分 | 说明 |")
    report_lines.append("|---------|------|------|------|")
    report_lines.append(f"| 技术能力 | 35% | {scores.get('technical', 0)} | Unity/C#/架构设计 |")
    report_lines.append(f"| 项目经验 | 25% | {scores.get('project', 0)} | 项目深度/复杂度/贡献 |")
    report_lines.append(f"| 算法基础 | 15% | {scores.get('algorithm', 0)} | 数据结构/算法/设计模式 |")
    report_lines.append(f"| 团队协作 | 10% | {scores.get('teamwork', 0)} | 沟通/协作意识 |")
    report_lines.append(f"| 发展潜力 | 10% | {scores.get('potential', 0)} | 学习能力/技术视野 |")
    report_lines.append(f"| 文化匹配 | 5% | {scores.get('culture', 0)} | 价值观/工作态度 |")
    report_lines.append("")

    # 优势亮点
    report_lines.append("## 优势亮点")
    report_lines.append("")
    for i, h in enumerate(highlights, 1):
        report_lines.append(f"{i}. {h}")
    report_lines.append("")

    # 风险点
    report_lines.append("## 风险点/需关注")
    report_lines.append("")
    for i, r in enumerate(risks, 1):
        report_lines.append(f"{i}. {r}")
    report_lines.append("")

    # 推荐意见
    report_lines.append("## 推荐意见")
    report_lines.append("")
    report_lines.append(recommendation)
    report_lines.append("")

    # 分割线
    report_lines.append("---")
    report_lines.append("")

    # 面试过程记录
    report_lines.append("## 面试过程记录")
    report_lines.append("")
    report_lines.append("### 1. 自我介绍（2分钟）")
    report_lines.append("- [ ] 为什么来面试该岗位？")
    report_lines.append("- **回答**：")
    report_lines.append("- **评价**：")
    report_lines.append("")

    # 项目经历 - 使用针对性问题
    report_lines.append("### 2. 项目经历深度挖掘（20分钟）")
    report_lines.append("")
    if project_questions:
        report_lines.append(project_questions)
    else:
        report_lines.append("- **项目**：《》")
        report_lines.append("- **技术问题1**：")
        report_lines.append("- **回答**：")
        report_lines.append("- **评价**：")
    report_lines.append("")

    # 基础能力 - 使用针对性问题
    report_lines.append("### 3. 基础能力考察（5分钟）")
    report_lines.append("")
    if capability_questions:
        report_lines.append(capability_questions)
    else:
        report_lines.append("- **编程语言**：")
        report_lines.append("- **数据结构**：")
        report_lines.append("- **算法**：")
    report_lines.append("- **回答摘要**：")
    report_lines.append("- **评价**：")
    report_lines.append("")

    report_lines.append("### 4. 非技术素质考察（2分钟）")
    report_lines.append("- [ ] 项目合作矛盾处理：")
    report_lines.append("- **回答**：")
    report_lines.append("- **评价**：")
    report_lines.append("- [ ] 未完成需求处理：")
    report_lines.append("- **回答**：")
    report_lines.append("- **评价**：")
    report_lines.append("- [ ] 遇到难题如何解决：")
    report_lines.append("- **回答**：")
    report_lines.append("- **评价**：")
    report_lines.append("")

    report_lines.append("### 5. 候选人提问（3分钟）")
    report_lines.append("- **问题**：")
    report_lines.append("- **评价**：")
    report_lines.append("")

    # 后续行动
    report_lines.append("## 后续行动")
    report_lines.append("")
    report_lines.append("- [ ] 进入下一轮面试")
    report_lines.append("- [ ] 要求提供代码作品")
    report_lines.append("- [ ] 背景调查")
    report_lines.append("- [ ] 发送Offer")
    report_lines.append("- [ ] 其他：")
    report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append(f"*报告由 resume-interview-evaluator skill 生成*")
    report_lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    report_content = "\n".join(report_lines)

    # 保存文件
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, f"interview_report_{name}_{datetime.now().strftime('%Y%m%d')}.md")
    else:
        filename = f"interview_report_{name}_{datetime.now().strftime('%Y%m%d')}.md"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)

    return filename, report_content


def interactive_mode():
    """交互式生成报告"""
    print("=" * 60)
    print("  游戏开发工程师面试评估报告生成器")
    print("=" * 60)
    print()

    # 基本信息
    name = input("候选人姓名: ").strip()
    if not name:
        print("❌ 候选人姓名不能为空")
        sys.exit(1)

    position = input("岗位名称: ").strip() or "Unity开发工程师"
    interviewer = input("面试官姓名: ").strip() or "面试官"

    # 项目信息
    print("\n" + "-" * 40)
    print("项目信息：")
    print("-" * 40)
    project_name = input("项目名称: ").strip()
    project_role = input("担任角色: ").strip() or "主程序"
    tech_input = input("技术栈（用逗号分隔）: ").strip()
    tech_stack = [t.strip() for t in tech_input.split(",") if t.strip()]

    weak_input = input("薄弱环节/需验证点（用逗号分隔）: ").strip()
    weak_areas = [w.strip() for w in weak_input.split(",") if w.strip()]

    output_dir = input("输出目录 (直接回车使用当前目录): ").strip() or None

    print("\n" + "-" * 40)
    print("请为各维度评分 (0-100):")
    print("-" * 40)

    scores = {}
    try:
        scores['technical'] = int(input("技术能力 (Unity/C#/架构) [0-100]: ") or 70)
        scores['project'] = int(input("项目经验 [0-100]: ") or 70)
        scores['algorithm'] = int(input("算法基础 [0-100]: ") or 70)
        scores['teamwork'] = int(input("团队协作 [0-100]: ") or 70)
        scores['potential'] = int(input("发展潜力 [0-100]: ") or 70)
        scores['culture'] = int(input("文化匹配 [0-100]: ") or 70)
    except ValueError:
        print("❌ 请输入有效的数字")
        sys.exit(1)

    print("\n" + "-" * 40)
    print("优势亮点 (输入空行结束):")
    print("-" * 40)
    highlights = []
    while True:
        h = input(f"  亮点 {len(highlights)+1}: ").strip()
        if not h:
            break
        highlights.append(h)
    if not highlights:
        highlights = ["技术基础扎实"]

    print("\n" + "-" * 40)
    print("风险点/需关注 (输入空行结束):")
    print("-" * 40)
    risks = []
    while True:
        r = input(f"  风险点 {len(risks)+1}: ").strip()
        if not r:
            break
        risks.append(r)
    if not risks:
        risks = ["需进一步验证"]

    print("\n" + "-" * 40)
    print("推荐意见：")
    print("-" * 40)
    print("示例: 建议录用为Unity实习生，有转正机会，可长期培养")
    recommendation = input().strip() or "建议进入下一轮面试"

    # 生成报告
    print("\n" + "=" * 60)
    print("正在生成报告...")
    print("=" * 60)

    filename, report_content = generate_report(
        name=name,
        position=position,
        interviewer=interviewer,
        scores=scores,
        highlights=highlights,
        risks=risks,
        recommendation=recommendation,
        project_name=project_name,
        project_role=project_role,
        tech_stack=tech_stack,
        weak_areas=weak_areas,
        output_dir=output_dir
    )

    print(f"\n✅ 报告已生成: {filename}")
    print(f"\n📊 推荐等级: {get_level(sum(scores[k] * weights[k] for k in scores.keys()))}")
    print("\n" + "=" * 60)
    print("报告预览:")
    print("=" * 60)
    print(report_content[:1500] + "..." if len(report_content) > 1500 else report_content)

    return filename


def main():
    parser = argparse.ArgumentParser(
        description='游戏开发工程师面试评估报告生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互模式（推荐）
  python3 generate_report.py

  # 快速模式
  python3 generate_report.py --name "张三" --position "Unity实习生" --score 80

  # 完整模式
  python3 generate_report.py \\
    --name "张三" \\
    --position "Unity开发实习生" \\
    --interviewer "李四" \\
    --technical 85 --project 80 --algorithm 75 \\
    --teamwork 80 --potential 85 --culture 80 \\
    --highlights "技术扎实" "学习能力强" \\
    --risks "经验较少" \\
    --recommendation "建议录用，有转正机会" \\
    --output-dir "./reports"
        """
    )

    parser.add_argument('--name', help='候选人姓名')
    parser.add_argument('--position', help='岗位名称')
    parser.add_argument('--interviewer', default='面试官', help='面试官姓名')
    parser.add_argument('--score', type=int, help='快速模式：所有维度使用相同分数')

    # 各维度分数
    parser.add_argument('--technical', type=int, help='技术能力得分 (0-100)')
    parser.add_argument('--project', type=int, help='项目经验得分 (0-100)')
    parser.add_argument('--algorithm', type=int, help='算法基础得分 (0-100)')
    parser.add_argument('--teamwork', type=int, help='团队协作得分 (0-100)')
    parser.add_argument('--potential', type=int, help='发展潜力得分 (0-100)')
    parser.add_argument('--culture', type=int, help='文化匹配得分 (0-100)')

    parser.add_argument('--highlights', nargs='+', help='优势亮点列表')
    parser.add_argument('--risks', nargs='+', help='风险点列表')
    parser.add_argument('--recommendation', help='推荐意见')
    parser.add_argument('--output-dir', help='输出目录')

    # 项目信息参数
    parser.add_argument('--project-name', help='项目名称')
    parser.add_argument('--project-role', help='项目角色')
    parser.add_argument('--tech-stack', nargs='+', help='技术栈列表')
    parser.add_argument('--weak-areas', nargs='+', help='薄弱环节列表')

    args = parser.parse_args()

    # 如果没有提供姓名，进入交互模式
    if not args.name:
        interactive_mode()
        return

    # 快速模式：使用相同分数
    if args.score:
        scores = {
            'technical': args.score,
            'project': args.score,
            'algorithm': args.score,
            'teamwork': args.score,
            'potential': args.score,
            'culture': args.score
        }
    else:
        scores = {
            'technical': args.technical or 70,
            'project': args.project or 70,
            'algorithm': args.algorithm or 70,
            'teamwork': args.teamwork or 70,
            'potential': args.potential or 70,
            'culture': args.culture or 70
        }

    highlights = args.highlights or ["技术能力符合岗位要求"]
    risks = args.risks or ["需进一步验证"]
    recommendation = args.recommendation or "建议进入下一轮面试"

    filename, report_content = generate_report(
        name=args.name,
        position=args.position or "Unity开发工程师",
        interviewer=args.interviewer,
        scores=scores,
        highlights=highlights,
        risks=risks,
        recommendation=recommendation,
        project_name=args.project_name,
        project_role=args.project_role,
        tech_stack=args.tech_stack,
        weak_areas=args.weak_areas,
        output_dir=args.output_dir
    )

    print(f"✅ 报告已生成: {filename}")


if __name__ == "__main__":
    # 权重定义供interactive_mode使用
    weights = {
        'technical': 0.35,
        'project': 0.25,
        'algorithm': 0.15,
        'teamwork': 0.10,
        'potential': 0.10,
        'culture': 0.05
    }
    main()
