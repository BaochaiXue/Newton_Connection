# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：five-part agenda  
结构：1. recall  2. performance analysis  3. penetration analysis  4. self-collision, Newton way  5. robotic with deformable objects  
目标：让 opening framing、transcript framing 和实际 deck 章节结构完全对齐

---

## Slide 1 — Xinjie Zhang
这一页是 opening speaker page。
这次 meeting 我会按五段讲：1. recall，2. performance analysis，3. penetration analysis，4. self-collision Newton way，5. robotic with deformable objects。
所以 opening 要做的不是再把会议压成“short recall + two results”，而是先把这五段主线直接说清楚。

## Slide 2 — Recall R1: The Bridge Baseline Was Already Established
第一页 recall 压成一张图就够了。
cloth、zebra、sloth、rope 这四条 baseline 不是今天新证明的内容。
这页的作用只是提醒老师：PhysTwin object import into Newton 这条大主线，上周已经建立了。

## Slide 3 — Recall R2: The Baseline Already Matched The Reference Motion
第二页 recall 继续只做 visual reminder。
上周不只是说“大概像”，而是已经把这些 baseline case 做成了更直接的 motion overlay 对照。
所以现在不是 bridge baseline 还没站住，而是 baseline 已经站住以后继续收窄问题。

## Slide 4 — Recall R3: Deformable-Rigid Interaction Already Existed
这一页只回忆一件事：novel rigid bunny interaction 早就不是空想，而是已经能工作。
所以这周的讨论，不再是“能不能 interact”，而是“interaction 已经有了以后，还剩下哪些真正的问题”。

## Slide 5 — Recall R4: Weight Change Did Not Remove Interaction
这一页 recall 上周的 weight compare。
它的作用不是再讲参数，而是提醒老师：weight 改了以后，interaction 仍然在。
所以后面 bunny penetration 的问题，不应该被讲成“bridge 根本没有 interaction”。

## Slide 6 — Recall R5: Bunny Was Harder Than Thick Box
这一页 recall 的作用很直接。
同样是 rigid support，换成 thick box 就明显更稳定。
所以上周真正被收窄出来的问题，是 bunny local geometry 和 support patch，不是 bridge 连 contact 都没有。

## Slide 7 — Recall R6: Radius Helped, But Thin Geometry Still Survived
最后一页 recall 只保留最后一个最难反驳的 visual point。
radius 变大确实会帮忙，但 thin-ear geometry 仍然会留下 penetration。
所以这周应该从一个更窄、更清楚的 baseline 继续往下做，而不是重新回去证明 bridge baseline。

## Slide 8 — Method: Fair Rope Benchmark Before Optimization
这里开始进入第二段 rope-case performance analysis，而且这次明确只讲 rope case，不再讲 robot case。
第一张 slide 的作用不是给结论，而是先把 benchmark method 锁死：same case、same replay、same physics settings、same GPU、no render。
Newton 侧的方法学是用 realtime viewer 的同一个 rope replay 入口，但切到 `--viewer null --profile-only`，所以这一步只说明 benchmark setup，不把 wrapper 当成 core proof。
PhysTwin 侧的方法学是 same trajectory 的 headless replay。因为教授先要 apples-to-apples throughput，所以这里故意不把 GUI / Gaussian / viewer loop 混进主比较。
同 case identity 也不是口头假设：当前 committed benchmark 里，PhysTwin controller trajectory 和 IR 的 max abs diff 是 0.0e+00。

## Slide 9 — H2: Comparable Spring-Damper Rope Update Intent
这一页回答的是更基础的 H2：两边是不是至少在做可比较的 spring-damper rope update intent。

