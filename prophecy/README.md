# Prophecy Scripture Research System

A Scripture-only research repository for building a teaching manual on Daniel and its explicit biblical connections.

## Core principle

The repository is the permanent record. Chat is only a working interface.

The system stores these layers separately:

1. **Passages** — bounded Scripture references and text-bound observations.
2. **Statements** — individual claims explicitly stated in a passage.
3. **Connections** — relationships between passages, classified by textual evidence.
4. **Chronology** — dates, reigns, durations, and sequence markers stated in Scripture.
5. **Topics** — indexes for gathering related records.
6. **Output plan** — ordered records for future lessons, timelines, and manual chapters.

## Research restrictions

- Scripture is the only source.
- No theological teaching is stored.
- No historical identification is entered unless Scripture itself identifies it.
- Shared wording does not automatically prove that two passages describe the same event.
- Distinct titles remain distinct.
- Unknown referents remain unknown.
- Licensed Bible text must remain local and must not be committed.

## Evidence classes

- **E1 — Explicit cross-reference:** One passage names another prophet, writing, or saying.
- **E2 — Explicit identification:** Scripture identifies a symbol, person, kingdom, or object.
- **E3 — Shared wording/entity/number:** Passages share a term, title, place, person, number, or image.
- **E4 — Stated chronological relation:** Scripture uses sequence or duration language.
- **E5 — Observed verbal parallel:** Similar wording appears, but Scripture does not explicitly join the passages.

Only E1 and E2 may establish identity, and only within the scope stated by the text.

## Repository structure

- `schema.sql` — database schema for local generation.
- `data/*.csv` — canonical, reviewable research records committed to Git.
- `templates/` — passage, topic, and manual templates.
- `scripts/collector.py` — local search, validation, and export utility.
- `exports/` — generated outputs; normally not committed unless intentionally published.

A local SQLite database may be generated from the CSV data, but the committed CSV records are the portable source of truth.

## Initial research scope

Primary Daniel units:

- Daniel 2
- Daniel 7
- Daniel 9

Explicit or textually relevant framework passages currently seeded:

- Jeremiah 25 and 29 — seventy years, explicitly named in Daniel 9:2
- Jeremiah 30 — Jacob's trouble
- Daniel 12 — time of trouble
- Matthew 24 — explicit reference to Daniel and great tribulation
- Day of the LORD passages
- Kingdom passages
- Babylon passages
- Messiah / Anointed One passages
- The prince that shall come
- The command concerning Jerusalem

## Recommended workflow

1. Add a passage record.
2. Break it into explicit statements.
3. Record connections with an evidence class.
4. Add chronology only when Scripture gives a marker.
5. Mark records verified after checking the selected source text.
6. Add verified record IDs to the output plan.
7. Generate a topic study, timeline, or manual draft locally.
