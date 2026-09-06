# RAP-AGENT

## Ω∞ Polish Rap Forge — Singularity Creator DNA

Autonomous framework for building a persistent fictional Polish rap artist with a coherent creative genome: biography, psychology, language, regional influences, voice identity, flow behavior, musical identity, memory, originality controls, adversarial critique, and artistic evolution.

### Design principles

- Polish-native language and phonetics first.
- Original creator identity, not imitation of existing artists.
- Persistent Creator Genome and Canon.
- Lubelszczyzna → Slovakia → Silesia → prison-experience linguistic biography.
- Raw, uncensored artistic language when contextually justified.
- Voice/timbre/accent as part of the character model.
- Headspace narrative: listener enters the creator's internal world.
- Multi-pass generation, adversarial critique, anti-generic and anti-AI checks.
- Generator-ready music, vocal, flow, production, mix and master specifications.

## Runtime architecture

```text
User stimulus
     |
     v
+-------------------+
| Psychic State     |
| emotion + arousal |
+-------------------+
     |
     +---------------------+
     |                     |
     v                     v
+----------------+   +-------------------+
| Synaptic       |<->| Wandering Thought |
| Memory Graph   |   | Random Walk       |
+----------------+   +-------------------+
     |                     |
     +----------+----------+
                v
          +-----------+
          | Ω∞ LLM    |
          | Generator |
          +-----------+
                |
                v
          +-----------+
          | Adversary |
          | Line      |
          | Critic    |
          +-----------+
                |
          reject/rebuild
                |
                v
           Track Result
```

### API

- `GET /health`
- `GET /state`
- `GET /memory/stats`
- `POST /forge`

### Run locally

```bash
python -m pip install -r requirements.txt
export OPENAI_API_KEY='...'
uvicorn api:app --host 0.0.0.0 --port 8000
```

## Engineering boundary

The project implements computational continuity: persistent state, background drift, associative memory and evolving creative context. “Continuous consciousness” is an architectural model, not a claim that the software is literally conscious or sentient.
