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

## Slide 2 — Recall 1: Earlier Bridge Baseline Already Worked
第一页 recall 压成一张图就够了。
cloth、zebra、sloth、rope 这四条 baseline 不是今天新证明的内容。
这页的作用只是提醒老师：PhysTwin object import into Newton 这条大主线，上周已经建立了。

## Slide 3 — Recall 2: Earlier Bridge Baseline Also Matched The Reference Motion
第二页 recall 继续只做 visual reminder。
上周不只是说“大概像”，而是已经把这些 baseline case 做成了更直接的 motion overlay 对照。
所以现在不是 bridge baseline 还没站住，而是 baseline 已经站住以后继续收窄问题。

## Slide 4 — Recall 3: Bunny+Rope Already Showed Deformable-Rigid Interaction
这一页只回忆一件事：novel rigid bunny interaction 早就不是空想，而是已经能工作。
所以这周的讨论，不再是“能不能 interact”，而是“interaction 已经有了以后，还剩下哪些真正的问题”。

## Slide 5 — Recall 4: Weight Changes Already Preserved Interaction
这一页 recall 上周的 weight compare。
它的作用不是再讲参数，而是提醒老师：weight 改了以后，interaction 仍然在。
所以后面 bunny penetration 的问题，不应该被讲成“bridge 根本没有 interaction”。

## Slide 6 — Recall 5: Bunny Was Harder Than Thick Box
这一页 recall 的作用很直接。
同样是 rigid support，换成 thick box 就明显更稳定。
所以上周真正被收窄出来的问题，是 bunny local geometry 和 support patch，不是 bridge 连 contact 都没有。

## Slide 7 — Recall 6: Radius Helped, But Thin Geometry Still Survived
最后一页 recall 只保留最后一个最难反驳的 visual point。
radius 变大确实会帮忙，但 thin-ear geometry 仍然会留下 penetration。
所以这周应该从一个更窄、更清楚的 baseline 继续往下做，而不是重新回去证明 bridge baseline。

## Slide 8 — Method: Fair Rope Benchmark Before Optimization
这里开始进入第二段 performance analysis。
这一页先把 hypothesis 改成教授要的版本。
不是先讲优化，而是先把比较做公平。也就是同一个 rope case、同一条 controller trajectory、同一个 dt、同一个 substeps、同一张 GPU，而且主比较必须把 rendering 排除掉。
所以这次 profiling section 的逻辑很硬：先用 Newton A0、Newton A1、PhysTwin B0 回答谁快谁慢；再用 A2、A3、B1 解释为什么慢。
这样做是为了避免把 attribution 模式自己的同步开销误当成真实吞吐，也避免把不公平的 GUI path 混进主表。
另外 same-case identity 这次不是口头假设，而是已经检查到 PhysTwin controller trajectory 和 IR 的 max abs diff 是 0.0e+00，所以 benchmark 的输入本身是对上的。

## Slide 9 — Source Proof: Same Replay, Different Execution Style
这一页是 source proof，不是结果页。
左边说明 Newton 这条 rope benchmark 本身已经把 no-render throughput、attribution，以及 baseline versus precomputed controller-write mode 显式做成了参数，所以 A0 到 A3 不是临时 hack，而是原生 benchmark interface。
右边说明 PhysTwin rope path 默认 `use_graph = True`，而且在 simulator 初始化时会 capture `forward_graph`。所以 B0 不是 GUI loop，而是 graph-captured replay path 的 headless timing。
这页真正要说明的是：两边不是在比不同任务，而是在比同任务下两种 execution style。这正是后面 H2 的证据基础。

## Slide 10 — Result: Newton A1 Is 3.30x Slower Than PhysTwin B0
这一页是新的主结果页，不再沿用之前那组只看 Newton 单边的旧数字。
完整 rope replay 现在已经做成同 case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。
authoritative 数字很直接：Newton A0 `0.066934 ms/substep`，Newton A1 `0.035721 ms/substep`，PhysTwin B0 `0.010840 ms/substep`。
所以这里的主结论非常清楚：即使把 controller bridge tax 降下去，Newton 在 clean rope replay 上仍然比 PhysTwin 慢 `3.295x`。这不是 viewer 污染，也不是 contact-heavy 场景误导，而是公平 baseline 本身的结果。

