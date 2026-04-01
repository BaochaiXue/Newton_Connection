    # Meeting Transcript — PhysTwin → Newton Bridge

    语言：中文主讲 + English terminology  
    形式：按照当前 44 页 deck 逐页口播  
    目标：让 transcript 和 slides 的页序、标题、叙事完全对齐  
    slide 设计原则：hypothesis-driven、源码摘录短、GIF 讲效果、detailed analysis 全部放 transcript  
    口播策略：slides 只保留 15-20 秒内能读完的 claim / takeaway，复杂推导与 caveat 统一放在这里

    ---

## Slide 1 — Xinjie Zhang
    这一页只是 opening speaker page。  
    我会直接从 recall 开始，不在这里展开技术内容。

## Slide 2 — Recall 1: PhysTwin → Newton Bridge: Working
    第一页 recall 先把旧 cloth PASS case 拉回来。  
    它的作用只是提醒老师：bridge baseline 不是今天新讲的东西。

## Slide 3 — Recall 1: PhysTwin → Newton Bridge: Working
    第二页 recall 对应 zebra。  
    作用同样是告诉老师：旧 PASS case 已经建立，我们今天不重复证明旧结论。

## Slide 4 — Recall 1: PhysTwin → Newton Bridge: Working
    第三页 recall 对应 sloth。  
    这里仍然只是视觉回顾，不承担新的 hypothesis 证明。

## Slide 5 — Recall 1: PhysTwin → Newton Bridge: Working
    第四页 recall 对应 rope。  
    它提醒老师：rope 这一条 bridge baseline 已经成立。

## Slide 6 — Recall 1: PhysTwin → Newton Bridge: Working
    最后一页 recall 回到 bridge flow 本身。  
    它的作用是把旧 deck 的主线重新唤起：PhysTwin outputs -> bridge IR -> Newton reconstruction。

## Slide 7 — Recall 2: Bunny+Rope
    这一页 recall 的重点不再是旧 PASS case，而是 bunny+rope。  
    它提醒老师：novel rigid bunny interaction 这条线早就已经开始工作，只是当时还没有展开 cloth 归因。

## Slide 8 — H1: Particle-Mesh Contact Is Already Bidirectional
    H1 第一页先证明 contact 不是“视觉上碰到了”，而是源码里已经存在真实的双向力交换。  
    左边的 `create_soft_contacts` 说明 bunny 是 mesh query，不是 particle cloud；右边的 `eval_particle_body_contact` 说明同一份 penalty contact 同时更新 cloth particle 和 rigid bunny。

## Slide 9 — H1 Method Note: Why We Do Not Lower Rope Mass Alone
    这一页把实验设计边界讲清楚。  
    在 Newton core 里，spring force 直接由 `ke` 和 `kd` 决定，而粒子积分再乘一次 `inv_mass`。  
    所以如果只单独改 rope mass，不改 spring 和 contact，系统的有效 `ke / m`、`kd / m` 都会一起变，已经不是同一根 rope 了。

## Slide 10 — H1: Short IR Pipeline Reconstructs The Right Newton Objects
    这页要证明 bridge 做的是 native reconstruction，不是 replay 旧轨迹。  
    importer 直接把 IR 里的 object arrays 变成 Newton particles 和 springs，再把 bunny 变成 rigid body + attached mesh shape，最后才交给 solver。

## Slide 11 — H1: Mesh Defines Contact; Rigid State Moves The Bunny
    这一页继续把 geometry 和 dynamics 拆开。  
    mesh query 决定 contact point 和 normal 在哪里；contact kernel 再把这份力写成 rigid bunny 的 force 和 torque。  
    所以最准确的说法是：mesh 定义 contact geometry，rigid state 接收 reaction wrench。

## Slide 12 — H1 Result: Deformable-Rigid Interaction Is Validated
    到这里，H1 的最小 claim 已经成立：  
    object-only rope 在 Newton 里已经能和 novel rigid bunny 发生真实双向互动。

## Slide 13 — H1 Addendum: Rope+Bunny Still Works At 1 kg And 5 kg Total Rope Mass
    这里把 rope total mass 调成 `1 kg` 和 `5 kg` 做对照。  
    takeaway 是：interaction 仍然在，更重的 rope 只是让 bunny 的响应更明显。

## Slide 14 — H1 Addendum: Cloth+Bunny OFF Still Works At 1 kg And 5 kg Total Cloth Mass
    这一页把 H1 扩展到 cloth+bunny，而且明确是 self-collision OFF。  
    takeaway 还是 interaction 还在，不是说 weight 一变 interaction 就没了。

