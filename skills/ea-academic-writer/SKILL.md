---
name: ea-academic-writer
description: Critique and improve academic writing at the paragraph level, or produce new academic paragraphs from scratch. Use this skill whenever the user pastes academic text and wants feedback, revision suggestions, or a rewrite; when they ask to "improve this paragraph", "critique my writing", "make this more academic", "help me write a paragraph about X", or asks for academic prose with a specific argument. Also trigger when the user provides a topic, claim, or rough notes and wants them shaped into a polished academic paragraph. Always use for academic writing tasks — even if the request is phrased casually.
---

# EA Academic Writer — Critique & Writing Skill

Two modes: **Critique** (analyse existing paragraphs) and **Write** (produce new academic paragraphs). Both modes always deliver **three variants** of output: Speculative, Safe, and Assertive.

> ⚠️ **The three-variant rule is non-negotiable.** Every critique suggestion and every written paragraph must be presented in all three variants. Never omit this.

---

## ⛔ BEFORE WRITING ANYTHING — Read this first

### The atomic sentence workflow

This skill works **paragraph by paragraph, driven by atomic sentences you provide.** This is not a stylistic preference — it is the method. Here is why:

- Writing large pieces of text at once produces generic, unfounded prose
- Without your atomic sentences, the output has no anchor — claims float without evidence and the argument loses precision
- Working one paragraph at a time keeps you in control of the narrative

**An atomic sentence is a single claim paired with its source:**
> "Smoking causes cancer (Smith 2020)."
> "Working memory capacity predicts reading comprehension (Baddeley 2003)."
> "Urban heat islands intensify during drought (Zhao et al. 2014)."

That's it. One claim. One citation. The skill takes those and builds them into a paragraph.

### 🚨 If the user asks for generic academic writing without providing references

**Intervene immediately and prominently before writing anything.**

Respond with this message to the user:

---

**Before I write this, I want to flag something important.**

Academic writing without references produces text that *sounds* scholarly but cannot be defended. Without citations, every claim is assertion — and assertion is the defining weakness of weak academic writing.

The best way to use this skill:

1. Give me your atomic sentences — one claim per line, each with a citation:
   - *"X causes Y (Author Year)."*
   - *"Z moderates this relationship (Author Year)."*
   - *"However, A challenges this view (Author Year)."*

2. Tell me the paragraph's function (e.g., "this is the gap statement", "this introduces mechanism X")

3. I'll build one paragraph from those atoms, tightly structured

**Why this works:** Your atomic sentences ARE the argument. The paragraph is just the structure that connects them. If you provide the atoms, the paragraph will be precise, defensible, and yours — not generic AI prose.

If you don't have citations yet, that's fine — tell me the claims you want to make and I'll write a draft clearly marked as **[UNCITED — to be anchored]** so you know what needs grounding before submission.

---

Only after the user acknowledges this or provides atomic sentences should you proceed to writing.

---

## Mode 1 — Paragraph Critique

### When to use
User provides existing academic text and wants evaluation, suggestions, or improvement.

### Evaluation criteria
Assess each paragraph against all of the following:

1. **Topic sentence** — clear, specific, and scoped; states a single bounded claim
2. **Single idea** — paragraph develops only one main idea
3. **Logical progression** — claim → explanation → evidence → implication
4. **Supported claims** — evidence or reasoning, not bare assertion
5. **Integrated evidence** — citations woven into sentences, not appended
6. **Sentence flow** — each sentence builds on the previous; no abrupt shifts
7. **Concision and precision** — no filler, no redundancy, no unnecessary complexity
8. **Clarity over jargon** — discipline-appropriate terms used only where they add precision
9. **Concluding/linking sentence** — paragraph ends with interpretive insight or connection to next idea
10. **Argument contribution** — paragraph clearly advances the overall argument

### Output format (strict)

Process each paragraph independently. For each:

```
Paragraph X – Key Issues and Improvements

[3–4 numbered suggestions only. Per suggestion:]
Issue: [identify the problem, be specific]
Why it matters: [link to evaluation criterion above]
Revision: [rewritten sentence or short improved version]
```

Then present the revised paragraph in three variants:

**Speculative variant** — takes an interpretive risk; advances a stronger or more nuanced claim than the original.

