import imaplib
import email
from email.header import decode_header
import smtplib
from datetime import datetime, timedelta
from flask import current_app
import threading
import re

def fetch_emails(user, limit=5):
    try:
        # Get user email settings
        imap_server = user.imap_server or f"imap.{user.email_provider}.com"
        imap_port = user.imap_port or 993
        email_username = user.email_username or user.email
        email_password = user.email_password

        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_username, email_password)
        mail.select("inbox")

        # Search for latest emails
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return []

        email_ids = messages[0].split()[-limit:]  # Get only the latest 'limit' emails
        emails = []

        for email_id in reversed(email_ids):  # Process newest first
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or "utf-8")

            sender, encoding = decode_header(msg.get("From"))[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or "utf-8")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            date_tuple = email.utils.parsedate_tz(msg["Date"])
            if date_tuple:
                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                formatted_date = local_date.strftime("%b %d, %Y %I:%M %p")
            else:
                formatted_date = msg["Date"]

            body = clean_email_body(body)

            emails.append({
                "id": email_id.decode(),
                "sender": sender,
                "subject": subject[:100] + "..." if len(subject) > 100 else subject,
                "body": body[:200] + "..." if len(body) > 200 else body,
                "full_body": body,
                "timestamp": formatted_date,
                "sender_profile_picture": None
            })

        mail.close()
        mail.logout()
        return emails

    except Exception as e:
        current_app.logger.error(f"Error fetching emails: {str(e)}")
        return []
    

def clean_email_body(body):
    """Clean and format email body text"""
    if not body:
        return ""
    
    # Remove excessive whitespace
    body = ' '.join(body.split())
    
    # Remove common email signatures (simple pattern matching)
    signature_patterns = [
        r'--\s*\n.*',
        r'________________.*',
        r'Sent from my.*',
        r'Best regards,.*'
    ]
    
    for pattern in signature_patterns:
        body = re.sub(pattern, '', body, flags=re.DOTALL|re.IGNORECASE)
    
    return body.strip()