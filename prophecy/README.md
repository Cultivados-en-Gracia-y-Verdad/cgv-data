# Prophecy Scripture Research Graph

A Scripture-only, file-based research system for Daniel and its explicit biblical connections.

## Locked architecture

The permanent record is a graph of small, versioned files. Search results, browser state, and chat are temporary workspaces only.

The system follows this flow:

```text
Original-language corpora
        ↓
Compiler quarry/search tools
        ↓
Researcher review
        ↓
Accepted linked files in cgv-data/prophecy
        ↓
Generated indexes, timelines, studies, and manuals
        ↓
LBF presentation output
```

## Language policy

- **Hebrew, Aramaic, and Greek are canonical for research.**
- Original-language tokens, lemmas, morphology, syntax, and textual links are the basis for quarrying and verification.
- **LBF is the only Bible surface used in generated Spanish output.**
- LBF wording is resolved at render/export time; it is not the basis for lexical identity or original-language connections.
- A research record may point to an LBF reference or alignment, but it must preserve the original-language anchor.

## Repository roles

### `cgv-data`

Stores stable, reviewable research files and generated indexes:

- passage records
- terms and entities
- explicit statements
- connections
- chronology events and relations
- topic and study structures
- unresolved questions
- generated query indexes

### `cgv-reader`

The existing **Compiler** is the quarrying and assembly application. It reads original-language corpora and `cgv-data/prophecy`, lets the researcher accept or reject findings, writes settled records, and generates LBF-facing output.

The app must not treat localStorage or a live search result as the final research record.

## File graph

```text
prophecy/
├── README.md
├── schema.sql                  # optional generated-index database schema
├── passages/                   # bounded passage records
├── statements/                 # explicit textual claims
├── terms/                      # original-language terms and named entities
├── events/                     # events stated in Scripture
├── connections/                # passage-to-passage evidence records
├── chronology/                 # sequence and duration relations
├── studies/                    # ordered research structures
├── unresolved/                 # retained questions and unknown referents
├── indexes/                    # generated manifests/query indexes
└── data/                       # legacy/bootstrap tabular data during migration
```

## File principles

1. One file represents one durable research object.
2. Every object has a stable ID independent of its filename.
3. Links use stable IDs, not free-text titles.
4. Statements distinguish exact textual facts from researcher observations.
5. Connections always include an evidence class.
6. Unknown referents remain unresolved records; they are not silently identified.
7. Generated indexes may be rebuilt and are not authoritative over source files.
8. Accepted research must be written to disk before it can be used as settled manual structure.

## Evidence classes

- **E1 — Explicit cross-reference:** One passage names another prophet, writing, or saying.
- **E2 — Explicit identification:** Scripture identifies a symbol, person, kingdom, object, or term.
- **E3 — Shared wording/entity/number:** Passages share a term, title, place, person, number, or image.
- **E4 — Stated chronological relation:** Scripture uses sequence or duration language.
- **E5 — Observed verbal parallel:** Similar wording appears, but Scripture does not explicitly join the passages.

Only E1 and E2 may establish identity, and only within the scope stated by the text.

## Research restrictions

- Scripture is the only source for research claims.
- No theological teaching is stored.
- No historical identification is entered unless Scripture itself identifies it.
- Shared wording does not automatically prove that two passages describe the same event.
- Distinct titles remain distinct.
- Unknown referents remain unknown.
- Search discovers candidates; the researcher decides what becomes a file.

## First graph scope

The initial passage anchors are:

- Daniel 2:31–45 — Aramaic
- Daniel 7:1–28 — Aramaic
- Daniel 9:20–27 — Hebrew

The initial explicit external connection is Daniel 9:2 to the writings of Jeremiah concerning seventy years.

## Save lifecycle

A quarry result moves through these states:

```text
candidate → reviewed → accepted → file written → indexed → available for output
```

Rejected candidates are not treated as connections. Accepted records remain editable through normal Git history.