[Newton/newton/newton/_src/solvers/semi_implicit/kernels_particle.py : 27-29, 43-52]
[What | Newton]
L27-L29 先把每条边的 stiffness、damping 和 rest length 取出来，说明 Newton rope force 不是黑箱约束，而是按 edge-wise spring parameter 逐条计算。
L43-L44 用当前边向量归一化得到 `dir`，这一步把几何形变投到当前边方向上，决定了后面恢复力和阻尼力的方向。
L46-L47 同时计算 stretch `c = l - rest` 和沿边方向的相对速度 `dcdt`，也就是把弹性形变和速度阻尼拆成两个独立物理量。
L50 用 `fs = dir * (ke * c + kd * dcdt)` 把弹性项和阻尼项重新合成一个 spring-damper force，这就是 Newton rope edge 的核心力学表达。
L52-L53 把这一对 edge force 以反向方式原子加回两个端点，所以这个 kernel 的物理意义是 pairwise internal spring force assembly，而不是接触求解。
[Why | Newton]
这段代码足以支撑一个比较谨慎但重要的判断：Newton rope core 至少不是在用完全不同于 spring-damper 的奇异更新思路。
它明确是边级别的 stretch + relative-velocity damping force assembly，所以后面 benchmark 里出现的 gap，不能直接归结成“Newton 做的不是 rope spring physics”。
[Risk | Newton]
这段源码只证明 Newton core 的 rope-side force assembly intent，不能单独推出整条 replay path 与 PhysTwin 逐项完全同构，因为完整 replay 还包括积分、控制点写入和 runtime organization。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 121-132, 156-160]
[What | PhysTwin]
L121-L127 先用当前边方向 `d` 和应变 `(dis_len / rest - 1)` 写出 `spring_force`，这里 PhysTwin 同样是 edge-wise 弹簧恢复力，而不是位置投影式约束。
L129-L130 再把相对速度在边方向上的投影乘上 `dashpot_damping`，得到 `dashpot_forces`，这和 Newton 侧的 damping term 是同一类物理对象。
L132 把 spring 和 dashpot 合成 `overall_force`，说明 PhysTwin rope 主内力同样是 spring-damper force，而不是 collision-first path。
L156-L160 再把总力转成加速度，用 `v1 = v0 + a * dt` 更新速度，并在最后施加 drag 衰减，所以它仍然是 force-driven time update。
[Why | PhysTwin]
这段代码把 PhysTwin 侧的 rope update intent 讲得更直接：spring-damper internal force 加 gravity，然后按 `dt` 推速度，这和 Newton 侧至少在物理意图上是可比较的。
因此 Q1 的 apples-to-apples benchmark 可以被解释成同类 rope update path 的性能比较，而不是两套毫无关系的 physics 在碰运气。
[Risk | PhysTwin]
这里也不能过强宣称“same formula means same runtime”。代码只能支持 comparable physical intent；runtime gap 还可能来自 graph replay、launch structure、bookkeeping 和 control feed path。

## Slide 10 — Result: Newton A1 Is 3.30x Slower Than PhysTwin B0
这一页只回答 Q1，不提前解释原因。
完整 rope replay 现在已经做成 same-case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。
主结果很直接：Newton A0 是 `0.066934 ms/substep`，Newton A1 是 `0.035721 ms/substep`，PhysTwin B0 是 `0.010840 ms/substep`。
A0 和 A1 的差别只在 controller feed path，不是换了一套 rope task。
所以这页真正要让老师带走的结论只有一句：在公平 rope replay benchmark 下，Newton A1 仍然比 PhysTwin B0 慢 `3.30x`，也就是大约 `3.30x`。

## Slide 11 — H4: Bridge Tax Is Real, But It Does Not Explain The Whole Gap
这一页回答 Q2 的第一半：bridge tax 到底有多真，以及它是不是全部解释。
A0 到 A1 的 speedup 是 `1.874x`，所以 controller-write overhead 不是猜测，而是已经被同 case benchmark 直接量出来了。
但 bridge 不是全部，因为 Newton A3 里 bridge 只有 `0.037 ms/substep`，而 post-bridge residual 仍然有 `0.081 ms/substep`。
同一张表里 collision bucket 只有 `0.004 ms/substep`，而且这个 baseline 本身就是 weak-contact rope replay，所以 collision-first explanation 在这里不够强。
这一页必须故意收着讲：它支持的是『bridge tax is real, but not the whole gap』，而不是直接宣称 residual gap 已经被完全归因。

## Slide 12 — H5: The Residual Gap Looks More Like Launch Structure Than Collision
这一页回答 Q2 的第二半，也就是 residual gap 更像什么，然后才有资格回答 Q3 的优化方向。