## Slide 11 — Result: Bridge Tax Is Real, But Not The Whole Gap
这一页把 attribution 结论真正拆开。
首先 H1 现在很硬：A0 到 A1 是 `1.874x` 的提升，所以 controller bridge tax 不是猜测，而是真实存在的。
但 bridge tax 不是全部。Newton A3 的 precomputed attribution 里，bridge 仍然有 `0.037 ms/substep`，internal force `0.025`，integration `0.025`，collision 只有 `0.004`，还剩 `0.031` 的 runtime overhead。
而 PhysTwin B1 的 frame-level attribution 说明它的大头基本就是 simulator launch 本身，大约 `6.601 ms/frame`；controller target `0.254` 和 state reset `0.438` 都是小头。
所以这页真正说服人的地方不是某一个数字，而是结构：controller bridge tax 确实存在，但 collision 几乎不占主因，残余 gap 仍然指向 runtime / execution structure。

## Slide 12 — Nsight: Residual Gap Looks Like Launch Structure
这一页再往下收一层，用 Nsight Systems 给 H2 加系统级证据。
Newton A1 的 CUDA API 时间里，`cuLaunchKernel` 占到 77.2%，GPU kernel 侧前四名分别是 spring、integrate_particles、precomputed write_kinematic_state 和 drag correction。这说明 Newton 这条 replay 路径仍然是大量 decoupled kernel launch。
PhysTwin B0 的 CUDA API 时间里，92.6% 是 `cudaGraphLaunch`，GPU kernel 主要是在 graph 里面执行 spring、velocity update、control point update 这些 kernel。也就是说，它不是完全不同的 physics，而是更像 graph-captured replay execution style。
所以这页真正的作用是堵住一个常见反驳：如果 residual gap 主要来自 collision，那 Nsight 不会长成现在这样；如果 residual gap 主要来自 execution structure，那它就会长成现在这样。
因此现在的优化路线才是有根据的：第一步保留 precomputed controller writes；第二步优先研究 Newton replay 能不能更 graph-like 或更 batched；只有这一步做完以后，再谈更细的 kernel micro-optimization。与此同时，weak-contact profiling 要继续独立处理，不要再和 pure rope baseline 混讲。

## Slide 13 — Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism
这里开始进入第三段 penetration analysis。
这一页先把新的 hypothesis 说清楚。
教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。
真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。
所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。

## Slide 14 — Source Proof: The Diagnostic Really Splits Contact Forces And Renders A Global+Local Layout
这一页是新的 source proof。
左边这段 bridge code 说明 trigger substep 不是黑盒截图，而是在同一个 substep 里把 `f_spring`、`f_internal_total` 和 `f_external_total` 明确分开。这里的 external force 不是猜的，而是 particle-body contact 之后相对于 internal path 的增量。
右边这段 render code 说明 accepted 版本没有再把主画面换成一个 contact-only camera。它保留全局主相机，在 3D scene 里直接画 world-space glyph，再加右侧 zoom panel，所以 full cloth context 和 local readability 才能同时存在。
另外 accepted 版本还把 force artifact render 单独放进 fresh helper process，所以 phenomenon video 和 force video 不会再互相污染成黑片。

## Slide 15 — Result F1: Accepted Global Phenomenon Videos Cover The Whole Penetration Story
这一页只讲 phenomenon，不讲 force。
现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。
从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。
也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。

## Slide 16 — Result F2: Accepted Force Videos Keep The Full Cloth And Still Explain The Local Contact Patch
这一页专门讲 force mechanism。
现在 accepted 的 force video 已经满足一个很关键的视觉要求：左侧主面板仍然能看到 full cloth 和 bunny，右侧 zoom panel 才负责讲 local force patch。
所以我们不再在 global story 和 local readability 之间二选一。
从这四个 case 可以直接看出，主要问题不是 outward direction 错了，而是 contact support 太弱，尤其是 bunny baseline、low inertia 和 larger scale 这三条 still point to insufficient contact magnitude。

