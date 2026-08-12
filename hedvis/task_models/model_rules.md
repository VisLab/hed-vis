# Model rules

This work extracts a directed graph model of the task structure for neuroscience and
behavioral experiments from the experimental events in the data.

The data is assumed to be in BIDS (Brain Imaging Data Structure) format. Event files end
in `_events.tsv`. Metadata about the events is in the accompanying `events.json`
sidecar.

Rules are numbered continuously for cross-reference, not by priority. Sternberg examples
throughout refer to the model in `json_examples/sternberg/models/event_type_task_role/`,
built from `eeg_ds004117s_hed_sternberg`; see that model's `reports/model_summary.md`
and `reports/log.md`. Questions that remain genuinely undecided are collected near the
end as Q1-Q7 rather than stated as rules.

## What a model is

1. A model is a JSON file whose structure and values are based on columns of the
   `_events.tsv` files of one experiment.

2. A graph node is created for each unique combination of the values in the specified
   `columns`. Each row of each `_events.tsv` file maps to exactly one node.

3. Nodes are defined in the `nodes` dictionary, keyed `N0`, `N1`, ..., each value a
   dictionary of that node's properties. Numbering follows rule 22.

4. The `event_columns` list in a node definition gives the column-value combinations
   belonging to that node. A `*` for a column value means any value of that column is
   acceptable and the remaining columns determine the node.

5. An edge `E(i,j)` corresponds to a row mapping to `Ni` being immediately followed by a
   row mapping to `Nj`. One edge per unique ordered pair, carrying a count (rule 29).

6. A model also declares its phases and their order (rules 14-19), its trial boundaries
   (rules 23-27), its provenance (rule 36), and the rows it excluded (rules 25-26).
   Field reference:

   ```
   task, description, dataset
   columns, columns_source        - the node key and where it came from
   phases                         - ordered list, experiment-specific (rule 15)
   phase_definitions              - per phase: order, nodes, node_kind, from_description
   phase_edges                    - the phase-level graph (rule 19)
   start_nodes, end_nodes         - trial boundaries (rule 23)
   excluded_column_values         - combinations skipped entirely
   excluded_rows                  - [{file, rows, reason}] (rule 25)
   nodes                          - label, in_phase, description, event_columns, count
   edges                          - source, target, transition, count,
                                    out_probability, phase_step, self_loop
   trial_identification           - method, n_trials, cross-check
   generated_from                 - files, row counts, ignored columns, first/last nodes
   ```

## Understanding the task

7. **The generator must understand the experiment, not just the column names.** Whether
   a row is relevant is a semantic judgment, and it cannot be made from names alone.
   Never exclude a row because its name looks wrong, and never keep one because its name
   looks right. In Sternberg, `bad_trial` happens to be documented and to mean what it
   says - most experiments have no such marker, and where one exists the name may
   mislead. Conversely the one row that had to go was `left_click` / `ignored_correct`,
   a combination that is legitimate 89 other times.

   The task description is the primary source. The Sternberg README established the
   phase order, identified the dash as a cue and the probe as the go signal, marked the
   ready press as a rest, and stated that response accuracy is the dependent measure.
   None of that is recoverable from column names.

8. **When a value's meaning cannot be established, ask rather than guess.** If the
   sidecar, the README, and the event structure all fail to settle what a column value
   means, emit a concise list of specific questions - "does `value = 255` encode the
   button or the response?" - and leave those rows in with the ambiguity flagged. A
   wrong guess is silently destructive; an open question is not. The questions belong in
   the model summary (rule 41).

## Choosing the columns

9. **Which columns define the nodes is the most consequential decision in the model.**
   Every dataset names and encodes its task differently, and the column choice
   determines whether the resulting graph describes the task or garbles it. Nothing
   downstream recovers from a bad choice.

   Intended workflow: a high-level agent proposes a column set, the model is generated,
   and the agent evaluates whether the result describes the task and revises.
   **Currently the user supplies the columns**, and the model records this in
   `columns_source` so an inferred set is never mistaken for a specified one.

