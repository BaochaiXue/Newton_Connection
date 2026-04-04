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

## Slide 8 — H1: Why did the rope viewer miss realtime before, and why does it reach realtime now?
这一页先直接回答你刚才提的 practical question：为什么我们原来的 rope viewer 到不了 realtime，现在又为什么能到 realtime。
这里我专门补了一个旧路径对照实验。三行都还是同一个 `rope_double_hand`、同一条 replay trajectory、同样的 `dt` 和 `667` 个 substeps。区别只在于 Newton 侧 replay feeding 的实现，以及有没有把 rendering 打开。
旧的 visible viewer 路径，也就是 baseline controller replay path，`viewer FPS` 大约是 `20.75`，`RTF` 只有 `0.692x`，所以它确实达不到 realtime。现在的 visible viewer 路径换成 precomputed controller replay 以后，`viewer FPS` 大约是 `37.85`，`RTF` 变成 `1.262x`，所以它已经能过 realtime。
这两条 visible-viewer row 的核心区别，不是 physics 变了，也不是场景变了，而是 controller replay feeding 变了。我们把原来每个 substep 都要重复做的 interpolation 和 state write 预先展开，所以 viewer end-to-end wall time 大约改善了 `1.82x`。
再和当前 path 的 render OFF 行放在一起看，A1 的 `RTF` 还能到 `1.400x`。这说明现在 viewer 能过 realtime，不是因为突然把 rendering 变得特别轻了，而是因为 replay path 本身已经先被减负。
所以 profiling 的价值就非常直接：它不是在绕开 real viewer，而是在解释 real viewer 为什么以前慢，以及为什么现在终于能过 realtime。边界是，这个结论只针对当前 clean rope replay case，不自动推广到所有更复杂的 contact scene。

## Slide 9 — H2: What stays fixed in the controlled rope benchmark?
这一页先只讲 fairness controls，不急着解释 E1、A0、A1、B0 这些名字。
我要先让观众知道：后面所有 rope profiling row 都是同一个 `rope_double_hand`，同一条 controller trajectory，同样的 `dt=5e-05` 和 `667` 个 substeps，而且都在同一张 RTX 4090 上跑。
这里最关键的一句是：主 apples-to-apples comparison 把 rendering 关掉，不是因为我们不关心 viewer，而是因为要先隔离 simulator replay 本身。与此同时，same-trajectory 也不是口头假设，当前 benchmark 记录的 IR 与 PhysTwin controller trajectory max abs diff 是 0.0e+00。
这页对 real viewer 的意义是，它告诉听众后面那个 no-render benchmark 到底是在控制什么变量。边界是：这里只定义 fairness，不解释每个 benchmark row 的具体含义。

## Slide 10 — H2b: What do E1, A0, A1, and B0 mean?
这一页再把 benchmark rows 的名字讲成人话，避免听众只看到一堆内部缩写。
E1 是 visible render ON 的 real viewer row，所以它回答 practical question：viewer 本身现在跑得怎么样。A0 和 A1 都是同一个 no-render rope replay，只是 Newton 侧 feeding 同一条 trajectory 的方式不同。B0 则是同 case、同 trajectory 的 PhysTwin headless reference。
所以 A0/A1/B0 不是三个不同任务，而是同一个 controlled rope benchmark 上的三个 measurement row。真正不同的是：有没有打开 rendering，以及 Newton 这边 controller replay overhead 有没有被预先压掉。
这页对 real viewer 的意义是，把 practical row 和 simulator-only rows 的角色分清楚。这样后面看结果表时，观众才不会把 viewer FPS 和 ms/substep 混成一回事。
边界同样要讲清楚：E1 不是拿来和 PhysTwin B0 直接比 wall time 的；它是 viewer-facing context row。真正 apples-to-apples 的 throughput 对照还是 A0/A1 对 B0。

