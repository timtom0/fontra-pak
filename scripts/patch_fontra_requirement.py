# Build Fontra Pak against a Fontra fork that includes the OpenType feature
# editor, rather than upstream Fontra.
#
# requirements.txt points at timtom0/fontra@opentype-features-gui. To build
# against upstream Fontra instead, change that line back to:
#
#     git+https://github.com/fontra/fontra.git
#
# To build against a different fork, set FONTRA_PAK_FONTRA_URL before running
# pyinstaller, e.g.
#
#     set FONTRA_PAK_FONTRA_URL=git+https://github.com/you/fontra.git@my-branch

import os
import pathlib
import re

repoDir = pathlib.Path(__file__).resolve().parent.parent
reqsPath = repoDir / "requirements.txt"

fontraURL = os.environ.get(
    "FONTRA_PAK_FONTRA_URL", "git+https://github.com/timtom0/fontra.git@opentype-features-gui"
)

# Match the "git+https://github.com/<owner>/fontra.git[@<ref>]" line, whatever
# fork and ref it currently points at.
pattern = re.compile(
    r"^git\+https://github\.com/[^/\s]+/fontra\.git(@[^\s]+)?$", re.MULTILINE
)

text = reqsPath.read_text(encoding="utf-8")
newText, count = pattern.subn(fontraURL.replace("\\", "\\\\"), text)

if count == 0:
    raise SystemExit(
        f"could not find a fontra requirement line in {reqsPath}; "
        f"expected a line like 'git+https://github.com/<owner>/fontra.git[@<ref>]'"
    )

if count > 1:
    raise SystemExit(f"found {count} fontra requirement lines in {reqsPath}, expected 1")

if newText != text:
    reqsPath.write_text(newText, encoding="utf-8")
    print(f"using fontra requirement: {fontraURL}")
else:
    print(f"requirements already point at: {fontraURL}")
