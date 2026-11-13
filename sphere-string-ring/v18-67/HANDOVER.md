# Hand-over: the derivation site of "Gravitation from Hilbert-Space Granularity: The Sphere, the String, and the Ring"

Paper revision `v11-1-18-11-6-38-74` · Lean package RegisterGravity, tree `v18-67` · built 2026-11-12

## What this is

Three static web pages that show how the paper's results follow from its inputs, as the Lean 4
package RegisterGravity checks it.

| File | Page | What it shows |
|---|---|---|
| `index.html` | The derivation | every statement of the Lean package as a box, with what rests on what |
| `paper.html` | The paper | the paper's text; a click on a sentence lists the Lean statements behind it |
| `lean.html` | The Lean text | the Lean files with a table of contents; each declaration links to its box |

## How to publish

1. Put the three files in one directory of the site, with these names. They link to each other by
   relative name (`index.html`, `paper.html`, `lean.html`), so any directory works, and nothing
   else is needed beside them.
2. Serve them as `text/html` in UTF-8. That is all: each page carries its own styles, scripts,
   fonts and data. No page asks the network for anything, there is no server-side code and no
   build step.
3. Do not rename the files and do not edit their contents: the links between the pages are
   anchors inside them (`index.html#Register-Main-newton`, `paper.html#s-IVC-4-9`,
   `lean.html#Register-Main-newton`), and a change on one side breaks the other.

The pages follow the visitor's light or dark setting and work on a phone. Each has its own
`<title>` and a `<meta name="description">`.

## Updating

Every revision of the paper or of the Lean package gives a new package like this one. Replace all
three files together: they are built as a set and their anchors must match.

## Checksums (SHA-256)

```
19a72142ce2ec388b9eaa43effb71c2a5d798deb43ce93f378702be92c226011  index.html  (4,891,545 bytes)
e1cc3344427cbef51d605002cd589b8b07a1d003abc04a770fbb1d8586ed66eb  paper.html  (3,147,628 bytes)
797d5735a8ce30264e3721801dfecdf5565fcedb609e7ad9adc7616791514652  lean.html  (2,895,743 bytes)
```

## What is inside, and its licenses

* The paper's text and the Lean text: by Andrew Korytko.
* Fonts, embedded as subsets and renamed as the licenses ask: Latin Modern Roman (GUST Font
  License), Inter (SIL Open Font License 1.1), JuliaMono (SIL Open Font License 1.1), and the
  KaTeX fonts (SIL Open Font License 1.1).
* Scripts, embedded: KaTeX's stylesheet (MIT License; the mathematics is rendered at build time)
  and dagre (MIT License; it lays out the tree view of the derivation page).
