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

## Slide 8 — H1: Why is rope profiling relevant to the real viewer?
这一页先回答第一个最实际的问题：为什么 rope profiling 值得讲，而且它和 real viewer 到底有什么关系。
这次我先做了一个新的 E1 experiment。它不是 no-render benchmark，而是同一个 `rope_double_hand`、同一条 replay trajectory、同样的 `dt` 和 `667` 个 substeps，但是把 visible `ViewerGL` render path 打开，直接量 end-to-end viewer speed。
结果先说人话：这个 rope viewer 在当前 workstation 上并没有掉到 real time 以下。E1 的 `viewer FPS` 大约是 `37.85`，`RTF` 大约是 `1.262x`。把同一条 replay 换成 render OFF 的 A1 以后，wall time 只再快了大约 `1.11x`。
所以 profiling 的价值不是证明『rope viewer 完全跑不动』，而是更准确地回答：如果这个 viewer 还需要更多 headroom，优先级到底应该放在 rendering，还是放在 simulator replay 本身。
这页的边界也要讲清楚：E1 只回答当前 rope case 的 real-viewer relation。它不代表所有更重的 contact scene 都已经没问题，也不替代后面和 PhysTwin 的 apples-to-apples benchmark。

## Slide 9 — H2: What is the controlled rope benchmark?
这一页的目的，是把实验对象讲清楚，避免听众只看到 A0、A1、B0 这些内部缩写。
这四行其实都在测同一个对象：`rope_double_hand` 这条 rope replay。区别不在任务本身，而在我们是不是打开 rendering，以及 Newton 这边怎么把同一条 replay trajectory 喂进 simulator。
Newton viewer 也就是 E1，是 visible render ON 的 end-to-end rope viewer。Newton A0 是 render OFF，但是保留 baseline controller replay path。Newton A1 还是 render OFF，不过把每个 substep 都要重复做的 replay feeding 预先展开。PhysTwin B0 则是同 case、同 trajectory、同 `dt`、同 `667` substeps 的 headless replay reference。
公平性这里不是口头假设。当前 benchmark 保存的 parity check 里，PhysTwin controller trajectory 和 IR 的 max abs diff 是 0.0e+00，所以它不是在比较两条不同的 control history。
这页对 real viewer 的意义是：一旦把这四行定义讲清楚，后面观众才能分得出哪些数字是在回答 viewer 本身，哪些数字是在回答 simulator-only benchmark。它的边界是，这里只锁定 benchmark design，不先下结论。

## Slide 10 — H3: Under the same rope replay, how far is Newton from PhysTwin?
这一页只回答数字本身，不先解释原因。
先看 practical row：E1 这个 visible rope viewer 大约是 `37.85 FPS`，`RTF` 是 `1.262x`。所以它回答的是『viewer 现在能不能跑』这个问题。
再看 apples-to-apples rows：Newton A0 是 `0.066934 ms/substep`，Newton A1 是 `0.035721 ms/substep`，PhysTwin B0 是 `0.010840 ms/substep`。
所以最核心的一句结论必须讲成人话：在同一个 clean rope replay benchmark 下，就算把 Newton 的 replay feeding 改成 A1 这种更轻的路径，它还是比 PhysTwin B0 慢大约 `3.30x`。
这页对 real viewer 的意义在于，它把两个问题分开了：viewer 今天能不能跑，是一回事；如果我们要更大 headroom，Newton 和 PhysTwin 在相同 replay benchmark 下还差多远，又是另一回事。
边界也要讲清楚：viewer row 和 no-render rows 不应该被混成一个数。viewer row讲 end-to-end practical speed；A0/A1/B0 讲的是 simulator throughput。

## Slide 11 — H4: What does A0 -> A1 actually isolate?
这一页专门把 A0 和 A1 讲清楚，因为如果这里讲不明白，后面的推导都会很含糊。
A0 和 A1 不是两个随便取的配置名。它们测的是同一条 rope replay、同一套 physics、同一组 `dt` 和 substeps。唯一想隔离出来的问题是：把同一条 replay trajectory 喂进 Newton，本身要花多少额外时间。
结果是 A0 到 A1 有 `1.87x` 的 speedup，所以 controller replay overhead 的确存在。同步 attribution 里，这部分大约是 `0.037 ms/substep`。
但这不是全部答案，因为把这部分降下来以后，Newton A1 相对 PhysTwin B0 还是慢 `3.30x`。而且 viewer ON 相对 A1 render OFF 只慢 `1.11x`，这说明 replay overhead 和 runtime organization 的问题，量级上比单纯 render cost 更值得先看。
这页对 real viewer 的价值很直接：如果只优化 controller feeding，viewer 会变好一些，但不会把同 case 的 Newton-vs-PhysTwin headroom gap 自动消掉。它的边界是，这个结论只针对 clean rope replay，不是对所有 scene 的一刀切判断。