## Slide 15 — H1 Addendum: Cloth+Bunny OFF Still Works At 0.1 kg And 0.5 kg Total Cloth Mass
    这里进一步把 cloth total mass 压到低质量区间。  
    作用是把 H1 和 H2 分开：低质量 cloth 仍然可以和 bunny 互动，但 penetration 问题并没有自动消失。

## Slide 16 — H2 Counterexample: 1x/2x Radius Still Penetrates Bunny
    H2 从最直接的 radius sweep 开始。  
    先看 `1x` 和 `2x`：radius 变大有帮助，但 penetration 没有消失。

## Slide 17 — H2 Counterexample: 3x/4x Radius Still Penetrates Bunny
    这里继续把 `particle_radius` 往上推到 `3x` 和 `4x`。  
    这页服务的是同一个结论：radius 是重要旋钮，但不是一开就 pass 的单旋钮。

## Slide 18 — H2 Counterexample: 8x/10x Radius Still Penetrates Thin Ears
    到 `8x` 和 `10x` 时，thin ear 仍然会出问题。  
    所以这页的重点是：即使暴力放大 radius，薄耳朵这类 geometry 仍然不是一个干净的 parameter-only 问题。

## Slide 19 — H2 Counterexample: Bunny Is Harder Than Thick Box At Same Radius
    这页把 geometry 单独拿出来对比。  
    同样的 cloth、同样的 rigid mass、同样的 radius，box 仍然比 bunny 更容易提供稳定支撑。

## Slide 20 — H2 Counterexample: 1x/1.5x Bunny Size Still Penetrates
    这里开始只改 bunny size。  
    即使把 bunny 放大到 `1.5x`，penetration 仍然存在，所以不能简单说“只是因为 bunny 太小”。

## Slide 21 — H2 Counterexample: 2x/3x Bunny Size Still Penetrates
    这一页继续把 bunny 放大到 `2x` 和 `3x`。  
    rigid geometry 的确变了，但 penetration 还是没有自动消失。

## Slide 22 — H2 Counterexample: Smaller `dt` Still Does Not Eliminate Penetration
    这里单独测试 timestep。  
    把 `dt` 再缩两个数量级以后，penetration 仍然在，所以它最多是 numerical sanity check，不是主解。

## Slide 23 — H2 Counterexample: Even 0.01 kg And 0.005 kg Still Penetrate Bunny
    这里把 cloth total mass 再压低一个量级，到 `0.01 kg` 和 `0.005 kg`。  
    结果还是 nonzero penetration，所以更小的 cloth weight 也不是自动解法。

## Slide 24 — H2: Bunny Penetration Is Mainly A Support Problem
    到这里，counterexample 已经够多了。  
    这一页正式把 H2 的问题写窄：我们不是在怀疑 mesh contact 是否存在，而是在问 external support quality 到底为什么还不够。

## Slide 25 — H2 Evidence: Continuous Mesh Contact Still Depends On `particle_radius`
    这页把源码里的机制再说清楚。  
    detection 条件是 `d < margin + radius`，force 里 penetration depth 也直接减了 `radius`。  
    所以 `particle_radius` 同时控制接触何时开始发生，以及 penalty support 何时开始把 cloth 往外推。

## Slide 26 — H2: 64-Run OFF Grid Separates Three Main Effects
    这页说明我们不是在 cherry-pick 视频。  
    64-run OFF grid 固定其余条件，只扫三个主轴：`contact_collision_dist`、drop height、bunny mass。

## Slide 27 — H2: `contact_collision_dist` Dominates Across 64 OFF Runs
    这页把 aggregate trend 画出来。  
    takeaway 是：在 OFF 模式下，`contact_collision_dist` 是最强主旋钮；bunny mass 有帮助，但不是主杠杆。

## Slide 28 — H2: Bunny Now Has A Near-Working Point
    这页给出目前最好的 bunny working point。  
    它说明我们不是完全没进展，而是已经逼近一个 near-working regime，只是还没有把 root cause 讲清楚。

## Slide 29 — H2 Mechanism: Trigger-Substep Force Diagnostic Separates Contact vs Spring
    这一页补上 H2 里最缺的机制证据。  
    我们在 trigger collision 的 substep 上，把 outward normal、external contact force、spring-maintenance force 和 resulting acceleration 分开可视化。  
    先用 clean box control 做 sanity check：如果 box case 的方向都不对，那后面 bunny 耳朵的讨论就没有意义。

## Slide 30 — H2 Result: Validated And Falsified Hypotheses
    这一页把 H2 收成一句话。  
    被验证的是：radius 重要、box 比 bunny 更容易支撑、thin ear geometry 特别难。  
    被否掉的是：只靠减小质量、减小 height 或减小 `dt` 就能把问题彻底解决。

