"""
Run Image List Test

Script to run the image list test with preconfigured paths and artifacts.
After ileapp finishes, stamp only the Media Path Probe copies so LAVA can
show whether it read report/media or _HTML/media.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.lavafuncs import lava_db_name  # noqa: E402

BANNER_CANONICAL = "report/media"
BANNER_HTML = "_HTML/media"


def _banner_font(size=48):
    for candidate in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
    ):
        path = Path(candidate)
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def stamp_png(path: Path, banner: str, fill):
    img = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size
    draw.rectangle((0, 0, width, height), fill=fill)
    font = _banner_font()
    draw.text((40, height // 2 - 24), banner, fill=(255, 255, 255), font=font)
    img.save(path, "PNG")


def probe_extraction_paths(report_dir: Path):
    db_path = report_dir / lava_db_name
    if not db_path.is_file():
        raise SystemExit(f"Missing LAVA database: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT extraction_path FROM _lava_media_info WHERE artifact_name = ?",
            ("Media Path Probe",),
        ).fetchall()
    finally:
        conn.close()

    paths = [row[0] for row in rows if row[0]]
    if not paths:
        raise SystemExit(
            f"No media rows in {db_path} for artifact 'Media Path Probe'"
        )
    return paths


def diverge_and_stamp(report_dir: Path, extraction_path: str):
    canonical = report_dir / extraction_path
    html = report_dir / "_HTML" / "media" / Path(extraction_path).name
    if not canonical.is_file():
        raise SystemExit(f"Missing canonical media: {canonical}")

    html.parent.mkdir(parents=True, exist_ok=True)
    if html.exists() and canonical.samefile(html):
        html.unlink()
    if not html.exists():
        shutil.copy2(canonical, html)

    stamp_png(canonical, BANNER_CANONICAL, (20, 90, 40))
    stamp_png(html, BANNER_HTML, (120, 30, 30))
    print(f"Stamped {canonical} -> {BANNER_CANONICAL}")
    print(f"Stamped {html} -> {BANNER_HTML}")


def run_test():
    """
    Run the image list test with preconfigured paths and artifacts.
    """

    os.chdir(REPO_ROOT)

    input_path = "admin/test/samples_data"
    output_path = "admin/test/output/"
    output_folder = "image_list_test_" + datetime.now().strftime("%Y%m%d-%H%M%S")
    custom_artifacts_path = "scripts/test_artifacts"

    os.makedirs(output_path, exist_ok=True)

    profile = {
        "leapp": "ileapp",
        "format_version": 1,
        "plugins": ["image_list", "media_path_probe"],
    }
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ilprofile", delete=False, encoding="utf-8"
    ) as profile_file:
        json.dump(profile, profile_file)
        profile_path = profile_file.name

    cmd = [
        sys.executable,
        "ileapp.py",
        "-t", "fs",
        "-i", input_path,
        "-o", output_path,
        "--custom_output_folder", output_folder,
        "--custom_artifacts_path", custom_artifacts_path,
        "-m", profile_path,
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError running test: {e}")
        sys.exit(1)
    finally:
        os.unlink(profile_path)

    report_dir = Path(output_path) / output_folder
    for extraction_path in probe_extraction_paths(report_dir):
        diverge_and_stamp(report_dir, extraction_path)

    print("\nTest completed successfully.")
    print(f"Report folder: {report_dir}")
    print(f"Open in LAVA: {report_dir / '_lava_data.lava'}")
    print(
        "In Media Path Probe: "
        f"{BANNER_CANONICAL!r} means the canonical path, "
        f"{BANNER_HTML!r} means the HTML fallback."
    )


if __name__ == "__main__":
    run_test()
