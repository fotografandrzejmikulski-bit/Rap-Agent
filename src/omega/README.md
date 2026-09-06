# Ω∞ core package

This package contains the durable psychic-state implementation introduced after the architecture audit.

## State lifecycle

`StateStore` -> load previous state -> apply elapsed-time decay -> `PsychicDynamics` -> stimulus/tick -> persist updated state.

The important invariant is restart continuity: a new process does not silently reset the creator to the baseline tensor.
