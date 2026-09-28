# Jev Model Demo

A small Python script for trying out [TypeSafe's Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) model and measuring how fast it makes decisions.

Jev doesn't write text. You give it some input and a set of typed questions, and it returns each answer with a probability or confidence score. This demo sends three sample support tickets to Jev and asks four questions about each one.

| Question | Type | What it answers |
| --- | --- | --- |
| `department` | Choice | Which team should handle the ticket: billing, technical or sales |
| `frustration` | Score | How frustrated the customer is, on a 3-level scale |
| `refund_requested` | Noul | Probability (0–1) that the customer is asking for a refund |
| `urgent` | Noul | Probability (0–1) that the message is time-sensitive |

If Jev is at least 80% confident about the team, the script routes the ticket there. Otherwise it sends the ticket to a human.

## Requirements

- Python 3.10 or later
- A TypeSafe API key from [console.typesafe.ai](https://console.typesafe.ai)

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and replace the placeholder with your key:

```
TYPESAFE_API_KEY=sk-...
```

`.env` is listed in `.gitignore`, so your key won't be committed. You can also skip the file and set `TYPESAFE_API_KEY` in your shell.

## Run

```bash
python jev_demo.py
```

For each ticket, the script prints Jev's answers, the token usage, the routing decision and the time the call took. It ends with a speed summary:

```
Decision speed (client-side round trip, includes network):
  calls:         3
  min / max:     ... ms
  mean / median: ... ms
  throughput:    ... decisions/s (12 decisions)
```

## How speed is measured

- The script times each call on your machine, so the times include network delay as well as the model's own processing. Expect them to be slower than TypeSafe's published figures.
- Time per decision is the call's time divided by the number of questions it asked.
- One untimed call runs first, so the time spent opening the connection doesn't count against the results.
- Three tickets is a small sample. For steadier numbers, add tickets to `TICKETS` in `jev_demo.py`.

## Trying your own questions

Edit `TICKETS` to change the input and `QUESTIONS` to change what Jev is asked. The model supports three question types:

- `Choice(instructions, criteria={...})` picks one of up to 255 named options.
- `Score(instructions, criteria=[...])` rates on an ordered scale of 2 to 10 levels.
- `Noul(instructions)` gives the probability that a statement is true.

TypeSafe's guidance is to spell out instructions literally. Jev doesn't infer negations or implied conditions, and it is unreliable at counting and date arithmetic. Do those in code and give Jev only the context it needs.

## Files

| File | Purpose |
| --- | --- |
| `jev_demo.py` | The demo script |
| `requirements.txt` | Python dependencies (`typesafe-sdk`, `python-dotenv`) |
| `.env.example` | Template for your API key |
| `.gitignore` | Keeps `.env` out of version control |

## References

- [TypeSafe documentation](https://docs.typesafe.ai/introduction)
- [Quick start](https://docs.typesafe.ai/introduction/quickstart)
