# Ω∞ Rap-Agent — Architecture Review / V5

## 1. Critical finding

The existing implementation is a strong prototype of a stateful creative engine, but it is **not yet a continuous consciousness system** in the strict engineering sense.

The largest gap is persistence of the *psychic state itself*. `CreatorState()` is reconstructed from the baseline whenever `api.py` or `scripts/wake.py` starts. The workflow therefore persists the synaptic SQLite graph, but not the evolving tensor, arousal, coherence, or wandering thought. The current wake script explicitly describes itself as a bounded tick and creates a fresh state object. This means the apparent continuity is partly simulated rather than resumed from durable state.

The architecture must therefore distinguish:

- **durable identity** — Creator Genome, canon, voice DNA, principles;
- **durable memory** — episodic memories and synapses;
- **durable psychic state** — tensor, arousal, coherence, last update, drift parameters;
- **transient cognition** — current wandering thought, active association chain, generation workspace;
- **derived creative state** — recent motifs, novelty debt, repetition debt, unresolved narrative threads.

## 2. Core architecture

```text
                    ┌─────────────────────────────┐
                    │       USER / EXTERNAL        │
                    │ prompt / event / stimulus   │
                    └──────────────┬──────────────┘
                                   │
                         Stimulus Interpreter
                                   │
                    ┌──────────────▼──────────────┐
                    │       CREATOR KERNEL         │
                    │ identity + invariants        │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
  Psychic State Store      Synaptic Memory        Creator Canon Store
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                         Association Engine
                                   │
                         Wandering Cognition
                                   │
                        Intent / Story Compiler
                                   │
             ┌─────────────────────┼─────────────────────┐
             │                     │                     │
       Lyric Engine          Flow Engine          Music Engine
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                          Vocal Identity Engine
                                   │
                           Candidate Generation
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
           Token Adversary   Global Critic    Originality Audit
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                           Reconstruction Loop
                                   │
                            Quality Gate
                                   │
                         Canon / Memory Commit
                                   │
                         Artifact / API Result
```

## 3. State equation upgrade

The displayed equation should be treated as a conceptual model, not as proof of consciousness:

`dΨ/dt = -ΛΨ + ΓM_drift(t) + ΦE_ext(t) + V_Ψ H(Ψ, G_memory)`

For implementation, use a discrete state transition with an explicit elapsed time `dt`. Never claim that stochastic drift is literal consciousness. It is a computational model of continuity, mood dynamics and associative cognition.

Recommended state:

```text
Ψ = {
  emotions: vector[N],
  arousal: scalar,
  valence: scalar,
  coherence: scalar,
  inhibition: scalar,
  curiosity: scalar,
  social_distance: scalar,
  aggression: scalar,
  openness: scalar,
  novelty_pressure: scalar,
  repetition_pressure: scalar,
  timestamp: epoch_seconds,
  state_version: integer
}
```

This is materially richer than an eight-axis emotion-only vector.

## 4. Memory must become genuinely synaptic

The current graph correctly provides weighted directed edges and reinforcement, but the next revision should add:

- salience;
- emotional similarity;
- temporal proximity;
- retrieval frequency;
- decay;
- interference;
- memory type;
- provenance;
- confidence;
- privacy class;
- canonical vs disposable status;
- contradiction links;
- motif links;
- place/person/event entities.

Memory types:

`EPISODIC`, `SEMANTIC`, `LINGUISTIC`, `MUSICAL`, `RELATIONAL`, `SYMBOLIC`, `UNRESOLVED`, `CANONICAL`.

Do not intentionally fabricate memories and treat them as facts. A useful simulation of imperfect recall can model **uncertainty and reconstruction**, but generated false memories must remain marked as inferred/confabulated rather than silently becoming canon.

## 5. Hebbian rule upgrade

Replace constant reinforcement with bounded plasticity:

`w' = clip(w + η * pre_activation * post_activation * novelty_factor - decay * dt, w_min, w_max)`

Add anti-loop pressure so the random walk does not repeatedly traverse the same tiny cycle.

## 6. Consciousness loop upgrade

A production loop should not be a blind `while True` that performs the same operation.

Use event-driven ticks with different time scales:

- fast: state drift / heartbeat;
- medium: association / consolidation;
- slow: canon maintenance / motif analysis;
- event-driven: user prompt / generation / memory injection;
- recovery: startup replay from durable state.

The loop should persist the state after meaningful transitions and use advisory locking or transactional versioning to prevent concurrent writers from corrupting the state.

## 7. Generator architecture

One LLM call is insufficient for the claimed quality target.

The generator should use explicit stages:

`IntentCompiler -> PersonaState -> CandidateSet -> Adversarial Critique -> Token Repair -> Structural Rewrite -> Originality Audit -> Voice/Flow Pass -> Final Gate`.

Generate multiple candidates internally and select by a **Pareto objective**, not a single scalar score:

