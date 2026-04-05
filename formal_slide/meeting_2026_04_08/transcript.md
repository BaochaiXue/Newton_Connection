# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：opening + recall + self-collision update + robot baseline  
结构：1. opening  2. recall  3. stable self-collision diagnosis  4. conservative robot SemiImplicit baseline  
目标：给 `2026-04-08` meeting 保留 recall baseline，并补上本周最稳妥的 robot visual result。  

---

## Slide 1 — PhysTwin -> Newton Bridge
这一页是 opening slide。
我会把这次 meeting 强行压成三段：recall，stable self-collision diagnosis，和 conservative robot baseline。
这样做的目的是避免所有结果混在一起，导致听众既抓不到当前最强结论，也分不清哪些事情仍然没有做到。

## Slide 2 — Agenda: Keep Four Claims Separate
这一页是全场最重要的 scope slide。
我先把四件事拆开：第一，bridge baseline 已经存在；第二，self-collision 现在是 mechanism question；第三，robot 结果现在只讲 conservative one-way baseline；第四，physical blocking、full two-way coupling 和 self-collision parity 今天都不 claim。
如果这一页不先说清楚，后面所有 visual 都会被误读得更强。

## Slide 3 — Recall: The Bridge Baseline Already Exists
这一页只做一件事：提醒听众 bridge baseline 不是本周才第一次成立。
cloth、zebra、sloth、rope 这四个 import 都已经是 earlier meeting 的 established baseline。
所以从这里开始，我们讨论的不是『能不能 import deformable』，而是 import 之后剩下哪些 narrower failure modes。

## Slide 4 — Recall: The Remaining Issue Is Contact Behavior, Not Import
同样是 rigid support，换成 thick box 以后现象就明显更稳定，所以问题不是 bridge 连 contact baseline 都没有。
这个对比把问题收窄到 geometry-sensitive contact behavior。
所以 recall 的作用已经够了：后面不再需要继续证明 import，而是直接进入本周的 narrowed diagnosis。

## Slide 5 — Self-Collision: The Case-3-Over-Case-4 Ranking Is Now Stable
这一页是本周 self-collision 章节的核心证据页。
左上角是稳定的 `2 x 2` matrix，最优 full-rollout 组合仍然是 case 3，也就是 PhysTwin-style self-collision 加 native Newton ground-contact。
右上角是 case 3 和 case 4 的 per-frame RMSE 曲线。这里最关键的不是谁最后均值更小，而是 case 4 在 early rollout 其实更好，它是在 frame 40 首次翻符号、并在 frame 107 开始进入持续更差区间。
下排把机制证据压在一张图里：左边是 frame 40、107、137 的 active ground particle 对比，右边是 self-contact active nodes 加 controller mismatch reminder。
所以这页只想传达一句话：case 4 不是因为 local self-collision law 错了才输，而是因为 fully PhysTwin-style branch 暴露了 bridge 里剩余的 whole-step mismatch。

## Slide 6 — Self-Collision: Native Newton Ground And PhysTwin-Style Ground Are Different Update Laws
这一页的目标是把 ground law 的源码差异直接摆出来，而且一眼能看懂。
左边 Newton native path 在 solver 里先累计 contact force，然后再 integrate particles，所以它是 force-space spring-damper contact。
右边 bridge strict PhysTwin-style path则是先 `update_vel_from_force_phystwin`，再做 PhysTwin-style self-collision，最后做 `integrate_ground_collision_phystwin`，也就是 velocity-level TOI update。
所以 case 3 和 case 4 的差异从源码上就不是一个小参数差异，而是整个 update law 不同。

## Slide 7 — Self-Collision: Controller Semantics Are Still Not PhysTwin-Native
这一页讲 current strongest mismatch。
PhysTwin 原版 spring law 会区分 object state 和 controller channel：如果弹簧端点连到 controller，它直接读 `control_x` 和 `control_v`。
但我们当前 bridge rollout 是先把 controller target 写进 `state_in.particle_q` 和 `state_in.particle_qd`，再让 spring path继续往下跑。
这两个 runtime semantics 不同，所以即使 isolated self-collision operator 已经很强，whole-step rollout 里仍然会留下 controller-spring mismatch。

## Slide 8 — Self-Collision: What We Can Say Today
这一页只做结论收口。
第一，stable matrix 已经证明 case 3 比 case 4 更好这个排序是真的。
第二，但这个 stable result 不能被误读成 native Newton ground-contact 更 PhysTwin-faithful。我们现在更支持的解释是 native ground 在当前 bridge 里起到了 stabilizing compensation 的作用，而 fully PhysTwin-style pair 暴露了更上层的 mismatch。
第三，所以 recommendation 不变，仍然是 C：bridge-side PhysTwin-style self-collision 还是必要的。
真正没解决掉的，是 rollout-level whole-step interaction，尤其 controller-spring semantics。

## Slide 9 — Robot: This Week's Claim Is Intentionally Narrow
进入 robot section 之前，我先把 claim boundary 再说一遍。
这周 robot 结果的目标不是 articulated physical blocking，也不是 full two-way coupling。
我们现在只 claim 一件事：native Franka 在 native tabletop scene 里，通过 `SolverSemiImplicit` 下的 deformable rope interaction，给出一个 truthful one-way robot-to-rope baseline。
这一页是为了避免后面所有 robot visual 被误听成更强的 physics claim。

## Slide 10 — Robot: Best Meeting Visual Is The Honest Visible-Tool Baseline
这一页我先放这周最适合上会的 visual result。
它不是 direct-finger claim，而是更保守、更直观的 visible-tool baseline：native Franka 挂一个可见 short rod，这根 rod 本身就是实际接触体。
这里我把 hero 和 validation 放成同一条 rollout 的双视角，左边更适合 presentation，右边更适合确认 contact story。
这个结果的好处很直接：tool first contact 是清楚的，`1.73` 秒先接触，rope 的 lateral motion 和 deformation 都更晚，所以不会给人 remote push 的感觉。
所以如果周三现场只需要一条最容易被接受的 robot visual，我会优先停这一页，而且我会明确说它是 tool-mediated one-way baseline，不是更强的 blocking physics claim。

## Slide 11 — Robot: The Promoted Direct-Finger Result Still Matters
这一页再把 currently promoted 的 direct-finger path 摆出来。
我保留这页的原因不是因为它比 visible-tool 更好看，而是因为它对应的是当前被重新认证过的 conservative authority。
这里同样是 same-rollout 双视角，而且 proof surface 仍然是 actual finger-box contact。也就是说，`1.67` 秒才算真正接触，之后 rope deformation 和 lateral motion 才开始。
这页要讲清楚两点：第一，deformable interaction 是 `SolverSemiImplicit`；第二，这不是 full two-way，也不是 physical blocking。
所以周三如果老师追问当前 direct-finger claim 到底站到哪里，这页就是最安全的答案。

## Slide 12 — Close: What Is Ready For Wednesday
最后一页只做收尾，不加新信息。
如果周三只记住四句话，我希望就是这四条：bridge baseline 不是 open question；self-collision 的 stable ranking 已经拿到了；最适合上会的 robot visual 是 honest visible-tool baseline；而 direct-finger 这条 conservative authority 也已经被重新认证。
这样整场汇报的边界就很清楚：我们有真实进展，但没有 overclaim 到 physical blocking 或 full two-way coupling。