## Slide 11 — H3: Under the same rope replay, how far is Newton from PhysTwin?
这一页只回答数字本身，不先解释原因。
先看 practical row：E1 这个 visible rope viewer 大约是 `37.85 FPS`，`RTF` 是 `1.262x`。所以它回答的是『viewer 现在能不能跑』这个问题。
再看 apples-to-apples rows：Newton A0 是 `0.066934 ms/substep`，Newton A1 是 `0.035721 ms/substep`，PhysTwin B0 是 `0.010840 ms/substep`。
所以最核心的一句结论必须讲成人话：在同一个 clean rope replay benchmark 下，就算把 Newton 的 replay feeding 改成 A1 这种更轻的路径，它还是比 PhysTwin B0 慢大约 `3.30x`。
这页对 real viewer 的意义在于，它把两个问题分开了：viewer 今天能不能跑，是一回事；如果我们要更大 headroom，Newton 和 PhysTwin 在相同 replay benchmark 下还差多远，又是另一回事。
边界也要讲清楚：viewer row 和 no-render rows 不应该被混成一个数。viewer row讲 end-to-end practical speed；A0/A1/B0 讲的是 simulator throughput。

## Slide 12 — H4: What does A0 -> A1 actually isolate?
这一页专门把 A0 和 A1 讲清楚，因为如果这里讲不明白，后面的推导都会很含糊。
A0 和 A1 不是两个随便取的配置名。它们测的是同一条 rope replay、同一套 physics、同一组 `dt` 和 substeps。唯一想隔离出来的问题是：把同一条 replay trajectory 喂进 Newton，本身要花多少额外时间。
结果是 A0 到 A1 有 `1.87x` 的 speedup，所以 controller replay overhead 的确存在。这里所谓的方法，不是换 physics，而是把 controller target 和 velocity 先按 substep 预计算好，避免每一步都重复做 interpolation 和写状态。同步 attribution 里，这部分大约是 `0.037 ms/substep`。
但这不是全部答案，因为把这部分降下来以后，Newton A1 相对 PhysTwin B0 还是慢 `3.30x`。而且 viewer ON 相对 A1 render OFF 只慢 `1.11x`，这说明 replay overhead 和 runtime organization 的问题，量级上比单纯 render cost 更值得先看。
这页对 real viewer 的价值很直接：如果只优化 controller feeding，viewer 会变好一些，但不会把同 case 的 Newton-vs-PhysTwin headroom gap 自动消掉。它的边界是，这个结论只针对 clean rope replay，不是对所有 scene 的一刀切判断。

## Slide 13 — H5: What the residual gap suggests — and what it does NOT prove
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

## Slide 14 — H6: What should we optimize next for the real viewer?
最后一页只讲这整段 profiling 对 real viewer 到底有什么实际价值。
第一，A0 到 A1 已经告诉我们：如果目标是 viewer diagnosis，就不应该继续拿更重的 baseline feed path 当默认基线，因为光这一项就已经差了大约 `1.87x`。
第二，E1 对 A1 的比较又告诉我们：在这个 rope case 上，render ON 相对同 replay 的 render OFF 只多了大约 `1.11x` wall time，所以如果我们要争取更多 viewer headroom，优先级不应该只放在 rendering。
第三，A1 对 B0、再加上 Newton core staged step path 和 PhysTwin core graph replay path，一起给出的方向是：下一步更值得先研究 replay organization，也就是能不能把 Newton 这条 path 做得更 batched，或者更 graph-like。
第四，这一步做完以后，才值得认真判断 kernel micro-optimization 还有没有足够大的回报。
所以 profiling 这一段最后服务的不是一个抽象 benchmark，而是一个很实际的判断：如果 real viewer 还想要更多余量，我们下一步应该把工程时间先花在 replay path organization 上。
它的边界仍然不变：这里说的是 controlled rope replay benchmark，不是 robot，不是 self-collision，也不是 bunny penetration。

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

