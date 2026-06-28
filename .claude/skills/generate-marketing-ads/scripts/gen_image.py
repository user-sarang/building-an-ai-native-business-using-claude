"""Creator: generate a Samalyal marketing creative with Gemini (Nano Banana Pro).

Usage:
  python gen_image.py --prompt-file brief.txt --out candidates/v1.png \
      [--ref inputs/your_brand/logo.png --ref inputs/ugc/x.jpg] [--aspect 9:16]

The full creative prompt should already include brand styling (the SKILL.md /
creator-agent build it from brand-profile.md). Reference images are passed as
visual context (logo, brand style, ugc) so the model stays on-brand.
"""
from __future__ import annotations

import argparse
import mimetypes
import sys
from pathlib import Path

from gemini_client import get_client, image_model


def _load_part(path: Path):
    from google.genai import types

    mime = mimetypes.guess_type(str(path))[0] or "image/png"
    return types.Part.from_bytes(data=path.read_bytes(), mime_type=mime)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt", help="creative prompt text")
    g.add_argument("--prompt-file", help="file containing the creative prompt")
    ap.add_argument("--out", required=True, help="output image path (.png)")
    ap.add_argument("--ref", action="append", default=[],
                    help="reference image path (repeatable): logo, brand, ugc")
    ap.add_argument("--aspect", default="9:16",
                    help="aspect ratio hint, e.g. 9:16 (story), 1:1, 4:5")
    args = ap.parse_args()

    prompt = (Path(args.prompt_file).read_text(encoding="utf-8")
              if args.prompt_file else args.prompt)
    prompt = f"{prompt}\n\nComposition aspect ratio: {args.aspect}."

    contents = [prompt]
    for ref in args.ref:
        p = Path(ref)
        if p.exists():
            contents.append(_load_part(p))
        else:
            print(f"warning: reference not found, skipping: {ref}", file=sys.stderr)

    client = get_client()
    model = image_model()
    print(f"Generating with {model} (aspect {args.aspect})...", file=sys.stderr)
    resp = client.models.generate_content(model=model, contents=contents)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    saved = False
    for cand in resp.candidates or []:
        for part in (cand.content.parts or []):
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                out.write_bytes(inline.data)
                saved = True
                break
        if saved:
            break

    if not saved:
        print("ERROR: model returned no image. Text response (if any):",
              file=sys.stderr)
        print(getattr(resp, "text", "") or "<none>", file=sys.stderr)
        return 2

    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
