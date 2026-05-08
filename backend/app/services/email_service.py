"""Email sending service. Uses SMTP if configured; logs to console in dev."""
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import structlog

from app.config import settings

log = structlog.get_logger()


async def send_password_reset_email(to_email: str, token: str) -> None:
    reset_url = f"{settings.app_url}/auth/reset-password?token={token}"

    if not settings.smtp_host:
        log.info(
            "password_reset_link_dev",
            msg="SMTP not configured — use this link to reset the password",
            email=to_email,
            reset_url=reset_url,
        )
        return

    await asyncio.to_thread(_send_smtp, to_email, reset_url)


def _send_smtp(to_email: str, reset_url: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your CarGrab password"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    plain = f"Reset your CarGrab password by visiting:\n{reset_url}\n\nThis link expires in 1 hour."
    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Inter,sans-serif;background:#0a0f1e;color:#e2e8f0;padding:32px">
  <div style="max-width:480px;margin:0 auto">
    <h2 style="color:#22d3ee;margin-bottom:8px">Reset your password</h2>
    <p style="color:#94a3b8">Click the button below to reset your CarGrab password.
       This link expires in <strong>1 hour</strong>.</p>
    <a href="{reset_url}"
       style="display:inline-block;margin:24px 0;padding:12px 28px;
              background:#22d3ee;color:#0a0f1e;font-weight:600;
              border-radius:8px;text-decoration:none">
      Reset Password
    </a>
    <p style="color:#64748b;font-size:13px">
      If you didn't request this, you can safely ignore this email.
    </p>
  </div>
</body>
</html>"""

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        if settings.smtp_user:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        log.info("password_reset_email_sent", to=to_email)


async def send_price_alert_email(
    to_email: str,
    listing_title: str,
    listing_url: str,
    target_price_cents: int,
    current_price_cents: int,
) -> None:
    target = f"${target_price_cents / 100:,.0f}"
    current = f"${current_price_cents / 100:,.0f}"

    if not settings.smtp_host:
        log.info(
            "price_alert_triggered_dev",
            msg="SMTP not configured — price alert would be sent",
            email=to_email,
            listing=listing_title,
            target_price=target,
            current_price=current,
            listing_url=listing_url,
        )
        return

    await asyncio.to_thread(
        _send_price_alert_smtp, to_email, listing_title, listing_url, target, current
    )


def _send_price_alert_smtp(
    to_email: str,
    listing_title: str,
    listing_url: str,
    target_price: str,
    current_price: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Price alert: {listing_title} dropped to {current_price}"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    plain = (
        f"{listing_title} is now available at {current_price} (your target: {target_price}).\n\n"
        f"View listing: {listing_url}"
    )
    html = f"""<!DOCTYPE html>
<html>
<body style="font-family:Inter,sans-serif;background:#0a0f1e;color:#e2e8f0;padding:32px">
  <div style="max-width:480px;margin:0 auto">
    <h2 style="color:#22d3ee;margin-bottom:8px">Price Alert Triggered</h2>
    <p style="color:#94a3b8;margin-bottom:4px">{listing_title}</p>
    <p style="font-size:36px;font-weight:700;color:#22d3ee;font-family:monospace;margin:16px 0 4px">
      {current_price}
    </p>
    <p style="color:#64748b;font-size:13px">Your target price was {target_price}</p>
    <a href="{listing_url}"
       style="display:inline-block;margin:24px 0;padding:12px 28px;
              background:#22d3ee;color:#0a0f1e;font-weight:600;
              border-radius:8px;text-decoration:none">
      View Listing
    </a>
    <p style="color:#64748b;font-size:12px">
      You received this because you set a price alert on CarGrab.
    </p>
  </div>
</body>
</html>"""

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        if settings.smtp_user:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
        log.info("price_alert_email_sent", to=to_email)