[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]
[What | Newton]
L141-L145 说明 Newton `SolverSemiImplicit.step()` 先显式走 spring、triangle、bending、tetra 等多个力学子阶段，而不是一个已经打包好的 rope replay graph。
L160-L165 又继续串上 particle contact 和 triangle contact 相关阶段，所以这条 core step path 在组织上是明显的 multi-stage execution。
L172-L177 最后才进入 particle-shape contact 和 `integrate_particles(...)`，也就是先分段累积力，再统一做状态推进。
[Why | Newton]
这段代码本身不量化 wall time，但它确实说明 Newton rope viewer 落到的是一条分阶段的 core solver path，而不是天然 graph-replay path。
当它和 Nsight 的 `77.2% cuLaunchKernel` 一起看时，证据会更一致地指向 launch-heavy execution structure，而不是 collision 主导。
[Risk | Newton]
这里必须降 claim：Newton core 这段源码只能证明 step organization 是分阶段的，不能单独证明 residual gap 的全部比例都由 launch structure 造成。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 768-782, 800-802]
[What | PhysTwin]
L768-L782 直接表明 PhysTwin rope core 在 `cfg.use_graph` 为真时，会把 `self.step()` capture 成 CUDA graph，并把训练路径保存在 `self.graph`。
L800-L802 又额外保留了 `forward_graph`，这说明它不是只为训练准备 graph，而是连纯 forward replay 也有专门的 graph path。
[Why | PhysTwin]
这段源码是当前最强的 core evidence，因为它把 graph replay 直接写在 rope simulator 内核路径里，而不是外部 benchmark wrapper 临时包出来的技巧。
再结合 Nsight 的 `92.6% cudaGraphLaunch_v10000`，我们可以比较稳妥地说：PhysTwin 这条 rope replay 更像 graph-driven execution path。
[Risk | PhysTwin]
这里同样不能把证据说得过头。PhysTwin 有 graph replay，不等于 Newton 的全部 residual gap 就只有 graph 一个原因；更诚实的结论是『residual gap 更一致地像 execution / launch structure，而不是 collision』。

所以 Q3 的优化方向现在才成立：先保留 precomputed controller writes，再优先研究更 graph-like 或更 batched 的 Newton rope replay，而不是先冲去调 collision 参数或者改 `dt/substeps`。

## Slide 13 — Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism
这里开始进入第三段 penetration analysis。
这一页先把新的 hypothesis 说清楚。
教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。
真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。
所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。

## Slide 14 — Result F1: Global Phenomenon Videos Now Cover The Whole Penetration Process
这一页只讲 phenomenon，不讲 force。
现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。
从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。
也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。

## Slide 15 — Result F2: Split Single-Panel Videos Now Match The Current 2x2 Board
这一页现在不再放旧的四个历史 force mechanism 视频了。
这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
现在 F2 里的四个单视频，都是直接从当前 canonical `2 x 2` board 裁出来的单面板。
也就是说，这一页只负责把四个 panel 单独放大给老师看：box penalty、box total、bunny penalty、bunny total。
这样 F2 和下一页 F3 就不会再出现“这一页还是旧结果、下一页才是新结果”的割裂了。

## Slide 16 — Result F3: The New 2x2 Board Makes The Box-vs-Bunny Comparison Immediate
这一页就是新的 `2 x 2` board video，我把它直接放进 PPT 里了。
这里必须把实验设定写明：self-collision 是 OFF，cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
它的结构非常直接：左上是 box penalty，右上是 box total，左下是 bunny penalty，右下是 bunny total。
所以这一页的价值不是再讲一个局部 mechanism patch，而是把 box versus bunny、penalty versus total 这两个对比同时压进一个 meeting-readable clip。
如果现场只想停一页讲 penetration，我现在会优先停这一页，因为它最接近老师要的最终 visual comparison。

