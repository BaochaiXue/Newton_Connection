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

## Slide 11 — H4: Controller-Write Overhead Is Real, But Not The Whole Gap
这一页回答 Q2 的第一半：controller-write overhead 到底有多真，以及它是不是全部解释。
A0 到 A1 的 speedup 是 `1.874x`，这说明 baseline path 里每个 substep 反复做 controller interpolation、target assign 和 state write 的开销是真实存在的。
但这不是全部，因为 Newton A3 里这部分开销只有 `0.037 ms/substep`，而在把它降下来以后，post-write residual 仍然有 `0.081 ms/substep`。
同一张表里 collision bucket 只有 `0.004 ms/substep`，而且这个 baseline 本身就是 weak-contact rope replay，所以 collision-first explanation 在这里不够强。
所以这一页要传达的不是一个模糊术语，而是一个直接句子：controller-write overhead 真实存在，但它解释不了全部 slowdown。

## Slide 12 — Source Proof P2: Newton Still Executes The Replay As Many Solver Stages
这一页先把 Newton 侧剩余 gap 的证据单独讲清楚，不和 PhysTwin graph 证据混在一页里。

[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]
左边这段 Newton core 代码最重要的信息其实很简单：rope replay 不是一口气走完的，而是要一段一段地走 solver stages。
它会先后经过 spring、triangle、bending、tetra、contact，最后才 integrate particles。换句话说，当前 replay path 更像很多小步骤依次推进，而不是一次性回放完一整步。
这页右边再把实验和 Nsight 摆在一起看：A3 里 controller-write overhead 已经被压下去了，但 residual 还在；同时 Newton A1 的 CUDA API 时间里，`77.2%` 还是 `cuLaunchKernel`。
所以这一页真正想说的不是『已经证明就是某一个唯一原因』，而是更收敛的一句话：在 Newton 这一侧，剩余 slowdown 更像很多分开的 solver step 和 launch 继续存在，而不是 collision 还在主导。
这里也必须留一个风险提示：这只能说明方向更像运行组织方式的问题，不能单独给出精确归因比例。

## Slide 13 — Source Proof P3: PhysTwin Replays The Rope Case Through One Captured Graph Path
这一页再补 PhysTwin 侧，这样『为什么更像 execution / launch structure』就不是单边推断，而是两边证据对齐。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 768-782, 800-802]
PhysTwin 这段源码就更直接了：只要 `cfg.use_graph` 打开，它就会 capture `self.step()`，而且还专门保留一个 `forward_graph` 给前向 replay。
所以这里不是我们在外面套了一个 benchmark 技巧，而是 PhysTwin rope core 自己就把这条 replay path 做成了 graph path。
右边的系统证据把这件事闭合起来：B0 throughput summary 里写了 `use_graph = true`，而 Nsight 又显示 PhysTwin B0 的 CUDA API 时间里有 `92.6%` 是 `cudaGraphLaunch_v10000`。
因此这页的说服力来自三件事是一致的：实验是 clean rope replay，源码里真的有 core graph path，运行时也真的主要在 graph replay。
这里同样要诚实：这仍然不能推出『Newton 只差一个 graph 就一定追平』；但它足以支持更稳的判断，PhysTwin 这一侧的快路径确实带有明确的 graph-replay 特征。

## Slide 14 — Conclusion: Newton Still Launches Many Small Steps, While PhysTwin Replays A Graph
这一页只讲一句最直接的话：为什么我们现在更怀疑 launch organization，而不是 collision。
实验先给出第一层事实：在同一个 clean rope replay 上，Newton A1 还是比 PhysTwin B0 慢大约 `3.30x`。
A0 到 A1 再给出第二层事实：把 controller-write overhead 降下来以后，速度确实会变好，但大的差距并没有消失。
然后源码和 Nsight 再把最后一层补上：Newton 这边还是很多分阶段的小 step 和小 launch；PhysTwin 那边则是明确的 graph replay path，而且运行时也确实主要在 graph launch。
所以这页真正的结论不是一个抽象词，而是一句人话：Newton 现在更像是在一小步一小步地发很多 launch，PhysTwin 更像是在回放一张已经 capture 好的 graph。
也正因为这样，下一步最合理的优化方向才不是先调 collision，而是先研究能不能把 Newton rope replay 做得更 graph-like、或者至少更 batched。

## Slide 15 — Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism
这里开始进入第三段 penetration analysis。
这一页先把新的 hypothesis 说清楚。
教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。
真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。
所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。

## Slide 16 — Result F1: Global Phenomenon Videos Now Cover The Whole Penetration Process
这一页只讲 phenomenon，不讲 force。
现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。
从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。
也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。

