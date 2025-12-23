"""
Email service for sending emails via SMTP
Uses Titan Email service for reliable email delivery
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""
    
    SMTP_SERVER = "smtp.titan.email"
    SMTP_PORT = 465
    SMTP_USERNAME = "laspad-plateform@hamadouba.com"
    SMTP_PASSWORD = "laspad-plateform"
    FROM_EMAIL = "laspad-plateform@hamadouba.com"
    FROM_NAME = "Santaane Platform"
    
    @classmethod
    def send_email(
        cls,
        to_email: str | List[str],
        subject: str,
        body: str,
        is_html: bool = True,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email via SMTP
        
        Args:
            to_email: Recipient email address(es)
            subject: Email subject
            body: Email body content
            is_html: Whether the body is HTML (default: True)
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{cls.FROM_NAME} <{cls.FROM_EMAIL}>"
            
            # Handle multiple recipients
            if isinstance(to_email, list):
                message["To"] = ", ".join(to_email)
                recipients = to_email
            else:
                message["To"] = to_email
                recipients = [to_email]
            
            message["Subject"] = subject
            
            # Add CC and BCC
            if cc:
                message["Cc"] = ", ".join(cc)
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Attach body
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Connect to SMTP server with SSL
            with smtplib.SMTP_SSL(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)
                server.sendmail(cls.FROM_EMAIL, recipients, message.as_string())
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @classmethod
    def send_welcome_email(cls, to_email: str, full_name: str, password: str, role: str) -> bool:
        """
        Send welcome email with login credentials
        
        Args:
            to_email: Recipient email
            full_name: User's full name
            password: Generated password
            role: User role (e.g., EVALUATOR)
            
        Returns:
            bool: True if sent successfully
        """
        subject = "Bienvenue sur Santaane Platform"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .credentials {{ background-color: #fff; padding: 20px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
                .credential-item {{ margin: 10px 0; }}
                .credential-label {{ font-weight: bold; color: #555; }}
                .credential-value {{ color: #4CAF50; font-family: monospace; font-size: 16px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎓 Bienvenue sur Santaane Platform</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{full_name}</strong>,</p>
                    
                    <p>Votre compte <strong>{role}</strong> a été créé avec succès sur la plateforme Santaane.</p>
                    
                    <div class="credentials">
                        <h3>📧 Vos identifiants de connexion</h3>
                        <div class="credential-item">
                            <span class="credential-label">Email :</span><br>
                            <span class="credential-value">{to_email}</span>
                        </div>
                        <div class="credential-item">
                            <span class="credential-label">Mot de passe :</span><br>
                            <span class="credential-value">{password}</span>
                        </div>
                    </div>
                    
                    <p><strong>⚠️ Important :</strong></p>
                    <ul>
                        <li>Veuillez changer votre mot de passe dès votre première connexion</li>
                        <li>Ne partagez jamais vos identifiants avec qui que ce soit</li>
                        <li>Conservez ce mot de passe en lieu sûr</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="http://localhost:3000/login" class="button">
                            Se connecter
                        </a>
                    </p>
                    
                    <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
                    
                    <p>Cordialement,<br>
                    <strong>L'équipe Santaane Platform</strong></p>
                </div>
                <div class="footer">
                    <p>© 2025 Santaane Platform. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return cls.send_email(to_email, subject, body, is_html=True)
    
    @classmethod
    def send_password_reset_email(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        """
        Send password reset email with reset link
        
        Args:
            to_email: Recipient email
            full_name: User's full name
            reset_token: Password reset token
            
        Returns:
            bool: True if sent successfully
        """
        subject = "Réinitialisation de votre mot de passe - Santaane Platform"
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #FF9800; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
                .warning {{ background-color: #fff3cd; border-left: 4px solid #FF9800; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Réinitialisation de mot de passe</h1>
                </div>
                <div class="content">
                    <p>Bonjour <strong>{full_name}</strong>,</p>
                    
                    <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.</p>
                    
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button">
                            Réinitialiser mon mot de passe
                        </a>
                    </p>
                    
                    <div class="warning">
                        <p><strong>⚠️ Ce lien est valide pendant 24 heures.</strong></p>
                        <p>Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.</p>
                    </div>
                    
                    <p>Cordialement,<br>
                    <strong>L'équipe Santaane Platform</strong></p>
                </div>
                <div class="footer">
                    <p>© 2025 Santaane Platform. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return cls.send_email(to_email, subject, body, is_html=True)

    @classmethod
    def send_evaluation_request_email(
        cls,
        to_email: str,
        evaluator_name: str,
        manuscript_title: str,
        manuscript_pdf_url: str,
        evaluation_deadline: str
    ) -> bool:
        """
        Send evaluation request email to an evaluator
        
        Args:
            to_email: Evaluator email
            evaluator_name: Evaluator's name
            manuscript_title: Title of the manuscript
            manuscript_pdf_url: URL to the manuscript PDF
            evaluation_deadline: Deadline for evaluation (formatted date string)
            
        Returns:
            bool: True if sent successfully
        """
        subject = f"Demande d'évaluation - {manuscript_title}"
        
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .manuscript-box {{ background-color: #fff; border-left: 4px solid #FF9800; padding: 20px; margin: 20px 0; }}
                .button {{ display: inline-block; padding: 12px 30px; background-color: #FF9800; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .deadline {{ background-color: #fff3cd; border-left: 4px solid #FF9800; padding: 15px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #888; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📝 Demande d'évaluation</h1>
                </div>
                <div class="content">
                    <p>Cher(e) Pr. <strong>{evaluator_name}</strong>,</p>
                    
                    <p>Nous espérons que vous allez bien.</p>
                    
                    <p>Nous croyons que vous seriez un(e) excellent(e) rapporteur(rice) pour le manuscrit intitulé :</p>
                    
                    <div class="manuscript-box">
                        <h3 style="margin-top: 0; color: #FF9800;">"{manuscript_title}"</h3>
                        <p>qui a été soumis à la revue <strong>Global Africa</strong>.</p>
                    </div>
                    
                    <p>Le manuscrit est accessible via le lien suivant :</p>
                    <p style="text-align: center;">
                        <a href="{manuscript_pdf_url}" class="button">
                            📄 Consulter le manuscrit
                        </a>
                    </p>
                    
                    <p>La grille d'évaluation est également disponible sur la même page, juste en dessous de l'article.</p>
                    
                    <div class="deadline">
                        <p><strong>⏰ Délai d'évaluation :</strong></p>
                        <p>En espérant que vous accepterez notre demande, nous souhaiterions recevoir votre évaluation d'ici le <strong>{evaluation_deadline}</strong>.</p>
                    </div>
                    
                    <p>Dans l'attente de votre retour, veuillez agréer l'expression de notre considération distinguée.</p>
                    
                    <p style="margin-top: 30px;">Cordialement,<br>
                    <strong>L'équipe éditoriale de Global Africa</strong></p>
                </div>
                <div class="footer">
                    <p>© 2025 Global Africa - Santaane Platform. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return cls.send_email(to_email, subject, body, is_html=True)