10. **Criteria for judging a column set.** Applied by the evaluation step of rule 9:

    - Every distinguishable task event gets its own node, and no node conflates two task
      roles. This is the binding constraint.
    - Node count stays near the number of distinct events the description mentions. Far
      more means a stimulus-identity or condition column has leaked in.
    - Every node is assignable to exactly one phase.
    - The phase graph reproduces the described sequence (rules 15, 19).

    Measured over the 8 Sternberg files:

    | columns | nodes | verdict |
    |---|---|---|
    | `[event_type]` | 7 | **wrong** - `left_click` merges correct rejection, miss, and ready press; `right_click` merges hit, false alarm, and ready press. Destroys the dependent measure and puts one node in two phases. |
    | `[task_role]` | 13 | correct, and identical to the chosen model |
    | `[event_type, task_role]` | 14 | chosen; the extra row is `indicate_ready` split by button, collapsed by `*` |
    | `[event_type, task_role, memory_cond]` | 40 | condition leak |
    | `[event_type, task_role, letter]` | 92 | stimulus-identity leak |

    Note that `task_role` alone gives exactly the 13 nodes of the final model, because
    every other `task_role` maps to a single `event_type`. The `*` wildcard on
    `event_type` does precisely the work that dropping the column would do - the kind of
    redundancy the evaluation step should catch.

11. **Condition variables are not node columns.** An independent variable such as
    Sternberg's `memory_cond` (3, 5, or 7 letters to memorize) multiplies every node by
    the number of levels without changing the task structure - the graph shape is
    identical in all three conditions. Conditions belong as node or edge attributes, or
    as separate models to be compared. A naive agent will reach for the condition column
    first, so state this explicitly.

12. **Columns not documented in the sidecar are ignored**, and the model records which
    were dropped in `generated_from.columns_ignored_not_in_sidecar`. Sternberg's `value`
    column has no sidecar entry and is fully redundant with `event_type`, `task_role`,
    and `letter`.

13. **`n/a` means the column has no value defined for that row.** It marks the absence
    of a value; it is not itself a value. What that absence means for the task must be
    worked out - a semantic judgment (rule 7), not a parsing decision. Two cases behave
    very differently:

    - **Not applicable.** The column does not pertain to this kind of event. Sternberg's
      `letter` is `n/a` for all 601 button-press and sound rows and carries a value for
      all 2200 visual rows, so the absence is perfectly predicted by `event_type`. Here
      `n/a` conveys nothing the other columns do not already say, and must not create or
      split a node.
    - **Missing.** A value should exist for that row but was not recorded. That is a data
      quality problem. Report the affected rows; do not silently fold them into a node
      keyed on absence.

    Telling the two apart needs the task description. If `n/a` in one column is exactly
    predicted by the values of another, that is strong evidence for "not applicable" -
    and also a sign the column is redundant as part of the node key. If the absence
    follows no pattern, suspect "missing". When it cannot be settled, ask (rule 8).

    A column that is `n/a` for some rows deserves scrutiny before joining `columns` at
    all, since the resulting nodes would mix "has this property" with "this property does
    not apply".

## Phases

14. **Phase vocabulary.** The phases available to a trial-stimulus-response model:

    a. `start_trial_phase` - might be a fixation cross
    b. `cue_phase` - priming for the stimulus
    c. `stimulus_phase` - a sensory presentation
    d. `go_phase` - participant must withhold response until seeing this
    e. `response_phase` - some kind of response, real or imagined
    f. `feedback_phase`
    g. `rest_phase` - used when the participant must indicate ready to continue
    h. `end_trial_phase`

    This is a **vocabulary, not a temporal template**. Sternberg runs stimulus before
    cue: the letters are encoded first, then the dash cues rehearsal.

15. **Phase order comes from the prose describing the experiment, not from the data.**
    Each phase cites the text that establishes it, in
    `phase_definitions[*].from_description`, and the data is used to *confirm* the
    described order. When data and description disagree, that is a finding about the
    dataset, not a licence to reorder the model.

16. **Most experiments use a subset of the phases.** Absent phases are omitted from
    `phases` rather than listed empty. Sternberg uses seven of the eight and has no
    `end_trial_phase`: the rest-phase button press directly triggers the next trial's
    fixation cross, with no separate end-of-trial event.

17. **Each node declares `in_phase`, whose value must be a member of `phases`.** Use
    `in_phase` with `*_phase` values; do not mix in `*_block` naming.

18. **Only phases carry ordering.** Nodes within a phase have no intrinsic order - they
    are either mutually exclusive alternatives or repetitions. Node numbering within a
    phase is a naming convention and must never be read as a temporal claim: Sternberg's
    `N6` through `N9` look sequential but are four alternative outcomes of one button
    press.

    Record which case applies per phase in `node_kind`, derived from the edge set rather
    than from trial grouping: a phase is `repeated` if any edge runs between two of its
    own nodes (including a self-loop), `alternatives` otherwise. `stimulus_phase` is the
    only repeated phase in Sternberg, which is what tells a reader that `N1->N1` and
    `N1->N2` are normal there while a within-phase edge anywhere else is a data error.

