# Meeting Transcript — PhysTwin -> Newton Bridge

语言：中文主讲 + English terminology  
形式：five-part agenda  
结构：1. recall  2. performance analysis  3. penetration analysis  4. controlled self-collision / ground-contact laws  5. robotic with deformable objects  
目标：让 opening framing、transcript framing 和实际 deck 章节结构完全对齐

---

## Slide 1 — Xinjie Zhang
这一页是 opening speaker page。
这次 meeting 我会按五段讲：1. recall，2. performance analysis，3. penetration analysis，4. controlled self-collision and ground-contact laws，5. robotic with deformable objects。
所以 opening 要做的不是再把会议压成“short recall + two results”，而是先把这五段主线直接说清楚。

## Slide 2 — Recall: The Bridge Baseline Was Already Established
第一页 recall 只讲一句话：import baseline 早就已经站住了。
cloth、zebra、sloth、rope 这四个 baseline 都不是今天新证明的内容，所以后面的问题不再是 PhysTwin deformable 能不能 load 到 Newton。
这页的 takeaway 很明确：bridge baseline already works。

## Slide 3 — Recall: The Remaining Issue Is Contact Behavior, Not Bridge Existence
第二页 recall 只把问题进一步收窄。
同样是 rigid support，bunny 明显比 thick box 更难，这说明当前 open question 更像是 geometry-sensitive contact behavior，而不是 bridge 根本没有工作。
所以从这里开始，我们后面讨论的不是 bridge existence，而是 contact semantics 和 penetration mechanism。

## Slide 4 — H1: Replay Feeding Was The First Realtime Bottleneck
这一页先直接回答你刚才提的 practical question：为什么我们原来的 rope viewer 到不了 realtime，现在又为什么能到 realtime。
这里我专门补了一个旧路径对照实验。三行都还是同一个 `rope_double_hand`、同一条 replay trajectory、同样的 `dt` 和 `667` 个 substeps。区别只在于 Newton 侧 replay feeding 的实现，以及有没有把 rendering 打开。
旧的 visible viewer 路径，也就是 baseline controller replay path，`viewer FPS` 大约是 `20.75`，`RTF` 只有 `0.692x`，所以它确实达不到 realtime。现在的 visible viewer 路径换成 precomputed controller replay 以后，`viewer FPS` 大约是 `37.85`，`RTF` 变成 `1.262x`，所以它已经能过 realtime。
这两条 visible-viewer row 的核心区别，不是 physics 变了，也不是场景变了，而是 controller replay feeding 变了。我们把原来每个 substep 都要重复做的 interpolation 和 state write 预先展开，所以 viewer end-to-end wall time 大约改善了 `1.82x`。
再和当前 path 的 render OFF 行放在一起看，A1 的 `RTF` 还能到 `1.400x`。这说明现在 viewer 能过 realtime，不是因为突然把 rendering 变得特别轻了，而是因为 replay path 本身已经先被减负。
所以 profiling 的价值就非常直接：它不是在绕开 real viewer，而是在解释 real viewer 为什么以前慢，以及为什么现在终于能过 realtime。边界是，这个结论只针对当前 clean rope replay case，不自动推广到所有更复杂的 contact scene。

## Slide 5 — H2: Fair Rope Benchmark = Same Replay, Physics, And GPU
这一页先只讲 fairness controls，不急着解释 E1、A0、A1、B0 这些名字。
我要先让观众知道：后面所有 rope profiling row 都是同一个 `rope_double_hand`，同一条 controller trajectory，同样的 `dt=5e-05` 和 `667` 个 substeps，而且都在同一张 RTX 4090 上跑。
这里最关键的一句是：主 apples-to-apples comparison 把 rendering 关掉，不是因为我们不关心 viewer，而是因为要先隔离 simulator replay 本身。与此同时，same-trajectory 也不是口头假设，当前 benchmark 记录的 IR 与 PhysTwin controller trajectory max abs diff 是 0.0e+00。
这页对 real viewer 的意义是，它告诉听众后面那个 no-render benchmark 到底是在控制什么变量。边界是：这里只定义 fairness，不解释每个 benchmark row 的具体含义。

