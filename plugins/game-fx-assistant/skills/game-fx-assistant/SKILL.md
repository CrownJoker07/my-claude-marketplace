---
name: game-fx-assistant
description: Unity游戏动效设计助手。使用动效思维分析代码，为游戏UI、角色、特效推荐并生成DOTween动效代码。支持单个动效、连续动画、错落动画(Stagger)。Use when working with Unity code that needs animation effects, UI transitions, character movements, or any visual feedback improvements using DOTween.
---

# 游戏动效助手 (Game FX Assistant)

帮助Unity开发者使用DOTween为游戏代码添加专业动效。

## 动效思维核心

### 4大动效场景

分析代码时，识别当前最适合的动效场景：

| 场景 | 用途 | 常见代码信号 |
|------|------|-------------|
| **Entrance (入场)** | 元素首次出现 | `SetActive(true)`, `Instantiate()`, `Show()`, `Enable()` |
| **Emphasis (强调)** | 吸引注意力 | `Highlight()`, `Select()`, 重要数值变化 |
| **Exit (退场)** | 元素消失 | `SetActive(false)`, `Destroy()`, `Hide()`, `Disable()` |
| **Feedback (反馈)** | 用户操作响应 | `OnClick`, `OnPointerEnter`, `TakeDamage`, `CollectItem` |

### 代码分析维度

分析代码时考虑以下维度：

1. **元素类型**：UI组件(Button/Text/Image)、游戏角色、道具、特效
2. **用户行为**：点击、悬浮、拖拽、滑动、等待
3. **情感目标**：喜悦、紧张、成就、警示
4. **时机节奏**：即时响应(<0.2s)、标准反馈(0.3-0.5s)、戏剧效果(>0.6s)

## 工作流程

### 步骤1: 分析代码上下文 → 识别动效机会点

阅读代码，标记以下动效机会点：
- UI显示/隐藏逻辑
- 按钮交互回调
- 数值变化(血量、分数、资源)
- 物品收集/使用
- 状态切换

### 步骤2: 选择动效场景 → 确定动效类型

根据场景选择参考文件：
- **入场动效** → 查阅 [animation-patterns.md](references/animation-patterns.md) 的 Entrance 章节
- **强调动效** → 查阅 [animation-patterns.md](references/animation-patterns.md) 的 Emphasis 章节
- **退场动效** → 查阅 [animation-patterns.md](references/animation-patterns.md) 的 Exit 章节
- **反馈动效** → 查阅 [animation-patterns.md](references/animation-patterns.md) 的 Feedback 章节
- **列表/网格动效** → 查阅 [stagger-animation-guide.md](references/stagger-animation-guide.md)

### 步骤3: 生成DOTween代码

**输出策略：**

- **简单情况** (< 3个动效)：提供完整修改后的代码
- **复杂情况** (≥ 3个动效 或 错落动画)：提供代码片段 + 插入位置说明

## DOTween基础速查

### 链式调用语法

```csharp
// 基本链式调用
transform.DOMove(Vector3.right * 2, 0.5f)
    .SetEase(Ease.OutBack)
    .SetDelay(0.1f)
    .OnComplete(() => Debug.Log("Done"));

// 同时执行多个动画
Sequence seq = DOTween.Sequence();
seq.Append(transform.DOMoveX(10, 0.5f));
seq.Join(transform.DOScale(1.5f, 0.5f));  // 与上一动画同时执行
```

### Sequence使用要点

```csharp
Sequence seq = DOTween.Sequence();
seq.Append(tween1);      // 顺序执行
seq.Join(tween2);        // 与上一动画同时
seq.AppendInterval(0.5f); // 插入等待间隔
seq.Insert(0.3f, tween3); // 在指定时间点插入
seq.SetLoops(3, LoopType.Yoyo);
```

### 常用缓动函数

| 缓动 | 效果 | 适用场景 |
|------|------|---------|
| `Ease.OutBack` | 回弹效果 | 入场、出现 |
| `Ease.OutElastic` | 弹性回弹 | 强调、Q弹效果 |
| `Ease.InOutCubic` | 平滑加减速 | 标准移动 |
| `Ease.Shake` | 震动 | 错误、受伤 |
| `Ease.OutBounce` | 弹跳落地 | 掉落、收集 |

完整缓动函数参考 → [dotween-cookbook.md](references/dotween-cookbook.md)

## 完整动效库

详细动效模式参考：
- **按场景组织的动效模式** → [animation-patterns.md](references/animation-patterns.md)
- **错落动画专项指南** → [stagger-animation-guide.md](references/stagger-animation-guide.md)
- **DOTween代码片段库** → [dotween-cookbook.md](references/dotween-cookbook.md)

## 决策流程图

动效选择决策流程 → [assets/fx-decision-tree.md](assets/fx-decision-tree.md)

## 使用示例

### 示例1: 按钮点击反馈（含生命周期管理）

```csharp
// 原始代码
public void OnClick()
{
    DoSomething();
}

// 添加动效后 - 推荐做法
public class AnimatedButton : MonoBehaviour
{
    private Tween _pressTween;

    public void OnPointerDown()
    {
        _pressTween?.Kill();
        _pressTween = transform.DOScale(0.9f, 0.05f)
            .SetEase(Ease.OutQuad)
            .SetLink(gameObject);  // 自动清理
    }

    public void OnPointerUp()
    {
        _pressTween?.Kill();
        _pressTween = transform.DOScale(1f, 0.15f)
            .SetEase(Ease.OutBack)
            .SetLink(gameObject);  // 自动清理，无需 OnDestroy
    }
}
```

### 示例2: 面板入场（防重复触发）

```csharp
public class PanelController : MonoBehaviour
{
    private Tween _showTween;

    void ShowPanel()
    {
        // 防止重复播放
        _showTween?.Kill();

        panel.SetActive(true);
        panel.transform.localScale = Vector3.zero;

        _showTween = panel.transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetLink(gameObject);  // 自动清理
    }

    void HidePanel()
    {
        _showTween?.Kill();

        _showTween = panel.transform.DOScale(0f, 0.3f)
            .SetEase(Ease.InBack)
            .SetLink(gameObject)
            .OnComplete(() => panel.SetActive(false));
    }

    // 对象池回收或场景切换时调用
    void OnClose()
    {
        _showTween?.Kill();
    }
}
```

### 示例3: 卡片列表错落入场（Sequence 管理）

```csharp
public class CardListAnimator : MonoBehaviour
{
    private Sequence _staggerSeq;

    void AnimateCardsIn(List<CardView> cards)
    {
        // 清理旧动画
        _staggerSeq?.Kill(complete: false);
        _staggerSeq = DOTween.Sequence();

        for (int i = 0; i < cards.Count; i++)
        {
            int index = i;
            _staggerSeq.Append(cards[index].transform.DOScale(1f, 0.3f)
                .From(0f)
                .SetEase(Ease.OutBack));
            _staggerSeq.AppendInterval(0.05f);
        }

        // 关联生命周期
        _staggerSeq.SetLink(gameObject);
    }

    // 列表关闭或刷新时调用
    void OnClose()
    {
        _staggerSeq?.Kill(complete: false);
    }
}
```