## Slide 31 — H3: Newton Self-Collision Is Not PhysTwin Parity
    到这里，H2 的 external contact counterexample 已经够密了。  
    H3 负责给方法论边界：我们不能把 Newton native self-collision 讲成 PhysTwin self-collision parity。

## Slide 32 — H3: PhysTwin And Newton Use Different Self-Collision Models
    这页把差异落到 trigger 和 update 变量上。  
    PhysTwin 更像 approach-gated velocity correction；Newton 更像 overlap-triggered penalty-force accumulation。  
    所以这不是小调参，而是 contact model difference。

## Slide 33 — H3 Result: `self-collision ON` Is Only A Newton-Native Ablation
    所以 H3 的结论很明确：  
    `self-collision ON` 可以当 Newton-native ablation 展示，但不能当 PhysTwin parity evidence。

## Slide 34 — H4: Pair-Filtered Multi-Deformable Interaction Is Viable
    H4 的问题变成：多个 deformables 能不能彼此稳定互动，而不是只和 rigid 互动。  
    这里的 hypothesis 不是重写 physics，而是只改 pair selection。

## Slide 35 — H4: We Changed Pair Selection, Not The Physics Model
    这一页把 H4 的 intervention 说清楚。  
    我们保留 Newton 的 HashGrid 和 penalty model，只过滤允许哪些 particle pair 真正互动。

## Slide 36 — H4 Result: Filtered Cross-Object Contact Already Works In Two Demos
    这页给出两个最小正结果：rope+rope 和 rope+sloth。  
    它们说明 pair-filtered multi-deformable interaction 已经是 working demo，不只是概念。

## Slide 37 — H4 Addendum: Two-Rope Weight Contrast Still Works
    这里再补一个质量对照。  
    即使 lower rope 和 upper rope 的 total mass 不一样，cross-rope interaction 仍然存在，而且视频上仍然可读。

## Slide 38 — H4 Addendum: Two Crossed Ropes Also Work On A Rigid Box
    这页把 shared rigid support 拉进 H4。  
    不是只有 ground-only 场景能看见 rope-rope interaction，换成 one rigid box 也还能看见。

## Slide 39 — H4 Addendum: Native Franka Can Lift And Release The Bridge Rope
    这页把 H4 再往 downstream interaction 推一步。  
    这里已经不是 proxy pusher，而是直接复用 Newton 自带的 Franka Panda asset。  
    视频里现在能读出完整四段：no-contact start、approach、sustained lift、release result。  
    这次我会顺手把 4 个数字讲清楚：first contact 约 `88.4 ms`，contact duration 约 `90.4 ms`，rope COM displacement 约 `156.3 mm`，peak midpoint lift 约 `9.1 mm`。  
    接触判据这里也不再是假想 gripper center，而是 `gripper_center + fingers + finger span` 的 calibrated proxy，所以视频和 summary 现在是一致的。  
    所以这页的 claim 我会讲窄一点：这是 `taskful native baseline`，不是 full force-feedback robot policy。

## Slide 40 — H5: MPM One-Way Is Useful; Two-Way Is Not The Main Path
    H5 不是说 MPM 没用，而是把它放回正确位置。  
    问题不在 one-way 是否能做，而在 two-way spring-mass support 是否值得继续当主线。

## Slide 41 — H5: One-Way MPM Works; Two-Way Should Be Deprioritized
    这页给 H5 的正结果。  
    one-way kinematic collider 是工作的；真正不该继续当主线的是 two-way spring-mass support。

## Slide 42 — Newton Playground Profiling: Rope Replay Is Solver-Bound, Not Collision-Bound
    这一页补的是 infrastructure 结论，不是新的 physics claim。  
    在完整 rope-control replay 里，关掉 rendering 以后，主成本不是 collision generation，而是 internal spring-mass update：`integrate_particles`、`spring_forces`、`write_kinematic_state` 和 `drag_correction`。  
    所以下一步如果要做性能优化，应该先盯 internal update path，而不是先猜 broad phase。

## Slide 43 — Summary: Which Hypotheses Survived
    这一页把整个 deck 收紧。  
    H1 bridge interaction 成立，H2 external-support diagnosis 成立，H4 pair-filtered multi-deformable 成立。  
    H3 只给方法边界，H5 说明 MPM one-way 有用但 two-way 不该继续当主线。

## Slide 44 — Next Step: Fewer Slides, Stronger Evidence
    最后一页说下一步。  
    我们不会再继续无止境加页数，而是把每个 hypothesis 压成更短、更硬的 evidence chain：  
    一页 flow、一页 source proof、一页 best demo，再加上 profiling 和 force-diagnostic 这种真正能解释问题机制的页。
