# Unity 面试题库

## 初级 (了解)
1. Unity生命周期函数的执行顺序？（Awake -> OnEnable -> Start -> FixedUpdate -> Update -> LateUpdate -> OnDisable -> OnDestroy）
2. MonoBehaviour的原理？（组件化设计、反射机制、C++底层实现）
3. Transform和GameObject的关系？（每个GameObject都有Transform，Transform决定位置/旋转/缩放）
4. Prefab的作用是什么？如何实例化？（预制体、资源复用、Instantiate方法）
5. Unity中的碰撞器和触发器有什么区别？（Collider vs Trigger，OnCollision vs OnTrigger）
6. Resources.Load和AssetBundle的区别？（Resources编译打包、AssetBundle动态加载）
7. Unity中如何实现对象池？（预先创建对象、重复使用、减少GC）
8. Unity的渲染管线有哪些？（Built-in、URP、HDRP的区别和适用场景）
9. Unity中如何实现摄像机跟随？（设置父物体、LateUpdate更新位置、平滑插值）
10. Unity中的Layer和Tag有什么区别？（Layer用于物理和渲染分组，Tag用于对象标识）

## 中级 (熟练)
1. Addressable Assets System的优势和使用场景？（资源热更新、依赖管理、内存管理）
2. Unity的协程(Coroutine)原理？与多线程的区别？（主线程分时执行、yield return机制）
3. Unity的物理系统（Rigidbody vs CharacterController）？（物理模拟 vs 射线检测）
4. Unity中的委托和事件如何实现消息系统？（Action/Func、UnityEvent、C# event）
5. 如何实现Unity中的存档系统？（PlayerPrefs、JSON、SQLite、ScriptableObject）
6. Unity的Shader是如何工作的？ShaderLab结构？（Properties、SubShader、Pass）
7. Unity中的动画系统（Animator vs Animation）？（状态机、混合树、Avatar系统）
8. Unity的UGUI系统如何优化？（图集打包、Overdraw控制、Canvas分层）
9. Unity中如何实现自定义编辑器工具？（Editor窗口、PropertyDrawer、Gizmos）
10. Unity中的光照系统（烘焙vs实时光照、Lightmap、Reflection Probe）？
11. Unity中的粒子系统如何优化？（GPU粒子、粒子数量控制、LOD）
12. Unity中的音频系统如何使用？（AudioSource、AudioMixer、3D音效设置）

## 高级 (精通)
1. Unity DOTS/ECS架构的核心概念？（Entity-Component-System、Job System、Burst Compiler）
2. Unity的渲染流程？（Culling -> Shadow -> Depth -> GBuffer -> Lighting -> Post-processing）
3. 如何优化Unity游戏的内存使用？（纹理压缩、资源卸载、AssetBundle管理、对象池）
4. Unity的IL2CPP构建流程？（C# -> IL -> C++ -> 原生代码、性能优势）
5. 如何实现Unity的热更新方案？（Lua方案、HybridCLR、Addressable热更）
6. Unity的GPU Instancing和SRP Batcher原理？（减少Draw Call、批量渲染）
7. Unity中的异步加载和场景管理？（SceneManager、AsyncOperation、加载进度）
8. 如何编写高效的Unity Shader？（顶点优化、片段优化、变体管理）
9. Unity的Timeline和Cinemachine系统？（过场动画、镜头控制、轨道编辑）
10. Unity中的网络同步方案？（UNET、Mirror、Netcode for GameObjects）
11. 如何分析和解决Unity游戏的卡顿问题？（Profiler、Frame Debugger、Memory Profiler）
12. Unity的ScriptableObject使用场景？（数据配置、运行时资源、事件系统）

## 项目深挖
1. 项目中的资源管理方案是什么？为什么选择这个方案？
2. 项目中遇到的最严重的性能问题是什么？如何解决的？
3. 项目中的UI架构是如何设计的？如何解决UI频繁打开关闭的性能问题？
4. 项目中是否使用了热更新？技术方案是什么？遇到了哪些坑？
5. 项目中的场景加载时间过长，你会如何优化？
6. 项目中的动画系统是如何设计的？如何处理大量角色的动画？
7. 项目中的物理系统使用遇到了什么问题？（穿模、抖动、性能）
8. 项目中的摄像机系统是如何设计的？如何避免穿墙？
9. 项目中的特效是如何管理的？如何保证特效不会导致卡顿？
10. 项目中的AssetBundle是如何组织的？依赖关系如何处理？