## Slide 12 — H5: What the residual gap suggests — and what it does NOT prove
这一页回答最后一个最容易被说过头的问题：残余差距到底说明了什么，又不说明什么。

[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]
[What | Newton]
L141-L145 这段先后调用 spring、triangle、bending 等不同 force stage，说明 Newton 这一条 replay path 不是一个单一的整步更新，而是把每一类力和接触拆成多个阶段依次执行。
L160-L165 又继续进入不同 contact stage，所以就算当前 rope baseline 本身 contact 很弱，solver 组织方式仍然是“多段顺序推进”的结构，而不是一次性回放完一整步。
L172-L177 最后才做 `integrate_particles` 和下一步切换，因此从 runtime 角度看，这条 path 更像 many separated execution stages，而不是一个天然的 graph replay。
[Why | Newton]
这段代码不能直接给出性能比例，但它确实回答了一个结构性问题：Newton rope replay 的 core path 现在就是按多个 stage 组织起来的。结合 A1 之后残余差距还在、以及 Nsight 里 `cuLaunchKernel` 仍然占主导，这个方向上的解释是有支撑的。
[Risk | Newton]
这段源码不能单独证明“Newton 一定就是因为 launch 太多才慢”。它只能说明 residual gap 至少和当前这种 staged execution organization 是相容的，而不是无条件把原因精确锁死。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 768-782, 800-802]
[What | PhysTwin]
L768-L782 这里在 `use_graph` 打开时直接 capture `self.step()`，并把 capture 得到的 graph 存起来，所以 PhysTwin 不是在 wrapper 外面临时做 batching，而是 rope core 自己就暴露了一条 graph-based replay path。
L800-L802 又单独保留了 `forward_graph`，说明它不只是一次性 capture 一个训练图，而是前向 replay 也明确走 graph replay 语义。
[Why | PhysTwin]
这段代码把 PhysTwin 一侧的快路径讲得很清楚：同一个 clean rope replay，不只是 benchmark 上看起来快，core source 里也真的有 graph-based replay 这个结构。再加上 Nsight 里 `cudaGraphLaunch_v10000` 占主导，实验、源码和系统证据是对齐的。
[Risk | PhysTwin]
这也不能推出『Newton 只要照抄 graph 就一定追平』。它只支持一个更谨慎的结论：在这个 controlled rope benchmark 里，残余差距更像 runtime organization 的差异，而不只是 controller replay overhead。

所以这页最后的人话结论是：在 clean rope replay 里，残余 gap 更像 Newton 这边还保留了 many separated launches，而 PhysTwin 这边已经有 graph-based replay path。
但这页也必须明确说不证明什么：它不证明 full physics parity；它不消除 self-collision 或 bunny-contact mismatch 这些别的层次的问题；它也不意味着 collision 在所有场景里都不重要。它只说明在这个 controlled rope replay benchmark 里，controller replay overhead 不是全部答案。

## Slide 13 — H6: What should we optimize next for the real viewer?
最后一页只讲这整段 profiling 对 real viewer 到底有什么实际价值。
第一，A0 到 A1 已经告诉我们：如果目标是 viewer diagnosis，就不应该继续拿更重的 baseline feed path 当默认基线，因为光这一项就已经差了大约 `1.87x`。
第二，E1 对 A1 的比较又告诉我们：在这个 rope case 上，render ON 相对同 replay 的 render OFF 只多了大约 `1.11x` wall time，所以如果我们要争取更多 viewer headroom，优先级不应该只放在 rendering。
第三，A1 对 B0、再加上 Newton core staged step path 和 PhysTwin core graph replay path，一起给出的方向是：下一步更值得先研究 replay organization，也就是能不能把 Newton 这条 path 做得更 batched，或者更 graph-like。
第四，这一步做完以后，才值得认真判断 kernel micro-optimization 还有没有足够大的回报。
所以 profiling 这一段最后服务的不是一个抽象 benchmark，而是一个很实际的判断：如果 real viewer 还想要更多余量，我们下一步应该把工程时间先花在 replay path organization 上。
它的边界仍然不变：这里说的是 controlled rope replay benchmark，不是 robot，不是 self-collision，也不是 bunny penetration。

## Slide 14 — Hypothesis F1: A Force Video Must Preserve Both Global Cloth Behavior And Local Contact Mechanism
这里开始进入第三段 penetration analysis。
这一页先把新的 hypothesis 说清楚。
教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。
真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。
所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。

