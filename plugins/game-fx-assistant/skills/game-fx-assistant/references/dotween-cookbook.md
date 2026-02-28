# DOTween 代码片段库

常用DOTween代码片段速查。

---

## 动画生命周期管理（重要）

DOTween 动画需要妥善管理生命周期，避免内存泄漏和动画冲突。

### Tween 引用管理

始终保存 Tween 引用，以便后续控制。

```csharp
public class AnimatedButton : MonoBehaviour
{
    private Tween _scaleTween;  // 保存引用

    void OnPointerDown()
    {
        // 先杀掉旧动画，避免冲突
        _scaleTween?.Kill();

        _scaleTween = transform.DOScale(0.9f, 0.05f)
            .SetEase(Ease.OutQuad);
    }

    void OnPointerUp()
    {
        _scaleTween?.Kill();

        _scaleTween = transform.DOScale(1f, 0.15f)
            .SetEase(Ease.OutBack);
    }

    // 不需要 OnDestroy，因为 SetLink 会自动处理
    // 或者在对象池回收时手动调用 Cleanup()
}
```

### SetLink 自动清理（推荐）

使用 `SetLink` 让动画自动关联 GameObject 生命周期。

```csharp
// GameObject 销毁时自动 Kill 动画
transform.DOScale(1.2f, 0.3f)
    .SetLink(gameObject);  // 推荐：自动清理

// 可选参数：销毁时是否完成动画
transform.DOScale(1.2f, 0.3f)
    .SetLink(gameObject, LinkBehaviour.KillOnDestroy);

// 其他选项：
// - LinkBehaviour.CompleteOnDestroy: 销毁时完成动画
// - LinkBehaviour.CompleteAndKillOnDestroy: 销毁时完成并清理
// - LinkBehaviour.PauseOnDisable: 禁用时暂停
```

### Sequence 内存管理

Sequence 需要特别小心，避免内存泄漏。在关闭/卸载时手动清理。

```csharp
public class CardAnimator : MonoBehaviour
{
    private Sequence _entranceSeq;

    void PlayEntrance()
    {
        // 确保旧 Sequence 被清理
        _entranceSeq?.Kill(complete: false);
        _entranceSeq = DOTween.Sequence();

        _entranceSeq.Append(transform.DOScale(1f, 0.4f).From(0f));
        _entranceSeq.Join(GetComponent<CanvasGroup>().DOFade(1, 0.3f));

        _entranceSeq.SetLink(gameObject);  // 推荐：自动关联生命周期
    }

    void Close()  // 或 OnClose, Despawn, Unselect 等
    {
        // 面板关闭时清理动画，complete=false 避免触发回调
        _entranceSeq?.Kill(complete: false);
        _entranceSeq = null;
    }
}
```

### 重复播放保护

防止快速点击或重复调用导致的动画重叠。

```csharp
public class PanelController : MonoBehaviour
{
    private Tween _showTween;
    private bool _isAnimating;

    void ShowPanel()
    {
        // 方式1：检查并杀掉旧动画
        _showTween?.Kill();
        panel.SetActive(true);
        panel.transform.localScale = Vector3.zero;

        _showTween = panel.transform.DOScale(1f, 0.4f)
            .SetEase(Ease.OutBack)
            .SetLink(gameObject);  // 自动生命周期管理
    }

    // 方式2：使用 isAnimating 标志
    void HidePanel()
    {
        if (_isAnimating) return;
        _isAnimating = true;

        panel.transform.DOScale(0f, 0.3f)
            .SetEase(Ease.InBack)
            .OnComplete(() => {
                panel.SetActive(false);
                _isAnimating = false;
            });
    }

    // 方式3：DOTween 的 IsTweening 检查
    void TogglePanel()
    {
        if (DOTween.IsTweening(panel.transform)) return;

        panel.SetActive(!panel.activeSelf);
        // ... 动画代码
    }
}
```

### DOTween.Kill 与 DOTween.Complete

```csharp
// 杀掉特定对象的动画
DOTween.Kill(transform);

// 杀掉特定 ID 的动画
DOTween.Kill("myAnimationId");

// 杀掉特定类型的动画
DOTween.Kill(transform, true);  // true = 包括子对象

// 完成所有动画（触发 OnComplete）
DOTween.CompleteAll();
DOTween.Complete(transform);

// 杀掉所有动画（慎用）
DOTween.KillAll();

// 重启所有动画
DOTween.RestartAll();
```

### 最佳实践总结