19. **The model carries a phase-level graph**, `phase_edges`, obtained by collapsing
    nodes to their phases. This is the coarse structure an experimenter would recognize -
    for Sternberg, a 7-node cycle. Every edge, at both levels, is classified by
    `phase_step`:

    - `advances` - to the next phase in the declared order
    - `within_phase`
    - `wraps` - from the last phase to the first, i.e. the trial-to-trial loop
    - `anomaly` - anything else, always reported with its count

## Nodes

20. **`*` semantics.** A `*` matches any value of that column. An explicit match always
    wins over a `*` match. Sternberg's `Rest` node needs `*` for `event_type` because
    either button means ready. See Q1 for what is still unspecified.

21. **A node may not overlap another node's `event_columns`** after `*` resolution;
    every row maps to exactly one node (rule 2).

22. **Node numbering: phase order first, then first appearance.** Order nodes by their
    phase in the declared phase order, then within a phase by first appearance scanning
    from the first row onward. Two cautions:

    - **Do not use `KeyMap` ordering.** `KeyMap.col_map` is first-appearance order over
      the whole file, which interleaves phases; `make_template` re-sorts by descending
      count. Neither is stable or meaningful for numbering.
    - **First appearance alone is not enough.** It places `remembered_correct` before
      `probe_not_shown` - a response before the stimulus that causes it. Phase must be
      the primary key.

## Trials and excluded rows

23. **`start_nodes` and `end_nodes` are declared, not inferred, and they are
    load-bearing** - they are what segments a file into trials. The description often
    leaves the cycle-cut point ambiguous and the data cannot settle it: the Sternberg
    README opens the trial at the ready press, while the fixation cross is what starts
    it. Same loop, different offset. Declare the choice.

24. **Do not require a trial column.** Many datasets have none and reconstructing one is
    rarely deterministic. Trial boundaries come from `start_nodes` / `end_nodes`
    (rule 25), and everything else a trial column might provide is available from the
    edge set: repetition within a phase from within-phase edges, the trial-to-trial loop
    from the `wraps` edge, structural violations from `anomaly` edges. Trial-level
    statistics, if wanted, belong in a separate step.

    Where a trial column does happen to exist, use it as a free check. For Sternberg the
    derived boundaries match it exactly: 200 trials, 0 disagreements, with the column
    never used to build the model.

25. **Orphan rows at file edges: find them with a trial-boundary pass.** Events at the
    start or end of a file that fall outside any complete trial. A column-value filter
    cannot express this, since the offending combination is usually legitimate
    elsewhere. The difficulty is circular - identifying orphans requires trial
    boundaries, and trial boundaries require the model - so:

    1. Map every row to a node using `columns`, with nothing excluded.
    2. Segment each file into trials: a complete trial runs from a `start_nodes` event
       to the first following `end_nodes` event, with no intervening start event.
    3. Any row left outside a complete trial is an exclusion *candidate*. Report
       candidates rather than dropping them silently - a run of them may mean the phase
       model is wrong rather than the data.
    4. Rebuild with the candidates excluded and re-segment. Iterate until the
       segmentation stops changing, since excluding rows can merge or split trials.

    Record the result in `excluded_rows` as `{file, rows, reason}` with an explicit
    index convention, **not** as column values. Sternberg carries one entry: row 0 of
    `sub-003 ... run-3`, 0-based over data rows with the header excluded.

26. **Extraneous rows inside a trial are a separate and harder problem.** Rule 25 only
    catches rows outside a complete trial. Rows between a valid start and a valid end
    still need judging. Categories to exclude:

    - **Repeated responses.** Participant presses again when one press was specified.
      Keep the first, exclude the rest.
    - **Wrong button.** A press that is not one the task description assigns to that
      phase.
    - **Experiment-failure markers and external control events.** Scanner triggers,
      operator aborts, pause and resume markers - apparatus, not task.
    - **Timeouts.** The timeout event itself is apparatus and goes, but the trial it
      belongs to is a *missing response*, which is a task outcome and must stay visible
      in the model rather than being silently dropped.

    Detection uses the phase model: a phase declared `alternatives` (rule 18) should
    contain exactly one row per trial, so a second row in such a phase is the signal.
    That test generalizes; the category names do not.

27. **Never use exclusion to remove low-frequency task events.** Sternberg's incorrect
    responses are rare - 4 misses and 3 false alarms out of 200 - but they are the
    dependent measure, since the task exists to measure how well the participant
    remembers. A repeated press is extraneous; a wrong answer is data. The difference is
    semantic, not statistical (rule 7). Note that Sternberg's miss edge has count 4 and
    is real while its orphan edge had count 1 and was not: a low count alone proves
    nothing, and only the trial-boundary pass separates them.

