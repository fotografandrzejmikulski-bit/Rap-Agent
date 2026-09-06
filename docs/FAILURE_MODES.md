# Ω∞ Failure Modes and Hardening Register

This register records failure classes that must be prevented before the project is described as production-grade.

| Failure | Why it matters | Required control |
|---|---|---|
| Baseline reset on restart | destroys continuity | durable psychic state + elapsed-time resume |
| Randomness mistaken for cognition | creates theatrical rather than coherent behavior | explicit computational model and bounded stochasticity |
| RAG-only recall | retrieves facts but lacks associative continuity | graph memory + canonical state + memory dynamics |
| Random-walk loops | same motifs dominate output | anti-loop pressure + diversity term |
| Constant Hebbian increment | popular memories become runaway attractors | bounded plasticity + decay |
| Blind lexical stimulus | unrelated prompts move every emotion upward | dimension-specific stimulus interpreter |
| Fake quality score | hides weak output | independently evaluated quality vector |
| One-shot generation | low exploration | candidate set + Pareto selection |
| Line repair breaks the song | local fix damages flow or narrative | local repair followed by global audit |
| Forced dialect | creator becomes caricature | context-conditioned regional probabilities |
| Slang inflation | artificial street performance | provenance/context gate |
| Profanity spam | weakens character | functional profanity constraint |
| False-memory promotion | corrupts creator canon | explicit confidence/provenance and canon gate |
| Git as realtime database | race conditions and churn | database/service as authority, Git as snapshot transport |
| Unauthenticated /forge | remote abuse | authentication + rate limiting |
| CORS wildcard in production | excessive browser exposure | origin allowlist |
| Hidden provider assumptions | adapter breaks as APIs evolve | provider-specific adapters and versioned contracts |
| Unobservable mutations | impossible debugging | trace IDs and state/version audit trail |
| Unbounded background worker | runaway costs | bounded tick + scheduler controls + backpressure |
| Memory poisoning through user input | creator identity can be hijacked | trust tiers and canonicalization rules |

## Security of the fictional persona

The creator's fictional biography is treated as an authored identity model. Do not represent fictional memories as verified facts about a real person. User-supplied real-world information should not be silently incorporated into immutable canon merely because it appears in a prompt.

## Definition of done

The system is not considered production-ready until critical failures have executable tests and the state lifecycle survives start, restart, concurrent requests, scheduled wake, generation failure and recovery without losing the Creator Genome or durable psychic state.