## Slide 17 — Result F4: A 4x Slow-Motion Board Makes Contact Development Easier To Read
这一页是 F3 的补充版本，不改实验设定，只改播放节奏。
也就是说，self-collision 还是 OFF，cloth total mass 还是 0.1 kg，rigid target mass 还是 0.5 kg。
这里放的是同一套 `2 x 2` board，但是视频整体放慢四倍，而且每个 panel 里都显式写了 `4x slow motion`。
这页的作用不是替代正常速度版本，而是让老师在会议里更容易看清 pre-contact、first contact 和 penetration growth 的过渡。

## Slide 18 — What Strict `phystwin` Now Means
这里开始进入第四段 self-collision, Newton way。
这一页先把 strict phystwin 的 claim boundary 说死，不让老师误会它是在 claim 一个 generic rigid-support parity mode。
现在我们只 claim PhysTwin 原生 cloth contact scope：pairwise self-collision 加 implicit z 等于零 ground plane。
这条 strict path 完全在 bridge 层实现，没有改 Newton core，而且 cloth-box phystwin 在 demo 里是故意禁止的。
所以这一页的 take-home message 很简单：strict phystwin 是 cloth reference case 的 contact-stack mode，不是通用 rigid-support parity claim。

## Slide 19 — What Is Already Matched
第二页只回答一个问题：我们到底已经 match 了什么。
shared strict bridge stack 已经存在，而且 importer 和 parity validator 也已经把它接成一条 canonical strict path。
更关键的是 operator-level exactness 已经过，所以 isolated contact operator 本身已经不是现在最好的归因对象。
同时 cloth-box phystwin 依然是故意不支持的，这也是为了不把 unsupported rigid-support semantics 混进 strict parity claim。

## Slide 20 — Where The Remaining Mismatch Likely Is
第三页不再说“还有点不一样”，而是直接把 remaining mismatch 定位到 rollout level。
现在 frozen-table 默认已经把 60-frame case 拉得更好了，但 full 302-frame rollout 还是停在 1e-2 量级。
同时 current status 里的 controller-spring diagnostic 现在已经给出一个更强的信号：下一阶段最像 blocker 的是 whole-step cloth rollout stack，尤其是 controller-spring 这一层。
所以这一页的 take-home message 是：不要再把 blocked parity 粗暴地说成 self-collision kernel 仍然错误。

## Slide 21 — Claim Boundary: What We Are NOT Claiming
第四页专门把不该 claim 的东西说出来，防止老师自动脑补成更大的 equivalence claim。
我们不 claim cloth-box phystwin parity，不 claim generic rigid-support parity，也不 claim full PhysTwin cloth solver equivalence。
我们现在只 claim那条收紧过的 strict cloth contact scope，而且 blocker doc 也明确记录了 rollout mismatch 还没有解决。
所以这一页的 purpose 就是让 meeting 里的口径 fail-closed。

## Slide 22 — Scene Evidence Only: Native Is Not Enough On The Controlled Cloth+Box Scene
这一页是 scene-level video evidence，不是源码页。
这里直接放 controlled cloth+box decision videos：OFF、native、custom H2、phystwin。
这页要回答的 hypothesis 很窄：native 能不能直接承担 final self-collision claim。
同时也要再提醒一次，这里是 scene evidence，不是 strict phystwin parity target。
目前 answer 仍然是否定的。能继续 defend 下去的是 bridge-side phystwin candidate，而不是 native。
所以这页的 progress 不是“所有问题都 solved”，而是 decision scene 已经把 native 不足这件事视频化、可比较化了。

## Slide 23 — Progress S2: Demo Ready, Operator Exact, Full-Rollout A/B Still Fails
最后这一页把当前 self-collision progress 和 blocker 同时讲清楚。
左边是已经可汇报的 cloth+box `phystwin` hero demo，它通过了 black/blank、motion 和 scene-visibility 的 QC，所以 video claim 已经成立。
右边是最新 302-frame parity support video，用来提醒老师：strict parity 的 in-scope reference path 仍然在，而且我们不是拿错 scene 在讲 parity。
同时 exactness 本身也已经过了，`max_abs_dv` 在 1e-6 量级、`median_rel_dv` 在 1e-8 量级。
但 full-rollout A/B 仍然没有过线，所以当前 honest progress 应该讲成：demo-ready yes，operator exact yes，strict rollout parity not yet。

## Slide 24 — Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
