# Prophecy Scripture Research Graph

A Scripture-only, file-based research system whose source corpus is the entire Protestant canon, from Genesis through Revelation.

Daniel is the first research entry point. It is not the boundary of the system.

## Canon scope

- All 66 books of the Protestant canon are eligible source material.
- Neither Testament is secondary or merely supplementary.
- Prophetic data may occur in narrative, poetry, prophetic speech, dreams, visions, discourse, letters, quotations, promises, warnings, chronological statements, fulfillment statements, kingdom statements, resurrection statements, judgment statements, and other forms explicitly present in Scripture.
- Revelation, Acts, the Corinthian letters, the Thessalonian letters, John, Matthew, and every other canonical book may contribute records and connections.
- A passage is included because of what its text states or explicitly connects, not because of a theological system assigned to it.

The source-scope record is `scope/protestant-canon.yaml`.

## Locked architecture

The permanent record is a graph of small, versioned files. Search results, browser state, and chat are temporary workspaces only.

The system follows this flow:

```text
Hebrew, Aramaic, and Greek canonical corpora
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
- Language is assigned at the token or passage level from the original-language corpus, not assumed merely from the book or Testament.
- Original-language tokens, lemmas, morphology, syntax, discourse markers, and textual links are the basis for quarrying and verification.
- **LBF is the only Bible surface used in generated Spanish output.**
- LBF wording is resolved at render/export time; it is not the basis for lexical identity or original-language connections.
- A research record may point to an LBF reference or alignment, but it must preserve the original-language anchor.

## Repository roles

### `cgv-data`

Stores stable, reviewable research files and generated indexes:

- canon scope
- passage records from any canonical book
- terms and named entities
- explicit statements
- events
- passage-to-passage connections
- chronology events and relations
- topic and study structures
- unresolved questions
- generated query indexes

### `cgv-reader`

The existing **Compiler** is the quarrying and assembly application. It reads the original-language corpora and `cgv-data/prophecy`, lets the researcher accept or reject findings, writes settled records, and generates LBF-facing output.

The app must not treat localStorage, an in-memory result, or a live search result as the final research record.

## File graph

```text
prophecy/
├── README.md
├── schema.sql                  # optional generated-index database schema
├── scope/                      # canon and collection boundaries
├── passages/                   # bounded passage records from any canonical book
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
4. Every textual record retains its canonical reference and original-language anchor.
5. Statements distinguish exact textual facts from researcher observations.
6. Connections always include an evidence class.
7. Unknown referents remain unresolved records; they are not silently identified.
8. Generated indexes may be rebuilt and are not authoritative over source files.
9. Accepted research must be written to disk before it can be used as settled manual structure.
10. No book, author, genre, or Testament is excluded from the quarry.

## Evidence classes

- **E1 — Explicit cross-reference:** One passage names another prophet, writing, saying, or prior scriptural statement.
- **E2 — Explicit identification:** Scripture identifies a symbol, person, kingdom, object, event, or term.
- **E3 — Shared wording/entity/number:** Passages share an original-language term, title, place, person, number, image, or stated action.
- **E4 — Stated chronological relation:** Scripture uses sequence or duration language.
- **E5 — Observed verbal parallel:** Similar wording appears, but Scripture does not explicitly join the passages.

Only E1 and E2 may establish identity, and only within the scope stated by the text.

## Research restrictions

- Scripture is the only source for research claims.
- No theological teaching is stored.
- No historical identification is entered unless Scripture itself identifies it.
- Shared wording does not automatically prove that two passages describe the same event.
- Canonical proximity does not establish identity.
- Distinct titles remain distinct.
- Unknown referents remain unknown.
- Search discovers candidates; the researcher decides what becomes a file.
- A New Testament passage may explicitly identify, quote, explain, or connect an Old Testament passage; that relationship is stored according to the wording actually present.

## Initial filling order

The first passage anchors are:

- Daniel 2:31–45 — Aramaic
- Daniel 7:1–28 — Aramaic
- Daniel 9:20–27 — Hebrew

The first explicit external connection is Daniel 9:2 to the writings of Jeremiah concerning seventy years.

These are the first files being populated, not a limitation on later collection. The graph is designed to expand throughout Genesis–Revelation, including passages in Revelation, Acts, 1–2 Corinthians, 1–2 Thessalonians, John, Matthew, and the remainder of Scripture.

## Save lifecycle

A quarry result moves through these states:

```text
candidate → reviewed → accepted → file written → indexed → available for structure/output
```

Rejected candidates are not treated as connections. Accepted records remain editable through normal Git history.
