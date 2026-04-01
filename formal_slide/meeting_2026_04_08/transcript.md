# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：opening + recall-only initial draft  
结构：1. opening  2. recall  
目标：给 `2026-04-08` meeting 建立第一版 recall scaffold  

---

## Slide 1 — Xinjie Zhang
这一页是 `2026-04-08` meeting 的 opening page。
当前 bundle 只先建立 recall part，不提前假装后面的新结果已经定稿。
所以 opening 要做的只有一件事：把这次 recall 的边界讲清楚，也就是先把已经建立的 baseline 和已经收窄的问题重新摆稳。

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
