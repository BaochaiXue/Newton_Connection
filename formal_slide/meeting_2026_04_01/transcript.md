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

## Slide 8 — H1: On The Same Rope Replay, How Far Is Newton From PhysTwin?
这里开始进入第二段 Newton Interactive Playground 性能 Profiling，而且这次只讲 rope case，不再讲 robot case。
教授要求的研究顺序很清楚：先建立 apples-to-apples benchmark，再解释 gap，最后才谈优化。
因此第一步不是优化，而是问一个简单的问题：在同一个 `rope_double_hand` replay、完全一致的物理设定下，去掉 rendering 之后，Newton 到底比 PhysTwin 快还是慢。
rope case 之所以适合作为这个 benchmark，是因为它是弱碰撞 path。也就是说，如果这里仍然有明显 slowdown，第一嫌疑不应该自动落到 collision model 上。
公平条件必须写死：same rope case、same controller replay、same `dt`、same `substeps`、same GPU、no render。
同 case identity 不是口头假设。当前 committed benchmark 里，PhysTwin controller trajectory 和 IR 的 max abs diff 是 0.0e+00，所以输入轨迹本身已经对齐。

## Slide 9 — Source Proof P1: The Rope Core Is Spring Force + Semi-Implicit Update
这一页先不谈 graph，不谈优化，只回答一个更基础的问题：rope case 两边是不是在做可比的 spring-driven semi-implicit update。

[Newton/newton/newton/_src/solvers/solver.py : 38-46]
```python
# simple semi-implicit Euler. v1 = v0 + a dt, x1 = x0 + v1 dt
v1 = v0 + (f0 * inv_mass + world_g * wp.step(-inv_mass)) * dt
v1_mag = wp.length(v1)
if v1_mag > v_max:
    v1 *= v_max / v1_mag
x1 = x0 + v1 * dt
x_new[tid] = x1
v_new[tid] = v1
```
[What]
L38 明确把 Newton 粒子积分写成 semi-implicit Euler：先速度、后位置，这给出了最核心的时间推进骨架。
L39 真正的速度更新是 `v1 = v0 + a dt`，其中加速度来自力除以质量再加重力项，所以它是力驱动更新，不是位置投影黑盒。
L41-L43 是速度限幅稳定化，它不改变“先求新速度、再推进位置”的积分结构，但会在极端高速时截断数值爆炸。
L44 把新位置写成 `x1 = x0 + v1 dt`，这正是 semi-implicit Euler 和 explicit Euler 的关键差异：位置用的是新速度而不是旧速度。
L46-L47 把 `x1` 和 `v1` 写回 state，所以这一段不是抽象描述，而是 Newton core 真正落地的粒子推进算子。
[Why]
这段代码的说服力在于，它把 Newton 这一侧的核心时间推进直接对应到物理公式 `v_{t+1}=v_t+a_t\Delta t, x_{t+1}=x_t+v_{t+1}\Delta t`。
也就是说，如果 rope case 的主要工作量确实来自 spring force 和粒子推进，那么 Newton 这边的核心数学并不是一开始就和 PhysTwin 完全不同的另一套东西。
[Risk]
这里要诚实地降 claim：这段代码证明的是 Newton core 采用可比的 semi-implicit particle update intent，不是逐字符证明 Newton rope implementation 和 PhysTwin rope implementation 完全同构。
所以这页不能单独推出“所有公式完全一样”，但足以支撑一个更窄、更诚实的判断：弱碰撞 rope case 的主更新结构不是天然 collision-first。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 123-132, 156-160]
```python
spring_force = (
    wp.clamp(wp.exp(spring_Y[tid]), low=spring_Y_min, high=spring_Y_max)
    * (dis_len / rest - 1.0)
    * d
)
v_rel = wp.dot(v2 - v1, d)
dashpot_forces = dashpot_damping * v_rel * d
overall_force = spring_force + dashpot_forces
...
all_force = f0 + m0 * wp.vec3(0.0, 0.0, -9.8) * reverse_factor
a = all_force / m0
v1 = v0 + a * dt
v2 = v1 * drag_damping_factor
```
[What]
L123-L127 把 PhysTwin rope 的主内力写成 spring term：弹簧模量乘以应变 `(dis_len / rest - 1)` 再沿当前边方向 `d` 施加。
L129-L130 再加上 dashpot 阻尼项，也就是相对速度在边方向上的投影乘阻尼系数，这对应一维 Kelvin-Voigt 式的阻尼弹簧近似。
L132 把 spring 和 dashpot 合成 `overall_force`，说明这一侧的主动力学不是 contact impulse，而是 internal spring-damper force。
L156-L158 把总力加上重力再除以质量得到加速度 `a`，这一段直接把力学公式 `a = F/m` 写成代码。
L159 用 `v1 = v0 + a dt` 更新速度，L160 再施加 drag 衰减，所以 PhysTwin 这边的核心推进同样是 force-driven velocity update。
[Why]
这段源码真正参与说理的地方在于，它明确告诉我们 rope case 的主要物理量是 spring force、dashpot damping、gravity 和基于 `dt` 的速度推进。
因此如果当前 benchmark 选的是 weak-collision rope replay，那么首先应该怀疑的是 spring/integration path 的 runtime organization，而不是把 slowdown 直接归罪给 collision model。
[Risk]
这里同样要诚实：PhysTwin 这段代码比 Newton 侧展示得更具体，因为它直接把 spring force kernel 写出来了；Newton 侧我们目前展示的是 core integrator，而不是 rope-specific force assembly。
所以我们在 slide 上只能写“closely comparable semi-implicit rope update intent”，不能夸张成“逐项完全同一个 kernel”。

