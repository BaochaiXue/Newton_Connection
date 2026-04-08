# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：opening + recall + performance profiling + self-collision update + robot baseline  
结构：1. opening  2. recall  3. rope performance profiling  4. stable self-collision diagnosis  5. conservative robot SemiImplicit baseline  
目标：给 `2026-04-08` meeting 保留 recall baseline，同时把当前 rope performance、stable self-collision 和 conservative robot result 放回同一套可 defend 的 deck。  

---

## Slide 1 — PhysTwin -> Newton Bridge
这一页是 opening slide。
我会把这次 meeting 强行压成四段：recall，performance profiling，stable self-collision diagnosis，和 conservative robot baseline。
这样做的目的是避免所有结果混在一起，导致听众既抓不到当前最强结论，也分不清哪些事情仍然没有做到。

## Slide 2 — Agenda: Keep Four Claims Separate
这一页是全场最重要的 scope slide。
我先把四件事拆开：第一，bridge baseline 已经存在；第二，rope performance 现在仍然是 replay-organization question；第三，self-collision 现在是 mechanism question；第四，robot 结果现在只讲 conservative one-way baseline。
如果这一页不先说清楚，后面所有 visual 都会被误读得更强。

## Slide 3 — Recall: The Bridge Baseline Already Exists
这一页只做一件事：提醒听众 bridge baseline 不是本周才第一次成立。
cloth、zebra、sloth、rope 这四个 import 都已经是 earlier meeting 的 established baseline。
所以从这里开始，我们讨论的不是『能不能 import deformable』，而是 import 之后剩下哪些 narrower failure modes。

## Slide 4 — Recall: The Remaining Issue Is Contact Behavior, Not Import
同样是 rigid support，换成 thick box 以后现象就明显更稳定，所以问题不是 bridge 连 contact baseline 都没有。
这个对比把问题收窄到 geometry-sensitive contact behavior。
所以 recall 的作用已经够了：后面不再需要继续证明 import，而是直接进入本周的 narrowed diagnosis。

## Slide 5 — Performance: The Committed Rope Benchmark Still Sets The Main Gap
这一页先把 committed rope benchmark 的主数字重新摆出来，因为 04-08 这次也不能把 profiling 整段丢掉。
核心 benchmark 还是同一个 `rope_double_hand`、同一条 controller trajectory、同样的 `dt` 和 `667` 个 substeps。
先看 practical row：当前 visible viewer E1 大约是 `37.85 FPS`，`RTF` 是 `1.262x`，所以 practical viewer 已经能跑。
但 apples-to-apples rows 还是同一个结论：Newton A0 是 `0.066934 ms/substep`，Newton A1 是 `0.035721 ms/substep`，PhysTwin B0 是 `0.010840 ms/substep`。
所以最重要的人话结论没有变：即使换成更轻的 A1 replay path，Newton 还是比 PhysTwin B0 慢大约 `3.30x`。
也就是说，这一段 profiling 不该被理解成『viewer 已经能跑，所以 performance story 结束了』。viewer 能跑是一回事，same-case rope replay 还差多少 headroom 是另一回事。

## Slide 6 — Performance: Latest One-To-One Rope Matchup Preserves The Same Story
这一页再用最新 one-to-one rope cross-check 把 story 讲具体一点。
它还是同一个 rope case，只是这次我们把 Newton 和 PhysTwin 的操作按语义重新对齐，方便回答『rope case 还慢在哪些阶段』。
throughput anchor 先不变：Newton A0 是 `0.067757 ms/substep`，Newton A1 是 `0.036062 ms/substep`，PhysTwin 是 `0.010175 ms/substep`。
controller upload 这一行说明 replay feeding tax 在 rope 上是真实存在的，但 collision candidate generation 这一行三边都是 `n/a`，所以 rope case 不是 cloth 那种 collision-generation 主导的故事。
反过来，真正持续偏重的是 integration plus drag 这一桶，再加上 Newton 保留的更重 solver/runtime shell。
所以这页最后只服务一个判断：rope performance 的 remaining gap 更像 replay organization 之外的 broader solver shell，而不是 collision bottleneck。

## Slide 7 — Performance: Optimize Replay Organization Before Render Tuning
这一页只收 performance 的 actionable takeaway。
第一，A0 到 A1 已经省了大约 `1.87x`，所以 replay organization 确实重要。
第二，viewer ON 相对同 replay 的 render OFF 只慢大约 `1.11x`，所以 rope case 上 render tuning 不是第一优先级。
第三，latest one-to-one grouped matchup 又说明 rope 这里不是 collision-generation bottleneck。
所以更实际的工程结论还是不变：如果要给 viewer 再争取 headroom，先看 replay organization 和 broader solver shell，而不是先花时间在 render tuning 上。

