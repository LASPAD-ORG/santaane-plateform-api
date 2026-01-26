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
    
    # Constantes
    DEFAULT_LANGUAGE = 'fr'  # Langue par défaut pour les emails
    
    # Configuration SMTP
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
                logger.error(f"Erreur lors de l'envoi de l'email à l'auteur: {str(smtp_error)}")
                author_success = False
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
        """
        Vérifie si la langue est le français
        
        Args:
            lang: Code de langue (ex: 'fr', 'en'). Si None, utilise la langue par défaut.
            
        Returns:
            bool: True si la langue est le français, False sinon
        """
        if not lang:
            return cls.DEFAULT_LANGUAGE.startswith('fr')
        return str(lang).lower().startswith('fr')

    #====================================
    # EMAILS NOTIFICATIONS VERIFICATION AVEC OTP
    #====================================
    
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
            <p staccyle="color: #666; font-size: 14px; margin-top: 25px;">
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


    #====================================
    # EMAILS NOTIFICATIONS WELCOME
    #====================================
    @classmethod
    def send_new_user_credentials(cls, to_email: str, full_name: str, password: str, roles: str) -> bool:
        """
        Send welcome email with login credentials for new users
        
        Args:
            to_email: Recipient email
            full_name: User's full name
            password: User's plain text password
            roles: User roles (e.g., ADMIN, EDITOR, EVALUATOR, AUTHOR etc.)
        
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
                    <strong>Rôle(s) :</strong><br>
                    <span style="color: #59a498; font-family: monospace; font-size: 16px;">{roles}</span>
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
    def send_inactive_user(cls, to_email: str, full_name: str, admin_name: str = None, admin_email: str = None) -> bool:
        """
        Envoie une notification email quand un utilisateur est supprimé (soft delete)
        
        Args:
            to_email: Email de l'utilisateur supprimé
            full_name: Nom complet de l'utilisateur supprimé
            admin_name: Nom de l'admin qui a fait la suppression (optionnel)
            admin_email: Email de l'admin qui a fait la suppression (optionnel)
            
        Returns:
            bool: True si envoyé avec succès
        """
        subject = "Votre compte a été désactivé - Santaane Platform"
        
        admin_info = f"par l'administrateur <strong>{admin_name}</strong>" if admin_name else "par un administrateur"
        
        # Contact information for the admin
        contact_info = ""
        if admin_email:
            contact_info = f"veuillez contacter l'administrateur à l'adresse : <strong>{admin_email}</strong>"
        else:
            contact_info = "veuillez contacter l'administrateur de la plateforme"
        
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
                Votre compte sur la plateforme Santaane a été désactivé. Vous ne pourrez plus vous connecter avec vos identifiants actuels.
            </p>
            
            <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                Si vous pensez qu'il s'agit d'une erreur ou si vous avez des questions, 
                {contact_info}.
            </p>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Désactivation de votre compte", content)
        return cls.send_email(to_email, subject, body)

    @classmethod 
    def send_User_update(cls, to_email: str, full_name: str, updated_fields: dict = None, admin_name: str = None) -> bool:
        """
        Envoie une notification email quand un admin modifie un utilisateur
        
        Args:
            to_email: Email de l'utilisateur modifié
            full_name: Nom complet de l'utilisateur modifié
            updated_fields: Dictionnaire des champs modifiés (optionnel)
            admin_name: Nom de l'admin qui a fait la modification (optionnel)
            
        Returns:
            bool: True si envoyé avec succès
        """
        
        logger.info(f"send_User_update called: to_email={to_email}, updated_fields={updated_fields}, admin_name={admin_name}")
        
        # Personnaliser le sujet selon le type de modification
        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            if field_name == 'password':
                subject = "Votre mot de passe a été réinitialisé - Santaane Platform"
            elif field_name == 'is_active':
                subject = "Le statut de votre compte a été modifié - Santaane Platform"
            elif field_name == 'roles':
                subject = "Vos rôles ont été modifiés - Santaane Platform"
            else:
                subject = f"Votre {cls._get_field_display_name(field_name)} a été mis à jour - Santaane Platform"
        else:
            subject = "Votre profil a été mis à jour - Santaane Platform"
        
        # Construire le contenu des modifications si disponible
        changes_content = ""
        if updated_fields:
            # Si un seul champ, utiliser un message plus direct
            if len(updated_fields) == 1:
                field_name = list(updated_fields.keys())[0]
                field_display = cls._get_field_display_name(field_name)
                
                if field_name == 'password':
                    # Get the password value
                    password_value = list(updated_fields.values())[0]
                    # Check if it's the actual password or just a reset notification
                    if isinstance(password_value, str) and password_value != 'reset':
                        # It's the actual new password
                        changes_content = """
                        <div style="background: #e8f5f3; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <p style="margin: 0; font-size: 16px; color: #2e7d32; text-align: center;">
                                <strong>🔐 Votre mot de passe a été réinitialisé</strong><br>
                                <span style="font-size: 14px;">Voici votre nouveau mot de passe :</span>
                            </p>
                            <div style="background: #f8f9fa; border: 2px dashed #59a498; padding: 15px; margin: 15px 0; border-radius: 8px; text-align: center;">
                                <span style="font-family: monospace; font-size: 18px; font-weight: bold; color: #59a498; letter-spacing: 2px;">
                                """ + password_value + """
                                </span>
                            </div>
                            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666; text-align: center;">
                                <strong>Important :</strong> Veuillez changer ce mot de passe dès votre première connexion pour votre sécurité.
                            </p>
                        </div>
                        """
                    else:
                        # It's just a reset notification without the actual password
                        changes_content = """
                        <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 8px; margin: 25px 0;">
                            <p style="margin: 0; font-size: 16px; color: #856404; text-align: center;">
                                <strong>🔒 Votre mot de passe a été réinitialisé</strong><br>
                                <span style="font-size: 14px;">Pour votre sécurité, le nouveau mot de passe ne vous sera pas communiqué par email.</span>
                            </p>
                        </div>
                        """
                elif field_name == 'is_active':
                    is_active = list(updated_fields.values())[0]
                    status_text = "activé" if is_active else "désactivé"
                    status_color = "#28a745" if is_active else "#dc3545"
                    changes_content = f"""
                    <div style="background: {'#d4edda' if is_active else '#f8d7da'}; border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: {'#155724' if is_active else '#721c24'}; text-align: center;">
                            <strong>Votre compte a été {status_text}</strong>
                        </p>
                    </div>
                    """
                elif field_name == 'roles':
                    roles = list(updated_fields.values())[0]
                    if isinstance(roles, (list, tuple)):
                        roles_text = ", ".join(str(r) for r in roles) if roles else "Aucun rôle"
                    else:
                        roles_text = str(roles) if roles else "Non défini"
                    changes_content = f"""
                    <div style="background: #e8f5f3; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                            <strong>Vos nouveaux rôles :</strong><br>
                            <span style="font-size: 14px; color: #555;">{roles_text}</span>
                        </p>
                    </div>
                    """
                else:
                    value = list(updated_fields.values())[0]
                    value_str = str(value) if value is not None else "Non défini"
                    changes_content = f"""
                    <div style="background: #f8f9fa; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; font-size: 16px; color: #59a498;">
                            <strong>{field_display} :</strong><br>
                            <span style="font-size: 14px; color: #555;">{value_str}</span>
                        </p>
                    </div>
                    """
            else:
                # Plusieurs champs modifiés - afficher la liste
                changes_content = """
                <div style="background: #f8f9fa; border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #59a498; font-size: 16px;">Modifications apportées :</h3>
                    <ul style="margin: 0; padding-left: 20px; font-size: 14px; color: #555;">
                """
                
                for field, value in updated_fields.items():
                    field_name = cls._get_field_display_name(field)
                    if field == 'is_active':
                        value_str = "Activé" if value else "Désactivé"
                    elif field == 'password':
                        # Check if it's the actual password or just a reset notification
                        if isinstance(value, str) and value != 'reset':
                            value_str = f"🔐 Nouveau mot de passe : {value}"
                        else:
                            value_str = "🔒 Modifié (pour votre sécurité)"
                    elif field == 'roles':
                        if isinstance(value, (list, tuple)):
                            value_str = ", ".join(str(r) for r in value) if value else "Aucun rôle"
                        else:
                            value_str = str(value) if value else "Non défini"
                    else:
                        value_str = str(value) if value is not None else "Non défini"
                    changes_content += f"<li><strong>{field_name}</strong> : {value_str}</li>"
                
                changes_content += "</ul></div>"
        
        admin_info = f"par l'administrateur <strong>{admin_name}</strong>" if admin_name else "par un administrateur"
        
        # Personnaliser le message principal selon le type de modification
        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            if field_name == 'password':
                main_message = f"Votre mot de passe a été réinitialisé {admin_info}."
            elif field_name == 'is_active':
                is_active = list(updated_fields.values())[0]
                status_text = "activé" if is_active else "désactivé"
                main_message = f"Votre compte a été {status_text} {admin_info}."
            elif field_name == 'roles':
                main_message = f"Vos rôles ont été modifiés {admin_info}."
            else:
                field_display = cls._get_field_display_name(field_name)
                main_message = f"Votre {field_display} a été mis à jour {admin_info}."
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
                <a href="{cls.PLATFORM_URL}/login" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #59a498 0%, #4a8a7f 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                    Se connecter à mon compte
                </a>
            </div>
            
            <p style="font-size: 15px; margin-top: 25px;">
                Cordialement,<br>
                <strong style="color: {cls.PRIMARY_COLOR};">L'équipe Santaane Platform</strong>
            </p>
        </div>
        """
        
        body = cls._get_base_template("Mise à jour de votre profil", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def _get_field_display_name(cls, field_name: str) -> str:
        """Retourne le nom d'affichage français pour un champ"""
        field_mapping = {
            'email': 'email',
            'full_name': 'nom complet',
            'profile_photo': 'photo de profil',
            'orcid_id': 'ORCID ID',
            'bio': 'biographie',
            'position': 'position',
            'institution': 'institution',
            'is_active': 'statut du compte',
            'password': 'mot de passe',
            'roles': 'rôles'
        }
        return field_mapping.get(field_name, field_name)

    @classmethod
    def send_author_submission_confirmation_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        submission_date: str,
        lang: str = "fr"
     ) -> bool:
        """
        Envoie un email de confirmation à l'auteur après soumission de son manuscrit
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            submission_date: Date de soumission formatée (JJ/MM/AAAA)
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
                <p style="font-size: 18px; margin-bottom: 25prx;">
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
                        <strong>Reference:</strong> #{manuscript_id}<br>
                        <strong>Submission date:</strong> {submission_date}
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

    
    @classmethod
    def send_manuscript_accepted_email(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        custom_message: Optional[str] = None,
        lang: str = "fr"
     ) -> bool:
        """
        Envoie un email à l'auteur quand son manuscrit est accepté
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            custom_message: Message personnalisé optionnel de l'éditeur
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = f"Votre manuscrit est accepté pour la publication - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Bonne nouvelle !</strong> Votre manuscrit a été accepté pour la publication dans la revue Global Africa.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons le plaisir de vous informer que votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    a été accepté pour publication dans la revue <strong>Global Africa</strong>.
                </p>
                """
            
            # Ajouter le commentaire personnalisé s'il existe
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Message de l'éditeur :</strong><br>
                        {custom_message}
                    </p>
                </div>
                """
            
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
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Manuscrit Accepté", content)
        else:
            subject = f"Manuscript Accepted and Under Evaluation - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Great news!</strong> Your manuscript has been accepted and is currently under evaluation.
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
                """
            
            # Ajouter le commentaire personnalisé s'il existe
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Editor's Message:</strong><br>
                        {custom_message}
                    </p>
                </div>
                """
            
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
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Manuscript Accepted and Under Evaluation", content)
        
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
        
        logger.info(f"Rejection reason received: {rejection_reason}")
        
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
        custom_message: Optional[str] = None,
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
            custom_message: Message personnalisé optionnel de l'éditeur
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
                """
            
            # Ajouter le commentaire personnalisé s'il existe
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Message de l'éditeur :</strong><br>
                        {custom_message}
                    </p>
                </div>
                """
            
            content += f"""
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Vous pouvez partager ce lien avec vos collègues et sur vos réseaux professionnels :
                </p>
                
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
                """
            
            # Ajouter le commentaire personnalisé s'il existe
            if custom_message and custom_message.strip():
                content += f"""
                <div style="background: #f0f8ff; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 15px; color: #333;">
                        <strong>Editor's Message:</strong><br>
                        {custom_message}
                    </p>
                </div>
                """
            
            content += f"""
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    You can share this link with your colleagues and on your professional networks:
                </p>
                
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
            revision_comments: Commentaires de l'éditeur (optionnel)
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
                    <h4 style="margin: 0 0 10px 0; color: #ff9800;">Commentaires de l'éditeur :</h4>
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
                    Veuillez prendre en compte les commentaires de l'éditeur et soumettre une version révisée de votre manuscrit.
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
                    <h4 style="margin: 0 0 10px 0; color: #ff9800;">Editor's Comments:</h4>
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
                    Please address the editor's comments and submit a revised version of your manuscript.
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

    @classmethod
    def send_auteur_confirmation_docx_file(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        lang: str = "fr"
     ) -> bool:
        """
        Envoie un email de confirmation à l'auteur après dépôt de la version DOCX finale.
        
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
        greeting_name = (
            author_name.split()[0]
            if author_name and author_name.strip()
            else ("Auteur" if is_fr else "Author")
        )

        if is_fr:
            subject = f"Confirmation de réception de la version finale - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{greeting_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Votre version finale a bien été reçue !</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous accusons réception de la version finale de votre manuscrit :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Votre document a été enregistré avec succès et sera traité par notre équipe pour la publication.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir mon manuscrit
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

            body = cls._get_base_template("Version finale reçue", content)
        else:
            subject = f"Final Version Received - {manuscript_title[:50]}..."

            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{greeting_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Your final version has been received!</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We acknowledge receipt of the final version of your manuscript:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Your document has been successfully recorded and will be processed by our team for publication.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View My Manuscript
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for your trust and contribution to scientific research.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Global Africa Editorial Team</strong>
                </p>
            </div>
            """

            body = cls._get_base_template("Final Version Received", content)

        return cls.send_email(to_email, subject, body)

    @classmethod
    def _get_author_resubmission_confirmation(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        author_name: str,
        revision_number: int,
        is_french: bool
     ) -> tuple[str, str]:
        """Génère le contenu de l'email de confirmation pour l'auteur"""
        if is_french:
            subject = f"Confirmation de re-soumission - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name.split()[0]}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Votre manuscrit a bien été re-soumis !</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous accusons réception de la re-soumission de votre manuscrit intitulé :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id} | Version : Révision #{revision_number}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Votre manuscrit a été enregistré avec succès et sera examiné par notre comité éditorial dans les meilleurs délais.
                </p>
                
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
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Merci pour votre confiance et votre contribution à la recherche scientifique.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                    Cet email est une confirmation automatique, merci de ne pas y répondre directement.
                </p>
            </div>
            """.format(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript_title,
                author_name=author_name.split()[0],  # Juste le prénom
                revision_number=revision_number,
                **cls.__dict__
            )
            
            body = cls._get_base_template("Confirmation de re-soumission", content)
        else:
            subject = f"Resubmission Confirmation - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name.split()[0]}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Your manuscript has been successfully resubmitted!</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have received the resubmission of your manuscript titled:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id} | Version: Revision #{revision_number}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Your manuscript has been successfully recorded and will be reviewed by our editorial team as soon as possible.
                </p>
                
                <h4 style="color: {cls.PRIMARY_COLOR}; margin-top: 25px; margin-bottom: 15px;">Next Steps:</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #555; padding-left: 20px;">
                    <li>Review of changes by the editorial team</li>
                    <li>Additional evaluation if needed</li>
                    <li>Final editorial decision</li>
                </ul>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Track My Manuscript
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for your trust and contribution to scientific research.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Global Africa Editorial Team</strong>
                </p>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                    This is an automated email, please do not reply directly.
                </p>
            </div>
            """.format(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript_title,
                author_name=author_name.split()[0],  # Just first name
                revision_number=revision_number,
                **cls.__dict__
            )
            
            body = cls._get_base_template("Resubmission Confirmation", content)
            
        return subject, body


    @classmethod
    def send_manuscript_updated_author_notification(
        cls,
        to_email: str,
        author_name: str,
        manuscript_id: int,
        manuscript_title: str,
        changes: dict,
        lang: str = "fr"
            ) -> bool:
            """Envoie une notification à l'auteur lorsqu'un manuscrit est mis à jour par le staff"""
            is_fr = cls._is_french(lang)
            
            # Formater les changements en HTML
            changes_html = []
            for field, (old_val, new_val) in changes.items():
                changes_html.append(f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 25%; color: #555; font-weight: 500;">
                        {field}
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 35%; color: #e74c3c; text-decoration: line-through;">
                        {old_val or ('Non spécifié' if is_fr else 'Not specified')}
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 40%; color: #27ae60; font-weight: 500;">
                        {new_val or ('Non spécifié' if is_fr else 'Not specified')}
                    </td>
                </tr>
                """)
            
            changes_html = "\n".join(changes_html)
            
            if is_fr:
                greeting = author_name.split(' ')[0] if author_name and ' ' in author_name else author_name or 'Cher auteur'
                subject = f"Votre manuscrit a été mis à jour - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="padding: 30px; background: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    <p style="font-size: 18px; margin-bottom: 25px; color: #333;">
                        Bonjour <strong>{greeting}</strong>,
                    </p>
                    
                    <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; 
                                padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                        <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px; line-height: 1.5;">
                            Votre manuscrit a été mis à jour par l'équipe éditoriale.
                        </p>
                    </div>
                    
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0; border: 1px solid #eee;">
                        <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR}; font-size: 16px;">Détails du manuscrit</h3>
                        <p style="margin: 8px 0; color: #444; font-size: 14px;">
                            <strong style="color: #555;">Titre :</strong> {manuscript_title}
                        </p>
                        <p style="margin: 8px 0 0 0; color: #444; font-size: 14px;">
                            <strong style="color: #555;">Référence :</strong> <span style="color: {cls.PRIMARY_COLOR};">#{manuscript_id}</span>
                        </p>
                    </div>
                    
                    <h3 style="color: {cls.PRIMARY_COLOR}; margin: 30px 0 15px 0; font-size: 16px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">
                        Modifications effectuées
                    </h3>
                    
                    <div style="overflow-x: auto; margin: 20px 0 30px 0; font-size: 14px;">
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; font-size: 13px;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px;">Champ</th>
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px; border-left: 1px solid rgba(255,255,255,0.2);">Ancienne valeur</th>
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px; border-left: 1px solid rgba(255,255,255,0.2);">Nouvelle valeur</th>
                                </tr>
                            </thead>
                            <tbody>
                                {changes_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0 25px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" 
                        style="display: inline-block; padding: 12px 30px; 
                                background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                                color: white; text-decoration: none; 
                                border-radius: 6px; font-weight: 500; font-size: 14px;
                                box-shadow: 0 2px 8px rgba({int(cls.PRIMARY_COLOR[1:3], 16)}, {int(cls.PRIMARY_COLOR[3:5], 16)}, {int(cls.PRIMARY_COLOR[5:7], 16)}, 0.2);
                                transition: all 0.2s ease;">
                            Voir mon manuscrit
                        </a>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #f0f0f0; color: #666; font-size: 14px; line-height: 1.6;">
                        <p style="margin: 0 0 15px 0; line-height: 1.6;">
                            Si vous avez des questions concernant ces modifications, n'hésitez pas à répondre à cet email.
                        </p>
                        
                        <p style="margin: 20px 0 0 0; padding-top: 15px; color: #555; font-size: 14px; line-height: 1.6;">
                            Merci de contribuer à la recherche scientifique africaine.
                        </p>
                        
                        <p style="margin: 10px 0 0 0; color: #555; font-weight: 500;">
                            Cordialement,<br>
                            <span style="color: #59a498; font-weight: 600;">L'équipe éditoriale de Global Africa</span>
                        </p>
                    </div>
                </div>
                """
                
                email_body = cls._get_base_template(
                    title="Mise à jour de votre manuscrit",
                    content=content
                )
                
                return cls.send_email(
                    to_email=to_email,
                    subject=subject,
                    body=email_body,
                    is_html=True
                )


            else:
            # Version anglaise
                greeting = author_name.split(' ')[0] if author_name and ' ' in author_name else author_name or 'Author'
                subject = f" Your Manuscript Has Been Updated - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="padding: 30px; background: #ffffff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
                    <p style="font-size: 18px; margin-bottom: 25px; color: #333;">
                        Hello <strong>{greeting}</strong>,
                    </p>
                    
                    <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; 
                                padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                        <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px; line-height: 1.5;">
                            Your manuscript has been updated by the editorial team.
                        </p>
                    </div>
                    
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0; border: 1px solid #eee;">
                        <h3 style="margin: 0 0 15px 0; color: {cls.PRIMARY_COLOR}; font-size: 16px;">Manuscript Details</h3>
                        <p style="margin: 8px 0; color: #444; font-size: 14px;">
                            <strong style="color: #555;">Title:</strong> {manuscript_title}
                        </p>
                        <p style="margin: 8px 0 0 0; color: #444; font-size: 14px;">
                            <strong style="color: #555;">Reference:</strong> <span style="color: {cls.PRIMARY_COLOR};">#{manuscript_id}</span>
                        </p>
                    </div>
                    
                    <h3 style="color: {cls.PRIMARY_COLOR}; margin: 30px 0 15px 0; font-size: 16px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0;">
                        Changes Made
                    </h3>
                    
                    <div style="overflow-x: auto; margin: 20px 0 30px 0; font-size: 14px;">
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 6px; overflow: hidden; font-size: 13px;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px;">Field</th>
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px; border-left: 1px solid rgba(255,255,255,0.2);">Old Value</th>
                                    <th style="padding: 10px 12px; text-align: left; font-weight: 500; font-size: 13px; border-left: 1px solid rgba(255,255,255,0.2);">New Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {changes_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0 25px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" 
                        style="display: inline-block; padding: 12px 30px; 
                                background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                                color: white; text-decoration: none; 
                                border-radius: 6px; font-weight: 500; font-size: 14px;
                                box-shadow: 0 2px 8px rgba({int(cls.PRIMARY_COLOR[1:3], 16)}, {int(cls.PRIMARY_COLOR[3:5], 16)}, {int(cls.PRIMARY_COLOR[5:7], 16)}, 0.2);
                                transition: all 0.2s ease;">
                            View My Manuscript
                        </a>
                    </div>
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #f0f0f0; color: #666; font-size: 14px; line-height: 1.6;">
                        <p style="margin: 0 0 15px 0; line-height: 1.6;">
                            If you have any questions about these changes, please feel free to reply to this email.
                        </p>
                        
                        <p style="margin: 20px 0 0 0; padding-top: 15px; color: #555; font-size: 14px; line-height: 1.6;">
                            Thank you for contributing to African scientific research.
                        </p>
                        
                        <p style="margin: 10px 0 0 0; color: #555; font-weight: 500;">
                            Best regards,<br>
                            <span style="color: #59a498; font-weight: 600;">The Editorial Team of Global Africa</span>
                        </p>
                    </div>
                </div>
                """
                
                email_body = cls._get_base_template(
                    title="Your Manuscript Has Been Updated",
                    content=content
                )
        
            return cls.send_email(
                to_email=to_email,
                subject=subject,
                body=email_body,
                is_html=True
            )
  


    @classmethod
    def send_autor_manuscript_assigner_a_evaluator(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        lang: str = 'fr'
     ) -> bool:
        """
        Envoie une notification à l'auteur lorsqu'un évaluateur est assigné à son manuscrit
        
        Args:
            to_email: Email de l'auteur
            author_name: Nom complet de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            lang: Code de langue (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Un évaluateur a été assigné - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Un évaluateur a été assigné à votre manuscrit</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous vous informons qu'un évaluateur a été assigné à votre manuscrit :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    L'évaluateur a été informé de cette mission d'évaluation. 
                    Vous serez notifié(e) dès qu'il aura accepté ou décliné cette mission.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Le processus d'évaluation est une étape importante pour assurer la qualité des publications.
                    Nous vous remercions de votre confiance et de votre patience.
                </p>
                
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
            
            body = cls._get_base_template("Évaluateur assigné", content)
            
        else:
            subject = f"An Evaluator Has Been Assigned - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>An Evaluator Has Been Assigned to Your Manuscript</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We would like to inform you that an evaluator has been assigned to your manuscript:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    The evaluator has been notified of this evaluation assignment.
                    You will be notified as soon as they accept or decline this evaluation.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    The evaluation process is an important step to ensure the quality of publications.
                    We thank you for your trust and patience.
                </p>
                
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
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team at Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Evaluator Assigned", content)
        
        return cls.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=True
        )
        
    @classmethod
    def send_autor_reponse_evalutor_to_assignation(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        accepted: bool,
        lang: str = 'fr'
     ) -> bool:
        """
        Envoie une notification à l'auteur lorsqu'un évaluateur répond à une assignation
        
        Args:
            to_email: Email de l'auteur
            author_name: Nom complet de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            accepted: True si l'évaluateur a accepté, False s'il a refusé
            lang: Code de langue (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        is_fr = cls._is_french(lang)
        
        if accepted:
            if is_fr:
                subject = f"Confirmation d'évaluation - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">
                        Cher(e) <strong>{author_name}</strong>,
                    </p>
                    
                    <div style="background: linear-gradient(135deg, #e8f5e3 0%, #d4e7d4 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                            <strong>Votre manuscrit est en cours d'évaluation</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Nous avons le plaisir de vous informer que votre manuscrit est actuellement en cours d'évaluation par nos experts :
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                            Référence : #{manuscript_id}
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Le processus d'évaluation par les pairs est en cours et nous vous tiendrons informé(e) dès que nous aurons les résultats.
                        Cette étape est essentielle pour maintenir la qualité et l'excellence des publications dans notre revue.
                    </p>
                    
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Suivre mon manuscrit
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Nous vous remercions pour votre patience et votre compréhension.
                    </p>
                    
                    <p style="font-size: 15px; margin-top: 25px;">
                        Cordialement,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                    </p>
                </div>
                """
                
                body = cls._get_base_template("Manuscrit en Évaluation", content)
                
            else:
                subject = f"Evaluation Confirmation - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">
                        Dear <strong>{author_name}</strong>,
                    </p>
                    
                    <div style="background: linear-gradient(135deg, #e8f5e3 0%, #d4e7d4 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                            <strong>Your Manuscript is Under Evaluation</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        We are pleased to inform you that your manuscript is currently under evaluation by our experts:
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                            Reference: #{manuscript_id}
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        The peer review process is in progress, and we will keep you informed as soon as we have the results.
                        This step is essential to maintain the quality and excellence of publications in our journal.
                    </p>
                    
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Track My Manuscript
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Thank you for your patience and understanding.
                    </p>
                    
                    <p style="font-size: 15px; margin-top: 25px;">
                        Best regards,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                    </p>
                </div>
                """
                
                body = cls._get_base_template("Manuscript Under Evaluation", content)
                
        else:
            if is_fr:
                subject = f"Recherche d'évaluateur - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">
                        Cher(e) <strong>{author_name}</strong>,
                    </p>
                    
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #e65100;">
                            <strong>Recherche d'un nouvel évaluateur</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        L'évaluateur précédemment assigné à votre manuscrit n'a malheureusement pas pu accepter la mission d'évaluation.
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                            Référence : #{manuscript_id}
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Notre équipe est actuellement à la recherche d'un nouvel évaluateur qualifié pour votre manuscrit.
                        Nous faisons de notre mieux pour accélérer ce processus tout en maintenant nos standards de qualité.
                    </p>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Vous serez informé(e) dès qu'un nouvel évaluateur aura été assigné à votre manuscrit.
                    </p>
                    
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            Voir le statut
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Nous vous remercions pour votre compréhension et votre patience.
                    </p>
                    
                    <p style="font-size: 15px; margin-top: 25px;">
                        Cordialement,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                    </p>
                </div>
                """
                
                body = cls._get_base_template("Recherche d'évaluateur", content)
                
            else:
                subject = f"Evaluator Search - {manuscript_title[:50]}..."
                
                content = f"""
                <div style="color: #333;">
                    <p style="font-size: 18px; margin-bottom: 25px;">
                        Dear <strong>{author_name}</strong>,
                    </p>
                    
                    <div style="background: #fff3e0; border-left: 4px solid #ff9800; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                        <p style="margin: 0; font-size: 16px; color: #e65100;">
                            <strong>Searching for a New Evaluator</strong>
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        The evaluator previously assigned to your manuscript was unfortunately unable to accept the evaluation assignment.
                    </p>
                    
                    <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                        <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                            Reference: #{manuscript_id}
                        </p>
                    </div>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        Our team is currently searching for a new qualified evaluator for your manuscript.
                        We are making every effort to expedite this process while maintaining our quality standards.
                    </p>
                    
                    <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                        You will be notified as soon as a new evaluator has been assigned to your manuscript.
                    </p>
                    
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                            View Status
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Thank you for your understanding and patience.
                    </p>
                    
                    <p style="font-size: 15px; margin-top: 25px;">
                        Best regards,<br>
                        <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team of Global Africa</strong>
                    </p>
                </div>
                """
                
                body = cls._get_base_template("Evaluator Search", content)
        
        return cls.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=True
        )
    
    @classmethod
    def send_autor_reminder_evalutor(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        days_remaining: int,
        manuscript_id: int = None,
        lang: str = 'fr'
     ) -> bool:
        """
        Envoie une notification à l'auteur pour l'informer qu'un rappel a été envoyé à l'évaluateur
        
        Args:
            to_email: Email du destinataire
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            days_remaining: Nombre de jours restants avant la date limite d'évaluation
            manuscript_id: ID du manuscrit (optionnel)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Rappel envoyé à l'évaluateur - {manuscript_title[:50]}..."
            
            # Préparation du contenu conditionnel pour l'ID du manuscrit
            ref_html = f'<p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Référence : #{manuscript_id}</p>' if manuscript_id else ''
            button_html = f'''
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                    Voir mon manuscrit
                </a>
            </div>''' if manuscript_id else ''
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Rappel envoyé à l'évaluateur</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous vous informons qu'un rappel a été envoyé à l'évaluateur concernant votre manuscrit :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    {ref_html}
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous avons contacté l'évaluateur pour accélérer le processus d'évaluation. 
                    Il reste environ <strong>{days_remaining} jour(s)</strong> avant la date limite prévue pour l'évaluation.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous vous tiendrons informé(e) dès que nous aurons une mise à jour concernant l'évaluation de votre manuscrit.
                </p>
                
                {button_html}
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Merci pour votre patience et votre compréhension.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Rappel envoyé à l'évaluateur", content)
            
        else:
            subject = f"Reminder Sent to Reviewer - {manuscript_title[:50]}..."
            
            # Préparation du contenu conditionnel pour l'ID du manuscrit (version anglaise)
            ref_html = f'<p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">Reference: #{manuscript_id}</p>' if manuscript_id else ''
            button_html = f'''
            <div style="text-align: center; margin: 35px 0;">
                <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                    View My Manuscript
                </a>
            </div>''' if manuscript_id else ''
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Reminder Sent to Reviewer</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We would like to inform you that a reminder has been sent to the reviewer regarding your manuscript:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    {ref_html}
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We have contacted the reviewer to expedite the evaluation process. 
                    There are approximately <strong>{days_remaining} day(s)</strong> remaining until the evaluation deadline.
                </p>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We will keep you updated as soon as we have any news regarding the evaluation of your manuscript.
                </p>
                
                {button_html}
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Thank you for your patience and understanding.
                </p>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team at Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Reminder Sent to Reviewer", content)
        
        # Envoi de l'email
        return cls.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=True
        )
 
    @classmethod
    def evaluator_send_evauation(
        cls,
        to_email: str,
        author_name: str,
        manuscript_title: str,
        manuscript_id: int,
        lang: str = 'fr'
     ) -> bool:
        """
        Envoie une notification à l'auteur lorsqu'un évaluateur a soumis son évaluation.
        
        Args:
            to_email: Email de l'auteur
            author_name: Nom de l'auteur
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            evaluator_name: Nom de l'évaluateur
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Évaluation reçue - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Cher(e) <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Nouvelle évaluation reçue</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Nous vous informons qu'un évaluateur a soumis son évaluation pour votre manuscrit :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Référence : #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    Vous pouvez consulter les détails de l'évaluation dans votre espace auteur.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                        Voir mon manuscrit
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe éditoriale de Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Évaluation reçue", content)
            
        else:
            subject = f"Evaluation Received - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Dear <strong>{author_name}</strong>,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>New Evaluation Received</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    We would like to inform you that an evaluator has submitted their evaluation for your manuscript:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Reference: #{manuscript_id}
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    You can view the evaluation details in your author dashboard.
                </p>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 15px; font-weight: 500;">
                        View My Manuscript
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Editorial Team at Global Africa</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Evaluation Received", content)
        
        return cls.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            is_html=True
        )

    #============
    # MAIL FOR SYTEM
    # ===========    

    @classmethod
    def send_system_submitted_docx_file(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        author_name: str,
        author_email: str,
        lang: str = "fr"
     ) -> bool:
        """
        Envoie une notification au système lorsqu'un auteur dépose la version DOCX finale.
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            author_name: Nom de l'auteur
            author_email: Email de l'auteur
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Version DOCX reçue - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>Version DOCX reçue</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    L'auteur a soumis la version DOCX finale de son manuscrit.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">ID du manuscrit</td>
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
                </table>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        Voir le manuscrit
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    Cet email a été envoyé automatiquement. Merci de ne pas y répondre.
                </p>
            </div>
            """
            body = cls._get_base_template("Version DOCX reçue", content)
        else:
            subject = f"DOCX Version Received - {manuscript_title[:50]}..."
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: {cls.PRIMARY_COLOR_DARK};">
                        <strong>DOCX Version Received</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    The author has submitted the final DOCX version of their manuscript.
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
                </table>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        View Manuscript
                    </a>
                </div>
                
                <p style="font-size: 14px; color: #666; margin-top: 30px;">
                    This is an automated email. Please do not reply.
                </p>
            </div>
            """
            body = cls._get_base_template("DOCX Version Received", content)
        
        # Envoyer l'email à l'adresse système
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_system_new_submission_notification(
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


    @classmethod
    def send_evaluation_submitted_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        evaluator_name: str,
        evaluator_email: str,
        evaluation_decision: str,
        lang: str = "fr"
     ) -> bool:
        """
        Envoie une notification au système quand un évaluateur soumet sa grille d'évaluation
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            evaluator_name: Nom de l'évaluateur
            evaluator_email: Email de l'évaluateur
            evaluation_decision: Décision de l'évaluation
            lang: Langue de la notification (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        # Dictionnaires de traduction
        decision_map = {
            "fr": {
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
            },
            "en": {
                "accepter": "Accepted",
                "accepted": "Accepted",
                "accepted_with_validation": "Accepted with modifications",
                "favorable": "Favorable",
                "refuser": "Rejected",
                "rejected": "Rejected",
                "revision": "Revision requested",
                "resubmission_required": "Resubmission required",
                "mineur": "Minor revision",
                "majeur": "Major revision",
            }
        }
        
        decision_key = evaluation_decision.lower().strip()
        decision_label = decision_map["fr" if is_fr else "en"].get(decision_key, evaluation_decision)
        decision_color = "#59a498" if decision_key in ["accepter", "accepted", "favorable"] else ("#ffc107" if decision_key in ["revision", "resubmission_required", "mineur", "majeur"] else "#dc3545")
        
        if is_fr:
            subject = f"Évaluation soumise - {manuscript_title[:50]}..."
            
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
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Décision</td>
                        <td style="padding: 12px; border: 1px solid #ddd; color: {decision_color};"><strong>{decision_label}</strong></td>
                    </tr>
                </table>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}/evaluations" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        Voir l'évaluation
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    Cet email a été envoyé automatiquement suite à la soumission d'une évaluation.
                </p>
            </div>
            """
            
            body = cls._get_base_template("Évaluation Soumise", content)
        else:
            subject = f"Evaluation Submitted - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, #e8f5f3 0%, #d4ebe7 100%); border-left: 4px solid #59a498; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #4a8a7f;">
                        <strong>New Evaluation Submitted</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    An evaluator has submitted their evaluation for a manuscript.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">Manuscript</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Manuscript ID</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Evaluator</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Decision</td>
                        <td style="padding: 12px; border: 1px solid #ddd; color: {decision_color};"><strong>{decision_label}</strong></td>
                    </tr>
                </table>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}/evaluations" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        View Evaluation
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    This email was automatically sent after an evaluation was submitted.
                </p>
            </div>
            """
            
            body = cls._get_base_template("Evaluation Submitted", content)
            
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluator_response_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        evaluator_name: str,
        evaluator_email: str,
        response: str,  # "accepted" ou "declined"
        lang: str = "fr"
     ) -> bool:
        """
        Envoie une notification au système quand un évaluateur accepte ou refuse une demande
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            evaluator_name: Nom de l'évaluateur
            evaluator_email: Email de l'évaluateur
            response: Réponse de l'évaluateur ("accepted" ou "declined")
            lang: Langue de la notification (fr/en)
            
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        is_accepted = response.lower() in ["accepted", "accepté", "accepter"]
        
        if is_fr:
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
                
                {'' if is_accepted else '''
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>Action requise :</strong> Vous devrez peut-être assigner un autre évaluateur pour ce manuscrit.
                    </p>
                </div>
                '''}
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        Gérer le manuscrit
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    Cet email a été envoyé automatiquement.
                </p>
            </div>
            """
            
            body = cls._get_base_template("Réponse d'Évaluateur", content)
        else:
            status_text = "accepted" if is_accepted else "declined"
            status_display = "Accepted" if is_accepted else "Declined"
            status_color = "#59a498" if is_accepted else "#dc3545"
            
            subject = f"Evaluation Request {status_display} - {manuscript_title[:40]}..."
            
            content = f"""
            <div style="color: #333;">
                <div style="background: linear-gradient(135deg, {'#e8f5f3' if is_accepted else '#fce4e4'} 0%, {'#d4ebe7' if is_accepted else '#f5d4d4'} 100%); border-left: 4px solid {status_color}; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: {status_color};">
                        <strong>Evaluation Request {status_display.upper()}</strong>
                    </p>
                </div>
                
                <p style="font-size: 15px; margin-bottom: 20px;">
                    An evaluator has <strong>{status_text}</strong> the evaluation request for a manuscript.
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold; width: 30%;">Manuscript</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong>{manuscript_title}</strong></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Manuscript ID</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">#{manuscript_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Evaluator</td>
                        <td style="padding: 12px; border: 1px solid #ddd;">{evaluator_name} ({evaluator_email})</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; background: #f5f5f5; border: 1px solid #ddd; font-weight: bold;">Response</td>
                        <td style="padding: 12px; border: 1px solid #ddd;"><strong style="color: {status_color};">{status_display.upper()}</strong></td>
                    </tr>
                </table>
                
                {'' if is_accepted else '''
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px; color: #856404;">
                        <strong>Action Required:</strong> You may need to assign another evaluator for this manuscript.
                    </p>
                </div>
                '''}
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        Manage Manuscript
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    This email was sent automatically.
                </p>
            </div>
            """
            
            body = cls._get_base_template(f"Evaluator Response - {status_display}", content)
            
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
        Envoie des notifications quand un auteur re-soumet son manuscrit après révision :
        1. Une notification au système
        2. Une confirmation à l'auteur
        
        Args:
            manuscript_id: ID du manuscrit
            manuscript_title: Titre du manuscrit
            author_name: Nom de l'auteur
            author_email: Email de l'auteur
            revision_number: Numéro de la révision (par défaut: 1)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si les emails ont été envoyés avec succès
        """
        is_fr = cls._is_french(lang)
        
        # 1. Notification au système (comme avant)
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
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        Voir le manuscrit révisé
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    Cet email a été envoyé automatiquement suite à une re-soumission.
                </p>
            </div>
            """.format(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript_title,
                author_name=author_name,
                author_email=author_email,
                revision_number=revision_number,
                **cls.__dict__
            )
            
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
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(89, 164, 152, 0.4);">
                        View Revised Manuscript
                    </a>
                </div>
                
                <p style="font-size: 13px; color: #888; margin-top: 30px; text-align: center;">
                    This email was automatically sent after a resubmission.
                </p>
            </div>
            """.format(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript_title,
                author_name=author_name,
                author_email=author_email,
                revision_number=revision_number,
                **cls.__dict__
            )
            
            body = cls._get_base_template("Revised Manuscript", content)
        
        # Envoyer la notification au système
        system_success = cls.send_email(cls.FROM_EMAIL, subject, body)
        
        # 2. Envoyer une confirmation à l'auteur
        author_subject, author_body = cls._get_author_resubmission_confirmation(
            manuscript_id=manuscript_id,
            manuscript_title=manuscript_title,
            author_name=author_name,
            revision_number=revision_number,
            is_french=is_fr
        )
        
        author_success = cls.send_email(
            to_email=author_email,
            subject=author_subject,
            body=author_body
        )
        
        # Retourne True uniquement si les deux emails ont été envoyés avec succès
        return system_success and author_success

    @classmethod
    def send_request_evaluation(cls, to_email: str, evaluator_name: str, manuscript_title: str, manuscript_id: int, assignment_deadline: str = None, lang: str = "fr") -> bool:
        """
        Envoie une notification au système quand un évaluateur est assigné à un manuscrit
        
        Args:
            to_email: Email du destinataire (système/admin)
            evaluator_name: Nom de l'évaluateur assigné
            manuscript_title: Titre du manuscrit
            manuscript_id: ID du manuscrit
            assignment_deadline: Date limite d'évaluation (optionnel)
            lang: Langue de l'email (fr/en)
            
        Returns:
            bool: True si envoyé avec succès
        """
        is_fr = cls._is_french(lang)
        
        if is_fr:
            subject = f"Nouvelle assignation d'évaluateur - {manuscript_title[:50]}..."
            
            deadline_info = f"Date limite : {assignment_deadline}" if assignment_deadline else "Aucune date limite spécifiée"
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Bonjour,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>Nouvelle assignation d'évaluateur</strong><br>
                        Un évaluateur a été assigné à un manuscrit.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    L'évaluateur <strong>{evaluator_name}</strong> a été assigné au manuscrit :
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        ID du manuscrit : {manuscript_id}
                    </p>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Informations sur l'assignation :</strong><br>
                        {deadline_info}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        Voir le manuscrit
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Cordialement,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">L'équipe Santaane Platform</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Assignation d'Évaluateur", content)
        else:
            subject = f"New Evaluator Assignment - {manuscript_title[:50]}..."
            
            deadline_info = f"Deadline: {assignment_deadline}" if assignment_deadline else "No deadline specified"
            
            content = f"""
            <div style="color: #333;">
                <p style="font-size: 18px; margin-bottom: 25px;">
                    Hello,
                </p>
                
                <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); border-left: 4px solid #4caf50; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                    <p style="margin: 0; font-size: 16px; color: #2e7d32;">
                        <strong>New Evaluator Assignment</strong><br>
                        An evaluator has been assigned to a manuscript.
                    </p>
                </div>
                
                <p style="font-size: 15px; line-height: 1.6; margin-bottom: 20px;">
                    The evaluator <strong>{evaluator_name}</strong> has been assigned to the manuscript:
                </p>
                
                <div style="background: #f8f9fa; border-left: 4px solid {cls.PRIMARY_COLOR}; padding: 20px; border-radius: 8px; margin: 25px 0;">
                    <h3 style="margin: 0; color: {cls.PRIMARY_COLOR};">"{manuscript_title}"</h3>
                    <p style="margin: 10px 0 0 0; font-size: 14px; color: #666;">
                        Manuscript ID: {manuscript_id}
                    </p>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <p style="margin: 0; font-size: 15px; color: #856404;">
                        <strong>Assignment Information:</strong><br>
                        {deadline_info}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" style="display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: 600;">
                        View Manuscript
                    </a>
                </div>
                
                <p style="font-size: 15px; margin-top: 25px;">
                    Best regards,<br>
                    <strong style="color: {cls.PRIMARY_COLOR};">The Santaane Platform Team</strong>
                </p>
            </div>
            """
            
            body = cls._get_base_template("Evaluator Assignment", content)
        
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_updated_system_notification(
        cls,
        manuscript_id: int,
        manuscript_title: str,
        author_name: str,
        author_email: str,
        editor_name: str,
        changes: dict,
        lang: str = "fr"
     ) -> bool:
        """Envoie une notification au système lorsqu'un manuscrit est mis à jour par le staff"""
        is_fr = cls._is_french(lang)
        
        # Formater les changements en HTML avec un style amélioré
        changes_html = []
        for field, (old_val, new_val) in changes.items():
            changes_html.append(f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 25%; color: #555; font-weight: 500;">
                    {field}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 35%; color: #e74c3c; text-decoration: line-through;">
                    {old_val or ('Non spécifié' if is_fr else 'Not specified')}
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #e0e0e0; width: 40%; color: #27ae60; font-weight: 500;">
                    {new_val or ('Non spécifié' if is_fr else 'Not specified')}
                </td>
            </tr>
            """)
        
        changes_html = "\n".join(changes_html)
        
        if is_fr:
            subject = f" Manuscrit mis à jour - {manuscript_title[:50]}..."
            
            content = f"""
            <div style="max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
                <div style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                            padding: 25px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Mise à jour d'un manuscrit</h1>
                </div>
                
                <div style="padding: 25px; background: #ffffff; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin-top: 0; font-size: 15px;">
                        Le manuscrit ci-dessous a été mis à jour par un membre de l'équipe éditoriale.
                    </p>
                    
                    <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; 
                                padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                        <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px;">
                            Mise à jour effectuée par : <span style="color: {cls.PRIMARY_COLOR};">{editor_name}</span>
                        </p>
                    </div>
                    
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                        <h3 style="margin-top: 0; color: {cls.PRIMARY_COLOR};">Détails du manuscrit</h3>
                        <p style="margin: 10px 0;"><strong>ID :</strong> {manuscript_id}</p>
                        <p style="margin: 10px 0;"><strong>Titre :</strong> {manuscript_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Auteur :</strong> {author_name} &lt;{author_email}&gt;</p>
                    </div>
                    
                    <h3 style="color: {cls.PRIMARY_COLOR}; margin-top: 30px; font-size: 18px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">
                        Modifications effectuées
                    </h3>
                    
                    <div style="overflow-x: auto; margin: 20px 0 30px 0;">
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500;">Champ</th>
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">Ancienne valeur</th>
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">Nouvelle valeur</th>
                                </tr>
                            </thead>
                            <tbody>
                                {changes_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0 20px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" 
                           style="display: inline-block; padding: 14px 35px; 
                                  background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                                  color: white; text-decoration: none; 
                                  border-radius: 30px; font-weight: 600; font-size: 15px;
                                  box-shadow: 0 4px 15px rgba({cls.PRIMARY_COLOR[1:3]}, {cls.PRIMARY_COLOR[3:5]}, {cls.PRIMARY_COLOR[5:7]}, 0.3);
                                  transition: all 0.3s ease;">
                            Voir le manuscrit
                        </a>
                    </div>
                    
                    <p style="font-size: 13px; color: #888; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        Cet email a été envoyé automatiquement suite à la mise à jour d'un manuscrit.
                    </p>
                </div>
            </div>
            """
        else:
            subject = f" Manuscript Updated - {manuscript_title[:50]}..."
            content = f"""
            <div style="max-width: 600px; margin: 0 auto; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
                <div style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                            padding: 25px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">Manuscript Update</h1>
                </div>
                
                <div style="padding: 25px; background: #ffffff; border: 1px solid #e0e0e0; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin-top: 0; font-size: 15px;">
                        The following manuscript has been updated by an editorial team member.
                    </p>
                    
                    <div style="background: #f8fafc; border-left: 4px solid {cls.PRIMARY_COLOR}; 
                                padding: 15px; margin: 20px 0; border-radius: 0 4px 4px 0;">
                        <p style="margin: 0; color: #2c3e50; font-weight: 500; font-size: 15px;">
                            Updated by: <span style="color: {cls.PRIMARY_COLOR};">{editor_name}</span>
                        </p>
                    </div>
                    
                    <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                        <h3 style="margin-top: 0; color: {cls.PRIMARY_COLOR};">Manuscript Details</h3>
                        <p style="margin: 10px 0;"><strong>ID:</strong> {manuscript_id}</p>
                        <p style="margin: 10px 0;"><strong>Title:</strong> {manuscript_title}</p>
                        <p style="margin: 10px 0 0 0;"><strong>Author:</strong> {author_name} &lt;{author_email}&gt;</p>
                    </div>
                    
                    <h3 style="color: {cls.PRIMARY_COLOR}; margin-top: 30px; font-size: 18px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">
                        Changes Made
                    </h3>
                    
                    <div style="overflow-x: auto; margin: 20px 0 30px 0;">
                        <table style="width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                            <thead>
                                <tr style="background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); color: white;">
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500;">Field</th>
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">Old Value</th>
                                    <th style="padding: 12px 15px; text-align: left; font-weight: 500; border-left: 1px solid rgba(255,255,255,0.2);">New Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                {changes_html}
                            </tbody>
                        </table>
                    </div>
                    
                    <div style="text-align: center; margin: 40px 0 20px 0;">
                        <a href="{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}" 
                           style="display: inline-block; padding: 14px 35px; 
                                  background: linear-gradient(135deg, {cls.PRIMARY_COLOR} 0%, {cls.PRIMARY_COLOR_DARK} 100%); 
                                  color: white; text-decoration: none; 
                                  border-radius: 30px; font-weight: 600; font-size: 15px;
                                  box-shadow: 0 4px 15px rgba({cls.PRIMARY_COLOR[1:3]}, {cls.PRIMARY_COLOR[3:5]}, {cls.PRIMARY_COLOR[5:7]}, 0.3);
                                  transition: all 0.3s ease;">
                            View Manuscript
                        </a>
                    </div>
                    
                    <p style="font-size: 13px; color: #888; text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                        This email was automatically sent after a manuscript update.
                    </p>
                </div>
            </div>
            """
        
        return cls.send_email(cls.FROM_EMAIL, subject, content)