## Slide 6 — H3: E1, A0, A1, And B0 Are Four Rows Of One Benchmark
这一页再把 benchmark rows 的名字讲成人话，避免听众只看到一堆内部缩写。
E1 是 visible render ON 的 real viewer row，所以它回答 practical question：viewer 本身现在跑得怎么样。A0 和 A1 都是同一个 no-render rope replay，只是 Newton 侧 feeding 同一条 trajectory 的方式不同。B0 则是同 case、同 trajectory 的 PhysTwin headless reference。
所以 A0/A1/B0 不是三个不同任务，而是同一个 controlled rope benchmark 上的三个 measurement row。真正不同的是：有没有打开 rendering，以及 Newton 这边 controller replay overhead 有没有被预先压掉。
这页对 real viewer 的意义是，把 practical row 和 simulator-only rows 的角色分清楚。这样后面看结果表时，观众才不会把 viewer FPS 和 ms/substep 混成一回事。
边界同样要讲清楚：E1 不是拿来和 PhysTwin B0 直接比 wall time 的；它是 viewer-facing context row。真正 apples-to-apples 的 throughput 对照还是 A0/A1 对 B0。

## Slide 7 — Result P1: Newton A1 Is Still 3.30x Slower Than PhysTwin B0
这一页只回答数字本身，不先解释原因。
先看 practical row：E1 这个 visible rope viewer 大约是 `37.85 FPS`，`RTF` 是 `1.262x`。所以它回答的是『viewer 现在能不能跑』这个问题。
再看 apples-to-apples rows：Newton A0 是 `0.066934 ms/substep`，Newton A1 是 `0.035721 ms/substep`，PhysTwin B0 是 `0.010840 ms/substep`。
所以最核心的一句结论必须讲成人话：在同一个 clean rope replay benchmark 下，就算把 Newton 的 replay feeding 改成 A1 这种更轻的路径，它还是比 PhysTwin B0 慢大约 `3.30x`。
这页对 real viewer 的意义在于，它把两个问题分开了：viewer 今天能不能跑，是一回事；如果我们要更大 headroom，Newton 和 PhysTwin 在相同 replay benchmark 下还差多远，又是另一回事。
边界也要讲清楚：viewer row 和 no-render rows 不应该被混成一个数。viewer row讲 end-to-end practical speed；A0/A1/B0 讲的是 simulator throughput。

## Slide 8 — H4: A0 -> A1 Isolates Replay Overhead, Not The Whole Gap
这一页专门把 A0 和 A1 讲清楚，因为如果这里讲不明白，后面的推导都会很含糊。
A0 和 A1 不是两个随便取的配置名。它们测的是同一条 rope replay、同一套 physics、同一组 `dt` 和 substeps。唯一想隔离出来的问题是：把同一条 replay trajectory 喂进 Newton，本身要花多少额外时间。
结果是 A0 到 A1 有 `1.87x` 的 speedup，所以 controller replay overhead 的确存在。这里所谓的方法，不是换 physics，而是把 controller target 和 velocity 先按 substep 预计算好，避免每一步都重复做 interpolation 和写状态。同步 attribution 里，这部分大约是 `0.037 ms/substep`。
但这不是全部答案，因为把这部分降下来以后，Newton A1 相对 PhysTwin B0 还是慢 `3.30x`。而且 viewer ON 相对 A1 render OFF 只慢 `1.11x`，这说明 replay overhead 和 runtime organization 的问题，量级上比单纯 render cost 更值得先看。
这页对 real viewer 的价值很直接：如果只优化 controller feeding，viewer 会变好一些，但不会把同 case 的 Newton-vs-PhysTwin headroom gap 自动消掉。它的边界是，这个结论只针对 clean rope replay，不是对所有 scene 的一刀切判断。

## Slide 9 — H5: Residual Gap Points To Execution Structure
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

