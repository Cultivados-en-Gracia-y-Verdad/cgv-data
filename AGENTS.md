# cgv-data — agent entry point

Read [`DATA_CONTRACT.md`](DATA_CONTRACT.md) before changing any data, import,
export, alignment, translation, approval, or dataset-loading code.

If a request conflicts with `DATA_CONTRACT.md`, stop and explain the conflict.
Do not work around it.

Never move, copy, regenerate, synchronize, or delete canonical data unless the
task explicitly names the source repository, destination repository, migration
phase, and validation procedure.

When uncertain which copy is authoritative, stop. Do not choose by timestamp,
file size, apparent completeness, or Git history alone.

## What this repository is

This repository contains **published output only**. It is the distribution point
for stable CGV content, not a place to work. For LBF it is the published source
of truth; the editable source of truth is `Biblia-LBF`.

Canonical architecture: `Biblia-LBF/docs/architecture/CGV_DATA_ARCHITECTURE.md`.

## Hard rules

- Never manually edit generated LBF text or alignment. Fix it in `Biblia-LBF`
  and re-publish.
- Never add drafts, approvals, review queues, translator state, user progress, or
  repair scripts.
- **Existing release versions are immutable.** Publish a new version directory;
  never rewrite one that has shipped.
- LBF text and LBF alignment publish together, atomically, under the same version.
- Every file in a release is declared by that release's manifest. An undeclared
  file must not ship.
- LBF updates identify their exact `Biblia-LBF` source commit.
- Consumers may read; they may never write back into this repository.

## Dataset layout

```text
bibles/LBF/
  current.json          # small mutable pointer to one immutable version
  versions/
    1.0.0/
      manifest.json     # provenance, scope, licence, checksums
      ...               # every file listed in manifest.checksums
```

`manifest.json` validates against
[`schemas/dataset-manifest.schema.json`](schemas/dataset-manifest.schema.json)
and must carry:

| Field | Meaning |
| --- | --- |
| `generated: true` | machine-produced, not authored here |
| `doNotEdit: true` | edit the source repository and re-publish |
| `sourceRepository` | repository owning the editable truth |
| `sourceCommit` | exact 40-char commit SHA that produced these bytes |
| `generator` / `generatorVersion` | which exporter, which version |
| `schemaVersion` | consumer-facing format version |
| `datasetVersion` | semantic version of this release, immutable |
| `checksums` | every published file, path → sha256 |

`current.json` validates against
[`schemas/current-pointer.schema.json`](schemas/current-pointer.schema.json). It
is the only file in a dataset that may change after publication, and it may only
move to a version that exists and carries a valid manifest.

## Before you open a pull request

```bash
python3 scripts/check-data-contract.py
```

The check is read-only. It fails on any violation that is not already listed in
`.data-contract-baseline.json` — the problems that existed when the check was
introduced. Shrink that list; never grow it.

Do not edit data to make a check pass. If a check is wrong, fix the check and say
so in the pull request.
