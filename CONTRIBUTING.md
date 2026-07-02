# Contributing to Nora

Thanks for wanting to contribute. A few conventions keep the project's
ownership clean and the codebase consistent.

## Contributor License Agreement (required)

All contributions are accepted under the [Contributor License Agreement](CLA.md).
By opening a pull request you agree to its terms. This consolidates copyright
with the project owner so the project stays relicensable — please read it before
your first PR.

## License and copyright headers

Nora is licensed under the [MIT License](LICENSE). **New source files** should
start with an SPDX header so provenance is unambiguous file-by-file.

Python:

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Mohib Arshi
```

- Use `SPDX-License-Identifier: MIT` — the machine-readable, auditable way to
  state a file's license (preferred over pasting the full license text).
- Keep the copyright line pointing at the owner unless a file is contributed
  under different terms, in which case say so explicitly in that file.
- If a file legitimately incorporates third-party code, note its origin and
  license at the top of the file — never remove an existing license header.

Existing files predate this convention; there's no need to retrofit them in a
single sweep. Add the header as you touch files, so ownership is clean from here
forward.

## Adding a capability

1. Create `agent/capabilities/your_capability/tools.py` — define your tools.
2. Create `agent/capabilities/your_capability/capability.py` — export a
   `CAPABILITY` dict.
3. Register it in `agent/capabilities/registry.py`.

The planner picks it up automatically. Keep capabilities **general and
reusable** — no project-specific or single-purpose logic (see `CLAUDE.md`).

## Pull requests

- Keep changes focused and describe the intent, not just the diff.
- Match the surrounding code's style and structure.
- Don't commit secrets or the contents of `data/` (runtime state is gitignored).