## Slide 20 — Scope: Strict `phystwin`
先把场景边界说死。这里的 strict `phystwin` 只指 cloth reference case，物理范围只有 pairwise self-collision 和 implicit z-equals-zero ground。
实现入口在 `phystwin_contact_stack.py`，rollout 入口在 `newton_import_ir.py`，full-rollout gate 由 `validate_parity.py` 执行，而最新的公平 `2 x 2` law-isolation matrix 由 `run_ground_contact_self_collision_rmse_matrix.py` 统一驱动。
所以后面的分析都是在这一条 cloth-reference path 上进行，不是在讲 generic rigid-support contact。
这一步的作用是固定问题定义。只有问题定义先固定，后面才能判断到底是哪一层机制已经对齐，哪一层机制还没有对齐。

## Slide 21 — Mechanism Table A: Scope + Matched Mechanisms
这一页是总表的第一部分，只放 scope 和已经对齐的机制。
Shape contact penalty force 指的是按 penetration depth 连续施加接触力，通常是 stiffness 乘深度再加上法向 damping。这类机制属于 generic rigid-support contact，不属于当前 strict cloth mode。
Force-to-velocity injection 指的是先把 spring force 和 gravity 注入速度，代码形式就是 `v1 = v0 + a * dt`，然后再用 drag 去缩放这个速度。也就是说，contact 看到的是已经更新过的 velocity，而不是原始速度。
Point-plane TOI collision 指的是先判断这一小步里粒子是否跨过平面，再解 `toi = -x_z / v_z` 得到撞击时刻，然后在撞击点更新法向和切向速度，最后分别积分撞击前后两段轨迹。这是 velocity event update，不是 penetration-depth penalty force。
这一页的结论很简单：strict scope 自身是清楚的，而且 strict scope 内最核心的 contact mechanisms 已经对齐。

## Slide 22 — Mechanism Table B: Primary Mismatches + Final Gate
这一页是总表的第二部分，只放 primary mismatches 和最终 gate。
现在最值得盯住的源码差异就是两类：collision table runtime，以及 controller spring handling。
再往下的所有源码页，都是顺着这两类 primary mismatch 展开。
最后一行不再只看 old two-run A/B，而是看新的公平 `2 x 2` full-rollout gate。当前最佳组合是 self `phystwin` 加 ground `native`，这说明 fully `phystwin` pair 还不是最优 full-rollout pair。

## Slide 23 — Matched 1: Self-Collision Impulse Law
现在开始按总表逐项推演。第一项是 self-collision impulse law。
这两段代码都在做同一件事：先算相对速度的法向分量，再算 collision impulse，再算切向 friction correction，最后在所有有效 pair 上求平均，用 `J_sum / valid_count` 去修正 velocity。
这说明 local self-collision law 在 strict scope 内已经对齐到 operator level。也正因为这一点，当前 blocked parity 不能再简单归因为 self-collision kernel 还没抄对。

## Slide 24 — Matched 2: Force-to-Velocity Injection + Point-Plane TOI Ground
第二项和第三项是 force-to-velocity injection 和 point-plane TOI ground collision。
从代码上看，两边都是先把 force 注入 velocity，再进入 contact 处理；ground 这一块也都是先判定是否跨过 z-equals-zero 平面，再解 TOI，再更新法向和切向 velocity。
所以在 strict scope 内，ground event update 也已经基本同步了。这意味着现在最值得怀疑的地方，已经不再是 strict scope 内这两条局部 contact formula。

## Slide 25 — Mismatch 1: Collision Table Runtime
第一个 primary mismatch 是 collision table runtime。
PhysTwin 的做法是：在每个 frame 开头基于自己的 object state 构建 collision graph，填好 `collision_indices / collision_number`，然后整帧 substeps 都复用这张表。
我们现在虽然也改成了 per-frame frozen table，所以 lifecycle 已经更像 PhysTwin，但这张表仍然是 bridge runtime 自己重建的。也就是说，现在这边真正还没完全同步的，是 runtime table 的 provenance、ordering 和 truncation semantics，而不是前面那条 local impulse law。

