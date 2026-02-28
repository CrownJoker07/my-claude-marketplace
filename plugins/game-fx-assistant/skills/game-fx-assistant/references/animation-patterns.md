# 动效模式库 (Animation Patterns)

按4大场景组织的动效模式库。每个模式包含：适用场景、DOTween代码示例、可配置参数。

---

## 入场动效 (Entrance)

元素首次出现时使用。

### PopIn (弹入)

从0缩放到1，带轻微回弹。

**适用场景**：UI面板、弹窗、提示框、卡片出现

```csharp
// 基础版
transform.localScale = Vector3.zero;
transform.DOScale(1f, 0.4f).SetEase(Ease.OutBack);

// 带延迟（错落效果）
transform.localScale = Vector3.zero;
transform.DOScale(1f, 0.4f)
    .SetEase(Ease.OutBack)
    .SetDelay(index * 0.05f);
```

**可配置参数**：
- 持续时间: 0.3-0.5s
- 缓动: OutBack, OutElastic
- 延迟: 错落时使用

### SlideIn (滑入)

从屏幕外滑入。

**适用场景**：侧边栏、通知、Toast消息

```csharp
// 从左滑入
Vector2 startPos = new Vector2(-Screen.width, 0);
rectTransform.anchoredPosition = startPos;
rectTransform.DOAnchorPos(Vector2.zero, 0.4f).SetEase(Ease.OutCubic);

// 从下滑入
rectTransform.anchoredPosition = new Vector2(0, -200);
rectTransform.DOAnchorPos(Vector2.zero, 0.4f).SetEase(Ease.OutCubic);

// 带透明度
canvasGroup.alpha = 0;
rectTransform.DOAnchorPos(Vector2.zero, 0.4f).SetEase(Ease.OutCubic);
canvasGroup.DOFade(1, 0.3f);
```

**可配置参数**：
- 方向: 左/右/上/下
- 距离: 屏幕边缘或固定值
- 缓动: OutCubic, OutQuart

### FadeInScale (淡入+缩放)

透明度+缩放组合入场。

**适用场景**：背景遮罩、模态框、柔和出现

```csharp
// 需要CanvasGroup组件
canvasGroup.alpha = 0;
transform.localScale = Vector3.one * 0.8f;

Sequence seq = DOTween.Sequence();
seq.Join(canvasGroup.DOFade(1, 0.3f));
seq.Join(transform.DOScale(1f, 0.3f).SetEase(Ease.OutQuad));
```

### FlipIn (3D翻转入场)

3D翻转效果入场。

**适用场景**：卡片翻转、角色展示、戏剧性出现

```csharp
transform.localRotation = Quaternion.Euler(0, 90, 0);
transform.DORotate(Vector3.zero, 0.5f).SetEase(Ease.OutBack);

// Y轴翻转
transform.localRotation = Quaternion.Euler(0, 0, 90);
transform.DORotate(Vector3.zero, 0.5f).SetEase(Ease.OutBack);
```

---

## 强调动效 (Emphasis)

吸引注意力时使用。

### Pulse (脉动)

周期性缩放脉动。

**适用场景**：可交互提示、重要按钮、待处理任务

```csharp
// 单次脉动
transform.DOScale(1.1f, 0.15f)
    .SetEase(Ease.OutQuad)
    .SetLoops(2, LoopType.Yoyo);

// 持续脉动（提示）
transform.DOScale(1.05f, 0.5f)
    .SetEase(Ease.InOutSine)
    .SetLoops(-1, LoopType.Yoyo);
```

### Shake (震动)

水平或垂直震动。

**适用场景**：错误提示、拒绝操作、受伤反馈

```csharp
// 水平震动
transform.DOShakePosition(0.4f, new Vector3(10, 0, 0), 10, 90);

// 垂直震动
transform.DOShakePosition(0.4f, new Vector3(0, 10, 0), 10, 90);

// 组合：震动+颜色闪烁
Sequence seq = DOTween.Sequence();
seq.Append(transform.DOShakePosition(0.4f, new Vector3(10, 0, 0), 10, 90));
seq.Join(image.DOColor(Color.red, 0.1f).SetLoops(4, LoopType.Yoyo));
```

### Bounce (弹跳)

弹跳效果。

**适用场景**：收集物品、金币、奖励

```csharp
// 向上弹跳
transform.DOMoveY(transform.position.y + 50, 0.3f)
    .SetEase(Ease.OutQuad)
    .SetLoops(2, LoopType.Yoyo);

// 落地弹跳
Vector3 originalPos = transform.position;
Sequence seq = DOTween.Sequence();
seq.Append(transform.DOMoveY(originalPos.y + 100, 0.3f).SetEase(Ease.OutQuad));
seq.Append(transform.DOMoveY(originalPos.y, 0.4f).SetEase(Ease.OutBounce));
```

### Glow (发光脉冲)

发光效果脉冲。

**适用场景**：选中状态、能量充满、魔法效果

```csharp
// 使用Material的_EmissionColor
Material mat = GetComponent<Renderer>().material;
Color glowColor = Color.yellow * 2f;
mat.DOColor(glowColor, "_EmissionColor", 0.3f)
    .SetLoops(-1, LoopType.Yoyo);

// UI Glow效果
outline.effectDistance = Vector2.zero;
DOTween.To(() => outline.effectDistance, x => outline.effectDistance = x,
    new Vector2(5, 5), 0.5f).SetLoops(-1, LoopType.Yoyo);
```

