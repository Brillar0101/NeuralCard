# Working rules for this repo

Conventions I have already been corrected on. Read before editing anything.

## Writing

This is a public repo, so the prose has to read like a person wrote it.

- No em dashes or en dashes anywhere. Use a comma, a colon, a period, or
  parentheses. Numeric ranges use "to" or a hyphen.
- No decorative emoji in headings, bullets, or tables. Words instead.
- Straight quotes only, never curly.
- No inline-header bullets of the form "**Thing:** description". Write the
  sentence, or use a table with real columns.
- Avoid the usual AI vocabulary: leverage, robust, seamless, comprehensive,
  vibrant, testament, showcase, underscore, delve, landscape (figurative).
- Vary sentence length. State the finding, then the evidence. Skip the
  windup.
- Sentence case in headings, not Title Case.

## Commits

- Four words maximum, imperative, lowercase.
- No conventional-commit prefixes (`feat:`, `fix:`, `docs:`).
- Describe the change to the design, not the process used to make it. "edit
  docs", not "humanize prose". Never name the tooling or the assistant.

## Privacy

Nothing machine-specific ever gets committed.

- No absolute paths, no home directories, no usernames. 3D model references
  use `${KIPRJMOD}/...` so a fresh clone resolves them.
- No notes about the local OS, folder layout, or which tools are installed
  where.
- Generator scripts stay out of this repo entirely, and are not mentioned in
  docs, commits, or releases. `.gitignore` enforces the file side of this.

## Silkscreen

The fab floor is 0.15 mm printable line width, which decides the font.

- Reference designators (C1, U1, SW3): KiCad stroke font, 0.85 mm. They are
  meant to be unobtrusive.
- Everything else: Red Hat, with the family name as the face ("Red Hat Mono",
  not "Red Hat Mono Bold") plus the bold flag. A weight name that KiCad cannot
  resolve silently substitutes a thin fallback and fails DRC.
- Red Hat needs roughly 0.9 mm for uppercase and 1.5 mm for lowercase. The
  digits 6 and 9 are the thinnest glyphs and need 1.8 mm. Below those sizes,
  stroke font is the only option that prints.

## Verifying a copper change

Before committing anything that touches copper, all of these must pass:

1. DRC: 0 violations, 0 unconnected
2. ERC: 0 violations
3. Connectivity: every net a single cluster, checked in `pcbnew`
4. Regenerate gerbers, drill, CPL, both renders, and rebuild the fab zip

If the JLCPCB cart holds an older revision after a copper change, it needs the
new files or it will build the wrong board.

## Versioning

- Patch bump (v2.3.1) for fixes after a revision is declared done.
- Minor bump for new hardware capability.
- Bump the silkscreen, the PCB title block, and the schematic revision
  together. Tag the commit.

## Fab defaults

2 layers, 1.6 mm, green soldermask, HASL. 0.8 mm and ENIG are the nicer
options for boards meant to be handed out, and cost more. Neither changes the
gerbers.