```csharp
public class AnimationBestPractice : MonoBehaviour
{
    // 1. 为需要控制的动画声明引用
    [SerializeField] private Transform _target;
    private Tween _currentTween;
    private Sequence _sequence;

    void PlayAnimation()
    {
        // 2. 播放前清理旧动画
        _currentTween?.Kill();
        _sequence?.Kill(complete: false);

        // 3. 创建动画并保存引用
        _currentTween = _target.DOMove(Vector3.right * 100, 1f)
            .SetEase(Ease.OutBack);

        // 4. 使用 SetLink 自动关联生命周期
        _currentTween.SetLink(gameObject);

        // 5. 完成回调（无需赋 null，DOTween 自动处理）
        _currentTween.OnComplete(() => OnAnimationFinished());
    }

    void PlayComplexSequence()
    {
        _sequence?.Kill(complete: false);
        _sequence = DOTween.Sequence();

        _sequence.Append(_target.DOScale(1.2f, 0.2f));
        _sequence.Append(_target.DOScale(1f, 0.3f));

        // Sequence 也要 SetLink
        _sequence.SetLink(gameObject);
    }

    // 6. 在 Close/Despawn/Unselect 等方法中清理
    void OnClose()
    {
        _currentTween?.Kill();
        _sequence?.Kill(complete: false);
    }
}
```

---

## 基础变换动画

### 移动 (DOMove)

```csharp
// 世界坐标移动
transform.DOMove(new Vector3(5, 0, 0), 1f);
transform.DOMoveX(5, 1f);  // 仅X轴
transform.DOMoveY(3, 1f);  // 仅Y轴

// 局部坐标移动
transform.DOLocalMove(new Vector3(5, 0, 0), 1f);
transform.DOLocalMoveX(5, 1f);

// 相对移动
transform.DOMove(new Vector3(5, 0, 0), 1f).SetRelative(true);

// UI移动 (RectTransform)
rectTransform.DOAnchorPos(new Vector2(100, 0), 0.5f);
rectTransform.DOAnchorPosX(100, 0.5f);
```

### 旋转 (DORotate)

```csharp
// 欧拉角旋转
transform.DORotate(new Vector3(0, 90, 0), 1f);

// 局部旋转
transform.DOLocalRotate(new Vector3(0, 90, 0), 1f);

// 四元数旋转
transform.DORotateQuaternion(Quaternion.Euler(0, 90, 0), 1f);

// 超过360度的旋转
transform.DORotate(new Vector3(0, 720, 0), 2f, RotateMode.FastBeyond360);

// 看向目标
transform.DOLookAt(target.position, 1f);
```

### 缩放 (DOScale)

```csharp
// 均匀缩放
transform.DOScale(2f, 1f);

// 非均匀缩放
transform.DOScale(new Vector3(2, 0.5f, 1), 1f);

// 单轴缩放
transform.DOScaleX(2f, 1f);
transform.DOScaleY(0.5f, 1f);

// 从指定值开始缩放
transform.DOScale(1f, 0.5f).From(0f);
transform.DOScale(1f, 0.5f).From(2f);  // 从大变小
```

### 震动 (DOShake)

```csharp
// 位置震动
transform.DOShakePosition(1f, 1f);  // 持续时间, 强度
transform.DOShakePosition(1f, new Vector3(1, 1, 0), 10, 90);  // 自定义轴向

// 旋转震动
transform.DOShakeRotation(1f, 30f);

// 缩放震动
transform.DOShakeScale(1f, 0.5f);
```

---

## 颜色/透明度动画

### UI透明度 (CanvasGroup)

```csharp
// 淡入
canvasGroup.DOFade(1f, 0.5f);

// 淡出
canvasGroup.DOFade(0f, 0.5f);

// 闪烁
canvasGroup.DOFade(0.5f, 0.3f).SetLoops(-1, LoopType.Yoyo);

// 脉冲透明
canvasGroup.DOFade(0.8f, 0.5f)
    .SetEase(Ease.InOutSine)
    .SetLoops(-1, LoopType.Yoyo);
```

### Image颜色

```csharp
Image image = GetComponent<Image>();

// 变红
image.DOColor(Color.red, 0.5f);

// 闪烁
image.DOColor(Color.red, 0.1f).SetLoops(4, LoopType.Yoyo);

// 渐变到另一种颜色
image.DOColor(new Color(1, 0.5f, 0), 1f);

// 恢复原始颜色
image.DOColor(Color.white, 0.3f);
```

### SpriteRenderer颜色

```csharp
SpriteRenderer sprite = GetComponent<SpriteRenderer>();

sprite.DOColor(Color.red, 0.5f);
sprite.DOFade(0.5f, 0.5f);  // 仅透明度
```