## Slide 17 — Result F3: The Accepted 4-Case Summary Board Compresses The Meeting Story Into One Asset
最后这一页把 accepted package 压成一个 summary board。
每个 case 我都只保留了一张 phenomenon frame、一张 force frame、几项关键指标和一句 takeaway。
这样 meeting 里如果时间不够，就算只停在这一页，也能把四个 case 的区别讲清楚：box control 是 broad support patch，bunny 这几条则更像是 outward force 存在但 magnitude 不够。

## Slide 18 — Question, Claim, And Constraint: Final Self-Collision Campaign
这里开始进入第四段 self-collision, Newton way。
这一章展开成 6 页 self-collision campaign 证据块。
这一页先把 claim 说死：最终 promoted mode 是 bridge-side phystwin，而且整个 campaign 没有改 Newton core。
同时我也把当前 gate 状态讲清楚：exactness 已经过，final cloth-box demo 已经过 QC，但 strict self-collision parity 仍然被 blocker 卡住。

## Slide 19 — Source Evidence: Native Newton Semantics Are Not PhysTwin Exact
这一页是源码证据，不是实验结果。
第一段代码说明 bridge 会把 PhysTwin pairwise collision distance 映射成 Newton particle radius 语义，所以 native path 一开始就不是原封不动的 PhysTwin collision law。
第二段代码说明 cloth-box ON 场景里，off、native、custom、phystwin 四条路径是明确分开的；第三段代码说明 exact PhysTwin-style velocity correction 是 bridge-side 引入，而不是改 Newton core。
同时这里也要把边界说清楚：PhysTwin 这条 cloth spring-mass 源码原生只定义了 pairwise object_collision 和 implicit z=0 ground collision，没有 generic box-support contact。

## Slide 20 — Scene-Level Decision Matrix: Native Is Not Enough
这一页是 controlled scene-level evidence。
cloth-box matrix 的作用不是证明 phystwin 已经完美，而是证明 native 不足以直接被当成最终 claim。
所以 box scene 在这里是 scene evidence，不是 strict phystwin parity scene。
这里我只保留 cloth-box scope，不再把 bunny 或其他 scene 混进最终结论里。

## Slide 21 — Bridge-Side PhysTwin Exactness
这一页只回答一个问题：bridge-side phystwin operator 本身是不是 exact。
现在 verifier 的 strict gate 已经过：max_abs_dv 在 1e-6 量级，median_rel_dv 在 1e-8 量级。
所以我们可以把 exactness claim 说得很窄但很硬：operator-level PhysTwin collision equivalence 已经验证通过。

## Slide 22 — Final Demo: Cloth + Box + Self-Collision ON
这一页放最终 cloth-box phystwin hero demo。
我最后选的是 top-down presentation 视角，因为它同时保住了 cloth、box、接触区和后续 settle 过程。
但这个视频的作用是 demo evidence，不是 strict parity 的 claim scope。
这条视频已经通过 black/blank、motion 和 scene-visibility 的 QC gate，所以它是当前可以直接汇报的 self-collision ON 最终 demo。

## Slide 23 — Strict Self-Collision Parity Is Blocked By Rollout Mismatch
最后这一页专门讲最终 blocker，不粉饰。
现在 blocker 不是缺 reference，因为 cloth self-collision reference case 已经明确存在，而且我们就是拿它做的 strict parity。
这里的 strict scope 也收紧得很明确：只覆盖 PhysTwin 原生的 object_collision 加 implicit z=0 ground，不把 box scene 混进去。
真正的问题是：在当前 PhysTwin 到 Newton 的 rollout 语义下，这个 cloth case 连 self-collision off baseline 都远离 PhysTwin，所以 bridge-side phystwin operator 虽然 operator-level exact，整条 rollout 仍然达不到 1e-5 gate。

## Slide 24 — Robotic With Deformable Objects: Current Defendable Sub-Conclusion
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
