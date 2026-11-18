# Hand-over: the derivation site of "Gravitation from Hilbert-Space Granularity: The Sphere, the String, and the Ring"

Paper revision `v11-1-18-11-6-38-77` · Lean package RegisterGravity, tree `v18-72` · built 2026-11-18

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
   one folder for each build. This build goes to the folder `/sphere-string-ring/v18-72/` of
   papers.alphalatitude.com, as `https://papers.alphalatitude.com/sphere-string-ring/v18-72/`.
   The paper's Data availability and the tree's README both name this address. That folder
   holds an earlier draft now: replace every file in it by the files of this package. The
   folders of earlier builds (`v18-67/` to `v18-71/`) stay as they are: do not remove
   or replace them. Put the three files in the folder of this build, with these names. They link to
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
bd6c9890865e62c83452f9d37ecf55babbaf1fdde6c63f4a4f75044d275096f4  index.html  (5,297,589 bytes)
f8fd588054fa555c5034c52be960a6d8d050df4918eda76101a72e1843ffaaf2  paper.html  (3,203,978 bytes)
73ea6c7f2b257e531bf914be3e309eadab2113f2c99af6eca76b5c00e1e39625  lean.html  (3,275,634 bytes)
3bf3d223335936f18a1cb914563106937540ae2f9293c1648378a5495dc63b06  og.png  (167,490 bytes)
```

## What is inside, and its licenses

* The paper's text and the Lean text: by Andrew Korytko.
* Fonts, embedded as subsets and renamed as the licenses ask: Latin Modern Roman (GUST Font
  License), Inter (SIL Open Font License 1.1), JuliaMono (SIL Open Font License 1.1), and the
  KaTeX fonts (SIL Open Font License 1.1).
* Scripts, embedded: KaTeX's stylesheet (MIT License; the mathematics is rendered at build time)
  and dagre (MIT License; it lays out the tree view of the derivation page).