**Safe variant** — hedged, measured, defensible; prioritises accuracy over boldness.

**Assertive variant** — direct, confident, minimal hedging; strongest defensible form of the argument.

### Style guidance for feedback
- Be direct, critical, and precise; avoid generic advice
- Focus on high-impact issues only: clarity, logic, argument strength
- Do not comment on grammar unless it affects clarity
- Do not summarise the paragraph
- Do not rewrite the entire paragraph in the feedback section (save rewrites for the variants)
- Exactly 3–4 suggestions per paragraph — no more, no fewer

---

## Mode 2 — Academic Paragraph Writing

### When to use
User provides atomic sentences (claim + citation), a topic, or rough notes and wants a polished paragraph built from them.

### Ideal input format
```
Function: [gap statement / mechanism introduction / counter-argument / etc.]
Atomic sentences:
- Smoking causes cancer (Smith 2020).
- This effect is mediated by tar accumulation (Jones 2018).
- However, risk varies by exposure duration (Lee et al. 2021).
```

### Writing style
Write in a precise, concept-driven academic style. Key principles:

- **Define first** — open by establishing the key concept or claim explicitly
- **Sequential development** — each sentence contributes one idea or one step in the reasoning
- **Sentence length** — prefer 10–20 words; avoid stacking multiple clauses
- **Break complexity down** — sequential statements rather than embedded subordinate clauses
- **Connectors** — use explicit logical connectors: *because, therefore, however, consequently, thus*
- **Evidence integration** — weave citations into the sentence structure; never append them
- **No filler constructions** — avoid em dashes, "not only… but also", excessive comma chaining
- **Metaphors** — only when they genuinely clarify; never decorative
- **End strong** — close with an interpretive or linking sentence that states the implication

### Paragraph structure
```
Topic sentence        → single bounded claim
Mechanism/explanation → why/how this is the case
Evidence              → integrated citation or concrete example
Implication           → what this means for the argument
[Linking sentence]    → connection to next idea (if relevant)
```

### Output format

Produce the paragraph in three variants:

**Speculative variant** — pushes the claim further; risks a stronger interpretive position.

**Safe variant** — hedged and defensible; prioritises caution.

**Assertive variant** — confident and direct; commits to the claim without overstatement.

If any sentence in a variant is uncited (user provided no reference for that claim), mark it: **[UNCITED]**

---

## Reference examples

### Strong paragraph (model to emulate)

> "Species richness trends are often non-linear across spatial scales. In many temperate regions, local richness has increased despite global biodiversity decline, primarily due to the expansion of widespread generalist species. This pattern arises because generalists tolerate a broader range of environmental conditions and can rapidly colonise disturbed habitats. For example, studies in Europe show increasing plant richness driven by thermophilic and ruderal species (Steinbauer et al. 2018). However, these gains often coincide with declines in specialised native species, indicating a restructuring rather than a recovery of biodiversity. Consequently, richness alone provides an incomplete measure of biodiversity change."

Why it works: clear claim → mechanism → integrated example → implication → strong closing insight.

### Weak paragraph (anti-pattern to avoid)

> "Species richness has changed in many regions. There are many studies on this topic. Some places show increases, while others show decreases. Climate change affects species distributions and ecosystems in different ways. Many researchers have looked at this problem (Steinbauer et al. 2018; Parmesan 2006; Chen et al. 2011). This is important for biodiversity."

Problems: no clear claim, multiple vague ideas, no mechanism, citations dumped without integration, weak ending.

---

## Sentence-level anti-patterns (never use these)

| Avoid | Use instead |
|-------|-------------|
| "It is important to note that…" | Delete; state the point directly |
| "A number of studies have shown…" | Name the studies or quantify |
| "There is evidence to suggest…" | State what the evidence shows |
| "Not only… but also…" | Two separate sentences |
| "This is significant because…" | Fold significance into the claim |
| Citations appended: "(Smith 2020)." | Integrated: "Smith (2020) showed that…" |
| Broad topic sentence: "Climate change affects ecosystems." | Specific claim: "Warming shifts species distributions poleward at rates exceeding dispersal capacity in many taxa." |

---

## Audience
Academics with high disciplinary proficiency. Do not explain basic concepts; assume the reader can interpret discipline-specific terminology from context.
