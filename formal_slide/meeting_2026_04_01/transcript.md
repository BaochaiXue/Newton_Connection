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

## Slide 8 — Hypothesis P1: Fair Benchmark Before Optimization
这里开始进入第二段 performance analysis。
这一页现在只保留 hypothesis 和 benchmark contract，本来放在 slide 上的很多解释都移回 transcript。
左边这个 GIF 只是 visual anchor，提醒老师后面所有 profiling 数字对应的是同一个 `rope_double_hand` replay case，而不是另一个 playground scene。
真正的 speed claim 不是从 GIF 看出来的，而是从 no-render benchmark 里算出来的。
这里最重要的 methodological point 只有四个：same case、same controller trajectory、same `dt/substeps`、same GPU，而且主比较必须把 rendering 排除掉。
所以这次 profiling section 的逻辑固定成两步：先用 Newton A0、Newton A1、PhysTwin B0 回答谁快谁慢；再用 A2、A3、B1 和 Nsight 解释为什么慢。
这样做是为了避免把 attribution 模式自己的同步开销误当成真实吞吐，也避免把不公平的 GUI path 混进主表。
另外 same-case identity 不是口头假设，而是已经检查到 PhysTwin controller trajectory 和 IR 的 max abs diff 是 0.0e+00，所以 benchmark 的输入本身是对上的。

## Slide 9 — Source Proof P1: Same Replay, Different Execution Style
这一页我按你的反馈改成了真正有意义的 upstream source proof，不再引用我们自己写的 wrapper CLI。
左边现在引用的是 Newton core 里的 `asv/benchmarks/benchmark_mujoco.py`。它同时保留了三件关键事情：`if self.use_cuda_graph`、`with wp.ScopedCapture()`、以及 fallback 的 `for sim_substeps -> solver.step -> self.simulate()` 路径。
这段代码的作用不是说 rope benchmark 就是跑这个 benchmark 文件，而是说明 Newton upstream 自己就已经有一套 graph-capture execution idiom；如果不用这条 idiom，默认结构仍然像 repeated substep loop。
右边保留的是 PhysTwin `spring_mass_warp.py` 里的 upstream source code，而且只保留 `cfg.use_graph`、`ScopedCapture`、`self.graph`、`self.forward_graph` 这些最能说明 execution style 的行。
所以这页真正要证明的不是我们的 wrapper 参数，而是 upstream code 层面上，两边对 graph replay 的组织方式本来就不同；这才是后面 Nsight interpretation 的源码背景。

## Slide 10 — Result P1: A1 Is Still 3.30x Slower Than B0
这一页保留 table，因为这里的核心就是一个 bounded benchmark result。
我把 slide note 压短了，只保留同 case、no render、RTX 4090 这三个最重要的 reading keys；更细的 methodology 现在都回到 transcript。
完整 rope replay 现在已经做成 same-case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。
authoritative 数字很直接：Newton A0 `0.066934 ms/substep`，Newton A1 `0.035721 ms/substep`，PhysTwin B0 `0.010840 ms/substep`。
所以这里的结论仍然不变：即使把 controller bridge tax 降下去，Newton 在 clean rope replay 上仍然比 PhysTwin 慢 `3.295x`。
这一页不再重复太多 caveat，因为 fairness caveat 已经在前两页讲完了。

## Slide 11 — Conclusion P2: Bridge Tax Exists, But Collision Is Still Tiny
这一页不再用数据图，而是只保留 progress statement。
首先 H1 还是一样硬：A0 到 A1 是 `1.874x` 的提升，所以 controller bridge tax 是真实存在的。
但 bridge tax 不是全部。Newton A3 的 precomputed attribution 里，bridge 是 `0.037 ms/substep`，internal force `0.025`，integration `0.025`，collision 只有 `0.004`，还剩 `0.031` 的 runtime overhead。
右边的 PhysTwin B1 frame-level attribution 则说明它的大头基本就是 simulator launch，本身大约 `6.601 ms/frame`；controller target `0.254` 和 state reset `0.438` 都是小头。
所以这一页的真正 point 还是结构：bridge tax 确实存在，但 clean rope replay 的 remaining gap 不是 collision story。