## Slide 10 — H6: Optimize Replay Organization Before Render Tuning
最后一页只讲这整段 profiling 对 real viewer 到底有什么实际价值。
第一，A0 到 A1 已经告诉我们：如果目标是 viewer diagnosis，就不应该继续拿更重的 baseline feed path 当默认基线，因为光这一项就已经差了大约 `1.87x`。
第二，E1 对 A1 的比较又告诉我们：在这个 rope case 上，render ON 相对同 replay 的 render OFF 只多了大约 `1.11x` wall time，所以如果我们要争取更多 viewer headroom，优先级不应该只放在 rendering。
第三，A1 对 B0、再加上 Newton core staged step path 和 PhysTwin core graph replay path，一起给出的方向是：下一步更值得先研究 replay organization，也就是能不能把 Newton 这条 path 做得更 batched，或者更 graph-like。
第四，这一步做完以后，才值得认真判断 kernel micro-optimization 还有没有足够大的回报。
所以 profiling 这一段最后服务的不是一个抽象 benchmark，而是一个很实际的判断：如果 real viewer 还想要更多余量，我们下一步应该把工程时间先花在 replay path organization 上。
它的边界仍然不变：这里说的是 controlled rope replay benchmark，不是 robot，不是 self-collision，也不是 bunny penetration。

## Slide 11 — F1: Force Video Must Show Global Motion And Local Mechanism
这里开始进入第三段 penetration analysis。
这一页先把新的 hypothesis 说清楚。
教授要的不是一个只剩局部 probe 的 force patch，也不是一个 static trigger snapshot。
真正需要的是两件事同时成立：第一，看到整块 cloth 相对于 bunny 的整体 penetration 过程；第二，在 local patch 里看到 outward normal、external force、internal force 和 acceleration 的机制解释。
所以这次我把输出正式拆成 phenomenon video 和 force mechanism video，但 force mechanism 本身仍然保留 global panel 加 local zoom panel，而不是只放局部 close-up。

## Slide 12 — F2: Four Phenomenon Videos Show The Full Penetration Process
这一页只讲 phenomenon，不讲 force。
现在四个 case 都有 accepted 的 global process video，而且都过了 black-screen、motion 和 temporal-density 的 QA。
从这里可以清楚看到四种情况里，pre-contact、first contact、penetration growth 和后续 settle 的整体行为。
也就是说，我们现在已经不再依赖单帧截图来讲 penetration，而是真正有了 meeting-ready 的过程视频。

## Slide 13 — F3: Split Panels Match The Current 2x2 Board
这一页现在不再放旧的四个历史 force mechanism 视频了。
这里也把实验设定说清楚：cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
现在 F2 里的四个单视频，都是直接从当前 canonical `2 x 2` board 裁出来的单面板。
也就是说，这一页只负责把四个 panel 单独放大给老师看：box penalty、box total、bunny penalty、bunny total。
这样 F2 和下一页 F3 就不会再出现“这一页还是旧结果、下一页才是新结果”的割裂了。

## Slide 14 — F4: The New 2x2 Board Makes Box-vs-Bunny Immediate
这一页就是新的 `2 x 2` board video，我把它直接放进 PPT 里了。
这里必须把实验设定写明：self-collision 是 OFF，cloth total mass 是 0.1 kg，rigid target mass 是 0.5 kg。
它的结构非常直接：左上是 box penalty，右上是 box total，左下是 bunny penalty，右下是 bunny total。
所以这一页的价值不是再讲一个局部 mechanism patch，而是把 box versus bunny、penalty versus total 这两个对比同时压进一个 meeting-readable clip。
如果现场只想停一页讲 penetration，我现在会优先停这一页，因为它最接近老师要的最终 visual comparison。

## Slide 15 — F5: 4x Slow Motion Makes Contact Development Easier To Read
这一页是 F3 的补充版本，不改实验设定，只改播放节奏。
也就是说，self-collision 还是 OFF，cloth total mass 还是 0.1 kg，rigid target mass 还是 0.5 kg。
这里放的是同一套 `2 x 2` board，但是视频整体放慢四倍，而且每个 panel 里都显式写了 `4x slow motion`。
这页的作用不是替代正常速度版本，而是让老师在会议里更容易看清 pre-contact、first contact 和 penetration growth 的过渡。

