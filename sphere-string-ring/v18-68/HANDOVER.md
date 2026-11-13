# Hand-over: the derivation site of "Gravitation from Hilbert-Space Granularity: The Sphere, the String, and the Ring"

Paper revision `v11-1-18-11-6-38-75` · Lean package RegisterGravity, tree `v18-68` · built 2026-11-13

## What this is

Three static web pages that show how the paper's results follow from its inputs, as the Lean 4
package RegisterGravity checks it.

| File | Page | What it shows |
|---|---|---|
| `index.html` | The derivation | every statement of the Lean package as a box, with what rests on what |
| `paper.html` | The paper | the paper's text; a click on a sentence lists the Lean statements behind it |
| `lean.html` | The Lean text | the Lean files with a table of contents; each declaration links to its box |

## How to publish

1. The author publishes the pages at `https://papers.alphalatitude.com/sphere-string-ring/<tree>/`,
   one folder for each build. This build goes to the path `/sphere-string-ring/v18-68/`, as
   `https://papers.alphalatitude.com/sphere-string-ring/v18-68/`, the address that the paper
   names. The build under `/sphere-string-ring/v18-67/` stays in place: do not remove or
   replace it. Put the three files in the folder of this build, with these names. They link to
   each other by relative name (`index.html`, `paper.html`, `lean.html`), and nothing else is
   needed beside them.
2. Serve them as `text/html` in UTF-8. That is all: each page carries its own styles, scripts,
   fonts and data. No page asks the network for anything, there is no server-side code and no
   build step.
3. Do not rename the files and do not edit their contents: the links between the pages are
   anchors inside them (`index.html#Register-Main-newton`, `paper.html#s-IVC-4-9`,
   `lean.html#Register-Main-newton`), and a change on one side breaks the other.

The pages follow the visitor's light or dark setting and work on a phone. Each has its own
`<title>` and a `<meta name="description">`.

## Updating

Every revision of the paper or of the Lean package gives a new package like this one, for the
folder of its tree. The three files of a folder are built as a set and their anchors must match:
replace them only together, and leave the folders of earlier builds as they are.

## Checksums (SHA-256)

```
c077f8e087b5d04671805c11224714929769a549d8d2ed84167588aa2a522962  index.html  (4,890,959 bytes)
e863c136b9304ae7ffb191ba5b83b230a9785392e96bf330c6b9c31d5f4096cd  paper.html  (3,147,901 bytes)
e07435453255dd13166b516e37813768414b7b44e8157c0b30f0d8e1d0435a0c  lean.html  (2,895,692 bytes)
```

## What is inside, and its licenses

* The paper's text and the Lean text: by Andrew Korytko.
* Fonts, embedded as subsets and renamed as the licenses ask: Latin Modern Roman (GUST Font
  License), Inter (SIL Open Font License 1.1), JuliaMono (SIL Open Font License 1.1), and the
  KaTeX fonts (SIL Open Font License 1.1).
* Scripts, embedded: KaTeX's stylesheet (MIT License; the mathematics is rendered at build time)
  and dagre (MIT License; it lays out the tree view of the derivation page).
