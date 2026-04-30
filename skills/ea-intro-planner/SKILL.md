---
name: ea-intro-planner
description: "Plan and scaffold an academic introduction section from source papers, context, or rough notes. Use this skill whenever Ilya wants to structure an intro, outline a paper's opening, map the literature into a writing plan, figure out what paragraphs an introduction needs, or asks \"what should my intro cover?\", \"help me plan my introduction\", \"outline an intro from these papers\", \"what topics should I introduce?\", \"scaffold my intro section\", \"turn these papers into an intro plan\", or \"structure my background section\". Also trigger when the user uploads or pastes papers/abstracts and wants to know what to write about — even if they don't say \"introduction\" explicitly. This skill does NOT write the prose; it produces a clear paragraph-by-paragraph blueprint that guides writing. For the actual prose, hand off to ea-academic-writer."
---

# EA Introduction Planner

Transforms source papers, context, and rough notes into a structured, paragraph-by-paragraph **writing blueprint** for an academic introduction based on given sources. The sources define the totality of information, the user chooses what they want to focus on. The output tells the user exactly what to write in each paragraph — not the words themselves, but the logical instructions. For the actual prose, use **ea-academic-writer**.

---

## The logic behind this approach

An introduction fails when the writer doesn't know what each paragraph is *for*. The most common failure: a stream-of-consciousness literature dump that doesn't build an argument. This skill solves that by:

1. **Mapping the territory first** — extracting what topics exist in the literature
2. **Filtering to what matters** — letting the user choose the relevant thread using a series of multiple choice questions
3. **Designing the argument** — constructing paragraph blueprints that build logically toward the research gap and the paper's contribution

