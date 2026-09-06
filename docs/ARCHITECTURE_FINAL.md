# Ω∞ Architecture — Final Engineering Contract

## 1. System boundary

Ω∞ is a software system that maintains durable fictional creator state and uses that state to condition generative music-writing workflows. The words `consciousness`, `psychic`, `memory`, `synapse` and `wandering thought` name computational mechanisms; they are not scientific claims of subjective experience.

## 2. Canonical ownership

- `src/omega/` owns runtime behavior.
- `config/` owns identity and policy.
- SQLite owns mutable runtime state.
- JSON canon is a versioned creative continuity artifact.
- Git stores versioned persistence and code history.
- CI is the mandatory integrity boundary.

There must be exactly one authoritative implementation for each domain capability.

## 3. State machine

`BOOT -> RESTORE -> ELAPSED_EVOLUTION -> STIMULUS -> ASSOCIATIVE_RECALL -> CONCEPT -> GENERATE -> PREFILTER -> ADVERSARIAL_JUDGE -> REBUILD* -> QUALITY_GATE -> LEDGER -> CANON_UPDATE -> CHECKPOINT`

`REBUILD*` is bounded by policy. A failed gate is a valid outcome and never becomes a falsely accepted track.

## 4. Identity hierarchy

1. Immutable creator identity constraints.
2. Current canon.
3. Current psychic state.
4. User stimulus.
5. Candidate-specific stylistic choices.
6. Model randomness.

Lower layers cannot silently override higher layers.

## 5. Memory hierarchy

### Episodic memory
Events, songs, places, interactions and sensory fragments.

### Semantic memory
Recurring beliefs, symbols, concepts and meanings.

### Procedural memory
Creator-specific craft behavior: rhythm preferences, recurring structural habits, favored phonetic patterns and production tendencies.

### Reconsolidation
Retrieved memories may change interpretation. A reinterpretation is stored as a new event; the original event is never silently rewritten.

### Confabulation isolation
Random-walk or model-generated recollection receives explicit uncertainty metadata. It cannot become canon unless an explicit promotion step records it as such.

## 6. Psychic model

The state contains affect dimensions plus meta-dynamics such as arousal, valence, coherence, inhibition, curiosity, social distance, aggression, openness, novelty pressure and repetition pressure.

A useful representation is:

`dΨ/dt = decay(Ψ, baseline) + stimulus(ε) + stochastic_drift(η) + associative_influence(H)`

The equation is an engineering abstraction. Production code must clamp all state values to valid domains and persist every committed transition.

## 7. Originality architecture

Originality is not a single classifier. It is a cascade:

`deterministic lexical checks -> structural checks -> model adversarial critique -> creator-canon consistency -> similarity-risk reasoning -> final veto policy`

A track cannot pass merely because its aggregate score is high. Identity and originality are hard vetoes.

## 8. Creator-specific language

Regional and biographical language layers are conditional rather than decorative. The engine should prefer subtle traces and lived-context cues over caricatured dialect or forced slang.

Profanity is permitted as an expressive device, but its presence must be motivated by voice, rhythm, emotion, characterization or narrative context.

## 9. Production boundary

The current repository is a text/creative-runtime engine. Audio synthesis, waveform generation, voice cloning, beat generation and mastering are adapter domains and must not be conflated with the cognitive core.

Future adapters should implement narrow interfaces for:

- music generation;
- voice synthesis;
- audio analysis;
- mix/master analysis.

## 10. Failure containment

A provider failure must not corrupt creator state.

An invalid model response must not be written to canon.

A partially completed forge must remain distinguishable from a finalized artifact.

A scheduler failure must not produce duplicate state transitions.

A Git conflict must not silently overwrite a newer creator state.

## 11. Observability

Every important operation should produce a continuity event with:

- event type;
- deterministic payload hash;
- timestamp;
- request identifier;
- state version where relevant.

This makes the evolution of the creator auditable rather than merely rhetorical.

## 12. Security

- Secrets never enter Git.
- Public API deployments require authentication and rate limiting.
- Prompt length is bounded.
- Model output is schema-validated before mutation.
- User-provided content is treated as untrusted input.
- Canon and identity mutations require explicit internal policy paths.

## 13. Definition of finished

Finished means the system is coherent end-to-end: it can restore itself, evolve, recall, create, critique, rebuild, reject, finalize, persist, expose state through an API and survive restart without losing identity.

A system that only has an impressive prompt is not finished.
