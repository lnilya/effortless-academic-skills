---
name: ea-obsidian-world-builder
description: "Build a Wikipedia-style Obsidian knowledge network from academic PDFs, or expand an existing one with new papers. Use when the user wants to create a concept network, knowledge graph, or Obsidian world from papers — or add new papers to one already built. Trigger phrases include build an Obsidian world, create a knowledge network, extract concepts into Obsidian, build a knowledge graph, turn papers into an Obsidian vault, add this paper to my vault, expand my knowledge network, I have new papers to add, update the world with these papers. Use proactively whenever multiple PDFs are provided alongside mentions of Obsidian, concepts, or knowledge organisation."
---

# Academic Obsidian World Builder

This skill transforms a collection of academic PDFs into a rich, interconnected Obsidian knowledge network — a Wikipedia-style web of concept notes, each populated with atomic sentences drawn directly from the literature and linked to one another.

## Overview of the Workflow

This skill has two modes. Determine which applies before doing anything else:

- **Build mode** — Creating a new knowledge network from scratch (Phases 1–4)
- **Expand mode** — Adding new papers to an existing vault (Phase 5)

If the user mentions an existing vault or says they want to add papers to an existing network, use Expand mode (Phase 5). Otherwise, use Build mode.

### Build mode — four sequential phases

Complete each phase fully before starting the next. Phases 1 and 3 can use parallel subagents for large paper sets (≥5 papers or ≥10 concepts respectively).

1. **Extraction** — Read each PDF, extract text, and produce structured data per paper (concepts + atomic findings)
2. **Synthesis** — Aggregate concepts across all papers, deduplicate, and present a concept list for user review
3. **World Building** — Generate one Wikipedia-style Obsidian note per concept, populated with cited atomic sentences and wikilinks
4. **Paper Stubs** — Create reference notes for each paper

Before starting, ask the user:
- Where the PDFs are located (if not already clear from context)
- Where to write the output (which Obsidian vault folder, or create a new folder)

If the user has the `obsidian:obsidian-cli` skill available, use it to write notes directly to their vault. Otherwise, write `.md` files to the output directory and tell the user where to find them.

---

## Phase 1: PDF Extraction

### Install dependencies

```bash
pip install pdfplumber --break-system-packages 2>/dev/null
```

### Extract text from each PDF

Use the bundled script for each PDF:

```bash
python <skill_dir>/scripts/extract_pdf_text.py "<pdf_path>" "<workspace>/_extracted/<paper_slug>.txt"
```

The script outputs plain text. Store all extracted text in `<workspace>/_extracted/`.

If a PDF produces very little text (< 200 words), it is likely a scanned/image-only PDF. Note this and skip it, informing the user at the end.

### Extract structured data from each paper

For each paper, read its extracted text and produce a JSON file at `<workspace>/_paper_data/<paper_slug>.json`.

**If there are 5 or more papers, spawn one subagent per paper (or per batch of 3) to do this in parallel.** Each subagent receives:
- The full extracted text of its assigned paper(s)
- Instructions to produce the JSON below
- The output path(s) to write to

Each JSON file must follow this schema:

```json
{
  "title": "Full paper title as it appears in the document",
  "authors": ["Smith J", "Jones K", "Brown L"],
  "year": 2023,
  "citation_key": "Smith 2023",
  "abstract": "The abstract text...",
  "concepts": [
    "biodiversity",
    "climate change",
    "species richness",
    "habitat fragmentation"
  ],
  "findings": [
    {
      "concept": "biodiversity",
      "statement": "Global biodiversity loss is accelerating at rates 100–1000 times above natural background levels.",
      "related_concepts": ["climate change", "habitat fragmentation"],
      "section": "results"
    },
    {
      "concept": "climate change",
      "statement": "Elevated atmospheric CO₂ concentrations correlate with a 2.3°C increase in mean annual temperature across temperate biomes.",
      "related_concepts": ["biodiversity", "species distribution"],
      "section": "discussion"
    }
  ]
}
```

**Guidelines for extraction:**

*Citation key format:*
- All papers regardless of author count: `Smith 2023` (first author surname + space + year)
- If year is unclear, use `Smith ND` (no date)
- Always use this format — never append "Etal" or include co-author names in the key