The goal is that after this skill runs, the user knows exactly what every paragraph does and why, and can go look up the specific details (e.g., on [Consensus](https://consensus.app)) to fill in the citations.

---

## Phase 0 — Intake

Before doing anything else, assess what you've been given:

- **Papers or documents**: PDFs, pasted text, abstracts, URLs, excerpts
- **Context**: research question, field, thesis, any framing the user provided
- **Scope**: how many paragraphs? (default: 3–5 if not specified)

If you have no sources at all — just a topic name — proceed with knowledge-based analysis but clearly mark the topic hierarchy as **[from prior knowledge — verify with literature]**.

If you have more than 3 papers or substantial documents (>2000 words combined), use the **subagent strategy** below. Otherwise, analyse inline.

---

## Phase 1 — Source Analysis

### Subagent strategy

When sources are large or numerous, spawn one subagent per paper or per major document. Each subagent's job: read the source and return a compressed topic card in this exact format.

**Prompt to each subagent:**
```
Read the following source carefully.

Your job is to extract a topic card for an academic introduction planner.

Return ONLY a JSON object in this format:
{
  "source": "Author (Year) or filename",
  "field": "brief field/subfield",
  "cited_references": [
    "Author (Year) — one-line summary of what this paper is cited for in the source"
  ],
  "big_topics": [
    {
      "name": "Big Topic Name",
      "small_topics": [
        {
          "name": "specific concept or finding",
          "one_line": "one sentence explaining what this source says about it",
          "cited_refs": ["Author (Year)"]
        }
      ]
    }
  ]
}

Rules:
- 2–5 big topics per paper
- 3–8 small topics per big topic
- Keep names short and noun-phrase form (e.g., "working memory capacity", "neural plasticity mechanisms")
- The one_line must be a specific claim, not a vague description
- Do not add interpretation; report what the paper says
- cited_references: extract every reference cited in the paper with a one-line note on what claim it supports
- cited_refs per small topic: list the specific references from cited_references that back this small topic

Source:
[PASTE SOURCE HERE]
```

Once all subagents return, **merge their topic cards** in your main context (see Phase 1b).

### Phase 1b — Merge and build the hierarchy

Merge all topic cards into a unified two-level hierarchy. Also merge the `cited_references` lists from all papers into a single deduplicated reference pool — this becomes the source for reference suggestions in Phase 3.

```
Big Topic
└── Small Topic 1 (refs: Chen 2018, Parmesan 2006)
└── Small Topic 2 (refs: Thomas 2010)
└── Small Topic 3 (refs: Chen 2018, Walther 2002)  ← overlaps with Big Topic X
```

**Overlap rule:** If the same small topic appears across multiple sources or under multiple big topics, flag it with `⟳ overlaps with [Big Topic > Small Topic]`. Overlapping topics are structurally important — they often represent the connective tissue of the field and make strong candidates for introduction paragraphs.

**Save to file:** Write the full hierarchy to `intro_workspace.json` in the working directory (see format below). Include the merged reference pool. This keeps your context clean and gives you a persistent record. Update this file at the end of every phase.

---

## Workspace file format

```json
{
  "context": "brief description of the research area and paper",
  "sources": ["list of source names"],
  "reference_pool": [
    {"ref": "Author (Year)", "note": "what this paper is cited for"}
  ],
  "big_topics": [
    {
      "name": "Big Topic Name",
      "small_topics": [
        {
          "name": "small topic name",
          "one_line": "what the literature says about it",
          "refs": ["Author Year", "Author Year"],
          "overlaps_with": ["Other Big Topic > Other Small Topic"]
        }
      ],
      "key_refs": ["most cited refs across this big topic"]
    }
  ],
  "selected_big_topics": [],
  "selected_small_topics": [],
  "outline": []
}
```

---

## Phase 2 — Topic Curation (interactive)

Present the hierarchy to the user in a clean, readable format — not JSON, but a structured visual:

```
TOPIC MAP
─────────────────────────────────────────────────────

📌 [Big Topic 1: Name]
   Key references: Author Year; Author Year
   └─ Small topic 1.1: one-line description
   └─ Small topic 1.2: one-line description  ⟳ overlaps with Big Topic 3
   └─ Small topic 1.3: one-line description

📌 [Big Topic 2: Name]
   Key references: Author Year
   └─ Small topic 2.1: one-line description
   └─ Small topic 2.2: one-line description
   ...

─────────────────────────────────────────────────────
```

Then ask one focused question:

IMPORTANT: Ask questions with the clarifying questions interface, it should be interactive and clickable for the user, rather than in text.

> **Which of these are relevant to your introduction?**
> You can say things like:
> - "Keep Big Topics 1 and 3, drop 2"
> - "All of Big Topic 1, but only small topics 2.1 and 2.3 from Big Topic 2"
> - "Focus on anything related to [X]"
> - "Just keep the overlapping ones"
> - "All of it — use your judgment to pick the most important"

Wait for the user's response before proceeding to Phase 3.

---

## Phase 3 — Introduction Outline

Using the selected topics, generate a paragraph-by-paragraph **blueprint** for the introduction.

### Structural logic

A standard academic introduction moves through these functions. Not every intro needs all of them — choose based on the field and paper type:

1. **Establish the domain and stakes** — why does this area of research matter?
2. **Introduce the key mechanisms or constructs** — what are the central concepts at play?
3. **Describe the current state of knowledge** — what do we know, and how well-established is it?
4. **Identify the gap or tension** — what is unresolved, contested, or missing?
5. **Position the present study** — what does this paper do, and why does it matter?

Map the selected small topics onto these functions. Each paragraph should cover one coherent function and draw on 2–5 related small topics.

### Paragraph blueprint format

Keep everything tight. Topic sentences are one punchy claim. Content instructions are short verb phrases — the writer fills in the details. Closing sentences are one line.

```
**P[N] — [Function label]**

*[Specific claim sentence — no throat-clearing]*

- [Verb] [concept], because [1 clause why]
- [Verb] [concept], because [1 clause why]
- [Verb] [concept], because [1 clause why]

*→ [Implication / bridge / gap — one line]*

Refs: Author (Year); Author (Year) | 💡 "[search term]" on Consensus
```

**Content instructions — the rules:**

- Start with an action verb: *Explain, Show, Contrast, Argue, Note, Define, Establish, Trace*
- One clause for what, one clause for why (`because`, `which establishes`, `to set up`)
- Keep each instruction to one line — 10–15 words maximum
- 3–4 instructions per paragraph; 5 is the hard limit

**Good:** `→ Explain that SDMs predict presence not abundance, because this sets up their failure mode`
**Too long:** `→ Explain that species distribution models are trained on occurrence data and therefore predict habitat suitability rather than actual population abundance, which means they systematically fail to...`
**Too vague:** `→ Discuss SDM limitations`

**Topic sentence:** Must be a specific claim, not a topic announcement. No "X has been widely studied." No "This paragraph discusses."
- Weak: "Cognitive load has been studied in many educational contexts."
- Strong: "Cognitive load constrains learning when instructional design exceeds working memory capacity."

**Closing sentence:** One line — implication, bridge, or gap. Keep it short.

---

## Phase 4 — Handoff to ea-academic-writer

Once the blueprint is approved, remind the user:

> This blueprint gives you the structure and logic. When you're ready to write the actual prose for any paragraph:
> 1. Gather the citations for that paragraph (use Consensus, your reference manager, or the suggested refs)
> 2. Turn each citation into an atomic sentence: *"[Specific claim] (Author Year)."*
> 3. Use **ea-academic-writer** with those atomic sentences + the paragraph function label
>
> The blueprint is your map. The atomic sentences are your raw material. ea-academic-writer turns them into polished prose.

---

## Quality standards

Apply the same standards as ea-academic-writer throughout:

| Avoid | Use instead |
|-------|-------------|
| Vague big topics ("Background", "Literature") | Specific noun-phrase topics ("Attentional control under dual-task conditions") |
| Content instructions that describe ("talk about X") | Instructions that direct ("Explain X, because it establishes Y") |
| Topic sentences that announce ("This paragraph discusses…") | Topic sentences that claim ("X determines Y under condition Z") |
| Outlines with no logical thread | Outlines where each paragraph explicitly sets up the next |
| Generic reference suggestions | References that match the specific small topics selected |

---

## Notes on reference suggestions

**Always suggest references from the `reference_pool`** — these are papers cited *within* the uploaded manuscripts, not the manuscripts themselves. The user already has the manuscripts; what they need is the supporting literature those papers point to.

- Pull refs from `reference_pool` that match each paragraph's small topics
- If a topic has no matching pool refs, mark it: `[from knowledge — verify]`
- Always add a Consensus search tip so the user can find additional citations

The user needs the cited literature, not the papers they just gave you.