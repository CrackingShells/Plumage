---
name: coining-neologisms
description: Coin a precise new word — and its full morphological family — to name a novel practice, phenomenon, technique, method, effect, or project that lacks a compact name, by mining morphological families across the world's languages and adapting a root system rather than inventing from scratch. Engage this skill whenever a naming need arises, whether the user asks for one directly or the work itself surfaces it: any time a concept keeps being referred to by a long descriptive phrase, a recurring pattern or failure mode has no agreed term, a project or method needs a name with a particular register or rhetorical framing, or a coined term would benefit from generative derived forms (verb, agent, adjective, field). Reach for it proactively when, in the course of analysis, design, writing, or research, a distinction worth naming has no good name yet — coining it well, with etymological grounding and a usable family of forms, is preferable to leaving it unnamed or naming it ad hoc. Do not use it for translating existing text, defining or looking up an existing word's meaning, or casual naming of characters or products where etymological rigor is not wanted.
---

# Coining Neologisms

A skill for inventing a precise new word — and the family of forms around it — to name something that does not yet have a good name.

The central move is **not** invention from a blank page. Natural languages have already spent millennia carving conceptual space into root systems. A single root in some language often radiates into a whole paradigm (agent, process, result, place, quality) that already encodes the distinctions you care about. So the method is **morphological-family mining**: find the language family whose roots already cluster around the target concept, understand the *internal logic* of that family, and adapt it — rather than gluing together whatever morphemes come to mind.

The output is a short, structured report proposing one or more candidate words, each with its derived-form family, justified against the concept and against a set of explicit design dimensions.

## When the concept is the input

The hard conceptual work — defining the phenomenon and sensing which language traditions theorized it — usually arrives *with the request*. The user has noticed something real and is reaching for a name. Treat the phenomenon as the anchor, not as a step to perform. The skill's job begins at extracting the concept's *relational structure* and ends at a defensible, generative name.

## The five-step workflow

Run these in order. Steps 2 and 5 parallelize well (dispatch concurrent research/checks where the environment allows; otherwise do them as focused sequential searches). Step 3 is where the irreducible judgment lives — spend the thinking budget there.

1. **Frame** — Pin down the concept and the naming constraints.
2. **Mine** — Gather candidate root families across languages and, crucially, their internal logic.
3. **Configure** — Navigate the design dimensions to set an adaptation strategy.
4. **Forge** — Produce candidate word(s) and the full morphological family for each.
5. **Validate** — Run the mechanical checks the elegant work tends to skip.

### Step 1 — Frame

Extract, from the request and a question or two if needed:

- **The relational structure of the concept.** Not just "what is it" but *what kind of thing*: an agent, a process, a result, a tendency, a relation, a place, a quality? What is the single dimension of contrast that matters most (direction? scale? intentionality? temporality? social role?)? Write a one-sentence definition that would survive translation into an unrelated language — if it leans on an English pun or compound, it is not yet abstract enough.
- **The target community.** Who will use the word, in what setting? A term for a research paper can afford opacity (it ships with a definition); a vernacular term must feel almost self-evident on first contact.
- **The native register of the phenomenon**, and whether the user wants the name to *match* it or deliberately diverge (see the Register dimension — the gap is a rhetorical tool).
- **Hard constraints**, if any: must it be an ASCII-safe identifier (branch / package / filename)? A single token? Pronounceable by non-specialists?

If the concept is genuinely underspecified ("name this vibe"), ask one focused clarifying question rather than guessing. Otherwise proceed.

### Step 2 — Mine

The frontier here is the full set of human languages — the thousands spoken across the earth, not a shortlist of prestige tongues. A minority, indigenous, regional, or low-resource language is exactly as eligible as a dominant one, and is often *more* valuable: a language that grammaticalizes evidentiality, kinship, motion, social hierarchy, or temporality in ways English flattens may already hold the precise distinction you are trying to name. The best fit frequently lives outside the languages you happen to know.

This makes active research non-negotiable. Do not coin from the handful of roots that come to mind, and do not default to Greek and Latin — that reflex defeats the purpose of family-mining. Treat the concept's relational structure as a search query into the world's languages: ask which traditions developed dedicated vocabulary for *this* kind of distinction, then go and look, including in language families you have no prior familiarity with. Different traditions concentrated intellectual effort in different domains, so their history is a reasonable prior for where to start digging — but it is only a prior, and a weak one. Let the evidence from the search, not the convenience of the familiar, decide which families make the shortlist.

For each promising language family, gather (in parallel where possible):

- **The root and its whole family**, not a single word. The constellation of derived forms tells you which distinctions the language considered worth making — that is the asset you are mining.
- **The internal logic of the family** — the relational grammar that connects its members (how it forms agents vs. results vs. places). This is what you may want to import wholesale.
- **Semantic history and connotation** of each root: dominant contexts of use, and any religious, political, or otherwise charged associations that would distort the meaning in the new context.
- **An anchoring exemplar**, if one exists: a figure, image, or canonical usage that both makes the word memorable *and* carries the concept's relational structure. A good exemplar does conceptual work, not just mnemonic work.

**Stop condition:** search as widely as the concept warrants, but carry forward only the two or three viable families whose internal logic you actually understand. The cap is on the *shortlist*, not on the breadth of the search — casting a wide net is the point; what invites the rabbit hole is accumulating ever more candidates once a few clearly dominate (see Scope discipline).

### Step 3 — Configure

This is the core. The choice is not a flat menu of "loan vs. calque vs. template"; it is a configuration across several dimensions. Step through the table, decide each dimension from the framing, and the adaptation strategy falls out of the configuration.

