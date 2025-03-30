

from crewai.tools import tool
import smtplib
from email.mime.text import MIMEText

@tool('Send_email')
def send_email(to_email: str, subject: str, body: str) -> None:
    """
    Sends an email using Gmail's SMTP server.

    Args:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body content of the email.

    Returns:
        None

    Raises:
        smtplib.SMTPException: If an error occurs while sending the email.
    """

    GMAIL_USER = "testing.1234542422i1o@gmail.com"
    GMAIL_APP_PASSWORD = "pgxj hafh lvvi nblv"  # Replace with your App Password

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email  # Use recipient email here

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())
        print(f"Email sent successfully to {to_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")