## Slide 10 — Result P1: On The Fair Rope Replay, Newton A1 Is Still 3.30x Slower
这张表只回答 throughput gap 本身，不提前解释原因。
完整 rope replay 现在已经做成 same-case apples-to-apples throughput table。264 个 trajectory frame 展开以后是 175421 个 substep，对应 8.77 秒物理时间。
authoritative 数字很直接：Newton A0 `0.066934 ms/substep`，Newton A1 `0.035721 ms/substep`，PhysTwin B0 `0.010840 ms/substep`。
A0 和 A1 的差别只是在 controller target 的组织方式，不是换了一套物理任务。
所以这页给出的核心事实是：即使把 repeated controller write 降下来，Newton A1 仍然比 PhysTwin B0 慢 `3.295x`。

## Slide 11 — Source Proof P2: The Slow Path Is Runtime Structure, Not Rope Physics
这一页回答的是：如果 rope case 的主物理意图已经是可比的，那么 residual gap 更像出在什么层面。

先把调用链说清楚。我们自己的 realtime viewer 在 `[Newton/phystwin_bridge/demos/demo_rope_control_realtime_viewer.py : 342-347, 738]` 明确实例化并调用的是 `newton.solvers.SolverSemiImplicit`。所以左边这段不是 generic example，而是 rope viewer 真会走到的 Newton core solver path。

[Newton/newton/newton/_src/solvers/semi_implicit/solver_semi_implicit.py : 141-145, 160-165, 172-177]
```python
# damped springs
eval_spring_forces(model, state_in, particle_f)
# triangle elastic and lift/drag forces
eval_triangle_forces(model, state_in, control, particle_f)
...
# particle-particle interactions
eval_particle_contact_forces(model, state_in, particle_f)
# triangle/triangle contacts
if self.enable_tri_contact:
    eval_triangle_contact_forces(model, state_in, particle_f)
...
# particle shape contact
eval_particle_body_contact_forces(
    model, state_in, contacts, particle_f, body_f_work, body_f_in_world_frame=False
)
self.integrate_particles(model, state_in, state_out, dt)
```
[What]
L141-L145 说明 `SolverSemiImplicit.step()` 并不是一个单一 rope kernel，而是先后调用多个物理子阶段，其中 rope 相关的第一块就是 damped spring forces。
L160-L165 说明 solver 内部还会继续串上 particle contact 和 triangle contact 这些阶段；即使当前 rope case 是弱碰撞，这条 stage pipeline 依然存在。
L172-L177 最后才进入 particle-shape contact 和 `integrate_particles(...)`，也就是力学阶段先累积，再统一推进粒子状态。
所以左边真正给出的信息是：我们当前 viewer 调到的 Newton core solver path，本身就是 multi-stage step organization，而不是一个只做 rope force 的最小路径。
[Why]
这段代码真正参与说理的地方在于，它把“Newton core solver actually used by our rope viewer”这件事讲实了。
既然 viewer 最终落到的是 `SolverSemiImplicit.step()`，而这条 core path 本身是多阶段串行组织，那么 rope slowdown 的第一怀疑对象就可以自然落到 runtime structure，而不是先落到 spring formula 不一致。
[Risk]
这里要诚实的 caveat 变成另外一个问题：这段代码证明的是 solver 内部 stage organization，但它并不单独量化每个 stage 的 wall time 占比。
所以它只能和 throughput / profiler 证据一起用，不能单独推出 residual gap 的精确比例。

[PhysTwin/qqtt/model/diff_simulator/spring_mass_warp.py : 769-802]
```python
if cfg.use_graph:
    if cfg.data_type == "real":
        with wp.ScopedCapture() as capture:
            self.step()
            self.calculate_loss()
        self.graph = capture.graph
...
with wp.ScopedCapture() as forward_capture:
    self.step()
self.forward_graph = forward_capture.graph
```
[What]
L769-L782 表明 PhysTwin rope source 在 `use_graph` 打开时，会直接把核心 step path capture 成 graph，并保存在 `self.graph` 里。
L800-L802 进一步保留了一个专门的 `forward_graph`，说明它不仅有训练路径 graph，还有一个明确的前向 replay graph。
[Why]
这段代码直接参与后面的 bottleneck 判断，因为它说明 PhysTwin rope core 本身就把 graph replay 当成一等执行路径，而不是外部 profiling harness 临时包出来的技巧。
结合前一页的 throughput 结果，它给我们的不是最终证明，而是一个很强的结构性解释方向：两边的主要差异更像 runtime organization，而不是 rope physics 本身。
[Risk]
这里同样不能过度宣称：这段源码只能证明 PhysTwin core 明确拥有 graph replay 路径，不能单独证明 Newton residual gap 的全部比例都来自 launch structure。
最后仍然要结合系统级 timing 证据，也就是上一轮 benchmark 里的 A0/A1/B0/B1 和 profiler 结果。

