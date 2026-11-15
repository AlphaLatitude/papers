# Hand-over: the derivation site of "Gravitation from Hilbert-Space Granularity: The Sphere, the String, and the Ring"

Paper revision `v11-1-18-11-6-38-76` · Lean package RegisterGravity, tree `v18-69` · built 2026-11-14

## What this is

Three static web pages that show how the paper's results follow from its inputs, as the Lean 4
package RegisterGravity checks it.

| File | Page | What it shows |
|---|---|---|
| `index.html` | The derivation | every statement of the Lean package as a box, with what rests on what |
| `paper.html` | The paper | the paper's text; a click on a sentence lists the Lean statements behind it |
| `lean.html` | The Lean text | the Lean files with a table of contents; each declaration links to its box |
| `og.png` | The link-preview image | the top of the derivation page, 1200 x 630; the pages name it in og:image |

## How to publish

1. The author publishes the pages at `https://papers.alphalatitude.com/sphere-string-ring/<tree>/`,
   one folder for each build. This build goes to the path `/sphere-string-ring/v18-69/`, as
   `https://papers.alphalatitude.com/sphere-string-ring/v18-69/`, the address that the paper
   names. The build under `/sphere-string-ring/v18-68/` stays in place: do not remove or
   replace it. Put the three files in the folder of this build, with these names. They link to
   each other by relative name (`index.html`, `paper.html`, `lean.html`). Upload og.png to the
   same folder; link previews use it. Nothing else is needed beside these four files.
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
folder of its tree. The four files of a folder are built as a set and the anchors of the pages must match:
replace them only together, and leave the folders of earlier builds as they are.

## Checksums (SHA-256)

```
c91bd138e262a238495683af27743e0153f3b6642e2afaacffecff99b60aafeb  index.html  (5,032,457 bytes)
a2a2e5f0e5da5eee78e794d45eec2b603f0be76c31ac88f1a357b076d8713a66  paper.html  (3,158,830 bytes)
048bd6b729440cff33510dddde75e16ea475ab1dc2d0f120809f491fdca73e1d  lean.html  (3,036,452 bytes)
7de994b0a221243c36b13539e8bc1a21799f8691a398e61c79e402578594354d  og.png  (170,903 bytes)
```

## What is inside, and its licenses

* The paper's text and the Lean text: by Andrew Korytko.
* Fonts, embedded as subsets and renamed as the licenses ask: Latin Modern Roman (GUST Font
  License), Inter (SIL Open Font License 1.1), JuliaMono (SIL Open Font License 1.1), and the
  KaTeX fonts (SIL Open Font License 1.1).
* Scripts, embedded: KaTeX's stylesheet (MIT License; the mathematics is rendered at build time)
  and dagre (MIT License; it lays out the tree view of the derivation page).
