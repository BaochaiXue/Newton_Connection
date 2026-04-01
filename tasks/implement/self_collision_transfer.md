# Implement: self_collision_transfer

## Preconditions

- confirm the controlled box-support decision scene
- confirm which metrics already exist and which must still be added
- confirm whether the target is:
  - cloth+box scene evidence (`off/native/custom` only)
  - or strict cloth parity (`phystwin` with self-collision + implicit ground plane)

## Canonical Commands

```bash
python Newton/phystwin_bridge/tools/other/run_final_self_collision_campaign.py --help
python Newton/phystwin_bridge/tools/other/run_strict_self_collision_parity.py --help
python Newton/phystwin_bridge/tools/other/newton_import_ir_phystwin.py --help
python Newton/phystwin_bridge/tools/other/diagnose_phystwin_collision_table.py --help
python Newton/phystwin_bridge/tools/other/diagnose_controller_spring_semantics.py --help
```

## Step Sequence

1. run or inspect the controlled cloth+box decision matrix (`off/native/custom`)
2. use the shared strict `phystwin` importer path only for the PhysTwin-native cloth parity scene
3. treat strict `phystwin` as the frame-frozen explicit-table path by default and use the dynamic-query path only as a debug override
4. rerun OFF-baseline regression after any bridge-side `phystwin` change
5. run the collision-table and controller-spring diagnostics before claiming any rollout-level explanation
6. write the decision summary and slide-ready recommendation, clearly separating scene evidence from strict parity evidence

## Validation

- selected mode satisfies the declared acceptance line
- OFF-baseline regression remains acceptable
- cloth+box `phystwin` fails fast instead of silently mixing Newton box contact
- strict `phystwin` parity reports the narrowed contact scope explicitly
- strict `phystwin` parity reports the active candidate mode explicitly

## Output Paths

- self-collision campaign result bundle(s)
- decision summary and slide-ready assets
