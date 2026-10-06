# Plumage

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

Agent skills for the form of the work: the voice of its prose, the visual system of its figures and slides, the words it coins, and the formats its documents travel in.

A bird's plumage is the surface it shows the world and the way it signals to others. These skills do the same job for whatever an agent helps produce. They change how the work is presented, not what it does, so they apply in any field: a grant proposal, a product page, a paper, a slide deck. Plumage is part of the Cracking Shells family of repositories, alongside [Nest](https://github.com/CrackingShells/Nest), the org's plugin marketplace.

## Skills

| Skill | What it does |
|:------|:-------------|
| [`writing-prose`](skills/writing-prose/SKILL.md) | Drafts, revises and reviews prose the user signs in their own name, in their voice, with register control against LLM-default rhetoric. |
| [`writing-design-canons`](skills/writing-design-canons/SKILL.md) | Writes design canons, the layered reference documents a team uses to make assets in one coherent style: identity, token vocabulary, production guidelines and consumption guide. |
| [`importing-design-figures`](skills/importing-design-figures/SKILL.md) | Renders a figure or table from a Claude Design project into a print-quality image and places it, undistorted, into a local document. |
| [`coining-neologisms`](skills/coining-neologisms/SKILL.md) | Coins a precise new word, with its full family of derived forms, for a practice or phenomenon that has no compact name yet. |
| [`pdf-to-md`](skills/pdf-to-md/SKILL.md) | Converts digital-native PDFs into Markdown with figures embedded at their place in the text, using poppler and pandoc. |

`writing-prose` and `importing-design-figures` keep per-project settings under `__canons__/`, and each defers to a more specific project skill when one exists. `writing-design-canons` produces the canons those settings can point to.

## Installation

The skills are not yet packaged as agent plugins or release assets. Until they are, install a skill by copying its directory into your skills folder:

```bash
git clone https://github.com/CrackingShells/Plumage.git
cp -R Plumage/skills/<skill-name> ~/.claude/skills/
```

Copy into `.claude/skills/` inside a repository instead to make the skill available in that project only. Restart Claude Code for the new skill to load.

`writing-prose`, `writing-design-canons` and `importing-design-figures` were first released from [cracking-shells-playbook](https://github.com/CrackingShells/cracking-shells-playbook); their history and release tags moved here with them.

## Contributing

Questions and suggestions go to the [issue tracker](https://github.com/CrackingShells/Plumage/issues).

## License

AGPL-3.0. See [LICENSE](LICENSE).
