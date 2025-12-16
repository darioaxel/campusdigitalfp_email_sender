import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from campusdigitalfp_email_sender.utils import (
    get_today_csv_filename,
    is_processed,
    is_failed,
    add_email_to_csv,
    read_csv_tasks,
)


def test_get_today_csv_filename():
    path = get_today_csv_filename("mailing")
    date_str = datetime.now().strftime("%d-%m-%Y")
    assert path == Path(f"mailing/id_emails_{date_str}.csv")


def test_is_processed():
    assert is_processed(Path("id_emails_01-01-2025-PROCESADO.csv"))
    assert not is_processed(Path("id_emails_01-01-2025-FALLIDO.csv"))


def test_is_failed():
    assert is_failed(Path("id_emails_01-01-2025-FALLIDO.csv"))
    assert not is_failed(Path("id_emails_01-01-2025-PROCESADO.csv"))


def test_add_and_read_csv():
    with tempfile.TemporaryDirectory() as tmp:
        add_email_to_csv("a@b.com", "Hola", "<h1>Hi</h1>", mailing_dir=tmp)
        rows = read_csv_tasks(get_today_csv_filename(tmp))
        assert len(rows) == 1
        assert rows[0]["email"] == "a@b.com"
        assert rows[0].get("estado") is None  # ← corregido