### Material颜色

```csharp
Material mat = GetComponent<Renderer>().material;

// 基础颜色
mat.DOColor(Color.red, 1f);

// 发射颜色 (Glow效果)
mat.DOColor(Color.yellow * 2f, "_EmissionColor", 1f);

// 属性动画
mat.DOFloat(1f, "_Metallic", 1f);
mat.DOVector(new Vector4(1, 0, 0, 1), "_Color", 1f);
```

### Text颜色/渐变

```csharp
TextMeshPro text = GetComponent<TextMeshPro>();

// 透明度
text.DOFade(0, 0.5f);

// 颜色渐变
text.DOColor(Color.yellow, 0.5f);

// 文字渐变效果
text.DOGradientColor(new Color(1, 0, 0), new Color(0, 0, 1), 1f);
```

---

## 路径动画

### 曲线路径

```csharp
// 定义路径点
Vector3[] path = new Vector3[] {
    new Vector3(0, 0, 0),
    new Vector3(2, 4, 0),
    new Vector3(4, 0, 0),
    new Vector3(6, 2, 0)
};

// 线性路径
transform.DOPath(path, 2f, PathType.Linear);

// 曲线路径 (Catmull-Rom)
transform.DOPath(path, 2f, PathType.CatmullRom);

// 带朝向
transform.DOPath(path, 2f, PathType.CatmullRom)
    .SetOptions(true);  // 自动朝向路径方向

// 闭合路径
transform.DOPath(path, 2f, PathType.CatmullRom)
    .SetLoops(-1, LoopType.Restart);
```

### 贝塞尔曲线

```csharp
// 二次贝塞尔曲线
transform.DOPath(new Vector3[] {
    startPos,
    controlPoint,
    endPos
}, 1f, PathType.CatmullRom);

// 跳跃弧线
Vector3[] jumpPath = new Vector3[] {
    transform.position,
    transform.position + new Vector3(2, 3, 0),
    transform.position + new Vector3(4, 0, 0)
};
transform.DOPath(jumpPath, 1f, PathType.CatmullRom);
```

---

## 循环设置

### 循环类型

```csharp
// 无限循环
tween.SetLoops(-1);

// 有限循环
tween.SetLoops(3);

// Yoyo循环 (正向→反向→正向...)
tween.SetLoops(-1, LoopType.Yoyo);

// 重新开始循环
tween.SetLoops(-1, LoopType.Restart);

// 递增循环 (每次累加变化值)
tween.SetLoops(3, LoopType.Incremental);
```

### 循环回调

```csharp
// 每次循环完成
tween.OnStepComplete(() => Debug.Log("Step done"));

// 全部完成
tween.OnComplete(() => Debug.Log("All done"));
```

---

## 缓动函数选择指南

### 入场动效推荐

| 缓动 | 效果 | 适用 |
|------|------|------|
| `Ease.OutBack` | 回弹 | PopIn、卡片出现 |
| `Ease.OutElastic` | 弹性 | Q弹效果、橡皮筋感 |
| `Ease.OutBounce` | 弹跳 | 掉落、收集 |
| `Ease.OutCubic` | 平滑减速 | SlideIn、优雅入场 |

### 退场动效推荐

| 缓动 | 效果 | 适用 |
|------|------|------|
| `Ease.InBack` | 回吸收缩 | PopOut |
| `Ease.InCubic` | 平滑加速 | SlideOut |
| `Ease.InQuart` | 快速加速 | 急速消失 |

### 反馈动效推荐

| 缓动 | 效果 | 适用 |
|------|------|------|
| `Ease.OutQuad` | 轻微减速 | 按钮按下 |
| `Ease.Shake` | 震动 | 错误提示 |
| `Ease.InOutSine` | 正弦波 | 脉动、呼吸 |
| `Ease.Flash` | 闪烁 | 强调、警告 |

---

## Sequence组合动画

### 基础Sequence

```csharp
Sequence seq = DOTween.Sequence();

// 顺序执行
seq.Append(tween1);
seq.Append(tween2);

// 同时执行
seq.Join(tween2);  // 与上一动画同时

// 插入等待
seq.AppendInterval(0.5f);

// 在指定时间插入
seq.Insert(0.3f, tween3);  // 在0.3秒处插入

// 预准备
seq.Prepend(tween0);  // 在开头添加

// 预准备间隔
seq.PrependInterval(0.2f);
```

### Sequence回调

```csharp
Sequence seq = DOTween.Sequence();

seq.AppendCallback(() => Debug.Log("A"));
seq.AppendInterval(0.5f);
seq.AppendCallback(() => Debug.Log("B"));
seq.InsertCallback(0.25f, () => Debug.Log("Middle"));
```