## Slide 26 — Mismatch 2: Controller Spring Handling
第二个 primary mismatch 是 controller handling，而且现在它是更强的 blocker 信号。
在 PhysTwin 里，controller motion 是通过单独的 `control_x / control_v` 数组进入 spring system 的。也就是说，controller 是一个独立的 prescribed channel。
在我们当前 bridge 里，controller target 会先写进 Newton particle state，然后 spring path 从这个 state 里继续读。这会改变 controller-connected springs 参与 whole step 的方式。
这正是为什么 controller-spring diagnostic 现在这么重要：如果 full-rollout parity 还要继续往下压，这一层比继续打磨 isolated self-collision law 更值得先改。

## Slide 27 — 2x2 Result: Full Rollout Matrix
最后用新的公平 `2 x 2` full-rollout matrix 把前面的源码分析收口。
这四个 case 保持同一个 cloth IR、同一个 implicit ground scene、同一个 302-frame rollout、同一个 dt 和 substeps、同一个 drag 和 evaluator，只切 self law 和 ground law 两个轴。fairness check 已经明确通过。
结果上，ground 从 native 切到 `phystwin` 在 self OFF 时只改善了一点；self 从 OFF 切到 `phystwin` 在 ground native 时改善更明显。所以当前更大的 main effect 来自 self-collision law，不是 ground law。
更关键的是，最好的 full-rollout case 不是 fully `phystwin`，而是 case 3，也就是 self `phystwin` 加 ground `native`。这说明当前 remaining blocker 不能概括成 contact law 还没抄对，而更像是 whole-step interaction 还没有同步，尤其是 controller-spring path 加上 ground interaction 的组合效应。
右侧 GIF 只是 case 4 的 support clip，不代表整个 matrix。真正的结论以左边这张公平 `2 x 2` 表为准。

## Slide 28 — Robot Baseline R0: Native Robot + Semi-Implicit Rope Release/Drop Sanity Baseline
在进入 tabletop push 之前，我先把更窄的 robot stage-0 baseline 单独点出来。
这页不是 final manipulation claim，而是 `drop_release_baseline` 的 sanity baseline：native Newton Franka 在场，rope 先被 support，再 release，然后在 semi-implicit pipeline 里自由下落并撞到 real ground。
当前 authoritative OFF run 的关键数字是：release time 大约 `0.40 s`，first ground contact 大约 `0.7168 s`，impact speed 大约 `3.11 m/s`，early-fall acceleration 拟合约 `-9.80 m/s^2`。
右侧的 drag ON 是 matched A/B。当前 repo 里的结论是 drag 影响是 minor，不是这个 baseline 的主问题来源。
所以这页的作用很窄：它证明 native robot integration、semi-implicit rope free fall、real ground contact 和 1:1 readable video 这四件事已经成立，但不把它说成 full two-way coupling。

## Slide 29 — Conclusion R1: Native Tabletop Push Is Defendable, Not Full 2-Way Coupling
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论不再是 release/drop baseline，而是 native tabletop push baseline 已经成立，所以 robot-deformable chapter 至少有了一个更直接的 contact story。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `tabletop_push_hero` 证明了：native Franka、native tabletop、PhysTwin rope 同时可见，rope 在 visible clip 开始前已经 settle，然后 robot 的 own finger / claw 在桌面高度接近、接触、再推动 rope lateral motion。
但这页也必须明确写清楚：它还不是 full two-way coupling。当前 robot motion 仍然是 demo-side commanded open-loop joint trajectory，rope 会在 Newton 里因为真实接触而响应，但 rope 还不会反过来改变 robot command。
这次比旧版更关键的一点，是 contact-causality 做过修复。新的 promoted `c10` 把 visible first contact 提前，所以“rope 先动、手指后到”的观感明显减弱。
所以这页的结论是，robotic with deformable objects 这一章现在至少有了一个 native tabletop finger-push baseline，可以保守 defend 为 real contact baseline，但不能 overclaim 成 full manipulation 或 full bidirectional coupling。
