"""Assemble demo/demo.html into demo/out/index.html: `python3 demo/build.py`, then open it."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import statusui  # noqa: E402

out = ROOT / "demo" / "out"
out.mkdir(exist_ok=True)
(out / "index.html").write_text(
    statusui.assemble((ROOT / "demo" / "demo.html").read_text(encoding="utf-8")),
    encoding="utf-8",
)
print(out / "index.html")
