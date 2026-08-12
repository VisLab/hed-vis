# Log: sternberg / event_type_task_role

Built from `eeg_ds004117s_hed_sternberg` (hed-examples, read-only). 8 event files,
2 subjects (sub-001, sub-003), 4 runs each, 2801 rows, 1 excluded, 2800 used, all
pooled. Columns: `event_type`, `task_role`. Result: 13 nodes, 21 edges, 200 trials.

Files written, all under `sternberg/models/event_type_task_role/`:

- `sternberg_event_type_task_role.json` - the model
- `sternberg_event_type_task_role_keymap.tsv` - keymap with pooled counts
- `reports/model_summary.md`, `reports/log.md` - this directory

The rules are in `../../../../../model_rules.md`. This file holds dataset findings,
the calls I made, and open questions. The model itself is `../sternberg_event_type_task_role.json`.

## Trial identification and exclusion

Two passes, using no trial column.

**Pass A** maps every row to a node with nothing excluded, then segments each file into
trials: a complete trial runs from a `start_nodes` event (`N0` Fixation) to the first
following `end_nodes` event (`N12` Rest), with no intervening start event. Rows left
outside a complete trial are exclusion candidates.

```
file              rows  trials  incompl   orphan rows
sub-001_run-1      350      25        0             -
sub-001_run-2      350      25        0             -
sub-001_run-3      350      25        0             -
sub-001_run-4      350      25        0             -
sub-003_run-1      350      25        0             -
sub-003_run-2      350      25        0             -
sub-003_run-3      351      25        0        0 (N7)
sub-003_run-4      350      25        0             -
```

One orphan: row 0 of `sub-003 ... run-3`, a `left_click` / `ignored_correct` at onset
2.624 - the tail of a trial that began before recording started. It cannot be
identified by column values, since that same combination is a legitimate node 89 other
times.

**Pass B** rebuilds with that row excluded. `excluded_rows` is now recorded as a file
plus row indices, not a column filter:

```json
"excluded_rows": [
    {
        "file": "sub-003/ses-01/eeg/sub-003_ses-01_task-WorkingMemory_run-3_events.tsv",
        "rows": [0],
        "row_index": "0-based over data rows, header excluded",
        "reason": "Orphan events outside any complete trial: no start-of-trial event precedes them in the file."
    }
]
```

The segmentation did not change after exclusion, so one iteration sufficed. The
generator asserts no orphans remain, which is what would catch a case needing more.

**Independent check.** The derived boundaries were compared against the dataset's
`trial` column, which the model never uses: **200 agree, 0 disagree.** After exclusion
all 8 files begin on `Fixation` and end on `Rest`, and no edge is an anomaly.

## Incorrect responses are data, not artifacts

Corrected from the previous pass, where I wrongly grouped `ButtonInBad` and
`ButtonOutBad` with the orphan row as things "at risk". They are the dependent measure
- the task exists to measure how well the participant remembers - so they are modeled
like any other node, and their descriptions now say so.

Accuracy per file, which is the measurement:

```
file               hit    cr   miss    fa   pct_correct
sub-001_run-1       14    10      1     0        96.0%
sub-001_run-2       13    10      1     1        92.0%
sub-001_run-3       14     9      1     1        92.0%
sub-001_run-4       10    14      0     1        96.0%
sub-003_run-1       15    10      0     0       100.0%
sub-003_run-2       14    11      0     0       100.0%
sub-003_run-3       15    10      0     0       100.0%
sub-003_run-4        9    15      1     0        96.0%
POOLED             104    89      4     3        96.5%
```

Consistent with the README ("responses in the task were largely correct"). Note that
pooling averages away the thing being measured: sub-001 runs 92-96%, sub-003 is 100%
on three of four runs, and the pooled 96.5% describes neither. See open question 1.

This is also why a low edge count proves nothing on its own. The miss edge `E(4,8)` has
n=4 and is real; the orphan edge had n=1 and was not. Only the trial-boundary pass
separates them.

## Pooling

Counts are pooled over all 8 files. Per-file node counts, then the pooled total:

```
file            N0    N1    N2    N3    N4    N5    N6    N7    N8    N9   N10   N11   N12
sub-001_run-1   25    75   125    25    15    10    14    10     1     0    24     1    25
sub-001_run-2   25    77   123    25    14    11    13    10     1     1    23     2    25
sub-001_run-3   25    73   127    25    15    10    14     9     1     1    23     2    25
sub-001_run-4   25    75   125    25    10    15    10    14     0     1    24     1    25
sub-003_run-1   25    75   125    25    15    10    15    10     0     0    25     0    25
sub-003_run-2   25    77   123    25    14    11    14    11     0     0    25     0    25
sub-003_run-3   25    73   127    25    15    10    15    11     0     0    25     0    25
sub-003_run-4   25    75   125    25    10    15     9    15     1     0    24     1    25
POOLED         200   600  1000   200   108    92   104    89     4     3   193     7   200
```

A single file gives 25 fixations; the model reports 200 = 8 x 25. The keymap sits in the model
directory, not in `sternberg/data/` - that directory holds 1 of the 8 source files and
made the counts look single-file.

## Phase assignment

Everything maps onto the existing vocabulary in `model_rules.md`; no new phase names
were needed. Each phase cites the README section that establishes it:

