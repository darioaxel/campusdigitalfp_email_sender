import pytest
from campusdigitalfp_email_sender.mailer import send_email, SendResult
from unittest.mock import patch, MagicMock


@patch("campusdigitalfp_email_sender.mailer.smtplib.SMTP_SSL")
def test_send_email_ok(mock_smtp):
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    res = send_email(
        "smtp.gmail.com", 465, "user@gmail.com", "pass",
        "to@example.com", "Test", "<h1>Hi</h1>"
    )
    assert res.ok is True
    assert res.error == ""
    mock_server.login.assert_called_once_with("user@gmail.com", "pass")
    mock_server.send_message.assert_called_once()


@patch("campusdigitalfp_email_sender.mailer.smtplib.SMTP_SSL")
def test_send_email_auth_fail(mock_smtp):
    mock_smtp.return_value.__enter__.return_value.login.side_effect = Exception("Auth error")
    res = send_email(
        "smtp.gmail.com", 465, "user@gmail.com", "bad",
        "to@example.com", "Test", "<h1>Hi</h1>"
    )
    assert res.ok is False
    assert "Auth error" in res.error