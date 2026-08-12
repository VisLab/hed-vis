# Model summary: sternberg / event_type_task_role

**Task.** Modified Sternberg working memory. 8 letters shown one at a time (3, 5, or 7
black to memorize, the rest green to ignore), then a dash cues a 2-4 s rehearsal
period, then one red probe letter. Participant presses a button to report whether the
probe was in the memorized set, and hears a beep (correct) or buzz (incorrect). A
self-paced button press starts the next trial.

**Source.** `eeg_ds004117s_hed_sternberg` (ds004117), resolved via
`sternberg/data/dataset_source.json`. 8 event files (sub-001 and sub-003, 4 runs each).
2801 rows, 1 excluded, 2800 used, pooled. 200 trials.

**Columns.** `event_type`, `task_role` - user-supplied, not inferred.

## Structure

13 nodes, 21 edges, 7 phases. The phase graph is a single cycle:

```
start_trial -> stimulus -> cue -> go -> response -> feedback -> rest -.
     ^                                                                |
     `----------------------------------------------------------------'
```

| phase | nodes | count each |
|---|---|---|
| start_trial | Fixation | 200 |
| stimulus (repeated) | Green, Black | 600, 1000 |
| cue | Memory | 200 |
| go | ProbeIn, ProbeOut | 108, 92 |
| response | ButtonInGood, ButtonOutGood, ButtonInBad, ButtonOutBad | 104, 89, 4, 3 |
| feedback | FeedbackCorrect, FeedbackIncorrect | 193, 7 |
| rest | Rest | 200 |

`stimulus` is the only `repeated` phase - its two nodes interleave, giving self-loops
and cross-edges. Every other phase has exactly one event per trial. Node numbering is
by phase then first appearance; it carries no meaning within a phase.

Five transition mechanisms: `fixed_delay` (5.246 s fixation, 1.442 s inter-letter,
0.400 s response-to-feedback), `jittered_delay` (2.2-4.2 s rehearsal),
`response_latency` (0.54-7.23 s), `self_paced` (0.36-15.7 s), `triggered` (17-35 ms,
the ready press firing the next fixation).

## Behavior

Response accuracy is the dependent measure, so the four response nodes are modeled, not
filtered. Pooled: 96.5% correct (104 hits, 89 correct rejections, 4 misses, 3 false
alarms). Per subject: sub-001 runs 92-96%; sub-003 is 100% on three of four runs.

## Exclusions

One row: row 0 of `sub-003 ... run-3`, a `left_click`/`ignored_correct` orphan preceding
the first fixation cross - the tail of a trial that began before recording. Found by
trial segmentation, not by column values, since that combination is legitimate 89 other
times.

## Validation

- 200 trials derived from `start_nodes`/`end_nodes` alone; matches the dataset's
  `trial` column exactly (0 disagreements). The column is not used to build the model.
- After exclusion all 8 files begin on Fixation and end on Rest.
- 16 edges `advances`, 4 `within_phase`, 1 `wraps`, 0 anomalies.
- Out-probabilities sum to 1 at every node; pooled counts equal the per-file sums.
- No within-phase edge outside `stimulus`.
- Probe letters consistent: `probe_target` always in the memorized set (108/108),
  `probe_not_shown` in neither set (92/92). Feedback matches correctness 200/200.

## Unresolved questions

1. **Column choice is unvalidated.** `task_role` alone gives the same 13 nodes, since
   every other `task_role` maps to one `event_type` - the `*` wildcard on `event_type`
   does exactly what dropping the column would. Is the two-column key worth keeping for
   the modality it documents, or should it be simplified?

2. **Pooling hides the measurement.** The pooled 96.5% describes neither subject.
   Should response nodes carry per-subject counts, or is that a separate report?

3. **`bad_trial` is declared in the sidecar but absent from these two subjects.** When
   it appears in the full 23-subject dataset it will mark events *inside* complete
   trials, which the orphan pass will not catch. Does the model need a notion of
   excluded trials, and would that change counts or only annotate them?

4. **Where to cut the cycle.** The README opens the trial at the ready press
   ("[Trial initiation]"); the model cuts at the fixation cross. Both describe the same
   loop. The choice is declared, not derived.

5. **Rest between runs is not represented.** Each 25-trial block is a separate file, so
   the between-block rest is invisible to a within-file model. Currently out of scope
   per the decision to ignore block structure - flagging in case that changes.

## Anomalies

1. **`duration` is not in seconds.** Dividing by 250 reproduces the README exactly
   (cross 5.03 s, letter 1.22 s, dash 2.03-3.99 s), and `sample` vs `onset` implies
   249.9 Hz. This is a dataset bug to fix upstream; the model does not report duration.
   A single divisor will not work for the full dataset - the README says subject 14 was
   recorded at 1000 Hz and 15-24 at 500 Hz.

2. **`value` column is undocumented** - no sidecar entry, 69 values, fully redundant.
   Dropped at read time.

3. **The draft model does not parse.** `sternberg/models/draft/sternberg_model.json`,
   missing comma at line 143. It also predates the naming rule - it would be
   `sternberg_draft.json` under rule 43. Also misspells `tranisition`, and its `E(0,1)` description calls the first
   letter an ignore letter, though it is a to-remember letter in 116 of 200 trials.

4. **Untested exclusion rules.** The rules for extraneous within-trial rows (repeated
   presses, wrong button, control markers, timeouts) are written but exercise nothing
   here: all 200 trials are exactly 14 rows with one response and one ready press, no
   double presses, no timeouts, no responses under 150 ms. They need a dataset that
   triggers them.