*Concepts (list 5–20 per paper):*
- Include both specific concepts (e.g., "beta diversity", "nitrogen fixation") and broader ones (e.g., "biodiversity", "ecosystem function")
- Concepts should be nouns or noun phrases, not verbs or adjectives
- Use lowercase for concepts consistently

*Findings — this is the most important part:*
- Focus strictly on **Results, Discussion, and Conclusions** — do NOT include claims from the Introduction or Literature Review (those are background, not this paper's contribution)
- Each finding is one atomic sentence: a single, specific claim or measurement
- Findings should be the paper's **own contribution**, not citations to other work
- Write at 2–3 findings per concept the paper meaningfully addresses — not just mentions
- Academic language only; preserve numerical values, units, and statistical terms when present
- `related_concepts`: other concepts from the paper's concept list that appear meaningfully in the same claim
- `section`: one of `"results"`, `"discussion"`, or `"conclusions"`

---

## Phase 2: Concept Synthesis

Read all `_paper_data/*.json` files. Then:

1. **Collect** all concepts from every paper's `"concepts"` array
2. **Merge synonyms and near-duplicates** — e.g., "biodiversity loss" and "biodiversity decline" → choose the more common/precise term; "CO₂" and "carbon dioxide" → "carbon dioxide". Use your judgment; prefer specific over vague.
3. **Count** how many distinct papers reference each concept
4. **Sort** descending by paper count (most cross-cutting concepts first)
5. **Filter out** concepts cited by only one paper if there are more than 30 total concepts — flag them in a separate section for the user to optionally include

Write the concept list to `<workspace>/concept_list.md`:

```markdown
# Concept List — Please Review Before Proceeding

I've extracted **N concepts** from **M papers**. Review this list:
- ✏️ Edit names (this becomes the note title)
- ❌ Delete lines you don't want
- ➕ Add new lines for concepts you feel are underrepresented
- The indented lines show which papers discuss each concept

When you're happy, let me know and I'll build the knowledge network.

---

## Core Concepts (discussed in 3+ papers)

- biodiversity (12 papers: Smith 2023, Jones 2022, ...)
- climate change (10 papers)
- species richness (8 papers)

## Supporting Concepts (1–2 papers)

- trophic cascade (2 papers)
- keystone predator (1 paper)

## Concepts I'm Unsure About (possible duplicates — your call)

- biodiversity loss ↔ biodiversity (may overlap)
- CO₂ emissions ↔ carbon dioxide (may overlap)
```

**Present this file to the user and explicitly ask them to review it.** Say something like:

> "Here's the concept list I extracted across all your papers. Please review it — edit names, remove anything irrelevant, add any gaps you notice — and let me know when you're ready. I won't start building the notes until you confirm."

**Do NOT proceed to Phase 3 without explicit user confirmation.**

---

## Phase 3: World Building

After the user confirms the concept list, parse it to get the final list of approved concepts (ignore any lines that don't look like concept entries).

For each concept, generate one Obsidian note. **If there are 10 or more concepts, spawn subagents in batches of 10–15.** Each subagent:
- Receives its batch of concept names
- Has read access to all `_paper_data/*.json` files
- Scans **all** papers for relevant findings for each concept (not just papers that listed the concept)
- Writes the completed notes to `<vault_output>/Concepts/`

### Note structure

Every concept note follows this exact template:

```markdown
---
tags: [concept, knowledge-network]
aliases: []
---

# <Concept Name>

<A 2–3 sentence academic definition of this concept, written in your own words. This sets the stage — no citations needed here. Be precise and accurate.>

## <Thematic Section 1>

- <Atomic sentence with [[related concept]] linked inline where it appears.> [[CitationKey]]
- <Atomic sentence linking [[another concept]] where meaningful.> [[CitationKey]]

## <Thematic Section 2>

- <Atomic sentence.> [[CitationKey]]

## Related Concepts

- [[concept-a]] — <5–10 words explaining how it relates to this concept>
- [[concept-b]] — <5–10 words explaining how it relates to this concept>
- [[concept-c]] — <5–10 words explaining how it relates to this concept>
```

### Wikilink conventions

These are Obsidian wikilinks — they must exactly match the concept names in the approved list (Obsidian is case-insensitive but be consistent):

- **Concept links**: `[[biodiversity]]`, `[[climate change]]`, `[[habitat fragmentation]]`
  - Link a concept inline whenever it appears meaningfully in an atomic sentence — replace the word/phrase in the sentence itself, don't add the link separately
  - Only link concepts that are in the approved concept list; do not invent links
  - Also listed in the "Related Concepts" section at the bottom
- **Citation links**: `[[Smith 2023]]` — always at the **end** of the atomic sentence, in its own brackets, after the period
  - Format: `Sentence text here. [[CitationKey]]`
  - Never embed the citation mid-sentence

### Atomic sentence rules

An atomic sentence is a single, verifiable claim attributed to one source. It must:
- Express exactly **one claim**
- Be **specific** — quantitative where possible, never vague
- Be in **academic language** — no colloquialisms
- Be **1–2 sentences maximum** (occasionally 2 if inseparable)
- Come from the paper's **own findings**, not its background citations
- Include **inline wikilinks** for any concept from the approved list that appears in the claim — replace the term in the sentence: `[[Habitat fragmentation]] reduces [[species richness]] in old-growth temperate forests.` [[Pereira 2022]]
- If no approved concept appears naturally in a sentence, no inline link is needed — do not force links

### Related Concepts rules

The Related Concepts section must:
- List every approved concept that is meaningfully connected to this note's concept
- Use bullet list format, one concept per line: `- [[concept]] — <relation phrase>`
- The relation phrase is **5–10 words** explaining the specific relationship — not a generic description of the linked concept, but how it connects to *this* concept
- Good examples:
  - `- [[poleward shift]] — most range shifts move poleward specifically`
  - `- [[habitat fragmentation]] — reduces corridors needed for range expansion`
  - `- [[species richness]] — declines as ranges contract under warming`
- Bad examples (too vague or just defines the concept):
  - `- [[poleward shift]] — a type of range shift` ✗
  - `- [[habitat fragmentation]] — fragmentation of natural habitats` ✗

### Thematic sections

Group atomic sentences into 2–5 thematic sections per note. Choose headings that fit the concept naturally. Good options: *Global Trends*, *Mechanisms*, *Measurement & Indices*, *Regional Patterns*, *Ecological Impacts*, *Policy Implications*, *Methodological Considerations*, *Interventions & Restoration*, *Drivers*, *Relationships to Other Factors*.

Not every note needs the same sections — let the content guide you.

### Coverage requirement

Every concept note should contain at least **3 atomic sentences** from at least **2 different papers** (when available). If a concept is only discussed in one paper, write what's there and note it with a callout:

```markdown
> [!note] Limited sources
> This concept is currently documented from a single paper. Consider adding more literature.
```

---

## Phase 4: Paper Stub Notes

Create one note per paper in `<vault_output>/Papers/<CitationKey>.md`:

```markdown
---
tags: [paper]
title: "<Full paper title>"
authors: [<comma-separated author list>]
year: <year>
citation_key: <CitationKey>
---

# [[<CitationKey>.pdf|<Full paper title>]]

> [!abstract]
> <Abstract text>

## Key Concepts

[[concept-a]] | [[concept-b]] | [[concept-c]]

## Main Contributions

- <One atomic sentence summarising each major finding from this paper>
- <Another finding>
```

The "Key Concepts" line should list every concept from the approved concept list that this paper addresses.

---

## Quality Checks

Before declaring completion, verify:

1. Every concept note has ≥ 3 atomic sentences (or has a "Limited sources" callout)
2. Every atomic sentence ends with a `[[CitationKey]]` wikilink
3. The "Related Concepts" section has ≥ 2 entries, each with a non-generic relation phrase
4. A paper stub exists for every citation key used across all concept notes
5. No orphan concepts — every concept appears in at least one other note's "Related Concepts" section

If any check fails, fix it before presenting the output.

---

## Presenting Results

When all notes are written, tell the user:

- Total concept notes created
- Total paper stubs created
- Top 5 most-referenced concepts (by how many atomic sentences they appear in)
- Any PDFs that were skipped (scanned/unreadable)
- Any concepts from the approved list that ended up with < 3 sentences (limited coverage)

Example:

> ✅ Built **47 concept notes** and **18 paper stubs** across your Obsidian vault.
>
> **Most-connected concepts:** biodiversity (34 sentences), climate change (28), species richness (21), habitat fragmentation (19), ecosystem function (17)
>
> **Skipped PDFs:** `jones_2019_scan.pdf` (image-only, no extractable text)
>
> **Limited coverage:** "keystone predator" (only 1 paper, 2 sentences)

---

## Notes on Large Paper Sets

For very large collections (30+ papers), the extraction phase can take significant time. Keep the user informed of progress:
- "Processing paper 5/30..."
- "Concept synthesis complete — found 68 unique concepts across 30 papers"
- "Building concept notes in parallel — batch 1/4 underway..."

Transparency about progress makes the wait feel productive.

---

## Phase 5: Expand — Adding New Papers to an Existing Vault

Use this phase when the user already has a knowledge network built with this skill and wants to integrate one or more new papers into it.

### Before you begin

**Always issue this warning first, before doing anything else:**

> ⚠️ **Back up your vault before proceeding.** Expanding the network will modify existing concept notes in place. If something goes wrong, you'll want to be able to restore them. Copy your `Concepts/` and `Papers/` folders somewhere safe, then let me know when you're ready.

Wait for the user to confirm they've made a backup before proceeding.

Then ask:
- Where the new PDF(s) are located
- Where the existing vault is (path to `Concepts/` and `Papers/` folders)

---

### Step 5.1: Extract new paper data

Run Phase 1 (PDF extraction) on the new paper(s) only, writing to `<workspace>/_extracted/` and `<workspace>/_paper_data/` as usual.

---

### Step 5.2: Identify concepts — new vs. existing

Read the existing vault: scan all `.md` files in `Concepts/` and collect their note titles as the **existing concept list**.

From the new paper's extracted data, collect its concepts. Then classify each one:

- **Existing concept** — matches (or is a near-synonym of) a concept already in the vault
- **New concept** — genuinely absent from the vault

Present this classification to the user before making any changes:

```
Here's what I found in the new paper(s):

**Concepts already in your vault** (will be expanded with new sentences):
- biodiversity (matches existing note)
- species richness (matches existing note)
- climate change (matches existing note)

**New concepts not yet in your vault** (new notes will be created):
- thermal tolerance
- microhabitat heterogeneity

**Possible overlaps — your call:**
- "range contraction" ↔ existing "range shift" — treat as same or separate?

Shall I proceed with this plan, or would you like to adjust anything?
```

**Do not modify any files until the user confirms.** They may want to merge, rename, or skip certain concepts.

---

### Step 5.3: Update existing concept notes

For each existing concept that the new paper addresses, open the concept note from `Concepts/<concept>.md` and add new atomic sentences from the paper.

**Rules for updating:**
- Find the most appropriate thematic section and append the new sentence(s) there. If no existing section fits, add a new one.
- Do not remove or alter any existing content — only add.
- Follow all atomic sentence rules (inline concept wikilinks, citation link at end).
- If the new paper introduces a relationship between this concept and a concept not already in the Related Concepts section, add it with a relation phrase.

---

### Step 5.4: Create new concept notes

For any concepts classified as new, generate a full concept note following the same template and rules as Phase 3. Cross-link these new notes to existing concepts where relevant — both inline in atomic sentences and in the Related Concepts section.

Also check the reverse: for any existing concept that is meaningfully related to a new concept, open that existing note and add the new concept to its Related Concepts section.

---

### Step 5.5: Create the paper stub

Create a paper stub for the new paper in `Papers/<CitationKey>.md` following the Phase 4 template.

---

### Step 5.6: Present the expansion summary

When all edits are complete, give the user a clear summary:

```
✅ Expansion complete.

**New paper added:** Smith 2024 — "Full title here"

**Existing concept notes updated (N):**
- [[biodiversity]] — 3 new sentences added (Results, Drivers sections)
- [[species richness]] — 2 new sentences added (Regional Patterns section)
- [[climate change]] — 1 new sentence added; also added new related concept [[thermal tolerance]]

**New concept notes created (N):**
- [[thermal tolerance]] — 4 sentences from Smith 2024
- [[microhabitat heterogeneity]] — 3 sentences from Smith 2024

**Anything worth noting:**
```

Use that last section to flag anything that stands out — for example:
- A new concept that connects surprisingly strongly to many existing ones
- A finding that appears to tension with something already in the vault (e.g. a contradictory claim on the same concept)
- A concept from the new paper that is unusually isolated (few links to the rest of the network)
- An existing concept note that now has many more sentences than others and might benefit from being split

Keep this section brief and specific — only mention things that genuinely jump out, not generic observations.