## Slide 12 — Conclusion P3: The Residual Gap Still Looks Like Launch Structure
这一页也不再用数据图，只保留最终解释。
Newton A1 的 CUDA API 时间里，`cuLaunchKernel` 占到 77.2%，其余主要是 `cudaMemsetAsync` 21.5%。这说明 Newton replay 仍然像 many decoupled launches。
PhysTwin B0 的 CUDA API 时间里，92.6% 是 `cudaGraphLaunch`，`cuCtxSynchronize` 只有 2.9%。所以它不是 GUI path，而是 graph-captured replay execution style。
这页真正要堵住的反驳是：如果 residual gap 主要来自 collision，Nsight 不会长成现在这样；现在它长成了 launch structure 的样子。
因此 optimization implication 保持不变：先保留 precomputed writes，再优先研究更 graph-like 或更 batched 的 Newton replay，弱接触 rope profiling 继续独立处理。

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

## Slide 17 — Hypothesis S1: Native Newton Is Not Enough For The Final Self-Collision Claim
这里开始进入第四段 self-collision, Newton way。
这一章不再用静态 campaign board 讲，而是收成一个 hypothesis-driven block。
这一页先把 hypothesis 说清楚：如果 native Newton 已经足够，我们就不需要 bridge-side phystwin 这条更窄的 exact path。
同时 claim boundary 也要收紧：strict parity 只针对 PhysTwin 原生定义的 cloth self-collision 加 implicit ground，不把 box-support semantics 混进 exact claim 里。
当前 progress 也要一句话说死：operator exactness 已经过，但 rollout parity 仍然 blocked。

## Slide 18 — Source Proof S1: PhysTwin Native Contact Scope Is Pairwise Self-Collision + Ground
这一页只用 PhysTwin upstream source 来证明 strict parity 的 scope，不再 cite 我们自己的 bridge code。
左边这段是 `object_collision`，说明 PhysTwin 原生的 cloth contact 里有 pairwise object self-collision，而且速度修正是基于 collision impulse average。
右边这段是 `integrate_ground_collision`，说明 PhysTwin 原生还定义了 implicit ground-plane TOI 和 velocity update。
所以 strict parity 的 claim boundary 不是拍脑袋收窄，而是直接从 PhysTwin native contact source 推出来的：object self-collision 加 ground collision。
也正因为这个 source scope，本章后面的 cloth+box scene 只能作为 decision/demo evidence，不能被包装成 strict parity scene。

## Slide 19 — Result S1: Native Is Not Enough On The Controlled Cloth+Box Scene
这一页是 scene-level video evidence，不是源码页。
这里直接放 controlled cloth+box decision videos：OFF、native、custom H2、phystwin。
这页要回答的 hypothesis 很窄：native 能不能直接承担 final self-collision claim。
目前 answer 仍然是否定的。能继续 defend 下去的是 bridge-side phystwin candidate，而不是 native。
所以这页的 progress 不是“所有问题都 solved”，而是 decision scene 已经把 native 不足这件事视频化、可比较化了。

## Slide 20 — Progress S2: The Demo Is Ready, But Strict Parity Is Still Blocked
最后这一页把当前 self-collision progress 和 blocker 同时讲清楚。
左边是已经可汇报的 cloth+box `phystwin` hero demo，它通过了 black/blank、motion 和 scene-visibility 的 QC，所以 video claim 已经成立。
右边是 parity support video，用来提醒老师：strict parity 的 in-scope reference path 仍然在，而且我们不是拿错 scene 在讲 parity。
同时 exactness 本身也已经过了，`max_abs_dv` 在 1e-6 量级、`median_rel_dv` 在 1e-8 量级。
但 full rollout parity 仍然停在 1e-2 量级，所以当前 honest progress 应该讲成：demo-ready yes，operator exact yes，strict rollout parity not yet。

## Slide 21 — Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
