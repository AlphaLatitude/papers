Mirror of Andrew Korytko's physics preprints, kept because Zenodo is intermittently unavailable.

Cite the Zenodo DOI, not this repository.

https://papers.alphalatitude.com/

Derivation sites (the paper, the Lean package and the derivation between them) live under a
directory named for the revision, for example `sphere-string-ring/v18-67/`, so a paper can cite
that address and a newer build never replaces what an older paper points to. Add a build as a new
directory, never over an old one; `tools/build_mirror.py build` links the newest from the index.
The same run copies the newest build to the version-less address (`sphere-string-ring/`), adding
a line under the header bar with the build's version and the paper's Zenodo concept DOI; do not
edit those copies by hand, since the next build overwrites them.
