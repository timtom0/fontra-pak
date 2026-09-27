"""Check that the built Fontra Pak executable contains the current OpenType
feature editor: the per-rule samples, the collapsible sections, and the parser.
"""

import sys

from PyInstaller.archive.readers import CArchiveReader

exe = sys.argv[1] if len(sys.argv) > 1 else "dist/Fontra Pak.exe"

reader = CArchiveReader(exe)
names = list(reader.toc)
print(f"archive entries: {len(names)}")

candidates = [n for n in names if "views-fontinfo" in n]
if not candidates:
    print("FAIL: no fontinfo bundle in the archive")
    sys.exit(1)

name = candidates[0]
print(f"bundle: {name}")
data = reader.extract(name)
text = data.decode("utf-8", errors="replace") if isinstance(data, bytes) else str(data)
print(f"bundle size: {len(text)}")

# (needle, label). The minified bundle keeps string literals and class names,
# but mangles local function names -- so search for literals, not identifiers.
# "glyph-data.js" and the feature-groups helper live in the fontra-core chunk,
# not here, so they are checked separately below.
checks = [
    ("opentype-features-panel", "feature editor panel"),
    # Per-rule two-sided SVG preview
    ("ot-preview-input", "input-side preview box"),
    ("ot-preview-output", "output-side preview box"),
    ("ot-rule-sample-arrow", "arrow between the two sides"),
    ("ot-svg-run", "SVG glyph run class"),
    ("ot-rule-card-head", "card header row"),
    # Grid layout
    ("ot-rules-list", "rule grid"),
    ("auto-fill", "responsive grid columns"),
    ("ot-section-header", "collapsible section header"),
    ("ot-add-rule-row", "add-rule row"),
    ("chevron-right.svg", "collapse chevron icon"),
    ("glyphclassdef", "feature-code parser"),
    # rule-sample.js: the apostrophe terminator
    ("endsWith(\"'\")", "ignore-mark handling"),
    # feature-code-model.js: group titles are string literals, so they survive
    # minification even though the function names do not.
    ("ot-group-title", "group heading CSS"),
    ("Indic / other scripts", "deduplicated tag groups"),
]
missing = []
for needle, label in checks:
    found = needle in text
    print(f"  {label}: {'FOUND' if found else 'MISSING'}")
    if not found:
        missing.append(label)

# The previews must be SVG now, and the canvas version must be gone.
if "ot-rule-sample-canvas" in text:
    print("  WARNING: the old canvas preview is still present")
    missing.append("old canvas preview should be gone")
else:
    print("  old canvas preview: removed")

# The eye toggle is gone.
if "eye-closed.svg" in text:
    print("  WARNING: the eye toggle icon is still present")
    missing.append("eye toggle should be gone")
else:
    print("  eye toggle: removed")

# The old shared-preview box should be gone.
if "ot-features-preview-text" in text:
    print("  WARNING: the old shared preview box is still present")
    missing.append("old shared preview box should be gone")
else:
    print("  old shared preview box: removed")

# Things that live in the shared fontra-core chunk.
chunks = [n for n in names if "fontra-core" in n and n.endswith(".js")]
if chunks:
    cdata = reader.extract(chunks[0])
    ctext = cdata.decode("utf-8", errors="replace") if isinstance(cdata, bytes) else str(cdata)
    print(f"  core bundle: {chunks[0]} ({len(ctext)} bytes)")
    for needle, label in [("glyph-data.csv", "glyph database (sample-text lookup)")]:
        found = needle in ctext
        print(f"  {label}: {'FOUND' if found else 'MISSING'}")
        if not found:
            missing.append(label)
else:
    missing.append("fontra-core chunk")

print("OK" if not missing else f"FAIL: missing {missing}")
sys.exit(0 if not missing else 1)