## Slide 17 — Result F2: Split Single-Panel Videos Now Match The Current 2x2 Board
这一页现在不再放旧的四个历史 force mechanism 视频了。
这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
现在 F2 里的四个单视频，都是直接从当前 canonical `2 x 2` board 裁出来的单面板。
也就是说，这一页只负责把四个 panel 单独放大给老师看：box penalty、box total、bunny penalty、bunny total。
这样 F2 和下一页 F3 就不会再出现“这一页还是旧结果、下一页才是新结果”的割裂了。

## Slide 18 — Result F3: The New 2x2 Board Makes The Box-vs-Bunny Comparison Immediate
这一页就是新的 `2 x 2` board video，我把它直接放进 PPT 里了。
这里必须把实验设定写明：self-collision 是 OFF，cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
它的结构非常直接：左上是 box penalty，右上是 box total，左下是 bunny penalty，右下是 bunny total。
所以这一页的价值不是再讲一个局部 mechanism patch，而是把 box versus bunny、penalty versus total 这两个对比同时压进一个 meeting-readable clip。
如果现场只想停一页讲 penetration，我现在会优先停这一页，因为它最接近老师要的最终 visual comparison。

## Slide 19 — Result F4: A 4x Slow-Motion Board Makes Contact Development Easier To Read
这一页是 F3 的补充版本，不改实验设定，只改播放节奏。
也就是说，self-collision 还是 OFF，cloth total mass 还是 0.1 kg，rigid target mass 还是 0.5 kg。
这里放的是同一套 `2 x 2` board，但是视频整体放慢四倍，而且每个 panel 里都显式写了 `4x slow motion`。
这页的作用不是替代正常速度版本，而是让老师在会议里更容易看清 pre-contact、first contact 和 penetration growth 的过渡。

## Slide 20 — Strict `phystwin` = The In-Scope Cloth Reference Mode
这里开始进入第四段 self-collision, Newton way。
这一页先把 target scene 说清楚，避免把不在 scope 里的 scene 混进 strict parity。
现在我们只 claim PhysTwin 原生 cloth contact scope，也就是 pairwise self-collision 加 implicit z 等于零 ground plane。
这条实现完全在 bridge 层，没有改 Newton core，而且 parity validator 也是围绕这条 cloth reference path 组织的。
所以这一页的 take-home message 很简单：strict phystwin 只针对 in-scope cloth reference case。

## Slide 21 — Code Compare A: What Is Already Matched
第二页直接拿代码对代码，不再用抽象名词。
左边是 PhysTwin 原生的 `object_collision` 和 `integrate_ground_collision`，右边是我们 bridge 里的 strict phystwin 对应实现。
这页要说的结论很窄但很重要：strict scope 里的 self-collision law 和 ground contact law 已经对齐到 operator level。
所以 blocked parity 现在不应该再被描述成 self-collision 或 ground law 本身还没抄对。

## Slide 22 — Code Compare B: Collision Table Still Uses A Different Runtime Path
第三页继续只看代码，而且只看 collision table 这一个点。
左边是 PhysTwin 原版：每帧先 build collision graph，再填 `collision_indices / collision_number`，整帧 substeps 复用这张表。
右边是我们当前 strict phystwin：生命周期已经同步成 per-frame frozen table，但这张表还是 bridge runtime 自己重建的。
所以这页的结论是：collision table 这边已经更像 PhysTwin 了，但 provenance 和 runtime 语义还没有完全一样。

## Slide 23 — Code Compare C: Controller Handling Still Differs
第四页还是代码对代码，但这次看 controller handling。
左边 PhysTwin 的 spring path 直接吃 `control_x / control_v`；右边我们当前 bridge 还是把 controller 点写进 Newton particle state 里。
这也是为什么 current status 现在把 controller-spring diagnostic 当成下一阶段最像 blocker 的信号。
所以这页的结论是：如果还要继续压 full-rollout parity，这一层比继续纠缠 self-collision law 更值得先改。

## Slide 24 — Full-Rollout A/B: Strict `phystwin` Is Still Not Better Than OFF
最后一页只看 in-scope cloth reference case 的 full-rollout A/B，不再混 box scene。
右边是最新 302-frame parity support video，左边的表直接列 OFF 和 strict phystwin 的 full-rollout 数字。
现在 strict phystwin 只在前 30 帧更好，但 full-rollout 的 rmse_mean 还没有低于 OFF。
同时我们也把短窗口 improvement 和 controller-spring diagnostic 放进这一页的 note 里，所以这页已经足够把 blocker 讲完整。
所以这一页的 take-home message 很直接：当前 strict phystwin 还没有通过 full-rollout A/B gate。

## Slide 25 — Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
