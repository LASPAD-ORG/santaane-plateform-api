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
    """Service d'envoi d'emails"""
    
    DEFAULT_LANGUAGE = 'fr'
    
    # Configuration SMTP
    SMTP_SERVER = "smtp.titan.email"
    SMTP_PORT = 465
    SMTP_USERNAME = "laspad-plateform@hamadouba.com"
    SMTP_PASSWORD = "laspad-plateform"
    FROM_EMAIL = "laspad-plateform@hamadouba.com"
    FROM_NAME = "Global Africa Journal"
    PLATFORM_URL = "https://www.globalafricajournal.org"
    PRIMARY_COLOR = "#59a498"
    PRIMARY_COLOR_DARK = "#4a8a7f"

    # Branding
    LOGO_URL = "https://www.globalafricajournal.org/images/02-GA-Site-Page-Noir.gif"
    JOURNAL_NAME = "Global Africa"
    LAB_NAME = "LASPAD"
    LAB_URL = "https://laspad.org/"
    SCIENCES_URL = "https://www.globalafricasciences.org/"
    EVENTS_URL = "https://events.laspad.org/"

    @classmethod
    def _get_base_template(cls, title: str, content: str, footer_text: str = "") -> str:
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
                                    <img src="{cls.LOGO_URL}" alt="Global Africa Journal" style="height: 70px; width: auto; display: block; margin: 0 auto 15px auto;">
                                    <h1 style="color: #ffffff; margin: 0; font-size: 22px; font-weight: 600;">{title}</h1>
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
                                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin: 0 0 15px 0;">
                                        <tr>
                                            <td align="center">
                                                <a href="{cls.PLATFORM_URL}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none; font-size: 12px; margin: 0 8px;">Global Africa Journal</a>
                                                <span style="color: #ccc;">|</span>
                                                <a href="{cls.SCIENCES_URL}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none; font-size: 12px; margin: 0 8px;">Global Africa Sciences</a>
                                                <span style="color: #ccc;">|</span>
                                                <a href="{cls.EVENTS_URL}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none; font-size: 12px; margin: 0 8px;">LASPAD Events</a>
                                                <span style="color: #ccc;">|</span>
                                                <a href="{cls.LAB_URL}" style="color: {cls.PRIMARY_COLOR}; text-decoration: none; font-size: 12px; margin: 0 8px;">LASPAD</a>
                                            </td>
                                        </tr>
                                    </table>
                                    <p style="color: #888; font-size: 12px; margin: 10px 0 0 0;">
                                        &copy; 2025 {cls.JOURNAL_NAME} &mdash; {cls.LAB_NAME}. Tous droits réservés.
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
        try:
            logger.info(f"Preparing to send email to {to_email} with subject: {subject}")
            message = MIMEMultipart("alternative")
            message["From"] = f"{cls.FROM_NAME} <{cls.FROM_EMAIL}>"
            if isinstance(to_email, list):
                message["To"] = ", ".join(to_email)
                recipients = to_email
            else:
                message["To"] = to_email
                recipients = [to_email]
            message["Subject"] = subject
            if cc:
                message["Cc"] = ", ".join(cc)
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            if is_html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            logger.info(f"Connecting to SMTP server {cls.SMTP_SERVER}:{cls.SMTP_PORT}")
            try:
                with smtplib.SMTP_SSL(cls.SMTP_SERVER, cls.SMTP_PORT, timeout=10) as server:
                    logger.info("SMTP connection established, attempting login...")
                    server.login(cls.SMTP_USERNAME, cls.SMTP_PASSWORD)
                    logger.info("SMTP login successful, sending email...")
                    server.sendmail(cls.FROM_EMAIL, recipients, message.as_string())
                    logger.info(f"Email sent successfully to {to_email}")
                    return True
            except smtplib.SMTPException as smtp_error:
                logger.error(f"Erreur SMTP: {str(smtp_error)}")
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
    def _is_french(cls, lang: Optional[str] = None) -> bool:
        if not lang:
            return cls.DEFAULT_LANGUAGE.startswith('fr')
        return str(lang).lower().startswith('fr')

    #====================================
    # EMAILS NOTIFICATIONS VERIFICATION AVEC OTP
    #====================================

    @classmethod
    def send_otp_email(cls, to_email: str, otp_code: str) -> bool:
        subject = f"{otp_code} est votre code de vérification - {cls.JOURNAL_NAME}"
        
        content = f"""
        <div style="text-align: center;">
            <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                Merci de vous être inscrit sur <strong>{cls.JOURNAL_NAME}</strong>. 
                Utilisez le code ci-dessous pour vérifier votre email :
            </p>
            <div style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); padding: 25px 40px; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #ffffff; margin: 30px auto; border-radius: 10px; display: inline-block;">
                {otp_code}
            </div>
            <p style="color: #666; font-size: 14px; margin-top: 25px;">
                Ce code est <strong>confidentiel</strong> et expire dans <strong>2 heures</strong>.
            </p>
            <p style="color: #999; font-size: 13px;">
                Si vous n'avez pas créé de compte, ignorez cet email.
            </p>
            <p style="color: #999; font-size: 13px;">
                Vérifiez votre dossier spam, le cas échéant.
            </p>
        </div>
        """
        
        footer = f'<p style="color: #666; font-size: 12px;">Note: Vous pouvez demander jusqu\'à 5 codes par jour.</p>'
        body = cls._get_base_template("Vérification de votre compte", content, footer)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_account_activated_email(cls, to_email: str, full_name: str) -> bool:
        subject = f"Bienvenue sur {cls.JOURNAL_NAME} - Votre compte est activé"
        
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
                Vous faites maintenant partie de la communauté <strong>{cls.JOURNAL_NAME}</strong>, 
                la plateforme de publication scientifique de <strong>{cls.LAB_NAME}</strong>.
            </p>
            
            <h3 style="color: {cls.PRIMARY_COLOR}; margin-top: 30px; margin-bottom: 15px;">Que pouvez-vous faire maintenant ?</h3>
            <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                <li><strong>Soumettre vos manuscrits</strong> pour publication</li>
                <li><strong>Consulter les publications</strong> disponibles</li>
                <li><strong>Découvrir les thèmes ouverts</strong> aux contributions</li>
                <li><strong>Compléter votre profil</strong> pour une meilleure visibilité</li>
            </ul>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                    Se connecter à mon compte
                </a>
            </div>
            
            <p style="font-size: 14px; color: #666; margin-top: 30px;">
                Si vous avez des questions, n'hésitez pas à nous contacter.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template(f"Bienvenue sur {cls.JOURNAL_NAME}", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_secure_reset_link(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        subject = f"Réinitialisation de votre mot de passe - {cls.JOURNAL_NAME}"
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
                <a href="{reset_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
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
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_password_reset_email(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        subject = f"Réinitialisation de votre mot de passe - {cls.JOURNAL_NAME}"
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
                <a href="{reset_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
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
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)

    #====================================
    # EMAILS NOTIFICATIONS WELCOME
    #====================================

    @classmethod
    def send_new_user_credentials(cls, to_email: str, full_name: str, password: str, roles: str) -> bool:
        subject = f"Bienvenue sur {cls.JOURNAL_NAME} - Vos identifiants de connexion"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Votre compte a été créé avec succès sur la plateforme de soumission et de gestion éditoriale de la revue <strong>{cls.JOURNAL_NAME}</strong>.
            </p>
            <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR};">Vos identifiants de connexion</h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Email :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{to_email}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Mot de passe :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{password}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Rôle(s) :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{roles}</span>
                </p>
            </div>
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;"><strong>Important :</strong></p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; color: #856404;">
                    <li>Veuillez changer votre mot de passe dès votre première connexion</li>
                    <li>Ne partagez jamais vos identifiants avec qui que ce soit</li>
                    <li>Conservez ce mot de passe en lieu sûr</li>
                </ul>
            </div>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter
                </a>
            </div>
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template(f"Bienvenue sur {cls.JOURNAL_NAME}", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_welcome_email(cls, to_email: str, full_name: str, password: str, role: str) -> bool:
        subject = f"Bienvenue sur {cls.JOURNAL_NAME} - Vos identifiants de connexion"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Votre compte a été créé avec succès sur <strong>{cls.JOURNAL_NAME}</strong>.
            </p>
            <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR};">Vos identifiants de connexion</h3>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Email :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{to_email}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Mot de passe :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{password}</span>
                </p>
                <p style="margin: 8px 0; font-size: 14px;">
                    <strong>Rôle :</strong><br>
                    <span style="color: {cls.PRIMARY_COLOR}; font-family: monospace; font-size: 16px;">{role}</span>
                </p>
            </div>
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;"><strong>Important :</strong></p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; font-size: 14px; color: #856404;">
                    <li>Veuillez changer votre mot de passe dès votre première connexion</li>
                    <li>Ne partagez jamais vos identifiants avec qui que ce soit</li>
                    <li>Conservez ce mot de passe en lieu sûr</li>
                </ul>
            </div>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter
                </a>
            </div>
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template(f"Bienvenue sur {cls.JOURNAL_NAME}", content)
        return cls.send_email(to_email, subject, body)

    #====================================
    # EMAILS NOTIFICATIONS ÉVALUATEUR
    #====================================

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
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Demande d'évaluation - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{{evaluator_name}}</strong>,
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
                        Soumis à la revue <strong>{cls.JOURNAL_NAME}</strong>
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
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
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
                    Dear <strong>{{evaluator_name}}</strong>,
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
                        Submitted to <strong>{cls.JOURNAL_NAME}</strong> journal
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
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
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
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Rappel - Évaluation en attente - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{{evaluator_name}}</strong>,
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
                        Nous vous rappelons que la date limite est fixée au <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Si vous avez déjà soumis votre évaluation, nous vous remercions et veuillez ignorer ce message.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Accéder au manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
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
                    Dear <strong>{{evaluator_name}}</strong>,
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
                        We remind you that the deadline is <strong>{{evaluation_deadline}}</strong>.
                    </p>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    If you have already submitted your evaluation, please accept our thanks and disregard this reminder.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Access Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
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
    # EMAILS CHANGEMENT DE STATUT UTILISATEUR
    # ==========================================

    @classmethod
    def send_inactive_user(cls, to_email: str, full_name: str, admin_name: str = None, admin_email: str = None) -> bool:
        subject = f"Votre compte a été désactivé - {cls.JOURNAL_NAME}"
        admin_info = f"par l'administrateur <strong>{admin_name}</strong>" if admin_name else "par un administrateur"
        contact_info = f"veuillez contacter l'administrateur à l'adresse : <strong>{admin_email}</strong>" if admin_email else "veuillez contacter l'administrateur de la plateforme"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: #721c24;">
                    <strong>Information importante :</strong> Votre compte a été désactivé {admin_info}.
                </p>
            </div>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Votre compte sur {cls.JOURNAL_NAME} a été désactivé. Vous ne pourrez plus vous connecter avec vos identifiants actuels.
            </p>
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Si vous pensez qu'il s'agit d'une erreur ou si vous avez des questions, {contact_info}.
            </p>
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Désactivation de votre compte", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_User_update(cls, to_email: str, full_name: str, updated_fields: dict = None, admin_name: str = None) -> bool:
        logger.info(f"send_User_update called: to_email={to_email}, updated_fields={updated_fields}, admin_name={admin_name}")
        
        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            if field_name == 'password':
                subject = f"Votre mot de passe a été réinitialisé - {cls.JOURNAL_NAME}"
            elif field_name == 'is_active':
                subject = f"Le statut de votre compte a été modifié - {cls.JOURNAL_NAME}"
            elif field_name == 'roles':
                subject = f"Vos rôles ont été modifiés - {cls.JOURNAL_NAME}"
            else:
                subject = f"Votre {cls._get_field_display_name(field_name)} a été mis à jour - {cls.JOURNAL_NAME}"
        else:
            subject = f"Votre profil a été mis à jour - {cls.JOURNAL_NAME}"
        
        changes_content = ""
        if updated_fields:
            if len(updated_fields) == 1:
                field_name = list(updated_fields.keys())[0]
                field_display = cls._get_field_display_name(field_name)
                if field_name == 'password':
                    password_value = list(updated_fields.values())[0]
                    if isinstance(password_value, str) and password_value != 'reset':
                        changes_content = """
                        <div style="background: #e8f5f3; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <p style="margin: 0; font-size: 16px; color: #2e7d32; text-align: center;">
                                <strong>🔐 Votre mot de passe a été réinitialisé</strong><br>
                                <span style="font-size: 14px;">Voici votre nouveau mot de passe :</span>
                            </p>
                            <div style="background: #f8f9fa; border: 2px dashed #59a498; padding: 15px; margin: 15px 0; border-radius: 8px; text-align: center;">
                                <span style="font-family: monospace; font-size: 18px; font-weight: bold; color: #59a498; letter-spacing: 2px;">""" + password_value + """</span>
                            </div>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666; text-align: center;">
                                <strong>Important :</strong> Veuillez changer ce mot de passe dès votre première connexion.
                            </p>
                        </div>"""
                    else:
                        changes_content = """
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <p style="margin: 0; font-size: 16px; color: #856404; text-align: center;">
                                <strong>🔒 Votre mot de passe a été réinitialisé</strong>
                            </p>
                        </div>"""
                elif field_name == 'is_active':
                    is_active = list(updated_fields.values())[0]
                    status_text = "activé" if is_active else "désactivé"
                    status_color = "#28a745" if is_active else "#dc3545"
                    changes_content = f"""
                    <div style="background: {'#d4edda' if is_active else '#f8d7da'}; border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: {'#155724' if is_active else '#721c24'}; text-align: center;">
                            <strong>Votre compte a été {status_text}</strong>
                        </p>
                    </div>"""
                elif field_name == 'roles':
                    roles = list(updated_fields.values())[0]
                    roles_text = ", ".join(str(r) for r in roles) if isinstance(roles, (list, tuple)) and roles else str(roles) if roles else "Non défini"
                    changes_content = f"""
                    <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                            <strong>Vos nouveaux rôles :</strong><br>
                            <span style="font-size: 14px; color: #555;">{roles_text}</span>
                        </p>
                    </div>"""
                else:
                    value = list(updated_fields.values())[0]
                    value_str = str(value) if value is not None else "Non défini"
                    changes_content = f"""
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR};">
                            <strong>{field_display} :</strong><br>
                            <span style="font-size: 14px; color: #555;">{value_str}</span>
                        </p>
                    </div>"""
            else:
                changes_content = f"""
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR}; font-size: 16px;">Modifications apportées :</h3>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #555;">"""
                for field, value in updated_fields.items():
                    fn = cls._get_field_display_name(field)
                    if field == 'is_active':
                        vs = "Activé" if value else "Désactivé"
                    elif field == 'password':
                        vs = f"🔐 Nouveau mot de passe : {value}" if isinstance(value, str) and value != 'reset' else "🔒 Modifié (pour votre sécurité)"
                    elif field == 'roles':
                        vs = ", ".join(str(r) for r in value) if isinstance(value, (list, tuple)) and value else str(value) if value else "Non défini"
                    else:
                        vs = str(value) if value is not None else "Non défini"
                    changes_content += f"<li><strong>{fn}</strong> : {vs}</li>"
                changes_content += "</ul></div>"
        
        admin_info = f"par l'administrateur <strong>{admin_name}</strong>" if admin_name else "par un administrateur"
        
        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            if field_name == 'password':
                main_message = f"Votre mot de passe a été réinitialisé {admin_info}."
            elif field_name == 'is_active':
                is_active = list(updated_fields.values())[0]
                main_message = f"Votre compte a été {'activé' if is_active else 'désactivé'} {admin_info}."
            elif field_name == 'roles':
                main_message = f"Vos rôles ont été modifiés {admin_info}."
            else:
                main_message = f"Votre {cls._get_field_display_name(field_name)} a été mis à jour {admin_info}."
        else:
            main_message = f"Votre profil a été mis à jour {admin_info}."
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">
                Bonjour <strong>{full_name}</strong>,
            </p>
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                    <strong>Information importante :</strong> {main_message}
                </p>
            </div>
            {changes_content}
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter à mon compte
                </a>
            </div>
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Mise à jour de votre profil", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def _get_field_display_name(cls, field_name: str) -> str:
        field_mapping = {
            'email': 'email', 'full_name': 'nom complet', 'profile_photo': 'photo de profil',
            'orcid_id': 'ORCID ID', 'bio': 'biographie', 'position': 'position',
            'institution': 'institution', 'is_active': 'statut du compte',
            'password': 'mot de passe', 'roles': 'rôles'
        }
        return field_mapping.get(field_name, field_name)

    # ==========================================
    # EMAILS STATUT MANUSCRIT
    # ==========================================

    @classmethod
    def send_author_submission_confirmation_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, submission_date: str, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Confirmation de soumission - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Votre manuscrit a bien été soumis !</strong></p>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">Nous avons bien reçu votre manuscrit intitulé :</p>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        <strong>Référence :</strong> #{manuscript_id}<br>
                        <strong>Date de soumission :</strong> {submission_date}
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
                <p style="font-size: 14px; color: #666; margin-top: 30px;">Merci pour votre confiance et votre contribution à la recherche scientifique.</p>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>
            """
            body = cls._get_base_template("Soumission Confirmée", content)
        else:
            subject = f"Submission Confirmation - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Your manuscript has been successfully submitted!</strong></p>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">We have received your manuscript titled:</p>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        <strong>Reference:</strong> #{manuscript_id}<br>
                        <strong>Submission date:</strong> {submission_date}
                    </p>
                </div>
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
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>
            """
            body = cls._get_base_template("Submission Confirmed", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_accepted_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, custom_message: Optional[str] = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Votre manuscrit est accepté pour la publication - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Bonne nouvelle !</strong> Votre manuscrit a été accepté pour la publication dans la revue {cls.JOURNAL_NAME}.
                    </p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                """
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Message de l'éditeur :</strong><br>{custom_message}
                    </p>
                </div>"""
            content += f"""
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Étape suivante :</strong><br>
                        Veuillez nous soumettre la version finale de votre manuscrit au format <strong>DOCX ou Word</strong> pour la mise en page.
                    </p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Soumettre la version finale
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Manuscrit Accepté", content)
        else:
            subject = f"Manuscript Accepted for Publication - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Great news!</strong> Your manuscript has been accepted for publication in <strong>{cls.JOURNAL_NAME}</strong>.
                    </p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>"""
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Editor's Message:</strong><br>{custom_message}
                    </p>
                </div>"""
            content += f"""
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Next Step:</strong><br>
                        Please submit the final version of your manuscript in <strong>DOCX or Word format</strong> for typesetting.
                    </p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Submit Final Version
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Manuscript Accepted", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_rejected_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, rejection_reason: str = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        logger.info(f"Rejection reason received: {rejection_reason}")
        
        if is_fr:
            subject = f"Décision concernant votre manuscrit - {manuscript_title[:50]}..."
            reason_section = f"""
            <div style="background: #f8f9fa; border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h4 style="margin: 0 0 10px 0; color: #dc3545;">Motif de la décision :</h4>
                <p style="margin: 0; font-size: 14px; color: #555;">{rejection_reason}</p>
            </div>""" if rejection_reason else ""
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #fde8e8 0%, #fad4d4 100%); border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #dc3545;">
                        <strong>Décision éditoriale</strong> - Votre manuscrit n'a pas été retenu
                    </p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Après analyse approfondie par notre comité éditorial, nous avons le regret de vous informer que votre manuscrit <strong>n'a pas été retenu</strong> pour publication dans la revue {cls.JOURNAL_NAME}.
                </p>
                {reason_section}
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Cette décision ne remet pas en cause la qualité de votre travail. Nous vous encourageons à poursuivre vos recherches et à soumettre de nouveaux travaux à l'avenir.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir les détails
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Décision Éditoriale", content)
        else:
            subject = f"Editorial Decision - {manuscript_title[:50]}..."
            reason_section = f"""
            <div style="background: #f8f9fa; border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h4 style="margin: 0 0 10px 0; color: #dc3545;">Decision Details:</h4>
                <p style="margin: 0; font-size: 14px; color: #555;">{rejection_reason}</p>
            </div>""" if rejection_reason else ""
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #fde8e8 0%, #fad4d4 100%); border-left: 4px solid #dc3545; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #dc3545;">
                        <strong>Editorial Decision</strong> - Your manuscript has not been accepted
                    </p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    After thorough consideration, we regret to inform you that your manuscript has <strong>not been accepted</strong> for publication in <strong>{cls.JOURNAL_NAME}</strong>.
                </p>
                {reason_section}
                <p style="font-size: 15px; line-height: 1.6;">
                    We encourage you to continue your research and submit future work for our consideration.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Details
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Sincerely,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Editorial Decision", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_published_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, publication_url: str = None,
        custom_message: Optional[str] = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        publication_link = publication_url or f"{cls.PLATFORM_URL}/publications/{manuscript_id}"
        
        if is_fr:
            subject = f"Publication de votre article - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Félicitations !</strong> Votre article est maintenant publié.</p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    est désormais <strong>publié</strong> et accessible au public dans la revue <strong>{cls.JOURNAL_NAME}</strong>.
                </p>"""
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Message de l'éditeur :</strong><br>{custom_message}
                    </p>
                </div>"""
            content += f"""
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{publication_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir ma publication
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Article Publié", content)
        else:
            subject = f"Your Article Has Been Published - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Congratulations!</strong> Your article has been published.</p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    is now <strong>published</strong> and publicly available in <strong>{cls.JOURNAL_NAME}</strong>.
                </p>"""
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Editor's Message:</strong><br>{custom_message}
                    </p>
                </div>"""
            content += f"""
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{publication_link}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Publication
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Article Published", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_revision_requested_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, revision_comments: str = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Révision demandée - {manuscript_title[:50]}..."
            comments_section = f"""
            <div style="background: #f8f9fa; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h4 style="margin: 0 0 10px 0; color: #ff9800;">Commentaires de l'éditeur :</h4>
                <div style="font-size: 14px; color: #555; white-space: pre-line;">{revision_comments}</div>
            </div>""" if revision_comments else ""
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #ff8f00;"><strong>Révision demandée</strong> - Des modifications sont nécessaires</p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Le comité éditorial a décidé que des <strong>modifications sont nécessaires</strong> avant que le manuscrit ne puisse être accepté pour publication.
                </p>
                {comments_section}
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}/revise" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Soumettre une révision
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Révision Demandée", content)
        else:
            subject = f"Revisions Requested - {manuscript_title[:50]}..."
            comments_section = f"""
            <div style="background: #f8f9fa; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                <h4 style="margin: 0 0 10px 0; color: #ff9800;">Editor's Comments:</h4>
                <div style="font-size: 14px; color: #555; white-space: pre-line;">{revision_comments}</div>
            </div>""" if revision_comments else ""
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%); border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #ff8f00;"><strong>Revisions Requested</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                {comments_section}
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}/revise" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Submit Revision
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Sincerely,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Revisions Requested", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_auteur_confirmation_docx_file(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        greeting_name = author_name.split()[0] if author_name and author_name.strip() else ("Auteur" if is_fr else "Author")
        
        if is_fr:
            subject = f"Confirmation de réception de la version finale - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{greeting_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Votre version finale a bien été reçue !</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir mon manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Version finale reçue", content)
        else:
            subject = f"Final Version Received - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{greeting_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Your final version has been received!</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View My Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The {cls.JOURNAL_NAME} Editorial Team</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Final Version Received", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def _get_author_resubmission_confirmation(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        revision_number: int, is_french: bool
     ) -> tuple[str, str]:
        first_name = author_name.split()[0] if author_name else ("Auteur" if is_french else "Author")
        
        if is_french:
            subject = f"Confirmation de re-soumission - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{first_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Votre manuscrit a bien été re-soumis !</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id} | Version : Révision #{revision_number}
                    </p>
                </div>
                <h4 style="color: {cls.PRIMARY_COLOR}; margin-top: 25px; margin-bottom: 15px;">Prochaines étapes :</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                    <li>Examen des modifications par l'équipe éditoriale</li>
                    <li>Nouvelle évaluation si nécessaire</li>
                    <li>Décision éditoriale finale</li>
                </ul>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Suivre mon manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Confirmation de re-soumission", content)
        else:
            subject = f"Resubmission Confirmation - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{first_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Your manuscript has been successfully resubmitted!</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id} | Version: Revision #{revision_number}
                    </p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Track My Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The {cls.JOURNAL_NAME} Editorial Team</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Resubmission Confirmation", content)
        
        return subject, body

    @classmethod
    def send_manuscript_updated_author_notification(
        cls, to_email: str, author_name: str, manuscript_id: int,
        manuscript_title: str, changes: dict, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        changes_html = []
        for field, (old_val, new_val) in changes.items():
            changes_html.append(f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 25%; color: #555; font-weight: 500;">{field}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 35%; color: #e74c3c; text-decoration: line-through;">{old_val or ('Non spécifié' if is_fr else 'Not specified')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 40%; color: #27ae60; font-weight: 500;">{new_val or ('Non spécifié' if is_fr else 'Not specified')}</td>
            </tr>""")
        changes_html_str = "\n".join(changes_html)
        
        greeting = author_name.split(' ')[0] if author_name and ' ' in author_name else author_name or ('Cher auteur' if is_fr else 'Author')
        
        if is_fr:
            subject = f"Votre manuscrit a été mis à jour - {manuscript_title[:50]}..."
            title_label, field_label, old_label, new_label = "Titre", "Champ", "Ancienne valeur", "Nouvelle valeur"
            ref_label, btn_label = "Référence", "Voir mon manuscrit"
            detail_label = "Détails du manuscrit"
            change_label = "Modifications effectuées"
            intro = "Votre manuscrit a été mis à jour par l'équipe éditoriale."
            sign = f"L'équipe éditoriale de {cls.JOURNAL_NAME}"
        else:
            subject = f"Your Manuscript Has Been Updated - {manuscript_title[:50]}..."
            title_label, field_label, old_label, new_label = "Title", "Field", "Old Value", "New Value"
            ref_label, btn_label = "Reference", "View My Manuscript"
            detail_label = "Manuscript Details"
            change_label = "Changes Made"
            intro = "Your manuscript has been updated by the editorial team."
            sign = f"The {cls.JOURNAL_NAME} Editorial Team"
        
        content = f"""
        <div style="color: #333;">
            <p style="font-size: 18px; margin-bottom: 25px;">{'Bonjour' if is_fr else 'Hello'} <strong>{greeting}</strong>,</p>
            <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px;">{intro}</p>
            </div>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0; border: 1px solid #eee;">
                <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR}; font-size: 16px;">{detail_label}</h3>
                <p style="margin: 8px 0; color: #444; font-size: 14px;"><strong>{title_label} :</strong> {manuscript_title}</p>
                <p style="margin: 8px 0 0 0; color: #444; font-size: 14px;"><strong>{ref_label} :</strong> <span style="color: {cls.PRIMARY_COLOR};">#{manuscript_id}</span></p>
            </div>
            <h3 style="color: {cls.PRIMARY_COLOR}; margin: 30px 0 15px 0; font-size: 16px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">{change_label}</h3>
            <div style="overflow-x: auto; margin: 20px 0 30px 0;">
                <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; font-size: 13px;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                            <th style="padding: 10px 12px; text-align: left; font-weight: 500;">{field_label}</th>
                            <th style="padding: 10px 12px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">{old_label}</th>
                            <th style="padding: 10px 12px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">{new_label}</th>
                        </tr>
                    </thead>
                    <tbody>{changes_html_str}</tbody>
                </table>
            </div>
            <div style="text-align: center; margin: 40px 0 25px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white; text-decoration: none; border-radius: 6px; font-weight: 500; font-size: 14px;">
                    {btn_label}
                </a>
            </div>
            <p style="font-size: 15px; margin-top: 25px;">
                {'Cordialement' if is_fr else 'Best regards'},<br>
                <strong style="color: {cls.PRIMARY_COLOR};">{sign}</strong>
            </p>
        </div>"""
        
        email_body = cls._get_base_template(
            title="Mise à jour de votre manuscrit" if is_fr else "Your Manuscript Has Been Updated",
            content=content
        )
        return cls.send_email(to_email=to_email, subject=subject, body=email_body, is_html=True)

    @classmethod
    def send_autor_manuscript_assigner_a_evaluator(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = 'fr'
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Un évaluateur a été assigné - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Un évaluateur a été assigné à votre manuscrit</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    L'évaluateur a été informé de cette mission. Vous serez notifié(e) dès qu'il aura accepté ou décliné.
                </p>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Suivre mon manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Évaluateur assigné", content)
        else:
            subject = f"An Evaluator Has Been Assigned - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>An Evaluator Has Been Assigned to Your Manuscript</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Track My Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Evaluator Assigned", content)
        
        return cls.send_email(to_email=to_email, subject=subject, body=body, is_html=True)

    @classmethod
    def send_autor_reponse_evalutor_to_assignation(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, accepted: bool, lang: str = 'fr'
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if accepted:
            if is_fr:
                subject = f"Confirmation d'évaluation - {manuscript_title[:50]}..."
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                    <div style="background: linear-gradient(135deg, #e8f5e3 0%, #d4e7d4 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Votre manuscrit est en cours d'évaluation</strong></p>
                    </div>
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>
                    </div>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Suivre mon manuscrit
                        </a>
                    </div>
                    <p style="font-size: 15px; margin-top: 25px;">
                        Cordialement,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                    </p>
                </div>"""
                body = cls._get_base_template("Manuscrit en Évaluation", content)
            else:
                subject = f"Evaluation Confirmation - {manuscript_title[:50]}..."
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                    <div style="background: linear-gradient(135deg, #e8f5e3 0%, #d4e7d4 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Your Manuscript is Under Evaluation</strong></p>
                    </div>
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>
                    </div>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Track My Manuscript
                        </a>
                    </div>
                    <p style="font-size: 15px; margin-top: 25px;">
                        Best regards,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                    </p>
                </div>"""
                body = cls._get_base_template("Manuscript Under Evaluation", content)
        else:
            if is_fr:
                subject = f"Recherche d'évaluateur - {manuscript_title[:50]}..."
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #e65100;"><strong>Recherche d'un nouvel évaluateur</strong></p>
                    </div>
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>
                    </div>
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Notre équipe est actuellement à la recherche d'un nouvel évaluateur qualifié. Vous serez informé(e) dès qu'un nouvel évaluateur aura été assigné.
                    </p>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Voir le statut
                        </a>
                    </div>
                    <p style="font-size: 15px; margin-top: 25px;">
                        Cordialement,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                    </p>
                </div>"""
                body = cls._get_base_template("Recherche d'évaluateur", content)
            else:
                subject = f"Evaluator Search - {manuscript_title[:50]}..."
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #e65100;"><strong>Searching for a New Evaluator</strong></p>
                    </div>
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>
                    </div>
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Our team is searching for a new qualified evaluator. You will be notified as soon as a new evaluator has been assigned.
                    </p>
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            View Status
                        </a>
                    </div>
                    <p style="font-size: 15px; margin-top: 25px;">
                        Best regards,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                    </p>
                </div>"""
                body = cls._get_base_template("Evaluator Search", content)
        
        return cls.send_email(to_email=to_email, subject=subject, body=body, is_html=True)

    @classmethod
    def send_autor_reminder_evalutor(
        cls, to_email: str, author_name: str, manuscript_title: str,
        days_remaining: int, manuscript_id: int = None, lang: str = 'fr'
     ) -> bool:
        is_fr = cls._is_french(lang)
        ref_html = f'<p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">{"Référence" if is_fr else "Reference"} : #{manuscript_id}</p>' if manuscript_id else ''
        btn_html = f'''<div style="text-align: center; margin: 35px 0;">
            <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                {"Voir mon manuscrit" if is_fr else "View My Manuscript"}
            </a>
        </div>''' if manuscript_id else ''
        
        if is_fr:
            subject = f"Rappel envoyé à l'évaluateur - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Rappel envoyé à l'évaluateur</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    {ref_html}
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Il reste environ <strong>{days_remaining} jour(s)</strong> avant la date limite prévue pour l'évaluation.
                </p>
                {btn_html}
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Rappel envoyé à l'évaluateur", content)
        else:
            subject = f"Reminder Sent to Reviewer - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Reminder Sent to Reviewer</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    {ref_html}
                </div>
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    There are approximately <strong>{days_remaining} day(s)</strong> remaining until the evaluation deadline.
                </p>
                {btn_html}
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Reminder Sent to Reviewer", content)
        
        return cls.send_email(to_email=to_email, subject=subject, body=body, is_html=True)

    @classmethod
    def evaluator_send_evauation(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = 'fr'
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Évaluation reçue - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Cher(e) <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Nouvelle évaluation reçue</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                        Voir mon manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Évaluation reçue", content)
        else:
            subject = f"Evaluation Received - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Dear <strong>{author_name}</strong>,</p>
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>New Evaluation Received</strong></p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                        View My Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Evaluation Received", content)
        
        return cls.send_email(to_email=to_email, subject=subject, body=body, is_html=True)

    #============
    # MAIL FOR SYSTEM
    #============

    @classmethod
    def send_system_submitted_docx_file(
        cls, manuscript_id: int, manuscript_title: str,
        author_name: str, author_email: str, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Version DOCX reçue - {manuscript_title[:50]}..."
            title_label, btn_label = "Version DOCX reçue", "Voir le manuscrit"
            intro = "L'auteur a soumis la version DOCX finale de son manuscrit."
            id_label, titre_label, auteur_label = "ID du manuscrit", "Titre", "Auteur"
        else:
            subject = f"DOCX Version Received - {manuscript_title[:50]}..."
            title_label, btn_label = "DOCX Version Received", "View Manuscript"
            intro = "The author has submitted the final DOCX version of their manuscript."
            id_label, titre_label, auteur_label = "Manuscript ID", "Title", "Author"
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};"><strong>{title_label}</strong></p>
            </div>
            <p style="font-size: 15px; margin-bottom: 20px;">{intro}</p>
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">{id_label}</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{titre_label}</td>
                    <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                </tr>
                <tr>
                    <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{auteur_label}</td>
                    <td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td>
                </tr>
            </table>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    {btn_label}
                </a>
            </div>
        </div>"""
        
        body = cls._get_base_template(title_label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_system_new_submission_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, section_name: str, theme_name: str = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        theme_info = f"<strong>{theme_name}</strong>" if theme_name else ("<em>Aucun thème spécifié</em>" if is_fr else "<em>No theme specified</em>")
        
        if is_fr:
            subject = f"Nouvelle soumission - {manuscript_title[:50]}..."
            header_text = "Nouvelle soumission de manuscrit"
            intro = f"Un nouvel article a été soumis sur {cls.JOURNAL_NAME} et nécessite votre attention."
            id_label, titre_label, auteur_label = "ID Manuscrit", "Titre", "Auteur"
            section_label, theme_label = "Section", "Thème"
            btn_label = "Voir le manuscrit"
        else:
            subject = f"New submission - {manuscript_title[:50]}..."
            header_text = "New Manuscript Submission"
            intro = f"A new article has been submitted on {cls.JOURNAL_NAME} and requires your attention."
            id_label, titre_label, auteur_label = "Manuscript ID", "Title", "Author"
            section_label, theme_label = "Section", "Theme"
            btn_label = "View Manuscript"
        
        rows = f"""
        <tr>
            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">{id_label}</td>
            <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
        </tr>
        <tr>
            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{titre_label}</td>
            <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
        </tr>
        <tr>
            <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{auteur_label}</td>
            <td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td>
        </tr>"""
        
        if section_name:
            rows += f"""<tr>
                <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{section_label}</td>
                <td style="padding: 12px; border: 1px solid #ddd;">{section_name}</td>
            </tr>"""
        if theme_name:
            rows += f"""<tr>
                <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{theme_label}</td>
                <td style="padding: 12px; border: 1px solid #ddd;">{theme_info}</td>
            </tr>"""
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};"><strong>{header_text}</strong></p>
            </div>
            <p style="font-size: 15px; margin-bottom: 20px;">{intro}</p>
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">{rows}</table>
            <div style="text-align: center; margin: 35px 0 20px;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 15px; font-weight: 600;">
                    {btn_label}
                </a>
            </div>
        </div>"""
        
        body = cls._get_base_template(header_text, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluation_submitted_notification(
        cls, manuscript_id: int, manuscript_title: str, evaluator_name: str,
        evaluator_email: str, evaluation_decision: str, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        decision_map = {
            "fr": {"accepter": "Accepté", "accepted": "Accepté", "accepted_with_validation": "Accepté avec modifications",
                   "favorable": "Favorable", "refuser": "Refusé", "rejected": "Refusé",
                   "revision": "Révision demandée", "resubmission_required": "Révision demandée",
                   "mineur": "Révision mineure", "majeur": "Révision majeure"},
            "en": {"accepter": "Accepted", "accepted": "Accepted", "accepted_with_validation": "Accepted with modifications",
                   "favorable": "Favorable", "refuser": "Rejected", "rejected": "Rejected",
                   "revision": "Revision requested", "resubmission_required": "Resubmission required",
                   "mineur": "Minor revision", "majeur": "Major revision"}
        }
        
        decision_key = evaluation_decision.lower().strip()
        decision_label = decision_map["fr" if is_fr else "en"].get(decision_key, evaluation_decision)
        decision_color = "#59a498" if decision_key in ["accepter", "accepted", "favorable"] else ("#ffc107" if decision_key in ["revision", "resubmission_required", "mineur", "majeur"] else "#dc3545")
        
        if is_fr:
            subject = f"Évaluation soumise - {manuscript_title[:50]}..."
            header = "Nouvelle évaluation soumise"
            intro = "Un évaluateur a soumis sa grille d'évaluation pour un manuscrit."
            labels = ("Manuscrit", "ID Manuscrit", "Évaluateur", "Décision")
            btn_label = "Voir l'évaluation"
        else:
            subject = f"Evaluation Submitted - {manuscript_title[:50]}..."
            header = "New Evaluation Submitted"
            intro = "An evaluator has submitted their evaluation for a manuscript."
            labels = ("Manuscript", "Manuscript ID", "Evaluator", "Decision")
            btn_label = "View Evaluation"
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};"><strong>{header}</strong></p>
            </div>
            <p style="font-size: 15px; margin-bottom: 20px;">{intro}</p>
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">{labels[0]}</td><td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[1]}</td><td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[2]}</td><td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[3]}</td><td style="padding: 12px; border: 1px solid #ddd; color: {decision_color};"><strong>{decision_label}</strong></td></tr>
            </table>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}/evaluations" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    {btn_label}
                </a>
            </div>
        </div>"""
        
        body = cls._get_base_template(header, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluator_response_notification(
        cls, manuscript_id: int, manuscript_title: str, evaluator_name: str,
        evaluator_email: str, response: str, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        is_accepted = response.lower() in ["accepted", "accepté", "accepter"]
        status_color = "#59a498" if is_accepted else "#dc3545"
        
        if is_fr:
            status_text = "acceptée" if is_accepted else "refusée"
            subject = f"Demande d'évaluation {status_text} - {manuscript_title[:40]}..."
            header = f"Demande d'évaluation {status_text}"
            intro = f"Un évaluateur a <strong>{'accepté' if is_accepted else 'refusé'}</strong> la demande d'évaluation pour un manuscrit."
            labels = ("Manuscrit", "ID Manuscrit", "Évaluateur", "Réponse")
            status_display = "ACCEPTÉE" if is_accepted else "REFUSÉE"
            action_msg = "" if is_accepted else """<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;"><p style="margin: 0; font-size: 14px; color: #856404;"><strong>Action requise :</strong> Vous devrez peut-être assigner un autre évaluateur pour ce manuscrit.</p></div>"""
            btn_label = "Gérer le manuscrit"
        else:
            status_text = "accepted" if is_accepted else "declined"
            status_display = "ACCEPTED" if is_accepted else "DECLINED"
            subject = f"Evaluation Request {status_display.title()} - {manuscript_title[:40]}..."
            header = f"Evaluation Request {status_display.title()}"
            intro = f"An evaluator has <strong>{status_text}</strong> the evaluation request for a manuscript."
            labels = ("Manuscript", "Manuscript ID", "Evaluator", "Response")
            action_msg = "" if is_accepted else """<div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;"><p style="margin: 0; font-size: 14px; color: #856404;"><strong>Action Required:</strong> You may need to assign another evaluator for this manuscript.</p></div>"""
            btn_label = "Manage Manuscript"
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, {'#e8f5f3' if is_accepted else '#fce4e4'} 0%, {'#d4ebe7' if is_accepted else '#f5d4d4'} 100%); border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {status_color};"><strong>{header}</strong></p>
            </div>
            <p style="font-size: 15px; margin-bottom: 20px;">{intro}</p>
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">{labels[0]}</td><td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[1]}</td><td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[2]}</td><td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[3]}</td><td style="padding: 12px; border: 1px solid #ddd;"><strong style="color: {status_color};">{status_display}</strong></td></tr>
            </table>
            {action_msg}
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    {btn_label}
                </a>
            </div>
        </div>"""
        
        body = cls._get_base_template(header, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_manuscript_resubmitted_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, revision_number: int = 1, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Re-soumission - {manuscript_title[:50]}..."
            header = "Manuscrit révisé re-soumis"
            intro = "Un auteur a re-soumis son manuscrit après révision."
            labels = ("ID Manuscrit", "Titre", "Auteur", "Version")
            version_val = f"Révision #{revision_number}"
            action_note = "<strong>Action requise :</strong> Veuillez examiner les modifications apportées par l'auteur."
            btn_label = "Voir le manuscrit révisé"
        else:
            subject = f"Resubmission - {manuscript_title[:50]}..."
            header = "Revised Manuscript Resubmitted"
            intro = "An author has resubmitted their manuscript after revision."
            labels = ("Manuscript ID", "Title", "Author", "Version")
            version_val = f"Revision #{revision_number}"
            action_note = "<strong>Action Required:</strong> Please review the changes made by the author."
            btn_label = "View Revised Manuscript"
        
        content = f"""
        <div style="color: #333;">
            <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};"><strong>{header}</strong></p>
            </div>
            <p style="font-size: 15px; margin-bottom: 20px;">{intro}</p>
            <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">{labels[0]}</td><td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[1]}</td><td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[2]}</td><td style="padding: 12px; border: 1px solid #ddd;">{author_name} ({author_email})</td></tr>
                <tr><td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">{labels[3]}</td><td style="padding: 12px; border: 1px solid #ddd;">{version_val}</td></tr>
            </table>
            <div style="background: #e8f5f3; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; border-radius: 8px; margin: 25px 0;">
                <p style="margin: 0; font-size: 14px; color: {cls.PRIMARY_COLOR_DARK};">{action_note}</p>
            </div>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    {btn_label}
                </a>
            </div>
        </div>"""
        
        body = cls._get_base_template(header, content)
        system_success = cls.send_email(cls.FROM_EMAIL, subject, body)
        
        author_subject, author_body = cls._get_author_resubmission_confirmation(
            manuscript_id=manuscript_id, manuscript_title=manuscript_title,
            author_name=author_name, revision_number=revision_number, is_french=is_fr
        )
        author_success = cls.send_email(to_email=author_email, subject=author_subject, body=author_body)
        
        return system_success and author_success

    @classmethod
    def send_request_evaluation(
        cls, to_email: str, evaluator_name: str, manuscript_title: str,
        manuscript_id: int, assignment_deadline: str = None, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        deadline_info = (f"{'Date limite' if is_fr else 'Deadline'} : {assignment_deadline}") if assignment_deadline else ("Aucune date limite spécifiée" if is_fr else "No deadline specified")
        
        if is_fr:
            subject = f"Nouvelle assignation d'évaluateur - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Bonjour,</p>
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>Nouvelle assignation d'évaluateur</strong><br>L'évaluateur <strong>{evaluator_name}</strong> a été assigné au manuscrit.</p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">ID du manuscrit : {manuscript_id}</p>
                </div>
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;"><strong>Informations :</strong><br>{deadline_info}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir le manuscrit
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe {cls.JOURNAL_NAME}</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Assignation d'Évaluateur", content)
        else:
            subject = f"New Evaluator Assignment - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">Hello,</p>
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;"><strong>New Evaluator Assignment</strong><br>The evaluator <strong>{evaluator_name}</strong> has been assigned to the manuscript.</p>
                </div>
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Manuscript ID: {manuscript_id}</p>
                </div>
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;"><strong>Assignment Information:</strong><br>{deadline_info}</p>
                </div>
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Manuscript
                    </a>
                </div>
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The {cls.JOURNAL_NAME} Team</strong>
                </p>
            </div>"""
            body = cls._get_base_template("Evaluator Assignment", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_updated_system_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, editor_name: str, changes: dict, lang: str = "fr"
     ) -> bool:
        is_fr = cls._is_french(lang)
        
        changes_html = []
        for field, (old_val, new_val) in changes.items():
            changes_html.append(f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 25%; color: #555; font-weight: 500;">{field}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 35%; color: #e74c3c; text-decoration: line-through;">{old_val or ('Non spécifié' if is_fr else 'Not specified')}</td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 40%; color: #27ae60; font-weight: 500;">{new_val or ('Non spécifié' if is_fr else 'Not specified')}</td>
            </tr>""")
        changes_html_str = "\n".join(changes_html)
        
        if is_fr:
            subject = f"Manuscrit mis à jour - {manuscript_title[:50]}..."
            title_h = "Mise à jour d'un manuscrit"
            by_label = f"Mise à jour effectuée par : <span style='color: {cls.PRIMARY_COLOR};'>{editor_name}</span>"
            detail_h = "Détails du manuscrit"
            id_l, title_l, author_l = "ID", "Titre", "Auteur"
            change_h = "Modifications effectuées"
            field_l, old_l, new_l = "Champ", "Ancienne valeur", "Nouvelle valeur"
            btn_l = "Voir le manuscrit"
        else:
            subject = f"Manuscript Updated - {manuscript_title[:50]}..."
            title_h = "Manuscript Update"
            by_label = f"Updated by: <span style='color: {cls.PRIMARY_COLOR};'>{editor_name}</span>"
            detail_h = "Manuscript Details"
            id_l, title_l, author_l = "ID", "Title", "Author"
            change_h = "Changes Made"
            field_l, old_l, new_l = "Field", "Old Value", "New Value"
            btn_l = "View Manuscript"
        
        content = f"""
        <div style="color: #333;">
            <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px;">{by_label}</p>
            </div>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                <h3 style="margin-top: 0; color: {cls.PRIMARY_COLOR};">{detail_h}</h3>
                <p style="margin: 10px 0;"><strong>{id_l}:</strong> {manuscript_id}</p>
                <p style="margin: 10px 0;"><strong>{title_l}:</strong> {manuscript_title}</p>
                <p style="margin: 10px 0 0 0;"><strong>{author_l}:</strong> {author_name} &lt;{author_email}&gt;</p>
            </div>
            <h3 style="color: {cls.PRIMARY_COLOR}; margin-top: 30px; font-size: 18px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">{change_h}</h3>
            <div style="overflow-x: auto; margin: 20px 0 30px 0;">
                <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                    <thead>
                        <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                            <th style="padding: 12px 15px; text-align: left; font-weight: 500;">{field_l}</th>
                            <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">{old_l}</th>
                            <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">{new_l}</th>
                        </tr>
                    </thead>
                    <tbody>{changes_html_str}</tbody>
                </table>
            </div>
            <div style="text-align: center; margin: 40px 0 20px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white; text-decoration: none; border-radius: 30px; font-weight: 600; font-size: 15px;">
                    {btn_l}
                </a>
            </div>
        </div>"""
        
        full_body = cls._get_base_template(title_h, content)
        return cls.send_email(cls.FROM_EMAIL, subject, full_body)