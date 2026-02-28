# 错落动画专项指南 (Stagger Animation Guide)

错落动画(Stagger)是指多个元素按顺序依次执行动画，产生流畅的视觉节奏感。

---

## 基础写法

### Sequence + AppendInterval

最基础的错落动画实现方式。

```csharp
void StaggerWithSequence(List<Transform> items)
{
    Sequence seq = DOTween.Sequence();

    for (int i = 0; i < items.Count; i++)
    {
        // 每个元素的入场动画
        seq.Append(items[i].DOScale(1f, 0.3f)
            .From(0f)
            .SetEase(Ease.OutBack));

        // 添加间隔
        seq.AppendInterval(0.05f);
    }
}
```

### SetDelay 方式

更简洁的写法，适合简单错落。

```csharp
void StaggerWithDelay(List<Transform> items)
{
    for (int i = 0; i < items.Count; i++)
    {
        items[i].localScale = Vector3.zero;
        items[i].DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetDelay(i * 0.05f);  // 每个元素延迟0.05秒
    }
}
```

---

## 卡片列表依次入场

### 垂直列表错落入场

```csharp
void AnimateListItems(List<CardView> cards)
{
    for (int i = 0; i < cards.Count; i++)
    {
        int index = i;
        CardView card = cards[index];

        // 初始状态
        card.transform.localScale = Vector3.zero;
        card.canvasGroup.alpha = 0;

        // 错落动画
        Sequence seq = DOTween.Sequence();
        seq.SetDelay(index * 0.08f);  // 递增延迟

        seq.Append(card.transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack));
        seq.Join(card.canvasGroup.DOFade(1, 0.3f));
    }
}
```

### 从中心向两侧展开

```csharp
void AnimateFromCenter(List<CardView> cards)
{
    int centerIndex = cards.Count / 2;

    for (int i = 0; i < cards.Count; i++)
    {
        // 计算距中心的距离，决定延迟
        float distanceFromCenter = Mathf.Abs(i - centerIndex);
        float delay = distanceFromCenter * 0.05f;

        cards[i].transform.localScale = Vector3.zero;
        cards[i].transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetDelay(delay);
    }
}
```

---

## 网格布局错落动画

### 从左到右，从上到下

```csharp
void AnimateGrid(GridLayoutGroup grid, List<Transform> items)
{
    int columns = Mathf.FloorToInt(grid.GetComponent<RectTransform>().rect.width
        / (grid.cellSize.x + grid.spacing.x));

    for (int i = 0; i < items.Count; i++)
    {
        int row = i / columns;
        int col = i % columns;

        // 根据行列计算延迟
        float delay = (row + col) * 0.05f;

        items[i].transform.localScale = Vector3.zero;
        items[i].transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetDelay(delay);
    }
}
```

### 从中心扩散

```csharp
void AnimateGridFromCenter(GridLayoutGroup grid, List<Transform> items)
{
    int columns = 4; // 根据实际布局计算
    int rows = Mathf.CeilToInt((float)items.Count / columns);
    Vector2 center = new Vector2((columns - 1) / 2f, (rows - 1) / 2f);

    for (int i = 0; i < items.Count; i++)
    {
        int row = i / columns;
        int col = i % columns;

        // 计算距中心距离
        float distance = Vector2.Distance(new Vector2(col, row), center);
        float delay = distance * 0.08f;

        items[i].transform.localScale = Vector3.zero;
        items[i].transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetDelay(delay);
    }
}
```

### 波浪效果

```csharp
void AnimateWave(List<Transform> items, int columns)
{
    for (int i = 0; i < items.Count; i++)
    {
        int row = i / columns;
        int col = i % columns;

        // 波浪延迟计算
        float delay = (col * 0.05f) + (row * 0.1f);

        items[i].transform.DOLocalMoveY(20, 0.3f)
            .SetRelative(true)
            .SetEase(Ease.OutQuad)
            .SetDelay(delay)
            .SetLoops(2, LoopType.Yoyo);
    }
}
```

---

## 循环错落动画

