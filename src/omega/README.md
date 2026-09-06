# Ω∞ core package

The `src/omega` package is the canonical runtime domain. Legacy root-level runtime modules are retained only during migration and must not become a second source of truth.

## Production invariants

1. Creator identity is loaded from versioned configuration; it is not hard-coded in the model adapter.
2. Psychic state survives process restarts and evolves from elapsed time rather than resetting to baseline.
3. Memory, continuity events and forge evidence are durable.
4. Confabulated/wandering material is context, never an automatic canon fact.
5. Identity and originality are veto dimensions in final quality policy.
6. Scheduled wake-ups are bounded synchronization events, not claims of literal consciousness.
7. Git is a versioning/persistence boundary; runtime mutation must remain transaction-safe.
8. Every production artifact receives a stable hash and a forge ledger record.
