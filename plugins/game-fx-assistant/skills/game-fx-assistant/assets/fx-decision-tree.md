# 动效选择决策流程图

```
开始分析代码
    │
    ▼
代码中有什么动作?
    │
    ├── 元素首次出现 ──► 入场动效 (Entrance)
    │   │
    │   ├── UI面板/弹窗 ──► PopIn (回弹缩放入场)
    │   │
    │   ├── 列表/网格项 ──► Stagger PopIn (错落弹入)
    │   │
    │   ├── Toast/通知 ──► SlideIn (滑入)
    │   │
    │   ├── 背景/遮罩 ──► FadeInScale (淡入+缩放)
    │   │
    │   └── 角色/卡片展示 ──► FlipIn (3D翻转入场)
    │
    ├── 元素消失/关闭 ──► 退场动效 (Exit)
    │   │
    │   ├── 弹窗关闭 ──► PopOut (回弹缩小消失)
    │   │
    │   ├── Toast消失 ──► SlideOut + FadeOut (滑出+淡出)
    │   │
    │   ├── 背景遮罩 ──► FadeOut (单纯淡出)
    │   │
    │   └── 物品使用 ──► Shrink (缩小+淡出)
    │
    ├── 用户点击/交互 ──► 反馈动效 (Feedback)
    │   │
    │   ├── 按钮按下 ──► ButtonPress (按下缩放0.9→回弹)
    │   │
    │   ├── 操作成功 ──► Success (弹跳+勾选)
    │   │
    │   ├── 操作失败 ──► Error (震动+变红闪烁)
    │   │
    │   ├── 悬浮提示 ──► Hover (轻微放大/上移)
    │   │
    │   ├── 数值变化 ──► NumberPopup (数字弹出)
    │   │
    │   └── 收集物品 ──► Collect (飞入目标) + Bounce
    │
    └── 需要吸引注意力 ──► 强调动效 (Emphasis)
        │
        ├── 可交互提示 ──► Pulse (持续脉动)
        │
        ├── 重要事件 ──► Pulse + Glow (脉动+发光)
        │
        ├── 警示/拒绝 ──► Shake (震动)
        │
        └── 奖励/收集 ──► Bounce (弹跳)


========== 组合动效场景 ==========

【列表初始化】
   ├─ 简单列表: SetDelay 错落 PopIn
   └─ 复杂网格: Sequence + AppendInterval

【数值伤害显示】
   ├─ 位置: 对象上方生成
   ├─ 动画: 上移 + 淡出 + 缩放
   └─ 可选: 暴击加震动+放大

【角色受伤】
   ├─ 红色闪烁: DOColor 白→红→白
   ├─ 震动: DOShakePosition
   └─ 可选: 向后击退 DOJump/DOPath

【技能释放】
   ├─ 蓄力: 缩放到0.8 + 发光
   ├─ 释放: 缩放回1.2 + 颜色恢复
   └─ 命中: 目标Shake + 特效

【商店购买】
   ├─ 点击: ButtonPress
   ├─ 货币飞出: Collect动画到货币UI
   ├─ 物品飞入: Collect动画到背包
   └─ 成功: Success动画
```

---

## 快速参考表

| 代码信号 | 推荐动效 | 参考文件 |
|---------|---------|---------|
| `SetActive(true)` | PopIn / SlideIn | animation-patterns.md#entrance |
| `SetActive(false)` | PopOut / FadeOut | animation-patterns.md#exit |
| `OnClick` | ButtonPress / Pulse | animation-patterns.md#feedback |
| `OnPointerEnter` | Hover | animation-patterns.md#feedback |
| `Instantiate` + 列表 | Stagger PopIn | stagger-animation-guide.md |
| `TakeDamage` | Shake + 红色闪烁 | animation-patterns.md#feedback |
| `AddScore` | NumberPopup | animation-patterns.md#feedback |
| `CollectItem` | Bounce + Collect | animation-patterns.md#feedback |
