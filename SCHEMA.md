# Wiki Page Schema

Every wiki page must follow this structure.

## Required Metadata

Each page must contain YAML frontmatter:

- `title`: Page title
- `page_type`: source, concept, entity, or draft
- `status`: draft, reviewed, or published
- `created`: Creation date
- `updated`: Last update date
- `sources`: List of source IDs used

## Page Content

Each page must contain:

1. Summary
2. Main Content
3. Key Facts
4. Sources and Evidence
5. Related Pages

## Rules

- Every factual claim must have a source.
- Never invent sources or evidence.
- Clearly identify uncertain information.
- Keep content in Markdown format.
- Draft pages must be reviewed before publishing.


## Schema v2: LLM-maintained pages

Pages in `wiki/concepts/` and `wiki/entities/` are written by the LLM during ingest.

Extra frontmatter fields:
- `facts`: list of `{fact, source_id, lines, quote}`. This is the machine-readable knowledge. The body is rendered from it.
- `related`: list of page ids.
- `conflicts`: contradictions detected during ingest.
- `valid_until`: optional expiry date (YYYY-MM-DD).

Rules enforced by code (not by the LLM):
- A fact is saved only if its `quote` is found in `raw/<source_id>.md`.
- Figures in a fact must appear in its quote. The LLM may not calculate numbers.
- Line numbers are found by Python, not by the LLM.
- Existing facts are never deleted by an update.
- Any LLM change resets `status` to `draft`. Only a human review makes it `reviewed`.
- `raw/` is immutable. Page ids look like `concepts/power_subsidy` and are used for citations.