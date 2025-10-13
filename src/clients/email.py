from pathlib import Path
from typing import Protocol

import resend
from jinja2 import Environment, FileSystemLoader, Template


class EmailClientProtocol(Protocol):
    """Protocol for the client to enable dependency injection"""

    def send_verification_email(self, email: str, code: str) -> dict:
        """Send email verification code."""
        ...

    def send_password_reset_email(self, email: str, link: str) -> dict:
        """Send password reset link."""
        ...

    def send_waitlist_confirmation(self, email: str, name: str) -> dict:
        """Send waitlist confirmation."""
        ...


class EmailClient:
    def __init__(
        self,
        api_key: str,
        from_email: str,
        templates_dir: str | Path = "templates/emails",
    ):
        """
        Initialize the email service.

        Args:
            api_key: Resend API key
            from_email: Sender email address (e.g., "MillenniCare <noreply@millennicare.com>")
            templates_dir: Directory containing email templates
        """
        resend.api_key = api_key
        self.from_email = from_email

        # Set up Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=True,  # Important for security
        )

    def _render_template(self, template_name: str, **context) -> str:
        """Render a Jinja2 template with the given context."""
        template: Template = self.jinja_env.get_template(template_name)
        return template.render(**context)

    def _send_email(
        self,
        to: str,
        subject: str,
        html: str,
    ):
        """
        Internal method to send email via Resend.

        Args:
            to: Recipient email address
            subject: Email subject
            html: Rendered HTML content
        """
        params: resend.Emails.SendParams = {
            "from": self.from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        resend.Emails.send(params)

    def send_verification_email(self, email: str, code: str) -> None:
        """
        Send email verification code.

        Args:
            email: Recipient email address
            code: Verification code
        """
        html = self._render_template(
            "email_verification.html",
            email=email,
            code=code,
        )
        self._send_email(
            to=email,
            subject="Verify your email address",
            html=html,
        )

    def send_password_reset_email(self, email: str, link: str) -> None:
        """
        Send password reset link.

        Args:
            email: Recipient email address
            link: Password reset link
        """
        html = self._render_template(
            "reset_password.html",
            email=email,
            link=link,
        )
        self._send_email(
            to=email,
            subject="Reset your Millennicare password",
            html=html,
        )

    def send_waitlist_confirmation(self, email: str, name: str) -> None:
        """
        Send waitlist confirmation.

        Args:
            email: Recipient email address
            name: Recipient name
        """
        html = self._render_template(
            "waitlist_confirmation.html",
            name=name,
        )
        self._send_email(
            to=email,
            subject="Welcome to the Millennicare Waitlist",
            html=html,
        )
