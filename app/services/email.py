import os
import smtplib
from datetime import datetime
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from app.models.enums import Novedades
from app.utils.LogService import LogService


# Se inicializa nombre de tarea
TASK_NAME = "email.py"

class EmailService:
    def __init__(self, smtp_server, smtp_port,
                 sender_email, app_password, 
                 to_emails, bot_name = "NO_NAME"):
        """
        Initializes the EmailService with SMTP configuration.
        
        :param smtp_server: SMTP server address.
        :param smtp_port: SMTP server port.
        :param sender_email: Sender's email address.
        :param app_password: Sender's email app password.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.app_password = app_password
        self.bot_name = bot_name
        if isinstance(to_emails, str):
            to_emails = [to_emails]
        self.to_emails = to_emails

    def send_email(self, to_emails, subject, template_path, placeholders, attachments=None):
        """
        Sends an email notification with an HTML template and optional attachments.
        
        :param to_emails: List of recipient email addresses.
        :param subject: Email subject.
        :param template_path: Path to the HTML template file.
        :param placeholders: Dictionary containing placeholder values to replace in the template.
        :param attachments: List of file paths to attach to the email.
        """
        # if isinstance(to_emails, str):
        #     to_emails = [to_emails]
        
        try:
        #     # Read the HTML template
        #     with open(template_path, "r", encoding="utf-8") as file:
        #         html_template = file.read()
            
        #     # Replace placeholders with actual values
        #     for key, value in placeholders.items():
        #         html_template = html_template.replace(f"[{key}]", value)
            
        #     # Create the email message
        #     msg = MIMEMultipart()
        #     msg['From'] = self.sender_email
        #     msg['To'] = ", ".join(to_emails)
        #     msg['Subject'] = subject
            
        #     # Attach the HTML content
        #     msg.attach(MIMEText(html_template, "html"))
            
        #     # Attach files if any
        #     if attachments:
        #         for file_path in attachments:
        #             if os.path.exists(file_path):
        #                 with open(file_path, "rb") as attachment:
        #                     part = MIMEBase("application", "octet-stream")
        #                     part.set_payload(attachment.read())
        #                     encoders.encode_base64(part)
        #                     part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        #                     msg.attach(part)
        #             else:
        #                 LogService.error_log(f"Attachment not found: {file_path}", TASK_NAME)
            
        #     # Connect to SMTP server and send email
        #     with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        #         server.starttls()  # Secure connection
        #         server.login(self.sender_email, self.app_password)
        #         server.sendmail(self.sender_email, to_emails, msg.as_string())
            
            LogService.audit_log("Aqui enviara el Correo enviado correctamente", TASK_NAME)
        except Exception as e:
            LogService.error_log(f"Error enviando correo: {e}", TASK_NAME)
            raise e
    
    def notify_execution_end(self):
        """
        Sends a notification email indicating the end of execution.
        
        :param to_emails: List of recipient email addresses.
        """
        subject = "Notificacion Finalizacion"
        html_template = "app/resources/notificaciones/finalizacion.html"
        placeholders = {
            "bot_name": self.bot_name,
            "end_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.send_email(self.to_emails, subject, html_template, placeholders)
    
    def notify_novelty(self, novelty: Novedades, to_emails = None, attachments=None):
        """
        Sends a notification email indicating the end of execution.
        
        :param to_emails: List of recipient email addresses.
        """
        subject = "Notificación inmediata novedades"
        html_template = "app/resources/notificaciones/finalizacion.html"

        placeholders = {
            "novelty": novelty.value,
        }
        
        if to_emails is None:
            to_emails = self.to_emails
         
        self.send_email(to_emails, subject, html_template, placeholders, attachments)