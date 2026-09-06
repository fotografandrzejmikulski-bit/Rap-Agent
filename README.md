# RAP-AGENT

## Ω∞ Singularity Creator DNA

Autonomous framework for a persistent fictional Polish rap creator whose identity is modeled as a durable system rather than a prompt template.

### Current architecture

The repository separates four continuity domains:

1. **Creator Genome** — identity invariants, biography, language layers, voice DNA, originality boundaries and quality policy.
2. **Creator Canon** — durable fictional events, relationships, places, symbols, vocabulary, songs, unresolved threads and belief changes.
3. **Psychic State** — evolving multidimensional state with arousal, valence, coherence, inhibition, curiosity, social distance, aggression, openness and novelty/repetition pressure.
4. **Synaptic Memory** — weighted directed associative graph persisted in SQLite.

The current core implements weighted graph memory, reinforcement, state drift, stimulus perturbation, adversarial critique and reconstruction. The architecture audit identified the most important continuity defect: a fresh runtime reconstructed the psychic tensor from baseline, while the scheduled GitHub runner persisted only the memory database. The V5 target therefore makes psychic state a first-class durable artifact.

### Design principles

- Polish-native language and phonetics first.
- Original creator identity, not imitation of existing artists.
- Persistent Creator Genome and Canon.
- Lubelszczyzna → Slovakia → Silesia → fictional prison-experience linguistic biography.
- Raw artistic language when contextually justified; profanity is functional, not decorative.
- Voice/timbre/accent are identity attributes.
- Headspace narrative and nonlinear memory are allowed.
- Continuous state is modeled computationally; no claim of literal consciousness is made.
- Memory uncertainty and simulated confabulation remain explicitly labeled and cannot silently become canon.
- Multi-pass generation, adversarial critique, originality audit and hard quality gates.
- Git is versioned source/config persistence, not the real-time transactional state store.

### Runtime API

- `GET /health`
- `GET /state`
- `GET /memory/stats`
- `POST /forge`

### Local run

```bash
python -m pip install -r requirements.txt
export OPENAI_API_KEY='...'
uvicorn api:app --host 0.0.0.0 --port 8000
```

## Engineering boundary

The project implements computational continuity: durable state, background drift, associative memory and evolving creative context. “Continuous consciousness” is an architectural model, not a claim that the software is literally conscious or sentient.
