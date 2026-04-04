# Visible Rigid Tool Baseline Diagnosis Board

Last updated: 2026-04-04

| Candidate design choice | Why it is honest / dishonest | Visual risk | Contact risk | Implementation cost | Validation plan |
| --- | --- | --- | --- | --- | --- |
| short rounded rod | honest if the physical capsule and visible capsule use the same dimensions and transform | medium | low-medium | medium | tool/collider dimension report + full-video review |
| short rounded paddle | honest if physical box and visible box match exactly | low | low | low | tool-vs-collider report + event sheet |
| blunt hook | visually plausible but easier to misread/occlude and easier to fake with a hidden nose | medium-high | medium | medium-high | extra contact-sheet windows and validation-camera audit |
| single-finger-mounted rod with open gripper | dishonest in the current tabletop motion because the opposite bare finger can still contact first even if the tool itself is real and visible | medium | high | low | reject if `actual_finger_box_first_contact_time_s < actual_tool_first_contact_time_s` |
| single-finger-mounted rod with nearly closed gripper | potentially honest, but current quick tests still allow bare-finger-first contact or frame-0 start-in-contact when the motion/control semantics are not tool-aware | medium | medium-high | medium | require tool-first onset and no frame-0 contact in rollout diagnostics |
| central link7-mounted rod without tool-aware path | visually plausible, but on the current inherited body path it still reaches the rope later than bare finger contact | medium | medium-high | medium | replay-style clearance study before rerun |
| tool-aware IK or tool-aware trajectory | currently the only promising honest direction because it can make the visible tool, not an old gripper-center reference, define the first-contact geometry | medium | medium | medium-high | rerun full bundle only after onset ordering flips to tool-first |
