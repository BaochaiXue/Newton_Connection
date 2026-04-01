# Implement: self_collision_transfer

## Preconditions

- confirm the controlled box-support decision scene
- confirm which metrics already exist and which must still be added

## Canonical Commands

```bash
python Newton/phystwin_bridge/tools/other/run_final_self_collision_campaign.py --help
```

## Step Sequence

1. run or inspect the controlled decision matrix
2. add or verify peak-over-time overlap metrics
3. run bunny sanity-check and OFF-baseline parity regression on the selected mode
4. write the decision summary and slide-ready recommendation

## Validation

- selected mode satisfies the declared acceptance line
- OFF-baseline regression remains acceptable

## Output Paths

- self-collision campaign result bundle(s)
- decision summary and slide-ready assets
