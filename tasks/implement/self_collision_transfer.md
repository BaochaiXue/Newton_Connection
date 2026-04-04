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
python Newton/phystwin_bridge/tools/other/run_ground_contact_self_collision_rmse_matrix.py --help
python Newton/phystwin_bridge/tools/other/newton_import_ir_phystwin.py --help
python Newton/phystwin_bridge/tools/other/diagnose_phystwin_collision_table.py --help
python Newton/phystwin_bridge/tools/other/diagnose_controller_spring_semantics.py --help
```

## Step Sequence

1. use the PhysTwin-native cloth + implicit-ground scene for the controlled law-isolation matrix
2. run `run_ground_contact_self_collision_rmse_matrix.py` to get the fair `2 x 2` comparison:
   - self OFF / ground native
   - self OFF / ground phystwin
   - self phystwin / ground native
   - self phystwin / ground phystwin
3. verify the matrix fairness check before interpreting any RMSE delta
4. rerun OFF-baseline regression after any bridge-side contact-stack change
5. run the collision-table and controller-spring diagnostics before claiming any rollout-level explanation
6. write the blocker summary against the matrix and diagnostic evidence, not against mixed scenes

## Validation

- selected mode satisfies the declared acceptance line
- controlled `2 x 2` matrix proves which law pair actually ran in each case
- OFF-baseline regression remains acceptable
- cloth+box `phystwin` fails fast instead of silently mixing Newton box contact
- strict `phystwin` parity reports the narrowed contact scope explicitly
- strict `phystwin` parity reports the active candidate mode explicitly

## Output Paths

- self-collision campaign result bundle(s)
- decision summary and slide-ready assets