## Slide 15 — Result F1: Global Phenomenon Videos Now Cover The Whole Penetration Process
这一页只讲 phenomenon，不讲 force。
现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。
从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。
也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。

## Slide 16 — Result F2: Split Single-Panel Videos Now Match The Current 2x2 Board
这一页现在不再放旧的四个历史 force mechanism 视频了。
这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
现在 F2 里的四个单视频，都是直接从当前 canonical `2 x 2` board 裁出来的单面板。
也就是说，这一页只负责把四个 panel 单独放大给老师看：box penalty、box total、bunny penalty、bunny total。
这样 F2 和下一页 F3 就不会再出现“这一页还是旧结果、下一页才是新结果”的割裂了。

## Slide 17 — Result F3: The New 2x2 Board Makes The Box-vs-Bunny Comparison Immediate
这一页就是新的 `2 x 2` board video，我把它直接放进 PPT 里了。
这里必须把实验设定写明：self-collision 是 OFF，cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
它的结构非常直接：左上是 box penalty，右上是 box total，左下是 bunny penalty，右下是 bunny total。
所以这一页的价值不是再讲一个局部 mechanism patch，而是把 box versus bunny、penalty versus total 这两个对比同时压进一个 meeting-readable clip。
如果现场只想停一页讲 penetration，我现在会优先停这一页，因为它最接近老师要的最终 visual comparison。

## Slide 18 — Result F4: A 4x Slow-Motion Board Makes Contact Development Easier To Read
这一页是 F3 的补充版本，不改实验设定，只改播放节奏。
也就是说，self-collision 还是 OFF，cloth total mass 还是 0.1 kg，rigid target mass 还是 0.5 kg。
这里放的是同一套 `2 x 2` board，但是视频整体放慢四倍，而且每个 panel 里都显式写了 `4x slow motion`。
这页的作用不是替代正常速度版本，而是让老师在会议里更容易看清 pre-contact、first contact 和 penetration growth 的过渡。

## Slide 19 — Scope: Strict `phystwin`
这里开始进入第四段 self-collision, Newton way。
这一页先把 target scene 说清楚，避免把不在 scope 里的 scene 混进 strict parity。
现在我们只 claim PhysTwin 原生 cloth contact scope，也就是 pairwise self-collision 加 implicit z 等于零 ground plane。
这条实现完全在 bridge 层，没有改 Newton core，而且 parity validator 也是围绕这条 cloth reference path 组织的。
所以这一页的 take-home message 很简单：strict phystwin 只针对 in-scope cloth reference case。

## Slide 20 — Matched: Contact Law
第二页直接拿代码对代码，不再用抽象名词。
左边是 PhysTwin 原生的 `object_collision` 和 `integrate_ground_collision`，右边是我们 bridge 里的 strict phystwin 对应实现。
这页要说的结论很窄但很重要：strict scope 里的 self-collision law 和 ground contact law 已经对齐到 operator level。
所以 blocked parity 现在不应该再被描述成 self-collision 或 ground law 本身还没抄对。

## Slide 21 — Difference 1: Collision Table Runtime
第三页继续只看代码，而且只看 collision table 这一个点。
左边是 PhysTwin 原版：每帧先 build collision graph，再填 `collision_indices / collision_number`，整帧 substeps 复用这张表。
右边是我们当前 strict phystwin：生命周期已经同步成 per-frame frozen table，但这张表还是 bridge runtime 自己重建的。
所以这页的结论是：collision table 这边已经更像 PhysTwin 了，但 provenance 和 runtime 语义还没有完全一样。

## Slide 22 — Difference 2: Controller Handling
第四页还是代码对代码，但这次看 controller handling。
左边 PhysTwin 的 spring path 直接吃 `control_x / control_v`；右边我们当前 bridge 还是把 controller 点写进 Newton particle state 里。
这也是为什么 current status 现在把 controller-spring diagnostic 当成下一阶段最像 blocker 的信号。
所以这页的结论是：如果还要继续压 full-rollout parity，这一层比继续纠缠 self-collision law 更值得先改。

## Slide 23 — A/B Result: Full Rollout
最后一页只看 in-scope cloth reference case 的 full-rollout A/B，不再混 box scene。
右边是最新 302-frame parity support video，左边的表直接列 OFF 和 strict phystwin 的 full-rollout 数字。
现在 strict phystwin 只在前 30 帧更好，但 full-rollout 的 rmse_mean 还没有低于 OFF。
同时我们也把短窗口 improvement 和 controller-spring diagnostic 放进这一页的 note 里，所以这页已经足够把 blocker 讲完整。
所以这一页的 take-home message 很直接：当前 strict phystwin 还没有通过 full-rollout A/B gate。

## Slide 24 — Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