## Edges

28. **Each `_events.tsv` is processed independently and edges aggregated afterward.**
    Concatenating files would create false edges from the last event of one run to the
    first of the next.

29. **Every edge carries a count and an out-degree-normalized `out_probability`.** An
    edge seen 572 times and one seen 4 times are not equally informative, and counts are
    what let a reader judge an exclusion candidate from rule 25.

30. **Self-loops are legal.** Consecutive rows can map to the same node - Sternberg's
    letter sequence gives `N1->N1` (202) and `N2->N2` (572). They mean repetition within
    a phase, not a cycle in the task design, and a phase marked `repeated` (rule 18) is
    where they are expected.

31. **Every edge carries a typed transition with observed delay statistics.** The delay
    distribution is what separates an experimenter-controlled interval from a jitter
    from a reaction time from a self-paced pause - all four occur in Sternberg alone.
    Vocabulary:

    | type | meaning |
    |---|---|
    | `fixed_delay` | experimenter-controlled constant interval |
    | `jittered_delay` | deliberately randomized within a stated range |
    | `response_latency` | participant reaction time, not a task parameter |
    | `self_paced` | participant chooses when to continue |
    | `triggered` | the source event itself causes the target, near-zero delay |

    Assign from the source phase and the delay spread; no trial grouping is needed.
    Record `min`, `median`, `max`, `mean`, `sd` in seconds.

32. **Every edge carries `phase_step`** as defined in rule 19.

33. **Every edge carries `self_loop`.**

34. **Record the observed first-row and last-row node per file** in `generated_from`.
    Before exclusion, 7 of 8 Sternberg files begin on `Fixation` and all 8 end on
    `Rest`, which is precisely how the one bad file announces itself; after exclusion
    all 8 begin on `Fixation`.

## Aggregation and provenance

35. **State whether the model is per-run, per-subject, or pooled.** Pooling averages
    away the dependent measure: Sternberg's response nodes *are* the measurement, and
    accuracy varies by subject - sub-001 runs 92-96% correct while sub-003 is 100% on
    three of four runs, so the pooled 96.5% describes neither. See Q4.

36. **Provenance is required.** Record every file with its row count, rows excluded and
    used, the columns dropped as undocumented, and the observed first and last row
    nodes. Without it a model built from one run is indistinguishable from one built
    from a whole dataset, and pooled counts cannot be checked. Phase order additionally
    cites its source text (rule 15).

## Validation

37. **Invariants a generator should assert.** These are cheap and each caught a real
    problem while building the Sternberg model:

    - Every retained row maps to exactly one node.
    - Per node, outgoing edge counts sum to the node count minus its file-final
      occurrences.
    - Out-probabilities per node sum to 1.
    - Pooled node counts equal the sum of the per-file counts.
    - A phase declared `alternatives` has no within-phase edges.
    - After exclusion, every file starts on a `start_nodes` member and ends on an
      `end_nodes` member.
    - Every edge is `advances`, `within_phase`, or the single `wraps` edge; anything
      else is reported with its count.
    - Where a trial column exists, derived trial boundaries match it.

## Generating a model

38. **`KeyMap` covers node extraction only.** `KeyMap` in `hed.tools.analysis.key_map`
    extracts the unique combinations of the specified columns, and
    `make_template(show_counts=True)` adds a `key_counts` column. But it carries no
    transition information, does not preserve onset, and its `count_dict` is keyed by an
    unstable hash. Edge computation needs a separate onset-ordered pass per file.

39. **Ship the counted keymap as a committed artifact**, in the model's own directory
    (rule 42) and named per rule 43. It belongs with the model, not in `data/`: an
    8-file keymap sitting beside a 1-file sample reads as single-file counts. A `*` node
    appears as multiple keymap rows, which is a useful check on the wildcard -
    Sternberg's `Rest` is `right_click` 150 and `left_click` 50.

40. **Counts are pooled over exactly the files listed in provenance**, and the per-file
    row counts must make that arithmetic checkable.

41. **Every model ships with a `model_summary.md`** in its `reports/` directory
    (rule 42). The JSON is not reviewable by reading it, and the log accumulates
    history. The summary is what a person actually reads to decide whether the model is
    right: the task, the node and edge inventory, what was excluded and why, and - the
    part that matters most - an explicit list of unresolved questions and anomalies.
    Keep it short. It is also the natural input to the evaluation step of rule 9.

