# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：opening + recall + self-collision update + robot baseline  
结构：1. opening  2. recall  3. stable self-collision diagnosis  4. conservative robot SemiImplicit baseline  
目标：给 `2026-04-08` meeting 保留 recall baseline，并补上本周最稳妥的 robot visual result。  

---

## Slide 1 — Xinjie Zhang
这一页是 `2026-04-08` meeting 的 opening page。
当前 bundle 不再只是 recall scaffold。
这次 opening 要把三件事一次说清楚：baseline recall、stable self-collision diagnosis、以及这周最值得拿上会的 robot SemiImplicit visual result。
所以我的 opening 目标不是 overclaim，而是把已经成立的部分和还没有成立的部分彻底分开。

## Slide 2 — Recall R1: The Bridge Baseline Was Already Established
第一页 recall 只做 baseline reminder。
cloth、zebra、sloth、rope 这四条 bridge baseline 不是这周才第一次成立，它们已经是之前 meeting 里站住的内容。
所以这一页的作用不是重新证明 bridge 能 import，而是提醒听众：后面的新问题建立在一个已经存在的 baseline 上。

## Slide 3 — Recall R2: The Baseline Already Matched The Reference Motion
第二页 recall 继续只做 visual reminder。
之前不只是说 bridge case 看起来差不多，而是已经有 direct motion overlay 去对照 reference 和 Newton。
这意味着当前讨论的起点不是『baseline 还没对齐』，而是 baseline 对齐之后还剩下哪些更窄的问题。

## Slide 4 — Recall R3: Deformable-Rigid Interaction Already Existed
这一页回忆的是 interaction 本身已经存在。
也就是说，deformable-rigid 不是这周才第一次出现的效果；之前 rope 和 bunny 的 interaction 就已经是可见的。
所以后面如果继续讨论 bunny 或别的 rigid target，问题不应该再退回成『到底有没有 interaction』，而应该继续讲 interaction 之后暴露出来的 failure mode。

## Slide 5 — Recall R4: Bunny Was Harder Than Thick Box
这一页 recall 的 point 很直接。
同样是 rigid support，换成 thick box 以后现象就明显更稳定，所以问题不是 bridge 连 contact baseline 都没有。
这个对比把问题收窄到 geometry-sensitive support behavior，而不是把所有 rigid interaction 都打成失败。

## Slide 6 — Recall R5: Weight Change Did Not Remove Interaction
这一页 recall weight compare。
它的作用不是重新讲参数调优，而是提醒听众：weight 改了以后，interaction 仍然存在。
所以后面的 failure analysis 不能被讲成『只要 weight 一变，interaction 就没了』，更准确的是 behavior 变了，但 interaction baseline 没被抹掉。

## Slide 7 — Recall R6: Radius Helped, But Thin Geometry Still Survived
最后一页 recall 只保留最难反驳的 visual counterexample。
radius 变大确实会帮忙，但 thin geometry 还是能把 penetration 问题保留下来。
这页的作用是把后续讨论重新固定在一个更窄的问题上：不是 bridge baseline 缺失，而是 thin geometry 和 local contact behavior 仍然需要新的解释或修复。

## Slide 8 — Self-Collision S1: Stable 2x2 Matrix And Mechanism Board
这一页是本周 self-collision 章节最重要的可视化成果。
左上角是稳定的 `2 x 2` matrix，最优 full-rollout 组合仍然是 case 3，也就是 PhysTwin-style self-collision 加 native Newton ground-contact。
右上角是 case 3 和 case 4 的 per-frame RMSE 曲线。这里最关键的不是谁最后均值更小，而是 case 4 在 early rollout 其实更好，它是在 frame 40 首次翻符号、并在 frame 107 开始进入持续更差区间。
下排把机制证据压在一张图里：左边是 frame 40、107、137 的 active ground particle 对比，右边是 self-contact active nodes 加 controller mismatch reminder。
这张图想传达的主句只有一句：case 4 不是因为 local self-collision law 错了才输，而是因为 fully PhysTwin-style branch 暴露了 bridge 里剩余的 whole-step mismatch。

## Slide 9 — Self-Collision S2: Current Conclusion And Recommendation
这一页只做 decision close，不再堆图。
第一，stable matrix 已经证明 case 3 比 case 4 更好这个排序是真的，不是之前那种不稳定 ranking artifact。
第二，但这个 stable result 不能被误读成 native Newton ground-contact 更 PhysTwin-faithful。我们现在更支持的解释是，native ground 在当前 bridge 里起到了一个 stabilizing compensation 的作用，而 fully PhysTwin-style pair 反而把剩下的 whole-step mismatch 暴露出来了。
第三，所以 recommendation 不变，仍然是 C，也就是 bridge-side PhysTwin-style self-collision is necessary。
现在没有被解决掉的，不是 isolated self-collision operator，而是更上层的 rollout interaction，尤其 controller-spring semantics。

## Slide 10 — Robot R1: Best Meeting Visual Is The Honest Visible-Tool Baseline
这一页我先放这周最适合上会的 visual result。
它不是 direct-finger claim，而是更保守、更直观的 visible-tool baseline：native Franka 挂一个可见 short rod，这根 rod 本身就是实际接触体。
这里我把 hero 和 validation 放成同一条 rollout 的双视角，左边更适合 presentation，右边更适合确认 contact story。
这个结果的好处很直接：tool first contact 是清楚的，`1.73` 秒先接触，rope 的 lateral motion 和 deformation 都更晚，所以不会给人 remote push 的感觉。
所以如果周三现场只需要一条最容易被接受的 robot visual，我会优先停这一页，而且我会明确说它是 tool-mediated one-way baseline，不是更强的 blocking physics claim。

## Slide 11 — Robot R2: The Promoted Direct-Finger Path Stays Conservative
这一页再把 currently promoted 的 direct-finger path 摆出来。
我保留这页的原因不是因为它比 visible-tool 更好看，而是因为它对应的是当前被重新认证过的 conservative authority。
这里同样是 same-rollout 双视角，而且 proof surface 仍然是 actual finger-box contact。也就是说，`1.67` 秒才算真正接触，之后 rope deformation 和 lateral motion 才开始。
这页要讲清楚两点：第一，deformable interaction 是 `SolverSemiImplicit`；第二，这不是 full two-way，也不是 physical blocking。
所以周三如果老师追问当前 direct-finger claim 到底站到哪里，这页就是最安全的答案。