---

## 退场动效 (Exit)

元素消失时使用。

### PopOut (弹出消失)

缩放到0消失。

**适用场景**：弹窗关闭、提示消失

```csharp
transform.DOScale(0f, 0.3f)
    .SetEase(Ease.InBack)
    .OnComplete(() => gameObject.SetActive(false));
```

### SlideOut (滑出)

滑出屏幕后消失。

**适用场景**：Toast消息、侧边栏收起

```csharp
// 向下滑出
rectTransform.DOAnchorPos(new Vector2(0, -200), 0.3f)
    .SetEase(Ease.InCubic)
    .OnComplete(() => gameObject.SetActive(false));

// 带淡出
Sequence seq = DOTween.Sequence();
seq.Append(canvasGroup.DOFade(0, 0.2f));
seq.Join(rectTransform.DOAnchorPos(new Vector2(0, -50), 0.3f));
seq.OnComplete(() => gameObject.SetActive(false));
```

### FadeOut (淡出)

单纯淡出。

**适用场景**：背景、遮罩、温和消失

```csharp
canvasGroup.DOFade(0, 0.3f)
    .OnComplete(() => gameObject.SetActive(false));
```

### Shrink (缩小+淡出)

组合退场效果。

**适用场景**：卡片消失、物品使用

```csharp
Sequence seq = DOTween.Sequence();
seq.Join(transform.DOScale(0.5f, 0.3f));
seq.Join(canvasGroup.DOFade(0, 0.3f));
seq.SetEase(Ease.InCubic);
seq.OnComplete(() => gameObject.SetActive(false));
```

---

## 反馈动效 (Feedback)

用户操作响应。

### ButtonPress (按钮按下)

按下缩放反馈。

**适用场景**：所有可点击按钮

```csharp
public void OnPointerDown(PointerEventData eventData)
{
    transform.DOScale(0.9f, 0.05f).SetEase(Ease.OutQuad);
}

public void OnPointerUp(PointerEventData eventData)
{
    transform.DOScale(1f, 0.15f).SetEase(Ease.OutBack);
}
```

### Success (成功反馈)

勾选+缩放效果。

**适用场景**：任务完成、操作成功、收集确认

```csharp
void PlaySuccessAnimation()
{
    Sequence seq = DOTween.Sequence();

    // 缩放弹跳
    seq.Append(transform.DOScale(1.2f, 0.15f).SetEase(Ease.OutQuad));
    seq.Append(transform.DOScale(1f, 0.3f).SetEase(Ease.OutElastic));

    // 可选：勾选图标旋转出现
    checkIcon.transform.localScale = Vector3.zero;
    seq.Join(checkIcon.transform.DOScale(1f, 0.3f).SetEase(Ease.OutBack));
    checkIcon.transform.DORotate(new Vector3(0, 0, 360), 0.5f, RotateMode.FastBeyond360);
}
```

### Error (错误反馈)

左右震动+颜色变化。

**适用场景**：输入错误、操作失败

```csharp
void PlayErrorAnimation()
{
    // 震动
    transform.DOShakePosition(0.4f, new Vector3(10, 0, 0), 10, 90);

    // 变红闪烁
    Color originalColor = image.color;
    Sequence colorSeq = DOTween.Sequence();
    colorSeq.Append(image.DOColor(Color.red, 0.1f));
    colorSeq.Append(image.DOColor(originalColor, 0.1f));
    colorSeq.SetLoops(3);
}
```

### Hover (悬浮效果)

鼠标悬浮放大/上移。

**适用场景**：卡片、按钮、可交互元素

```csharp
public void OnPointerEnter(PointerEventData eventData)
{
    transform.DOScale(1.05f, 0.2f).SetEase(Ease.OutQuad);
    // 或上移
    // rectTransform.DOAnchorPosY(originalY - 10, 0.2f);
}

public void OnPointerExit(PointerEventData eventData)
{
    transform.DOScale(1f, 0.2f).SetEase(Ease.OutQuad);
}
```

### NumberPopup (数值弹出)

伤害数字/分数弹出效果。

**适用场景**：伤害数字、分数增加

```csharp
void ShowNumber(Vector3 position, int number, Color color)
{
    TextMeshPro text = Instantiate(numberPrefab, position, Quaternion.identity);
    text.text = number.ToString();
    text.color = color;

    Sequence seq = DOTween.Sequence();
    seq.Append(text.transform.DOMoveY(position.y + 50, 0.5f).SetEase(Ease.OutQuad));
    seq.Join(text.DOFade(0, 0.5f).SetDelay(0.2f));
    seq.OnComplete(() => Destroy(text.gameObject));
}
```

### Collect (收集飞入)

物品飞向目标（如金币飞入钱包）。

**适用场景**：收集资源、奖励领取

```csharp
void CollectToTarget(Vector3 startPos, Transform target, System.Action onComplete)
{
    GameObject item = Instantiate(collectiblePrefab, startPos, Quaternion.identity);

    item.transform.DOMove(target.position, 0.5f)
        .SetEase(Ease.InBack)
        .OnComplete(() => {
            Destroy(item);
            onComplete?.Invoke();
        });
}
```