### Sequence嵌套

```csharp
// 创建子Sequence
Sequence subSeq = DOTween.Sequence();
subSeq.Append(tweenA);
subSeq.Append(tweenB);

// 主Sequence
Sequence mainSeq = DOTween.Sequence();
mainSeq.Append(subSeq);
mainSeq.Append(tweenC);
```

---

## 控制与事件

### 播放控制

```csharp
Tween tween = transform.DOMoveX(10, 1f);

// 播放
tween.Play();

// 暂停
tween.Pause();

// 停止
tween.Kill();

// 重新开始
tween.Restart();

// 倒放
tween.PlayBackwards();

// 完成
tween.Complete();

// 跳转
tween.Goto(0.5f);  // 跳转到0.5秒
```

### 事件回调

```csharp
transform.DOMoveX(10, 1f)
    .OnStart(() => Debug.Log("Start"))
    .OnPlay(() => Debug.Log("Play"))
    .OnUpdate(() => Debug.Log("Update"))
    .OnStepComplete(() => Debug.Log("Step Complete"))
    .OnComplete(() => Debug.Log("Complete"))
    .OnKill(() => Debug.Log("Killed"));
```

### 参数设置

```csharp
transform.DOMoveX(10, 1f)
    .SetDelay(0.5f)              // 延迟
    .SetSpeedBased(true)         // 基于速度而非时间
    .SetId("myTween")            // ID标识
    .SetTarget(this)             // 目标对象
    .SetAutoKill(false)          // 不自动销毁
    .SetRecyclable(true);        // 可回收复用
```

### SetLink 自动生命周期管理（强烈推荐）

```csharp
// 基础用法：GameObject 销毁时自动 Kill
transform.DOMoveX(10, 1f).SetLink(gameObject);

// 指定行为
.SetLink(gameObject, LinkBehaviour.KillOnDestroy);        // 销毁时杀掉（默认）
.SetLink(gameObject, LinkBehaviour.CompleteOnDestroy);    // 销毁时完成
.SetLink(gameObject, LinkBehaviour.CompleteAndKillOnDestroy);  // 销毁时完成并杀掉
.SetLink(gameObject, LinkBehaviour.PauseOnDisable);       // 禁用时暂停
.SetLink(gameObject, LinkBehaviour.PauseOnDisablePlayOnEnable); // 禁用暂停，启用继续
```

---

## 值动画

### DOVirtual

```csharp
// 数值变化
DOVirtual.Float(0, 100, 1f, value => {
    healthBar.fillAmount = value / 100f;
});

// 延迟回调
DOVirtual.DelayedCall(2f, () => {
    Debug.Log("Delayed!");
});

// 执行N次
DOVirtual.Int(0, 10, 1f, i => {
    Debug.Log($"Count: {i}");
});
```

### DOTween.To

```csharp
// 通用值动画
DOTween.To(() => myValue, x => myValue = x, 100, 1f);

// 颜色渐变
DOTween.To(() => light.color, c => light.color = c, Color.red, 1f);

// 字段动画
DOTween.To(() => field, x => field = x, targetValue, 1f);
```

---

## 3D特效

### 跳跃

```csharp
void Jump(Vector3 targetPosition)
{
    Sequence seq = DOTween.Sequence();

    // 上升
    seq.Append(transform.DOMoveY(transform.position.y + 2, 0.3f)
        .SetEase(Ease.OutQuad));

    // 下落
    seq.Append(transform.DOMoveY(targetPosition.y, 0.3f)
        .SetEase(Ease.InQuad));

    // 水平移动（全程）
    seq.Join(transform.DOMoveX(targetPosition.x, 0.6f)
        .SetEase(Ease.Linear));
}
```

### 漂浮

```csharp
void Float()
{
    transform.DOLocalMoveY(10, 2f)
        .SetRelative(true)
        .SetEase(Ease.InOutSine)
        .SetLoops(-1, LoopType.Yoyo);
}
```

### 螺旋

```csharp
void Spiral(Transform center, float radius, float height, float duration)
{
    float angle = 0;
    DOTween.To(() => angle, a => angle = a, 720, duration)
        .SetEase(Ease.Linear)
        .OnUpdate(() => {
            float rad = angle * Mathf.Deg2Rad;
            float y = Mathf.Lerp(0, height, angle / 720f);
            transform.position = center.position + new Vector3(
                Mathf.Cos(rad) * radius,
                y,
                Mathf.Sin(rad) * radius
            );
        });
}
```
