import argparse
import logging
import sys
from pathlib import Path

from .config import load_config, DEFAULT_CONFIG_FILE
from .logger import setup_logger
from .mailer import send_email
from .utils import (
    add_email_to_csv,
    DEFAULT_MAILING_DIR,
    get_today_csv_filename,
    read_csv_tasks,
    write_csv_with_status,
    rename_after_process,
    is_processed,
    is_failed,
)

logger = logging.getLogger("campusvirtualfp-email-sender")


def build_parser() -> argparse.ArgumentParser:
    cfg = load_config()

    parser = argparse.ArgumentParser(
        description="Gestiona/envía correos vía SMTP (Campus Virtual FP)."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--add",
        type=str,
        help='Añadir fila CSV: "email;asunto;contenido"',
    )
    group.add_argument(
        "--send",
        action="store_true",
        help="Enviar pendientes del CSV del día",
    )
    group.add_argument(
        "--retry-failed",
        type=str,
        metavar="PATH",
        help="Re-intentar fallidos de un fichero *-FALLIDO.csv",
    )

    # SMTP
    parser.add_argument(
        "--smtp-host",
        default=cfg.get("smtp_host") or "smtp.gmail.com",
    )
    parser.add_argument(
        "--smtp-port",
        type=int,
        default=cfg.get("smtp_port") or 465,
    )
    parser.add_argument(
        "--smtp-user",
        default=cfg.get("smtp_user"),
    )
    parser.add_argument(
        "--smtp-password",
        default=cfg.get("smtp_password"),
    )
    parser.add_argument(
        "--from-name",
        default=cfg.get("from_name") or "",
    )

    # paths / logging
    parser.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_MAILING_DIR,
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default="email_sender.log",
    )

    return parser


def send_emails(args) -> None:
    csv_path = None
    if args.retry_failed:
        if not is_failed(args.retry_failed):
            logger.error("--retry-failed debe ser un fichero *-FALLIDO.csv")
            sys.exit(2)
        csv_path = Path(args.retry_failed)
    else:
        csv_path = Path(get_today_csv_filename(args.output_dir))

    if not csv_path.exists():
        logger.error("No se encontró %s", csv_path)
        sys.exit(1)
    if is_processed(csv_path):
        logger.error("El fichero ya está procesado completamente.")
        sys.exit(1)

    rows = read_csv_tasks(csv_path)
    if not rows:
        logger.warning("CSV vacío, nada que enviar.")
        return

    pending = (
        [r for r in rows if r.get("estado") not in {"ok", "fallido"}]
        if not args.retry_failed
        else [r for r in rows if r.get("estado") == "fallido"]
    )

    if not pending:
        logger.warning("No hay correos pendientes de envío.")
        return

    ok_count = 0
    fail_count = 0
    for row in pending:
        res = send_email(
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_user=args.smtp_user,
            smtp_password=args.smtp_password,
            to=row["email"],
            subject=row["asunto"],
            html=row["contenido"],
            from_name=args.from_name,
        )
        row["estado"] = "ok" if res.ok else "fallido"
        if res.ok:
            ok_count += 1
        else:
            fail_count += 1

    write_csv_with_status(csv_path, rows)
    all_ok = all(r.get("estado") == "ok" for r in rows)
    nuevo_nombre = rename_after_process(csv_path, all_ok)

    # RESUMEN FINAL
    logger.info("========== RESUMEN ==========")
    logger.info("Fichero: %s", nuevo_nombre.name)
    logger.info("Total  : %d", len(rows))
    logger.info("OK     : %d", ok_count)
    logger.info("Fallido: %d", fail_count)
    logger.info("=============================")


def main():
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logger(level=args.log_level, log_file=args.log_file)

    if not args.smtp_user or not args.smtp_password:
        logger.error(
            "Faltan credenciales SMTP. Crea %s o pasa --smtp-user y --smtp-password",
            DEFAULT_CONFIG_FILE,
        )
        sys.exit(1)

    if args.add:
        try:
            email, subject, content = args.add.split(";", 2)
            add_email_to_csv(
                email.strip(),
                subject.strip(),
                content.strip(),
                mailing_dir=args.output_dir,
            )
            logger.info("Email añadido correctamente.")
        except ValueError:
            logger.error("Formato incorrecto. Usa: email;asunto;contenido")
            sys.exit(1)
    else:
        send_emails(args)


if __name__ == "__main__":
    main()