### 持续浮动效果

```csharp
void StartFloatingAnimation(List<Transform> items)
{
    for (int i = 0; i < items.Count; i++)
    {
        items[i].DOLocalMoveY(10, 1f)
            .SetRelative(true)
            .SetEase(Ease.InOutSine)
            .SetDelay(i * 0.1f)
            .SetLoops(-1, LoopType.Yoyo);
    }
}
```

### 呼吸效果

```csharp
void StartBreathingAnimation(List<Transform> items)
{
    for (int i = 0; i < items.Count; i++)
    {
        items[i].DOScale(1.05f, 0.8f)
            .SetEase(Ease.InOutSine)
            .SetDelay(i * 0.1f)
            .SetLoops(-1, LoopType.Yoyo);
    }
}
```

### 旋转光环

```csharp
void StartRotatingRing(List<Transform> items, Transform center)
{
    float radius = 100f;
    float duration = 5f;

    for (int i = 0; i < items.Count; i++)
    {
        float angle = (i / (float)items.Count) * 360f;

        // 初始位置
        Vector3 pos = center.position + new Vector3(
            Mathf.Cos(angle * Mathf.Deg2Rad) * radius,
            Mathf.Sin(angle * Mathf.Deg2Rad) * radius,
            0);
        items[i].position = pos;

        // 环绕动画
        items[i].DORotateAround(center.position, Vector3.forward, 360, duration)
            .SetEase(Ease.Linear)
            .SetLoops(-1);
    }
}
```

---

## 回调函数在错落动画中的应用

### 依次播放音效

```csharp
void AnimateWithSounds(List<CardView> cards)
{
    Sequence seq = DOTween.Sequence();

    for (int i = 0; i < cards.Count; i++)
    {
        int index = i;

        seq.Append(cards[index].transform.DOScale(1f, 0.3f)
            .From(0f)
            .SetEase(Ease.OutBack)
            .OnComplete(() => {
                // 每个动画完成时播放音效
                AudioManager.Play("Pop", 0.5f + index * 0.05f);
            }));

        seq.AppendInterval(0.05f);
    }

    // 全部完成回调
    seq.OnComplete(() => {
        Debug.Log("All cards animated!");
        OnAllCardsShown?.Invoke();
    });
}
```

### 错落退场后执行操作

```csharp
void StaggerExitAndDestroy(List<Transform> items, System.Action onComplete)
{
    int completedCount = 0;

    for (int i = 0; i < items.Count; i++)
    {
        int index = i;

        items[index].DOScale(0f, 0.3f)
            .SetEase(Ease.InBack)
            .SetDelay(index * 0.03f)
            .OnComplete(() => {
                items[index].gameObject.SetActive(false);

                completedCount++;
                if (completedCount >= items.Count)
                {
                    onComplete?.Invoke();
                }
            });
    }
}
```

---

## 高级组合效果

### 飞入+错落

```csharp
void FlyInAndStagger(List<Transform> items, Vector3 fromPosition)
{
    for (int i = 0; i < items.Count; i++)
    {
        int index = i;
        Vector3 originalPos = items[index].position;

        items[index].position = fromPosition;
        items[index].localScale = Vector3.zero;

        Sequence seq = DOTween.Sequence();
        seq.SetDelay(index * 0.1f);

        seq.Append(items[index].DOMove(originalPos, 0.5f)
            .SetEase(Ease.OutCubic));
        seq.Join(items[index].DOScale(1f, 0.5f)
            .SetEase(Ease.OutBack));
    }
}
```

### 翻转+错落

```csharp
void FlipInStagger(List<Transform> items)
{
    for (int i = 0; i < items.Count; i++)
    {
        items[i].localRotation = Quaternion.Euler(0, 90, 0);
        items[i].localScale = Vector3.zero;

        Sequence seq = DOTween.Sequence();
        seq.SetDelay(i * 0.08f);

        seq.Append(items[i].DORotate(Vector3.zero, 0.4f)
            .SetEase(Ease.OutBack));
        seq.Join(items[i].DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack));
    }
}
```
