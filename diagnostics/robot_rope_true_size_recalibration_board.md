# True-Size Rope Recalibration Diagnosis Board

Last updated: 2026-04-03

| Suspected coupled factor | Evidence | Confidence | How to measure it | Candidate fix |
| --- | --- | --- | --- | --- |
| stale tabletop_curve shape | smaller physical radius may expose weird laydown / under-supported shape | medium | compare `tabletop_curve` vs `ir_shifted` after preroll settle | retune or replace laydown mode |
| insufficient hidden preroll settle | smaller rope may keep residual irregularity longer | medium | compare preroll metrics and first visible frames | raise preroll settle/damping |
| stale tabletop-rope-height | push trajectory may no longer match the shrunk rope top | high | measure settled rope center and rope-top height | recompute rope-height / contact stack |
| stale tabletop-ee-offset-z | finger may now be effectively too high | high | inspect actual finger-box clearance over time | sweep `tabletop-ee-offset-z` first |
| stale contact/push clearances | old clearances were tuned for thicker rope | high | compare actual finger-box first contact times across runs | sweep contact/push clearances |
| stale XY push offsets | finger may arrive beside the new laydown instead of into it | medium | compare current laydown center vs push-contact offset | bounded XY sweep |
| stale robot base offset | robot may approach from a no-longer ideal side | medium | compare reachability from current base | bounded base-offset sweep |
| render-only / physical mismatch | fixed in c12, but becomes wrong again if visual and physical sizes diverge | low | confirm visual radius follows physical radius | keep visual radius honest |
| actual finger-box contact happening too late | c15/c16 indicate later onset than c12 | high | compare summary contact onset times | adjust laydown + Z stack + XY together |
| camera making a true near-touch look like a miss | likely contributor after physics changes | medium | compare hero vs validation windows | tighten hero framing only after physics is right |
