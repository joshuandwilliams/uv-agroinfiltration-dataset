"""Generate anonymised copies of the raw per-scorer data files for public
(GitHub) visibility, without touching the original real-name files - those
stay on disk locally and are gitignored.

Reads:
  - anonymisation_keys/anonymisation_key.csv (scorer name -> ID)
  - data/cdascorer/set{1,2}/<Name>.csv
  - analyses/06_intra_rater_reliability/rescore_<Name>.csv
  - analyses/01_generate_raw_data/01_allocation_info/randomised_info.csv

Writes:
  - data/cdascorer_anon/set{1,2}/Scorer<ID>.csv (img column stripped to
    basename, dropping both the local machine path and the real name it
    contained as a directory segment)
  - analyses/06_intra_rater_reliability/rescore_anon/Scorer<ID>.csv (scorer
    column replaced with the ID)
  - analyses/01_generate_raw_data/01_allocation_info/randomised_info_anon.csv
    (scorer1/2/3 columns replaced with IDs)

Run this after regenerating any of the original files it reads from.
"""

from pathlib import Path

import pandas as pd

REPO_ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / ".git").exists())


def basename(path: str) -> str:
    """Basename of a path, regardless of whether it uses '/' or '\\' as a
    separator - some raw CDAScorer files were recorded from a mounted Windows
    share and use backslashes, which PurePosixPath/PureWindowsPath alone
    won't handle uniformly across every file."""
    return path.replace("\\", "/").rsplit("/", 1)[-1]


def load_scorer_key() -> dict[str, int]:
    key = pd.read_csv(REPO_ROOT / "anonymisation_keys" / "anonymisation_key.csv")
    return dict(zip(key["Scorer_Name"], key["ID"], strict=True))


def anonymise_cdascorer(name_to_id: dict[str, int]) -> None:
    for set_name in ["set1", "set2"]:
        src_dir = REPO_ROOT / "data" / "cdascorer" / set_name
        dst_dir = REPO_ROOT / "data" / "cdascorer_anon" / set_name
        dst_dir.mkdir(parents=True, exist_ok=True)
        for csv_path in sorted(src_dir.glob("*.csv")):
            scorer_id = name_to_id[csv_path.stem]
            df = pd.read_csv(csv_path)
            df["img"] = df["img"].apply(basename)
            df.to_csv(dst_dir / f"Scorer{scorer_id}.csv", index=False)


def anonymise_rescore(name_to_id: dict[str, int]) -> None:
    src_dir = REPO_ROOT / "analyses" / "06_intra_rater_reliability"
    dst_dir = src_dir / "rescore_anon"
    dst_dir.mkdir(parents=True, exist_ok=True)
    for csv_path in sorted(src_dir.glob("rescore_*.csv")):
        name = csv_path.stem.removeprefix("rescore_")
        scorer_id = name_to_id[name]
        df = pd.read_csv(csv_path)
        df["scorer"] = scorer_id
        df.to_csv(dst_dir / f"Scorer{scorer_id}.csv", index=False)


def anonymise_randomised_info(name_to_id: dict[str, int]) -> None:
    src_path = (
        REPO_ROOT
        / "analyses"
        / "01_generate_raw_data"
        / "01_allocation_info"
        / "randomised_info.csv"
    )
    df = pd.read_csv(src_path)
    for col in ["scorer1", "scorer2", "scorer3"]:
        df[col] = df[col].map(name_to_id)
    df.to_csv(src_path.parent / "randomised_info_anon.csv", index=False)


if __name__ == "__main__":
    scorer_key = load_scorer_key()
    anonymise_cdascorer(scorer_key)
    anonymise_rescore(scorer_key)
    anonymise_randomised_info(scorer_key)
    print("Done.")