| Dimension | Options | Key question |
|---|---|---|
| **Phonological fidelity** | Keep source sounds / Adapt to target phonology / Discard sounds (meaning only) | Will the audience need to *say* this word regularly? |
| **Morphemic transparency** | Opaque / Partial / Transparent | Should a reader be able to *guess* the meaning from the parts? |
| **Structural preservation** | Single word extracted / Pattern imported / Full family seeded | A one-off coinage, or the start of a productive family? |
| **Register target** | Scientific / Technical / Vernacular / Poetic | Match the phenomenon's native register, or deliberately diverge to reframe it? |
| **Generativity** | Noun only / Noun + verb / Full paradigm | How much grammatical flexibility does the word need? |
| **Cultural visibility** | Invisible / Acknowledged / Foregrounded | Does the source culture's presence help or hinder reception? |
| **Orthographic safety** | Free Unicode / Diacritic-tolerant / ASCII-identifier-clean | Must it survive as a code identifier, URL, or filename? |
| **Anchoring exemplar** | None / Mnemonic only / Structure-bearing | Is there a figure or image that both aids memory and carries the relational structure? |

**How the dimensions interact:**

- *Transparency* and *structural preservation* are correlated but optimize for different things — transparency is about the reader decoding meaning; structural preservation is about whether the family can grow later. Keep them separate even when they move together.
- *Register target* is the rhetorical lever. Lifting a vernacular phenomenon into a scientific register can legitimize it; dropping a formal concept into vernacular can demystify or subvert it. The *delta* between native and target register is itself the intended effect — set it deliberately.
- *Generativity* and *structural preservation* together decide whether you import one word or a whole pattern. If the user wants verb and adjective forms, pattern import becomes close to mandatory.

**The overriding selector — mapping fidelity.** The table tells you *how* to transfer; it does not tell you *whether* a candidate is acceptable. That test is always the same: **does the concept's relational structure survive the transfer?** A calque that translates the parts but loses the internal logic is worse than useless — it actively misleads. A candidate that merely sounds elegant but maps the wrong relation loses to a plainer candidate that maps the right one. Rank candidates by mapping fidelity first, then by the configured dimensions.

The adaptation strategy is then read off the configuration:

- **Loan** (keep sounds + opaque) when the source word is phonologically compatible and culturally neutral enough to travel intact.
- **Calque** (discard sounds + transparent) when the morphemic structure translates cleanly into the target language's own morphemes.
- **Template adaptation** (import the pattern) when neither a clean loan nor a clean calque works, but the *logic* of the root system is exactly what you want to preserve and grow. This is the most generative and the most error-prone — it is where the well-formedness checks in Step 5 matter most.

### Step 4 — Forge

Produce candidates. For each:

- The headword, in both its native-faithful spelling and its identifier-safe form.
- The **full morphological family** the configuration calls for. A useful default paradigm: the concept (noun), the field/enterprise, a single instance (countable noun), the practitioner/agent or instrument, the verb, the adjective(s), and the adverb. Generate only the forms that are actually well-formed — a forced form is a liability, not a flourish.
- A one-line note on what each candidate *gains and loses* relative to the others (this is what lets the user choose on the basis of what they want to accomplish).

Offer more than one candidate when the dimensions pull in different directions, so the tradeoff is visible. Name a recommendation, with the reasoning tied explicitly to mapping fidelity and the configuration — not to taste alone.

### Step 5 — Validate

Elegant, hand-crafted coinages reliably skip these checks. Make them non-optional. Anything you cannot actually verify (e.g., native well-formedness without a speaker or reference) is **flagged for human review, not silently passed**.

- **Collision / false friend.** Does the word — or a near-homophone — already exist in the target language(s) or in adjacent technical vocabulary with a conflicting meaning? Check both the source and target languages, and the immediate professional domain.
- **Morphological well-formedness.** Are the derived forms actually legal in a living language (correct affixation, stress, verb aspect, gender)? Forms built purely by analogy from reconstructed roots must be flagged as constructed, not asserted as correct.
- **Productivity reality check.** Can you genuinely produce the forms the configuration promised? If only the noun is viable but a full family was wanted, say so.
- **Tooling.** If an identifier-safe form is required, confirm it is ASCII-clean, has no reserved characters, and that the romanization still recognizably points back to the headword.
- **Baggage.** Re-confirm no charged religious, political, or offensive association in source or target.

## Scope discipline

The most common failure mode of this method is not a bad word — it is a beautiful one buried in an essay. Mythological tangents, cross-linguistic resonances, and theoretical mappings are seductive and expand without limit. They are *inputs* to the judgment, not the deliverable. Once you have a defensible recommendation, its family, and its validation flags, **stop**. If a resonance is genuinely load-bearing, state it in one or two sentences in the report; if it is decorative, leave it out. Resist generating a fourth and fifth candidate once two clearly dominate.

## Output

Produce a single structured report. The input contract (a framed concept) and the output contract (this report) are the interfaces that let this skill compose with others, so keep both clean and predictable. The report uses seven named sections, in this order:

1. **Concept Mapping** — the phenomenon, its relational structure, and the distinctions a name must encode.
2. **Root Sources** — the candidate root families, with etymology, cognates, and the internal logic of each.
3. **Candidates** — the proposed words, each with what it gains and loses.
4. **Morphological Family** — the full derived-form paradigm for the leading candidate(s).
5. **Recommendation** — the selected word, with numbered rationale tied to mapping fidelity and the configuration.
6. **Pronunciation & Orthography** — pronunciation guide, spelling notes, and the identifier-safe form.
7. **Provenance** — sources consulted (etymological references, domain literature) and any validation flags raised in Step 5.

For the detailed fill-in template of this report, read `references/output-report-template.md`.
