---
name: git-weekly-report
description: 自动生成Git仓库的周报，按提交人分类总结工作内容。使用场景：在仓库目录下运行，获取本周（或指定时间段）所有提交人的提交记录，生成包含提交统计、代码变更、AI智能总结的Markdown格式周报。适用于团队协作、项目汇报、代码审查等场景。
---

# Git 周报助手

自动生成Git仓库的周报，按提交人分类总结工作内容。

## 功能概述

- 自动计算本周时间范围（周一到周日），支持自定义时间段
- 统计所有提交人的提交记录，按人分组
- 自动分类提交类型（feat/fix/docs/refactor等）
- 统计代码变更量（新增/删除行数、修改文件数）
- 生成Markdown格式的周报文档

## 使用方法

### 基本用法

在Git仓库目录下运行技能：

```
/weekly-report
```

这将自动生成本周（周一到周日）的周报。

### 自定义时间范围

```
/weekly-report --since 2024-01-01 --until 2024-01-07
```

### 指定输出文件

```
/weekly-report --output my-report.md
```

## 工作流程

1. **收集提交数据**：运行 `scripts/collect_commits.py` 收集指定时间范围内的Git提交记录
2. **生成Markdown报告**：运行 `scripts/generate_report.py` 将JSON数据转换为格式化的Markdown周报
3. **输出结果**：生成包含总体统计、个人工作摘要、提交详情的完整周报

## 脚本说明

### collect_commits.py

收集Git提交数据并输出JSON格式。

**参数：**
- `--since`: 开始日期（YYYY-MM-DD，可选，默认本周一）
- `--until`: 结束日期（YYYY-MM-DD，可选，默认本周日）
- `--output`: 输出JSON文件路径（默认: commits.json）

**示例：**
```bash
python scripts/collect_commits.py --since 2024-01-01 --until 2024-01-07 --output commits.json
```

**输出JSON格式：**
```json
{
  "period": {"since": "2024-01-01", "until": "2024-01-07"},
  "authors": {
    "张三": {
      "commits": [...],
      "stats": {"total_commits": 5, "files_changed": 10, "insertions": 100, "deletions": 20},
      "commit_types": {"feat": 2, "fix": 1, "docs": 1, "refactor": 1}
    }
  },
  "overall_stats": {...}
}
```

### generate_report.py

将JSON数据转换为Markdown格式周报。

**参数：**
- `--input`: 输入JSON文件路径（默认: commits.json）
- `--output`: 输出Markdown文件路径（默认: weekly-report.md）

**示例：**
```bash
python scripts/generate_report.py --input commits.json --output weekly-report.md
```

**输出Markdown结构：**
- 总体统计（总提交数、活跃贡献者、代码变更量）
- 团队工作摘要
- 每个提交人的详细报告：
  - 工作概览（自动总结）
  - 提交统计
  - 提交类型分布
  - 提交详情表格

## 支持的提交类型

脚本会自动识别以下类型的提交：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 问题修复 |
| docs | 文档更新 |
| refactor | 代码重构 |
| test | 测试相关 |
| chore | 杂项 |
| style | 代码样式 |
| perf | 性能优化 |
| build | 构建相关 |
| ci | CI/CD |
| revert | 回滚 |
| other | 其他 |

## 使用建议

1. **定期生成**：建议每周一早上生成本周周报，用于周会汇报
2. **项目里程碑**：在重要节点生成周报，记录项目进展
3. **代码审查**：通过周报了解团队成员的工作重点和代码量
