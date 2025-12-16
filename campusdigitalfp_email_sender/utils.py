import csv
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict

DEFAULT_MAILING_DIR = "mailing"


# ----------  nombres y carpetas  ----------
def get_today_csv_filename(mailing_dir: str = DEFAULT_MAILING_DIR) -> Path:
    date_str = datetime.now().strftime("%d-%m-%Y")
    return Path(mailing_dir) / f"id_emails_{date_str}.csv"


def ensure_dir_exists(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ----------  comprobaciones de tipo de fichero  ----------
def is_processed(path: Path) -> bool:
    return path.name.lower().endswith("-procesado.csv")


def is_failed(path: Path) -> bool:
    return path.name.lower().endswith("-fallido.csv")


# ----------  escritura / lectura  ----------
def add_email_to_csv(
    email: str, subject: str, content: str, mailing_dir: str = DEFAULT_MAILING_DIR
) -> None:
    ensure_dir_exists(Path(mailing_dir))
    filename = get_today_csv_filename(mailing_dir)

    file_exists = filename.exists()
    with filename.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        if not file_exists:
            writer.writerow(["email", "asunto", "contenido"])
        writer.writerow([email, subject, content])


def read_csv_tasks(filename: Path) -> List[Dict[str, str]]:
    rows = []
    with filename.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            rows.append(dict(row))
    return rows


def write_csv_with_status(filename: Path, rows: List[Dict[str, str]]) -> None:
    fieldnames = list(rows[0].keys()) if rows else []
    if "estado" not in fieldnames:
        fieldnames.append("estado")

    with filename.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


# ----------  renombrado final  ----------
def rename_after_process(filename: Path, all_ok: bool) -> Path:
    nuevo = filename.with_name(f"{filename.stem}-PROCESADO{filename.suffix}" if all_ok else f"{filename.stem}-FALLIDO{filename.suffix}")
    if nuevo == filename:  # ya tenía el sufijo correcto
        return filename
    shutil.move(str(filename), str(nuevo))
    return nuevo