## Slide 8 — Self-Collision: Stable 2x2 RMSE Matrix
这一页先只放稳定的 `2 x 2` RMSE matrix，让听众先看到数，不先讲解释。
这四组现在已经是同一提交、同一环境下稳定可复现的结果。
最重要的 reading 只有两句：第一，best full-rollout pair 仍然是 case 3；第二，fully PhysTwin-style pair 也就是 case 4 反而不是最优。

## Slide 9 — Self-Collision: Stable 2x3 Compare For Case 3 And Case 4
这一页现在用的是和之前 slides 里一致的 `2x3` compare 格式。
也就是说，每一边都不是单 camera clip，而是同一个 case 的三视角 compare：上排是 Newton Bridge rollout，下排是 PhysTwin reference rollout。
左边是 case 3，右边是 case 4，唯一差别仍然是 ground-contact law。
这样老师不需要脑补 reference，因为每个 case 自己就带着 reference row，所以 case 3 和 case 4 的误差表现会更直观。

## Slide 10 — Self-Collision: Native Newton Ground And PhysTwin-Style Ground Are Different Update Laws
这一页的目标是把 ground law 的源码差异直接摆出来，而且一眼能看懂。
左边 Newton native path 在 solver 里先累计 contact force，然后再 integrate particles，所以它是 force-space spring-damper contact。
右边 bridge strict PhysTwin-style path则是先 `update_vel_from_force_phystwin`，再做 PhysTwin-style self-collision，最后做 `integrate_ground_collision_phystwin`，也就是 velocity-level TOI update。
所以 case 3 和 case 4 的差异从源码上就不是一个小参数差异，而是整个 update law 不同。

## Slide 11 — Self-Collision: Controller Semantics Are Still Not PhysTwin-Native
这一页讲 current strongest mismatch。
PhysTwin 原版 spring law 会区分 object state 和 controller channel：如果弹簧端点连到 controller，它直接读 `control_x` 和 `control_v`。
但我们当前 bridge rollout 是先把 controller target 写进 `state_in.particle_q` 和 `state_in.particle_qd`，再让 spring path继续往下跑。
这两个 runtime semantics 不同，所以即使 isolated self-collision operator 已经很强，whole-step rollout 里仍然会留下 controller-spring mismatch。

## Slide 12 — Self-Collision: What We Can Say Today
这一页只做结论收口。
第一，stable matrix 已经证明 case 3 比 case 4 更好这个排序是真的。
第二，但这个 stable result 不能被误读成 native Newton ground-contact 更 PhysTwin-faithful。我们现在更支持的解释是 native ground 在当前 bridge 里起到了 stabilizing compensation 的作用，而 fully PhysTwin-style pair 暴露了更上层的 mismatch。
第三，所以 recommendation 不变，仍然是 C：bridge-side PhysTwin-style self-collision 还是必要的。
真正没解决掉的，是 rollout-level whole-step interaction，尤其 controller-spring semantics。

## Slide 13 — Robot: This Week's Claim Is Intentionally Narrow
进入 robot section 之前，我先把 claim boundary 再说一遍。
这周 robot 结果的目标不是 articulated physical blocking，也不是 full two-way coupling。
我们现在只 claim 一件事：native Franka 在 native tabletop scene 里，通过 `SolverSemiImplicit` 下的 deformable rope interaction，给出一个 truthful one-way robot-to-rope baseline。
这一页是为了避免后面所有 robot visual 被误听成更强的 physics claim。

## Slide 14 — Robot: Main Demo Is Now The Direct-Finger Baseline
这一页现在改成 direct-finger 主展示页。
也就是说，主线里不再放 visible-tool 那条带红色 short rod 的 clip，而是直接用 robot 手指本体去接触 rope 的 conservative baseline。
这里我把 hero 和 validation 放成同一条 rollout 的双视角，左边更适合 presentation，右边更适合确认 contact story。
这里的 proof surface 仍然是 actual finger-box contact。也就是说，`1.67` 秒才算真正接触，之后 rope deformation 和 lateral motion 才开始。
所以这页的主要价值是：画面里不再有额外工具杆子，同时 claim 依然保持保守，不会被误听成 physical blocking 或 full two-way coupling。

## Slide 15 — Robot: Why The Visible-Tool Baseline Is No Longer In The Main Deck
这一页只解释一个换页决策：为什么我把 visible-tool 从主线里拿掉了。
答案不是因为它不 honest。它仍然是 honest baseline，而且 contact readability 其实更直接。
但因为画面里会多出一根 short rod，周三主线更容易被听众误以为我们还在靠额外工具做展示。
所以这次 deck 里我把它降成 backup，不再占主展示位。

## Slide 16 — Close: What Is Ready For Wednesday
最后一页只做收尾，不加新信息。
如果周三只记住四句话，我希望就是这四条：bridge baseline 不是 open question；self-collision 的 stable ranking 已经拿到了；robot 主线现在展示 direct-finger conservative baseline；visible-tool 只作为 backup。
这样整场汇报的边界就很清楚：我们有真实进展，但没有 overclaim 到 physical blocking 或 full two-way coupling。
