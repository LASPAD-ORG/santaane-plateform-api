"""
Email service for sending emails via SMTP
Uses Titan Email service for reliable email delivery
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.logging import get_logger
from app.core.config import Settings
logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""
    
    SMTP_SERVER = "smtp.titan.email"
    SMTP_PORT = 465
    SMTP_USERNAME = "laspad-plateform@hamadouba.com"
    SMTP_PASSWORD = "laspad-plateform"
    FROM_EMAIL = "laspad-plateform@hamadouba.com"
    FROM_NAME = "Santaane Platform"
    PLATFORM_URL = "https://santaane.mansatoulo.fr"
    PRIMARY_COLOR = "#59a498"
    PRIMARY_COLOR_DARK = "#4a8a7f"
    
    @classmethod
    def _get_base_template(cls, title: str, content: str, footer_text: str = "") -> str:
        """
        Template de base uniforme pour tous les emails Santaane
        
        Args:
            title: Titre affiché dans le header
            content: Contenu HTML principal de l'email
            footer_text: Texte supplémentaire optionnel pour le footer
            
        Returns:
            str: HTML complet de l'email
        """
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f5f5f5;">
                <tr>
                    <td align="center" style="padding: 40px 20px;">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
                            <!-- Header avec logo -->
                            <tr>
                                <td style="background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); padding: 30px 40px; border-radius: 12px 12px 0 0; text-align: center;">
                                    <img src="https://i.ibb.co/NgRQL99G/logo-santaane-removebg-preview.png" alt="Santaane" width="120" height="60" style="height: 60px; width: auto; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 600;">{title}</h1>
                                </td>
                            </tr>
                            
                            <!-- Contenu principal -->
                            <tr>
                                <td style="padding: 40px;">
                                    {content}
                                </td>
                            </tr>
                            
                            <!-- Footer -->
                            <tr>
                                <td style="background-color: #f8f9fa; padding: 25px 40px; border-radius: 0 0 12px 12px; text-align: center; border-top: 1px solid #eee;">
                                    {footer_text}
                                    <p style="color: #888; font-size: 12px; margin: 10px 0 0 0;">
                                        © 2025 Santaane Platform - LASPAD. Tous droits réservés.
                                    </p>
                                    <p style="color: #aaa; font-size: 11px; margin: 5px 0 0 0;">
                                        Cet email a été envoyé automatiquement, merci de ne pas y répondre directement.
                                    </p>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

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
            logger.info(f"Preparing to send email to {to_email} with subject: {subject}")
            
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
            
            logger.info(f"Connecting to SMTP server {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
            
            # Connect to SMTP server with SSL
            try:
                with smtplib.SMTP_SSL(cls.SMTP_SERVER, cls.SMTP_PORT, timeout=10) as server:
                    logger.info("SMTP connection established, attempting login...")
                    server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)
                    logger.info("SMTP login successful, sending email...")
                    server.sendmail(cls.FROM_EMAIL, recipients, message.as_string())
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
            except smtplib.SMTPException as smtp_error:
                logger.error(f"SMTP error while sending email: {str(smtp_error)}")
                return False
            except TimeoutError as timeout_error:
                logger.error(f"SMTP connection timeout: {str(timeout_error)}")
                return False
            except Exception as conn_error:
                logger.error(f"SMTP connection error: {str(conn_error)}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}. Error: {str(e)}", exc_info=True)
            return False
    
    @classmethod
    def send_otp_email(cls, to_email: str, otp_code: str) -> bool:
        """Envoie le code de vérification OTP pour l'inscription"""
        subject = f"{otp_code} est votre code de vérification - Santaane"
        
        content = f"""
        <div style="text-align: center;">
            <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                Merci de vous être inscrit sur <strong>Santaane Platform</strong>. 
                Utilisez le code ci-dessous pour vérifier votre email :
            </p>
            <div style="background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); padding: 25px 40px; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #ffffff; margin: 30px auto; border-radius: 10px; display: inline-block;">
                {otp_code}
            </div>
            <p style="color: #666; font-size: 14px; margin-top: 25px;">
                Ce code est <strong>confidentiel</strong> et expire dans <strong>2 heures</strong>.
            </p>
            <p style="color: #999; font-size: 13px;">
                Si vous n'avez pas créé de compte, ignorez cet email.
            </p>
        </div>
        """
        
        footer = '<p style="color: #666; font-size: 12px;">Note: Vous pouvez demander jusqu\'à 5 codes par jour.</p>'
        
        body = cls._get_base_template("Vérification de votre compte", content, footer)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_new_user_credentials(cls, to_email: str, full_name: str, password: str, role: str) -> bool:
        """
        Send welcome email with login credentials for new users
        
        Args:
            to_email: Recipient email
            full_name: User's full name
            password: User's plain text password
            role: User role (e.g., ADMIN, EDITOR, EVALUATOR,AUTHOR etc.)
                # Send new user credentials email
        
        Returns:
            bool: True if sent successfully
        """
        subject = "Bienvenue sur Santaane Platform - Vos identifiants de connexion"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Votre compte a été créé avec succès sur la plateforme Santaane.
            </p>
            
            <div style="background: #f8f9fa; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="margin: 0 0 15px 0; color: #59a498;">Vos identifiants de connexion</h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Email :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{to_email}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Mot de passe :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{password}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Rôle :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{role}</span>
                </p>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>Important :</strong>
                </p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; color: #856404;">
                    <li>Veuillez changer votre mot de passe dès votre première connexion</li>
                    <li>Ne partagez jamais vos identifiants avec qui que ce soit</li>
                    <li>Conservez ce mot de passe en lieu sûr</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                Si vous avez des questions, n'hésitez pas à nous contacter.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: #59a498;">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Bienvenue sur Santaane", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_account_activated_email(cls, to_email: str, full_name: str) -> bool:
        """
        Envoie un email de bienvenue après l'activation du compte
        
        Args:
            to_email: Email du destinataire
            full_name: Nom complet de l'utilisateur
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = "Bienvenue sur Santaane Platform - Votre compte est activé"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                    <strong>Félicitations !</strong> Votre compte a été vérifié et activé avec succès.
                </p>
            </div>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Vous faites maintenant partie de la communauté <strong>Santaane</strong>, 
                la plateforme de publication scientifique de <strong>LASPAD</strong>.
            </p>
            
            <h3 style="color: {cls.PRIMARY_COLOR}; margin-top: 30px; margin-bottom: 15px;">Que pouvez-vous faire maintenant ?</h3>
            
            <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                <li><strong>Soumettre vos manuscrits</strong> pour publication</li>
                <li><strong>Consulter les publications</strong> disponibles</li>
                <li><strong>Découvrir les thèmes ouverts</strong> aux contributions</li>
                <li><strong>Compléter votre profil</strong> pour une meilleure visibilité</li>
            </ul>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                    Se connecter à mon compte
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                Si vous avez des questions, n'hésitez pas à nous contacter.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Bienvenue sur Santaane", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def _is_french(cls, lang: str) -> bool:
        """Vérifie si la langue est le français"""
        return lang and lang.lower().startswith('fr')
        
    @classmethod
    def _is_french(cls, lang: str) -> bool:
        """Vérifie si la langue est le français"""
        return lang and lang.lower().startswith('fr')
        
    @classmethod
    def send_new_submission_notification(
        cls, 
        manuscript_id: int,
        manuscript_title: str, 
        author_name: str,
        author_email: str,
        section_name: str,
        theme_name: str = None,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie une notification au système quand un auteur soumet un manuscrit
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            author_name: Nom de l'auteur
            author_email: Email de l'auteur
            section_name: Nom de la section
            theme_name: Nom du thème (optionnel)
            lang: Langue du manuscrit (fr/en)
            
        Returns:
            bool: True si envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Nouvelle soumission - {manuscript_title[:50]}..."
            theme_info = f"<strong>{theme_name}</strong>" if theme_name else "<em>Aucun thème spécifié</em>"
            
            # Construire le contenu en plusieurs parties pour éviter les problèmes d'indentation
            content_parts = [
                f"""
                <div style="color: #333;">
                    <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};">
                            <strong>Nouvelle soumission de manuscrit</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; margin-bottom: 20px;">
                        Un nouvel article a été soumis sur la plateforme Santaane et nécessite votre attention.
                    </p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                        <tr>
                            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">ID Manuscrit</td>
                            <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Titre</td>
                            <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Auteur</td>
                            <td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td>
                        </tr>"""
            ]
            
            if section_name:
                content_parts.append(f"""
                        <tr>
                            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Section</td>
                            <td style="padding: 12px; border: 1px solid #ddd;">{section_name}</td>
                        </tr>""")
                
            if theme_name:
                content_parts.append(f"""
                        <tr>
                            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Thème</td>
                            <td style="padding: 12px; border: 1px solid #ddd;">{theme_info}</td>
                        </tr>""")
                
            content_parts.append(f"""
                    </table>
                    
                    <div style="text-align: center; margin: 35px 0 20px;">
                        <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 15px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                            Voir le manuscrit
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Cet email a été envoyé automatiquement. Merci de ne pas y répondre.
                    </p>
                </div>""")
            
            content = "".join(content_parts)
        else:
            subject = f"New submission - {manuscript_title[:50]}..."
            theme_info = f"<strong>{theme_name}</strong>" if theme_name else "<em>No theme specified</em>"
    def send_secure_reset_link(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        """Envoie le lien de réinitialisation avec avertissement d'expiration de 5 min"""
        subject = "Réinitialisation de votre mot de passe - Santaane"
        reset_link = f"{cls.PLATFORM_URL}/reset-password?token={reset_token}"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Cliquez sur le bouton ci-dessous pour changer votre mot de passe :
            </p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{reset_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Changer mon mot de passe
                </a>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>Important :</strong> Ce lien expirera dans 5 minutes pour votre sécurité.
                </p>
            </div>
            
            <p style="font-size: 14px; color: #666;">
                Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: #59a498;">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)
    
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
        subject = "Bienvenue sur Santaane Platform - Vos identifiants de connexion"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Votre compte a été créé avec succès sur la plateforme Santaane.
            </p>
            
            <div style="background: #f8f9fa; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="margin: 0 0 15px 0; color: #59a498;">Vos identifiants de connexion</h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Email :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{to_email}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Mot de passe :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{password}</span>
                </p>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>Important :</strong>
                </p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; color: #856404;">
                    <li>Veuillez changer votre mot de passe dès votre première connexion</li>
                    <li>Ne partagez jamais vos identifiants avec qui que ce soit</li>
                    <li>Conservez ce mot de passe en lieu sûr</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="http://localhost:3000/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                Si vous avez des questions, n'hésitez pas à nous contacter.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: #59a498;">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Bienvenue sur Santaane", content)
        return cls.send_email(to_email, subject, body)
    
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
        reset_link = f"{cls.PLATFORM_URL}/reset-password?token={reset_token}"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.
            </p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{reset_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Réinitialiser mon mot de passe
                </a>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>Ce lien est valide pendant 24 heures.</strong><br>
                    Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer cet email.
                </p>
            </div>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: #59a498;">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_evaluation_request_email(
        cls,
        to_email: str,
        evaluator_name: str,
        manuscript_title: str,
        manuscript_pdf_url: str,
        evaluation_deadline: str,
        lang: str = "fr"
    ) -> bool:
        """
        Send evaluation request email to an evaluator

        Args:
            to_email: Evaluator email
            evaluator_name: Evaluator's name
            manuscript_title: Title of the manuscript
            manuscript_pdf_url: URL to the manuscript PDF
            evaluation_deadline: Deadline for evaluation (formatted date string)
            lang: Email language (fr/en)

        Returns:
            bool: True if sent successfully
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Demande d'évaluation - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) Pr. <strong>{{evaluator_name}}</strong>,
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous espérons que vous allez bien.
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous croyons que vous seriez un(e) excellent(e) rapporteur(rice) pour le manuscrit intitulé :
                </p>

                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">\u201C{{manuscript_title}}\u201D</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Soumis à la revue <strong>Global Africa</strong>
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Les détails du manuscrit ainsi que la grille d'évaluation sont disponibles dans votre espace personnel sur la plateforme.
                </p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Se connecter
                    </a>
                </div>

                <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Délai d'évaluation :</strong><br>
                        En espérant que vous accepterez notre demande, nous souhaiterions recevoir votre évaluation d'ici le <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Dans l'attente de votre retour, veuillez agréer l'expression de notre considération distinguée.
                </p>

                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """.format(
                evaluator_name=evaluator_name,
                manuscript_title=manuscript_title,
                evaluation_deadline=evaluation_deadline
            )

            body = cls._get_base_template("Demande d'évaluation", content)
        else:
            subject = f"Evaluation Request - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear Dr. <strong>{{evaluator_name}}</strong>,
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We hope this message finds you well.
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We believe you would be an excellent reviewer for the manuscript entitled:
                </p>

                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">\u201C{{manuscript_title}}\u201D</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Submitted to <strong>Global Africa</strong> journal
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    The manuscript details and evaluation form are available in your personal space on the platform.
                </p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Log In
                    </a>
                </div>

                <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Evaluation Deadline:</strong><br>
                        Should you accept this invitation, we would appreciate receiving your evaluation by <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We look forward to your response and thank you for considering this request.
                </p>

                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """.format(
                evaluator_name=evaluator_name,
                manuscript_title=manuscript_title,
                evaluation_deadline=evaluation_deadline
            )

            body = cls._get_base_template("Evaluation Request", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_evaluation_reminder_email(
        cls,
        to_email: str,
        evaluator_name: str,
        manuscript_title: str,
        evaluation_deadline: str,
        lang: str = "fr"
    ) -> bool:
        """
        Send evaluation reminder email to an evaluator who hasn't responded

        Args:
            to_email: Evaluator email
            evaluator_name: Evaluator's name
            manuscript_title: Title of the manuscript
            evaluation_deadline: Deadline for evaluation (formatted date string)
            lang: Email language (fr/en)

        Returns:
            bool: True if sent successfully
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Rappel - Évaluation en attente - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) Pr. <strong>{{evaluator_name}}</strong>,
                </p>

                <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left: 4px solid #ffa000; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #e65100;">
                        <strong>Rappel : Évaluation en attente</strong>
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous n'avons pas encore reçu votre évaluation pour le manuscrit intitulé :
                </p>

                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">\u201C{{manuscript_title}}\u201D</h3>
                </div>

                <div style="background: #fff8e1; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: #ff8f00;">
                        <strong>Délai d'évaluation :</strong><br>
                        Nous vous rappelons que la date limite pour soumettre votre évaluation est fixée au <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>

                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Si vous avez déjà soumis votre évaluation, nous vous remercions et veuillez ignorer ce message.
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Dans le cas contraire, nous vous serions reconnaissants de bien vouloir procéder à l'évaluation dans les meilleurs délais.
                </p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Accéder au manuscrit
                    </a>
                </div>

                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Si vous rencontrez des difficultés pour accéder au manuscrit ou pour soumettre votre évaluation, n'hésitez pas à nous contacter.
                </p>

                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """.format(
                evaluator_name=evaluator_name,
                manuscript_title=manuscript_title,
                evaluation_deadline=evaluation_deadline
            )

            body = cls._get_base_template("Rappel d'évaluation", content)
        else:
            subject = f"Reminder - Pending Evaluation - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear Dr. <strong>{{evaluator_name}}</strong>,
                </p>

                <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); border-left: 4px solid #ffa000; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #e65100;">
                        <strong>Reminder: Pending Evaluation</strong>
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have not yet received your evaluation for the manuscript entitled:
                </p>

                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">\u201C{{manuscript_title}}\u201D</h3>
                </div>

                <div style="background: #fff8e1; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: #ff8f00;">
                        <strong>Evaluation Deadline:</strong><br>
                        We would like to remind you that the deadline for submitting your evaluation is <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    If you have already submitted your evaluation, please accept our thanks and disregard this reminder.
                </p>

                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    If not, we would be grateful if you could complete your evaluation at your earliest convenience.
                </p>

                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Access Manuscript
                    </a>
                </div>

                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    If you encounter any difficulties accessing the manuscript or submitting your evaluation, please do not hesitate to contact us.
                </p>

                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """.format(
                evaluator_name=evaluator_name,
                manuscript_title=manuscript_title,
                evaluation_deadline=evaluation_deadline
            )

            body = cls._get_base_template("Evaluation Reminder", content)
            
        return cls.send_email(to_email, subject, body)

    # ==========================================
    # EMAILS CHANGEMENT DE STATUT MANUSCRIT
    # ==========================================

    @classmethod
    def send_manuscript_accepted_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie un email à l'auteur quand son manuscrit est accepté
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Manuscrit accepté - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Bonne nouvelle !</strong> Votre manuscrit a été accepté.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons le plaisir de vous informer que votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    a été <strong>accepté</strong> pour publication dans la revue <strong>Global Africa</strong>.
                </p>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Action requise :</strong> Pour finaliser le processus de mise en page, nous vous prions de bien vouloir charger la <strong>version finale au format Word (.docx)</strong> via votre tableau de bord.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Téléverser la version finale
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Manuscrit Accepté", content)
        else:
            subject = f"Manuscript Accepted - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Great news!</strong> Your manuscript has been accepted.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We are pleased to inform you that your manuscript entitled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    has been <strong>accepted</strong> for publication in the <strong>Global Africa</strong> journal.
                </p>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Action required:</strong> To finalize the layout process, please upload the <strong>final version in Word format (.docx)</strong> via your dashboard.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Upload Final Version
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Manuscript Accepted", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_rejected_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        rejection_reason: str = None,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie un email à l'auteur quand son manuscrit est refusé
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            rejection_reason: Raison du rejet (optionnel)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Décision concernant votre manuscrit - {manuscript_title[:50]}..."
            
            reason_section = ""
            if rejection_reason:
                reason_section = f"""
                <div style="background: #f8f9fa; border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #dc3545;">Motif de la décision :</h4>
                    <p style="margin: 0; font-size: 14px; color: #555;">{rejection_reason}</p>
                </div>
                """
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #fde8e8 0%, #fad4d4 100%); border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #dc3545;">
                        <strong>Décision éditoriale</strong> - Votre manuscrit n'a pas été retenu
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons examiné attentivement votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Après analyse approfondie par notre comité éditorial, nous avons le regret de vous informer que votre manuscrit <strong>n'a pas été retenu</strong> pour publication dans la revue Global Africa.
                </p>
                
                {reason_section}
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Cette décision ne remet pas en cause la qualité de votre travail. Nous vous encourageons à poursuivre vos recherches et à soumettre de nouveaux travaux à l'avenir.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{{manuscript_id}}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir les détails
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Nous vous remercions de l'intérêt que vous portez à notre revue.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title, manuscript_id=manuscript_id)
            
            body = cls._get_base_template("Décision Éditoriale", content)
        else:
            subject = f"Editorial Decision - {manuscript_title[:50]}..."
            
            reason_section = ""
            if rejection_reason:
                reason_section = f"""
                <div style="background: #f8f9fa; border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #dc3545;">Decision Details:</h4>
                    <p style="margin: 0; font-size: 14px; color: #555;">{rejection_reason}</p>
                </div>
                """
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #fde8e8 0%, #fad4d4 100%); border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #dc3545;">
                        <strong>Editorial Decision</strong> - Your manuscript has not been accepted
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have carefully reviewed your manuscript entitled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    After thorough consideration by our editorial board, we regret to inform you that your manuscript has <strong>not been accepted</strong> for publication in the Global Africa journal.
                </p>
                
                {reason_section}
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    This decision does not reflect on the quality of your work. We encourage you to continue your research and submit future work for our consideration.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{{manuscript_id}}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Details
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for your interest in our journal.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Sincerely,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title, manuscript_id=manuscript_id)
            
            body = cls._get_base_template("Editorial Decision", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_published_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        publication_url: str = None,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie un email à l'auteur quand son manuscrit est publié
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            publication_url: URL de publication (optionnel)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        publication_link = publication_url or f"{cls.PLATFORM_URL}/publications/{manuscript_id}"
        
        if is_fr:
            subject = f"Publication de votre article - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Félicitations !</strong> Votre article est maintenant publié.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons le plaisir de vous annoncer que votre article intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    est désormais <strong>publié</strong> et accessible au public dans la revue <strong>Global Africa</strong>.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Vous pouvez partager ce lien avec vos collègues et sur vos réseaux professionnels :
                </p>
                
                <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 20px 0; word-break: break-all;">
                    <a href="{publication_link}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none;">
                        {publication_link}
                    </a>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{publication_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir ma publication
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Merci pour votre contribution à la recherche scientifique africaine.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title)
            
            body = cls._get_base_template("Article Publié", content)
        else:
            subject = f"Your Article Has Been Published - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Congratulations!</strong> Your article has been published.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We are pleased to inform you that your article entitled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    has been <strong>published</strong> and is now publicly available in the <strong>Global Africa</strong> journal.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    You can share this link with your colleagues and on your professional networks:
                </p>
                
                <div style="background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin: 20px 0; word-break: break-all;">
                    <a href="{publication_link}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none;">
                        {publication_link}
                    </a>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{publication_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Publication
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for contributing to African scientific research.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title)
            
            body = cls._get_base_template("Article Published", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_revision_requested_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        revision_comments: str = None,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie un email à l'auteur quand une révision est demandée
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            revision_comments: Commentaires des évaluateurs (optionnel)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Révision demandée - {manuscript_title[:50]}..."
            
            comments_section = ""
            if revision_comments:
                comments_section = f"""
                <div style="background: #f8f9fa; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #ff9800;">Commentaires des évaluateurs :</h4>
                    <div style="font-size: 14px; color: #555; white-space: pre-line;">{revision_comments}</div>
                </div>
                """
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #ff8f00;">
                        <strong>Révision demandée</strong> - Des modifications sont nécessaires
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons examiné votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Le comité éditorial a évalué votre travail et a décidé que des <strong>modifications sont nécessaires</strong> avant que le manuscrit ne puisse être accepté pour publication.
                </p>
                
                {comments_section}
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Veuillez prendre en compte les commentaires des évaluateurs et soumettre une version révisée de votre manuscrit.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{{manuscript_id}}/revise" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Soumettre une révision
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Vous pouvez consulter les commentaires détaillés et soumettre votre révision en cliquant sur le bouton ci-dessus ou en vous connectant à votre espace auteur.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title, manuscript_id=manuscript_id)
            
            body = cls._get_base_template("Révision Demandée", content)
        else:
            subject = f"Revisions Requested - {manuscript_title[:50]}..."
            
            comments_section = ""
            if revision_comments:
                comments_section = f"""
                <div style="background: #f8f9fa; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h4 style="margin: 0 0 10px 0; color: #ff9800;">Reviewer Comments:</h4>
                    <div style="font-size: 14px; color: #555; white-space: pre-line;">{revision_comments}</div>
                </div>
                """
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{{author_name}}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #ff8f00;">
                        <strong>Revisions Requested</strong> - Modifications Required
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have reviewed your manuscript entitled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{{manuscript_title}}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    The editorial board has evaluated your work and determined that <strong>revisions are required</strong> before the manuscript can be accepted for publication.
                </p>
                
                {comments_section}
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Please address the reviewers' comments and submit a revised version of your manuscript.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{{manuscript_id}}/revise" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Submit Revision
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    You can view the detailed comments and submit your revision by clicking the button above or by logging into your author dashboard.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Sincerely,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """.format(author_name=author_name, manuscript_title=manuscript_title, manuscript_id=manuscript_id)
            
            body = cls._get_base_template("Revisions Requested", content)
        
        return cls.send_email(to_email, subject, body)

    # ==========================================
    # EMAILS NOTIFICATIONS SYSTÈME ÉVALUATEUR
    # ==========================================

    @classmethod
    def send_evaluation_submitted_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        evaluator_name: str,
        evaluator_email: str,
        evaluation_decision: str
    ) -> bool:
        """Envoie une notification au système quand un évaluateur soumet sa grille d'évaluation"""
        subject = f"Évaluation soumise - {manuscript_title[:50]}..."
        # Traduction des décisions
        decision_map = {
            "accepter": "Accepté",
            "accepted": "Accepté",
            "accepted_with_validation": "Accepté avec modifications",
            "favorable": "Favorable",
            "refuser": "Refusé",
            "rejected": "Refusé",
            "revision": "Révision demandée",
            "resubmission_required": "Révision demandée",
            "mineur": "Révision mineure",
            "majeur": "Révision majeure",
        }
        decision_key = evaluation_decision.lower().strip()
        decision_label = decision_map.get(decision_key, evaluation_decision)
        decision_color = "#59a498" if decision_key in ["accepter", "accepted", "favorable"] else ("#ffc107" if decision_key in ["revision", "resubmission_required", "mineur", "majeur"] else "#dc3545")
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: #4a8a7f;">
                    <strong>Nouvelle évaluation soumise</strong>
                </p>
            </div>
            
            <p style="font-size: 15px; margin-bottom: 20px;">
                Un évaluateur a soumis sa grille d'évaluation pour un manuscrit.
            </p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">Manuscrit</td>
                    <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">ID Manuscrit</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Évaluateur</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td>
                </tr>
           
            </table>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}/evaluations" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Voir l'évaluation
                </a>
            </div>
            
            <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                Cet email a été envoyé automatiquement suite à la soumission d'une évaluation.
            </p>
        </div>
        """
        
        body = cls._get_base_template("Évaluation Soumise", content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluator_response_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        evaluator_name: str,
        evaluator_email: str,
        response: str  # "accepted" ou "declined"
    ) -> bool:
        """Envoie une notification au système quand un évaluateur accepte ou refuse une demande"""
        is_accepted = response.lower() in ["accepted", "accepté", "accepter"]
        status_text = "accepté" if is_accepted else "refusé"
        status_color = "#59a498" if is_accepted else "#dc3545"
        
        subject = f"Demande d'évaluation {status_text}e - {manuscript_title[:40]}..."
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, {'#e8f5f3' if is_accepted else '#fce4e4'} 0%, {'#d4ebe7' if is_accepted else '#f5d4d4'} 100%); border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {status_color};">
                    <strong>Demande d'évaluation {status_text}e</strong>
                </p>
            </div>
            
            <p style="font-size: 15px; margin-bottom: 20px;">
                Un évaluateur a <strong>{status_text}</strong> la demande d'évaluation pour un manuscrit.
            </p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">Manuscrit</td>
                    <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">ID Manuscrit</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Évaluateur</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Réponse</td>
                    <td style="padding: 12px; border: 1px solid #ddd;"><strong style="color: {status_color};">{status_text.upper()}</strong></td>
                </tr>
            </table>
            
            {"" if is_accepted else '''
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    <strong>Action requise :</strong> Vous devrez peut-être assigner un autre évaluateur pour ce manuscrit.
                </p>
            </div>
            '''}
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Gérer le manuscrit
                </a>
            </div>
            
            <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                Cet email a été envoyé automatiquement.
            </p>
        </div>
        """
        
        body = cls._get_base_template(f"Réponse Évaluateur", content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_manuscript_resubmitted_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        author_name: str,
        author_email: str,
        revision_number: int = 1,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie une notification au système quand un auteur re-soumet son manuscrit après révision
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            author_name: Nom de l'auteur
            author_email: Email de l'auteur
            revision_number: Numéro de la révision (par défaut: 1)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Re-soumission - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Manuscrit révisé re-soumis</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    Un auteur a re-soumis son manuscrit après révision.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">ID Manuscrit</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Titre</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Auteur</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Version</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">Révision #{revision_number}</td>
                    </tr>
                </table>
                
                <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Action requise :</strong> Veuillez examiner les modifications apportées par l'auteur.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir le manuscrit révisé
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    Cet email a été envoyé automatiquement suite à une re-soumission.
                </p>
            </div>
            """
            
            body = cls._get_base_template("Manuscrit Révisé", content)
        else:
            subject = f"Resubmission - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Revised Manuscript Resubmitted</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    An author has resubmitted their manuscript after revision.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">Manuscript ID</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Title</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Author</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Version</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">Revision #{revision_number}</td>
                    </tr>
                </table>
                
                <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Action Required:</strong> Please review the changes made by the author.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Revised Manuscript
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    This email was automatically sent after a resubmission.
                </p>
            </div>
            """
            
            body = cls._get_base_template("Revised Manuscript", content)
        
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_submission_confirmation_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        lang: str = "fr"
    ) -> bool:
        """
        Envoie un email de confirmation à l'auteur après soumission de son manuscrit
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Confirmation de soumission - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Votre manuscrit a bien été soumis !</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons bien reçu votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Votre soumission est maintenant en cours de traitement par notre équipe éditoriale. Vous serez notifié(e) par email à chaque étape importante du processus d'évaluation.
                </p>
                
                <h4 style="color: {cls.PRIMARY_COLOR}; margin-top: 25px; margin-bottom: 15px;">Prochaines étapes :</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                    <li>Vérification initiale par l'équipe éditoriale</li>
                    <li>Attribution à des évaluateurs experts</li>
                    <li>Processus d'évaluation par les pairs</li>
                    <li>Décision éditoriale finale</li>
                </ul>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Suivre mon manuscrit
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Merci pour votre confiance et votre contribution à la recherche scientifique.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Soumission Confirmée", content)
        else:
            subject = f"Submission Confirmation - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Your manuscript has been successfully submitted!</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have received your manuscript titled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Your submission is now being processed by our editorial team. You will be notified by email at each important stage of the evaluation process.
                </p>
                
                <h4 style="color: {cls.PRIMARY_COLOR}; margin-top: 25px; margin-bottom: 15px;">Next Steps:</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                    <li>Initial review by the editorial team</li>
                    <li>Assignment to expert reviewers</li>
                    <li>Peer review process</li>
                    <li>Final editorial decision</li>
                </ul>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Track My Manuscript
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for your trust and your contribution to scientific research.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Submission Confirmed", content)
            
        return cls.send_email(to_email, subject, body)