## Slide 16 — S1: Separate Self-Collision Law From Ground-Contact Law
这里开始我先统一术语，不再说 `phystwin mode` 或者 `Newton way` 这种容易混淆的词。
从现在开始只讲四个术语：native Newton self-collision，PhysTwin-style self-collision，native Newton ground-contact，PhysTwin-style ground-contact。
这样做的目的，是把 self-collision law 和 ground-contact law 明确分开。因为这次真正的问题不是某个 mode 名字，而是这两条 law 分别会怎样影响同一个 cloth reference case 的 RMSE。

## Slide 17 — S2: A 2x2 Matrix Isolates The Two Laws
这一页是这次 self-collision 段最重要的结构页。
现在我们不再把问题讲成一个整体 mode，而是做 controlled `2 x 2` matrix：一条轴是 self-collision law，另一条轴是 ground-contact law。
这样同一个 cloth scene、同一个 IR、同一个 dt 和 substeps 下，我们就能回答到底是哪一条 law 改变了 RMSE，以及两条 law 之间有没有 interaction effect。

## Slide 18 — S3: Operator Exactness Passes; Rollout Parity Is Still Blocked
最后这一页只讲当前能够 defend 的结论，不讲过多过程。
第一，operator-level exactness 已经很强，所以我们不能再把问题简单说成 self-collision kernel 还没有对齐。
第二，公平 `2 x 2` full-rollout matrix 已经说明，当前最好的组合不是 fully PhysTwin-style pair，而是 PhysTwin-style self-collision 加 native Newton ground-contact。
第三，四个 case 全部仍然没有过 strict `1e-5` gate。所以当前最准确的表述是：local operator evidence is strong, but rollout-level parity is still blocked。
也就是说，剩余问题更像 whole-step interaction mismatch，而不是 isolated self-collision law mismatch。

## Slide 19 — R0: Native Robot Release/Drop Is A Sanity Baseline
在进入 tabletop push 之前，我先把更窄的 robot stage-0 baseline 单独点出来。
这页不是 final manipulation claim，而是 `drop_release_baseline` 的 sanity baseline：native Newton Franka 在场，rope 先被 support，再 release，然后在 semi-implicit pipeline 里自由下落并撞到 real ground。
当前 authoritative OFF run 的关键数字是：release time 大约 `0.40 s`，first ground contact 大约 `0.7168 s`，impact speed 大约 `3.11 m/s`，early-fall acceleration 拟合约 `-9.80 m/s^2`。
右侧的 drag ON 是 matched A/B。当前 repo 里的结论是 drag 影响是 minor，不是这个 baseline 的主问题来源。
所以这页的作用很窄：它证明 native robot integration、semi-implicit rope free fall、real ground contact 和 1:1 readable video 这四件事已经成立，但不把它说成 full two-way coupling。

## Slide 20 — R1: Tabletop Push Is A Contact Baseline, Not Full 2-Way Coupling
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论不再是 release/drop baseline，而是 native tabletop push baseline 已经成立，所以 robot-deformable chapter 至少有了一个更直接的 contact story。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `tabletop_push_hero` 证明了：native Franka、native tabletop、PhysTwin rope 同时可见，rope 在 visible clip 开始前已经 settle，然后 robot 的 own finger / claw 在桌面高度接近、接触、再推动 rope lateral motion。
但这页也必须明确写清楚：它还不是 full two-way coupling。当前 robot motion 仍然是 demo-side commanded open-loop joint trajectory，rope 会在 Newton 里因为真实接触而响应，但 rope 还不会反过来改变 robot command。
这次比旧版更关键的一点，是 contact-causality 做过修复。新的 promoted `c10` 把 visible first contact 提前，所以“rope 先动、手指后到”的观感明显减弱。
所以这页的结论是，robotic with deformable objects 这一章现在至少有了一个 native tabletop finger-push baseline，可以保守 defend 为 real contact baseline，但不能 overclaim 成 full manipulation 或 full bidirectional coupling。
