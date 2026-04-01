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
```

## Step Sequence

1. run or inspect the controlled cloth+box decision matrix (`off/native/custom`)
2. use the shared strict `phystwin` importer path only for the PhysTwin-native cloth parity scene
3. rerun OFF-baseline regression after any bridge-side `phystwin` change
4. write the decision summary and slide-ready recommendation, clearly separating scene evidence from strict parity evidence

## Validation

- selected mode satisfies the declared acceptance line
- OFF-baseline regression remains acceptable
- cloth+box `phystwin` fails fast instead of silently mixing Newton box contact
- strict `phystwin` parity reports the narrowed contact scope explicitly

## Output Paths

- self-collision campaign result bundle(s)
- decision summary and slide-ready assets