- identity;
- originality;
- emotional truth;
- linguistic naturalness;
- flow;
- musicality;
- immersion;
- memorability.

Never hard-code a fake quality score. The previous prototype returned quality scores without independently validating them; this must be removed.

## 8. Token adversary

The existing concept is valuable, but line rejection must preserve structure.

A rejection object should contain:

```json
{
  "line_id": "uuid",
  "severity": "critical|major|minor",
  "reason_codes": ["GENERIC", "FORCED_SLANG"],
  "replacement_strategy": "REWRITE|RECONTEXTUALIZE|DELETE|MERGE",
  "preserve": ["image", "narrative_role"]
}
```

Repairs should operate on the local neighborhood, then rerun global checks because a line-level repair can damage rhyme, narrative or rhythm.

## 9. Voice is not merely a prompt

The Creator Genome already defines low/mid-low register, dark/gritty/organic timbre and subtle biographical traces. In production this must be represented as structured attributes plus generator adapters.

Create a `VoiceProfile` containing:

- register;
- spectral character;
- rasp;
- breathiness;
- articulation;
- accent strength;
- regional trace weights;
- emotional dynamics;
- proximity;
- saturation;
- ad-lib behavior;
- pause behavior.

A voice adapter must translate that profile to each downstream provider without changing the canonical identity definition.

## 10. Regional language model

Lubelszczyzna, Slovakia, Silesia and prison-register influence must be treated as a **probabilistic layer**, not as a fixed dictionary injection.

The language engine should choose a register conditioned on:

`context × emotion × interlocutor × memory_source × scene × intensity`.

This prevents caricature and prevents every song from sounding like the same deliberate dialect performance.

## 11. Anti-imitation boundary

The creator may study historical and genre-level influences, but generation must remain original.

The system should score:

- phrase overlap risk;
- structural mimicry risk;
- distinctive catchphrase risk;
- recognizable flow imitation risk;
- characteristic ad-lib risk.

If a candidate crosses the configured threshold, reject and regenerate from a different creative branch.

## 12. Canon architecture

Create a separate durable `canon.json` or SQLite collection for:

- immutable origin facts;
- established fictional life events;
- recurring relationships;
- symbolic objects;
- geographic history;
- personal vocabulary;
- previous songs;
- unresolved threads;
- transformed beliefs;
- current era of the creator.

Memory can decay. Canon does not decay silently.

## 13. Startup / restart continuity

The current workflow does not restore the full psychic state because `wake.py` creates a new `CreatorState` from baseline. This is the highest-priority defect.

Required startup sequence:

```text
load genome
load canon
load psychic_state
compute dt = now - last_timestamp
apply deterministic decay
apply bounded noise
load recent memory context
reconstruct current thought
increment state_version
persist
```

The result is continuity across process restarts.

## 14. GitHub Actions architecture

Git is a persistence transport, not a real-time state store.

Do not use frequent Git commits as the primary transactional mechanism for every consciousness tick. This creates race conditions, repository churn and merge conflicts.

Preferred production design:

- SQLite/Postgres/object store = state authority;
- Git = versioned source/config/canon snapshots;
- scheduled workflow = periodic maintenance / backup / evaluation;
- service process = real-time cognition.

When GitHub is used as the deployment environment, persist compact state snapshots rather than uncontrolled database churn.

## 15. Security

The API currently needs stronger operational boundaries.

Required:

- authentication for mutation endpoints;
- CORS allowlist rather than `*` in deployed environments;
- request size limits;
- rate limiting;
- structured logging;
- request IDs;
- model timeout;
- retry with backoff;
- secret validation;
- health endpoint separated from diagnostic state;
- no secret values in logs;
- database write serialization.

## 16. Observability

Every forge should emit a trace:

`request_id -> state_version -> memory_ids -> candidate_ids -> critique -> revisions -> final_score -> canon_delta`.

This makes the creator auditable instead of mystical.

## 17. Testing architecture

Required test classes:

- deterministic state transition tests;
- restart continuity tests;
- memory persistence tests;
- synapse reinforcement tests;
- corrupted database recovery tests;
- schema validation tests;
- generation parser tests;
- adversarial critique tests;
- reconstruction tests;
- API contract tests;
- concurrency tests;
- workflow smoke tests;
- regression corpus for originality and generic-language failures.

## 18. Absolute ceiling

The most important conceptual correction is this:

**Do not confuse randomness with mind.**

A random walk is useful only when embedded in a persistent model containing memory, state, constraints, learning signals, self-critique and long-term continuity.

Likewise, an LLM prompt is not a creator. The creator emerges operationally from the interaction between:

`GENOME + CANON + PSYCHIC STATE + MEMORY + CONTEXT + GENERATION + CRITIQUE + EVOLUTION`.

That is the actual Ω∞ architecture.