| phase | nodes | README section |
|---|---|---|
| start_trial_phase | Fixation | [Trial initiation] / [Letter sequence presentation] |
| stimulus_phase | Green, Black | [Letter sequence presentation] |
| cue_phase | Memory | [Memory maintenance] |
| go_phase | ProbeIn, ProbeOut | [Memory probe] |
| response_phase | ButtonInGood, ButtonOutGood, ButtonInBad, ButtonOutBad | [Memory probe] |
| feedback_phase | FeedbackCorrect, FeedbackIncorrect | [Response feedback] |
| rest_phase | Rest | [Trial initiation] |

`Rest` is the `indicate_ready` node - the rules define rest-phase as "used when
participant must indicate ready to continue". There is no `end_trial_phase`: the ready
press directly triggers the next fixation cross (17-35 ms), so no separate
end-of-trial event exists.

## Ordering

Only phases are ordered, and the order comes from the README prose. Each phase carries
a `from_description` field quoting the text that establishes it. The data confirms
rather than derives it: the phase graph is a 7-node cycle, 20 of 21 edges `advances` or
`within_phase`, 1 `wraps`, no anomalies.

Within a phase the nodes have no intrinsic order. `stimulus_phase` is `repeated`
(letters recur and interleave); the other six are `alternatives`. Node numbers are a
naming convention only - `N6` through `N9` look sequential but are four mutually
exclusive outcomes of one button press.

**Where the cycle is cut is a choice.** The README opens the trial at
`[Trial initiation]` (the ready press); the model cuts at fixation, declared as
`start_nodes: ["N0"]`. That declaration is load-bearing now, since it is what segments
files into trials.

## Data findings

1. **`bad_trial` is in the sidecar but never in the data.** No node for it. Presumably
   it appears in the full 23-subject dataset, where it would mark whole trials to
   exclude - a different mechanism again from orphan rows, since those events would sit
   *inside* a complete trial.

2. **`value` is undocumented** and dropped at read time per your instruction, recorded
   in `generated_from.columns_ignored_not_in_sidecar`.

3. **`duration` units** - set aside; to be fixed in the dataset. Not reported.

## Checks that passed

- 200 trials derived, matching the `trial` column exactly (0 disagreements).
- After exclusion, all 8 files start on `Fixation` and end on `Rest`.
- `probe_target` letter is always in that trial's `to_remember` set (108/108);
  `probe_not_shown` letter is in neither set (92/92).
- Feedback matches response correctness in all 200 responses (193 beep, 7 buzz).
- Out-probabilities sum to 1 at every node.
- Pooled node counts equal the sum of the per-file counts.
- No within-phase edge outside `stimulus_phase`.

## Transition types

Classified from the source phase and the delay spread, with no trial grouping:

| type | edges | evidence |
|---|---|---|
| `fixed_delay` | Fixation->letter (5.246 s), letter->letter (1.442 s), response->feedback (0.400 s) | range < 20 ms |
| `jittered_delay` | Memory->probe | 2.246-4.207 s, sd 0.53 |
| `response_latency` | probe->button | 0.543-7.228 s, sd 0.9; participant RT, not a task parameter |
| `self_paced` | feedback->Rest | 0.364-15.684 s, mean 3.8 s |
| `triggered` | Rest->Fixation | 17-35 ms |

## Open questions

1. **Per-subject response counts.** Accuracy is the dependent measure and it differs
   between these two subjects. Should the model carry per-file or per-subject counts on
   the response nodes alongside the pooled ones, or is that strictly a separate report?

2. **Whole-trial exclusion.** `bad_trial` marks events that would sit inside a complete
   trial, so the orphan-row mechanism will not catch them. Does the model need a
   separate notion of excluded *trials*, and if so does that change the counts or just
   annotate them?

3. **Iteration limit.** The procedure says iterate until segmentation stabilizes. One
   pass sufficed here. Worth deciding what a generator should do if it does not
   converge - that would usually mean the phase model is wrong, not the data.

4. **What belongs in `data/`.** It currently holds one of the eight source files plus
   the sidecar and README, with `dataset_source.json` stating that models are not built
   from it. Should it hold all eight, or none at all with the spec doing all the work?
   A partial copy beside a full-dataset model is what made the counts look single-file
   in the first place.

5. **Portability of `dataset_source.json` roots.** The relative root
   (`../../../../../../hed-examples/...`) works only if hed-vis and hed-examples are
   siblings. The absolute root is mine. Neither survives a clone on a fresh machine, so
   the first build there will fail with the list of roots tried - which is the intended
   behavior, but it means a new contributor must add a root before anything runs. Is a
   downloadable identifier (OpenNeuro accession, DOI) worth resolving automatically?

## Bug in the draft model file

`../../draft/sternberg_model.json` does not parse - missing comma between the two dicts
in N13's `event_columns`:

```
JSONDecodeError: Expecting ',' delimiter: line 143 column 21 (char 4797)
```

Also `"tranisition"` is misspelled in `E(0,1)`, and that edge's description says "first
letter (an ignore letter)" while the first letter after fixation is a to-remember
letter in 116 of 200 trials.

## Reproducing

Build scripts are in my scratchpad, not committed. A committed generator needs: sidecar
filtering of columns, node assignment with `*` support, phase-then-first-appearance
numbering, the two-pass trial segmentation and orphan exclusion, and one onset-ordered
pass per file for transitions. `KeyMap` covers node extraction and counts via
`make_template(show_counts=True)`. Say the word and I will add it under `hedvis/tools/`.