## Slide 12 — Takeaway P1: Measure The Gap First, Locate The Slow Stage Second
这一页把 profiling 逻辑收束成真正的研究顺序，而不是内部优化待办。
第一，公平 benchmark 已经把 gap 定量出来：Newton A1 相对 PhysTwin B0 的 slowdown 是 `3.295x`。
第二，A0 到 A1 的 speedup 是 `1.874x`，所以 controller-write overhead 确实存在，但它不能独自解释全部差距。
第三，A3 里 collision 只有 `0.004 ms/substep`，而 rope case 本身又是弱碰撞，这使得 collision-first explanation 没有说服力。
所以这段 profiling 的正确收束方式不是“马上去优化”，而是先承认研究顺序：先 benchmark，后定位 bottleneck，再做针对性优化。
只有当 bottleneck explanation 被讲清楚以后，后面的优化目标，例如更 graph-like 的 replay、更少的 launch、更少的 host/device 往返，才会有说服力。

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

## Slide 18 — Hypothesis S1: Native Newton Is Not Enough For The Final Self-Collision Claim
这里开始进入第四段 self-collision, Newton way。
这一章不再用静态 campaign board 讲，而是收成一个 hypothesis-driven block。
这一页先把 hypothesis 说清楚：如果 native Newton 已经足够，我们就不需要 bridge-side phystwin 这条更窄的 exact path。
同时 claim boundary 也要收紧：strict parity 只针对 PhysTwin 原生定义的 cloth self-collision 加 implicit ground，不把 box-support semantics 混进 exact claim 里。
当前 progress 也要一句话说死：operator exactness 已经过，但 rollout parity 仍然 blocked。

## Slide 19 — Source Proof S1: PhysTwin Native Contact Scope Is Pairwise Self-Collision + Ground
这一页只用 PhysTwin upstream source 来证明 strict parity 的 scope，不再 cite 我们自己的 bridge code。
左边这段是 `object_collision`，说明 PhysTwin 原生的 cloth contact 里有 pairwise object self-collision，而且速度修正是基于 collision impulse average。
右边这段是 `integrate_ground_collision`，说明 PhysTwin 原生还定义了 implicit ground-plane TOI 和 velocity update。
所以 strict parity 的 claim boundary 不是拍脑袋收窄，而是直接从 PhysTwin native contact source 推出来的：object self-collision 加 ground collision。
也正因为这个 source scope，本章后面的 cloth+box scene 只能作为 decision/demo evidence，不能被包装成 strict parity scene。

## Slide 20 — Result S1: Native Is Not Enough On The Controlled Cloth+Box Scene
这一页是 scene-level video evidence，不是源码页。
这里直接放 controlled cloth+box decision videos：OFF、native、custom H2、phystwin。
这页要回答的 hypothesis 很窄：native 能不能直接承担 final self-collision claim。
目前 answer 仍然是否定的。能继续 defend 下去的是 bridge-side phystwin candidate，而不是 native。
所以这页的 progress 不是“所有问题都 solved”，而是 decision scene 已经把 native 不足这件事视频化、可比较化了。

## Slide 21 — Progress S2: The Demo Is Ready, But Strict Parity Is Still Blocked
最后这一页把当前 self-collision progress 和 blocker 同时讲清楚。
左边是已经可汇报的 cloth+box `phystwin` hero demo，它通过了 black/blank、motion 和 scene-visibility 的 QC，所以 video claim 已经成立。
右边是 parity support video，用来提醒老师：strict parity 的 in-scope reference path 仍然在，而且我们不是拿错 scene 在讲 parity。
同时 exactness 本身也已经过了，`max_abs_dv` 在 1e-6 量级、`median_rel_dv` 在 1e-8 量级。
但 full rollout parity 仍然停在 1e-2 量级，所以当前 honest progress 应该讲成：demo-ready yes，operator exact yes，strict rollout parity not yet。

## Slide 22 — Conclusion R1: The Current Robot-Deformable Claim Is A Defendable Native Baseline
最后一段是 robotic with deformable objects。
这一章今天的可 defend 结论，不是“完整 manipulation 已经完成”，而是 native Franka 的 release/drop baseline 已经成立，所以 robot-deformable chapter 至少有了一个物理上可信、视频上可读的起点。
更具体地说，它用 `demo_robot_rope_franka.py` 里的 `drop_release_baseline` 证明了：robot visible、rope 先被 support、release 前先过 settle gate、release 后以 gravity-dominated free fall 落到 real ground collider，而且 presentation video 保持 1:1 time。
所以这页不是把 robot 章节降格成一个无关小 demo，而是把它收敛成当前最能 defend 的子结论。
右边保留 matched drag ON 版本，只是为了说明 A/B 已经做过。结论不是“drag 救了 free fall”，而是 OFF 和 ON 都通过主 gate，所以 drag 不是这个 baseline 的根因解释。