## Output structure and naming

42. **Layout: one directory per dataset, holding `data/` and `models/`.** A dataset may
    have several models, each in its own directory under `models/`:

    ```
    <dataset>/
      data/
        dataset_source.json            - where the real data lives (rule 44)
        ...                            - sidecar, README, optional sample rows
      models/
        <model>/
          <dataset>_<model>.json       - the model
          <dataset>_<model>_keymap.tsv - the counted keymap
          reports/
            model_summary.md           - rule 41
            log.md                     - findings, decisions, questions
            ...                        - any other report for this model
    ```

    Everything belonging to one model stays inside that model's directory, so a model
    can be read, diffed, or deleted as a unit. Reports go one level below the model
    rather than beside it, so the model directory lists its artifacts and not its
    history.

43. **Names.** The dataset directory is named for the dataset. The model directory is
    named for the model, and the model's `name` field must equal that directory name.
    The model file is `<dataset-name>_<model-name>.json` and the keymap
    `<dataset-name>_<model-name>_keymap.tsv`, so a file is identifiable once detached
    from its directory. Model names should be short and should say what distinguishes
    this model from the others for that dataset - most often the column choice
    (rule 9), which is also recorded inside as `columns` and `columns_source`.

44. **The data location is specified in `data/dataset_source.json`, never hardcoded in
    a build script.** This is the only machine-dependent part of the pipeline. The spec
    names the dataset, gives an identifier where one exists, and lists candidate roots
    tried in order, so the same model directory builds on any machine by adding a root
    rather than editing code:

    ```json
    {
      "dataset_name": "sternberg",
      "bids_dataset": "eeg_ds004117s_hed_sternberg",
      "identifier": "ds004117",
      "source": {
        "type": "local_bids",
        "roots": ["<relative path>", "<absolute path>"],
        "events_glob": "sub-*/ses-*/eeg/*_events.tsv",
        "sidecar": "task-WorkingMemory_events.json"
      }
    }
    ```

    Relative roots resolve against the spec file. The generator records which root it
    resolved to in the model's `dataset_source.resolved_root`, so provenance (rule 36)
    is unambiguous even when several roots would have worked. If no root exists, fail
    with the list that was tried - never fall back to a partial local copy.

45. **`data/` may hold a sample, but models are never built from it.** A dataset
    directory usually cannot hold a full BIDS dataset, so `data/` typically carries the
    sidecar, the README, and perhaps one events file for reference. Say so explicitly in
    `dataset_source.local_sample`, because a counted artifact sitting beside a one-file
    sample reads as single-file counts - this is why the keymap lives with the model
    (rule 39) and not in `data/`.

## Open questions

**Q1. `*` scope.** May `*` appear in more than one column of a single `event_columns`
entry? Rule 20 fixes precedence but not this.

**Q2. Does `n/a` match `*`?** Rule 13 settles what `n/a` means but not how it behaves
against a wildcard in `event_columns`, nor whether a "not applicable" row should be
matchable at all when its column is part of the node key.

**Q3. Declared nodes with no matching data.** Is a node with zero observed rows an
error, dropped, or kept as a declared-but-unobserved placeholder? Same question for a
combination present in the sidecar `Levels` but never in any `_events.tsv` -
`bad_trial` in Sternberg.

**Q4. Per-subject counts.** Should response nodes carry per-file or per-subject counts
alongside the pooled ones (rule 35), or is that strictly a separate report?

**Q5. Whole-trial exclusion.** `bad_trial` marks events that sit *inside* complete
trials, which neither rule 25 nor rule 26 catches. Does the model need a notion of
excluded trials, and would that change counts or only annotate them?

**Q6. `model_type` semantics.** What may a consumer assume from
`trial-stimulus-response` - presumably a dominant cycle of period one trial? What are
the other legal values?

**Q7. Relation to HED.** The sidecar carries a HED string per column value
(`Sensory-event`, `Agent-action`, `(Cue, Recall)`, `(Feedback, Correct-action)`). These
encode much of what `phases` and `task_role` express, and they are what identified the
Sternberg dash as a cue and the probe as the go signal. Should HED tags be carried into
node definitions, and may phase assignment be inferred from them rather than assigned by
hand?

## Untested rules

Rule 26 is written but exercises nothing in the Sternberg data: all 200 trials are
exactly 14 rows with one response and one ready press - no double presses, no timeouts,
no responses under 150 ms, and every button press carries one of the five expected
roles. It needs a dataset that triggers it.
