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
    DEFAULT_LANGUAGE = 'fr'

    # Configuration SMTP
    SMTP_SERVER = "smtp.titan.email"
    SMTP_PORT = 465
    SMTP_USERNAME = "laspad-plateform@hamadouba.com"
    SMTP_PASSWORD = "laspad-plateform"
    FROM_EMAIL = "laspad-plateform@hamadouba.com"
    FROM_NAME = "Global Africa Journal"
    PLATFORM_URL = "https://www.globalafricajournal.org"
    EVENTS_URL = "https://events.laspad.org"
    LASPAD_URL = "https://laspad.org"

    # Logo GIF hébergé sur le frontend
    LOGO_URL = "https://www.globalafricajournal.org/images/logo/02-GA-Site-Page-Noir.gif"

    # Couleurs de la charte graphique
    PRIMARY_COLOR = "#59a498"
    PRIMARY_COLOR_DARK = "#4a8a7f"
    HEADER_BG = "#0a1628"        # Bleu marine foncé (identité Global Africa)
    ACCENT_COLOR = "#c8a96e"     # Or/doré (accent africain)

    @classmethod
    def _get_base_template(cls, title: str, content: str, footer_text: str = "") -> str:
        """
        Template de base uniforme pour tous les emails Global Africa Journal.
        Identité visuelle : fond sombre (bleu marine), logo GIF, accents or.
        """
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} — Global Africa Journal</title>
        </head>
        <body style="margin:0;padding:0;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background-color:#f0f2f5;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f0f2f5;">
                <tr>
                    <td align="center" style="padding:40px 20px;">
                        <table role="presentation" width="600" cellspacing="0" cellpadding="0"
                               style="background-color:#ffffff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,0.12);overflow:hidden;">

                            <!-- ═══ HEADER ═══ -->
                            <tr>
                                <td style="background-color:{cls.HEADER_BG};padding:32px 40px;text-align:center;">
                                    <!-- Logo GIF -->
                                    <img src="{cls.LOGO_URL}"
                                         alt="Global Africa Journal"
                                         width="180"
                                         style="display:block;margin:0 auto 18px auto;max-width:180px;height:auto;" />
                                    <!-- Ligne de séparation or -->
                                    <div style="width:60px;height:3px;background-color:{cls.ACCENT_COLOR};margin:0 auto 16px auto;border-radius:2px;"></div>
                                    <!-- Titre de l'email -->
                                    <h1 style="color:#ffffff;margin:0;font-size:20px;font-weight:600;letter-spacing:0.5px;">{title}</h1>
                                    <!-- Sous-titre LASPAD -->
                                    <p style="color:#8a9bb8;margin:8px 0 0 0;font-size:12px;letter-spacing:1px;text-transform:uppercase;">
                                        Revue scientifique du LASPAD
                                    </p>
                                </td>
                            </tr>

                            <!-- ═══ CONTENU PRINCIPAL ═══ -->
                            <tr>
                                <td style="padding:40px;">
                                    {content}
                                </td>
                            </tr>

                            <!-- ═══ FOOTER ═══ -->
                            <tr>
                                <td style="background-color:#f8f9fa;padding:24px 40px;border-top:2px solid {cls.ACCENT_COLOR};text-align:center;">
                                    {footer_text}
                                    <!-- Liens -->
                                    <div style="margin-bottom:14px;">
                                        <a href="{cls.PLATFORM_URL}" style="color:{cls.PRIMARY_COLOR};text-decoration:none;font-size:12px;margin:0 10px;">Revue</a>
                                        <span style="color:#ccc;">|</span>
                                        <a href="{cls.EVENTS_URL}" style="color:{cls.PRIMARY_COLOR};text-decoration:none;font-size:12px;margin:0 10px;">Événements</a>
                                        <span style="color:#ccc;">|</span>
                                        <a href="{cls.LASPAD_URL}" style="color:{cls.PRIMARY_COLOR};text-decoration:none;font-size:12px;margin:0 10px;">LASPAD</a>
                                    </div>
                                    <p style="color:#888;font-size:12px;margin:6px 0 0 0;">
                                        © 2025 Global Africa Journal — LASPAD, Université Gaston Berger, Saint-Louis, Sénégal.
                                    </p>
                                    <p style="color:#aaa;font-size:11px;margin:4px 0 0 0;">
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
        Send an email via SMTP.
        Logique inchangée — seul le template a changé.
        """
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
                logger.error(f"SMTP error: {str(smtp_error)}")
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

    # ══════════════════════════════════════════════
    # HELPERS INTERNES DE MISE EN FORME
    # ══════════════════════════════════════════════

    @classmethod
    def _info_box(cls, text: str, color: str = None) -> str:
        """Boîte d'information colorée (bandeau gauche)."""
        c = color or cls.PRIMARY_COLOR
        return f"""
        <div style="background:#f8f9fa;border-left:4px solid {c};padding:18px 20px;
                    border-radius:0 8px 8px 0;margin:20px 0;">
            {text}
        </div>"""

    @classmethod
    def _alert_box(cls, text: str, level: str = "info") -> str:
        """Boîte d'alerte (info / warning / success / danger)."""
        colors = {
            "info":    ("#e8f4fd", "#1a73e8"),
            "warning": ("#fff8e1", "#f9a825"),
            "success": ("#e8f5e9", "#2e7d32"),
            "danger":  ("#fce4e4", "#c62828"),
        }
        bg, border = colors.get(level, colors["info"])
        return f"""
        <div style="background:{bg};border-left:4px solid {border};padding:16px 20px;
                    border-radius:0 8px 8px 0;margin:20px 0;">
            <p style="margin:0;font-size:14px;color:{border};">{text}</p>
        </div>"""

    @classmethod
    def _manuscript_card(cls, title: str, extra: str = "") -> str:
        """Carte de présentation d'un manuscrit."""
        return f"""
        <div style="background:#f8f9fa;border:1px solid #e8e8e8;border-top:3px solid {cls.ACCENT_COLOR};
                    padding:20px;border-radius:8px;margin:20px 0;">
            <h3 style="margin:0 0 8px 0;color:{cls.HEADER_BG};font-size:16px;font-style:italic;">
                &laquo;&nbsp;{title}&nbsp;&raquo;
            </h3>
            {extra}
        </div>"""

    @classmethod
    def _cta_button(cls, url: str, label: str) -> str:
        """Bouton Call-to-Action centré."""
        return f"""
        <div style="text-align:center;margin:32px 0;">
            <a href="{url}"
               style="display:inline-block;padding:14px 36px;
                      background-color:{cls.PRIMARY_COLOR};
                      color:#ffffff;text-decoration:none;
                      border-radius:6px;font-size:15px;font-weight:600;
                      letter-spacing:0.3px;">
                {label}
            </a>
        </div>"""

    @classmethod
    def _signature(cls, is_fr: bool = True) -> str:
        if is_fr:
            return f"""
            <p style="font-size:15px;margin-top:28px;color:#333;">
                Cordialement,<br>
                <strong style="color:{cls.PRIMARY_COLOR};">Le Comité Éditorial — Global Africa Journal</strong><br>
                <span style="font-size:12px;color:#888;">LASPAD · Université Gaston Berger · Saint-Louis, Sénégal</span>
            </p>"""
        return f"""
        <p style="font-size:15px;margin-top:28px;color:#333;">
            Best regards,<br>
            <strong style="color:{cls.PRIMARY_COLOR};">The Editorial Board — Global Africa Journal</strong><br>
            <span style="font-size:12px;color:#888;">LASPAD · Université Gaston Berger · Saint-Louis, Senegal</span>
        </p>"""

    # ══════════════════════════════════════════════
    # OTP / VÉRIFICATION
    # ══════════════════════════════════════════════

    @classmethod
    def send_otp_email(cls, to_email: str, otp_code: str) -> bool:
        """Envoie le code de vérification OTP."""
        subject = f"{otp_code} — Votre code de vérification | Global Africa Journal"

        content = f"""
        <p style="font-size:16px;color:#333;margin-bottom:20px;text-align:center;">
            Merci de rejoindre <strong>Global Africa Journal</strong>.<br>
            Utilisez le code ci-dessous pour vérifier votre adresse email :
        </p>
        <div style="background:{cls.HEADER_BG};padding:28px 40px;text-align:center;
                    border-radius:10px;margin:28px auto;max-width:280px;">
            <span style="font-size:38px;font-weight:700;letter-spacing:10px;color:{cls.ACCENT_COLOR};
                         font-family:'Courier New',monospace;">
                {otp_code}
            </span>
        </div>
        <p style="color:#666;font-size:14px;text-align:center;">
            Ce code est <strong>confidentiel</strong> et expire dans <strong>2 heures</strong>.
        </p>
        <p style="color:#999;font-size:13px;text-align:center;">
            Si vous n'avez pas créé de compte, ignorez cet email.
        </p>"""

        footer = '<p style="color:#888;font-size:12px;">Vous pouvez demander jusqu\'à 5 codes par jour.</p>'
        body = cls._get_base_template("Vérification de votre compte", content, footer)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # BIENVENUE / ACTIVATION
    # ══════════════════════════════════════════════

    @classmethod
    def send_account_activated_email(cls, to_email: str, full_name: str) -> bool:
        """Email de bienvenue après activation du compte."""
        subject = "Bienvenue sur Global Africa Journal — Compte activé"

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        {cls._alert_box("<strong>Félicitations !</strong> Votre compte a été vérifié et activé avec succès.", "success")}
        <p style="font-size:15px;line-height:1.7;margin-bottom:20px;color:#444;">
            Vous faites désormais partie de la communauté <strong>Global Africa Journal</strong>,
            la revue scientifique à comité de lecture du
            <a href="{cls.LASPAD_URL}" style="color:{cls.PRIMARY_COLOR};">LASPAD</a>
            (Laboratoire d'Analyse des Sociétés et Pouvoirs / Afrique – Diasporas),
            Université Gaston Berger de Saint-Louis, Sénégal.
        </p>
        <h3 style="color:{cls.HEADER_BG};font-size:15px;margin-top:28px;">Que pouvez-vous faire maintenant ?</h3>
        <ul style="font-size:14px;line-height:2;color:#555;padding-left:20px;">
            <li>Soumettre vos manuscrits pour évaluation</li>
            <li>Consulter les publications et appels à contributions</li>
            <li>Découvrir les événements scientifiques sur <a href="{cls.EVENTS_URL}" style="color:{cls.PRIMARY_COLOR};">events.laspad.org</a></li>
            <li>Compléter votre profil chercheur</li>
        </ul>
        {cls._cta_button(cls.PLATFORM_URL + "/login", "Accéder à mon espace")}
        {cls._signature()}"""

        body = cls._get_base_template("Bienvenue sur Global Africa Journal", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_new_user_credentials(cls, to_email: str, full_name: str, password: str, roles: str) -> bool:
        """Email de bienvenue avec identifiants pour les nouveaux utilisateurs créés par l'admin."""
        subject = "Vos identifiants — Global Africa Journal"

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        <p style="font-size:15px;line-height:1.6;color:#444;">
            Votre compte a été créé sur la plateforme <strong>Global Africa Journal</strong>.
        </p>
        {cls._info_box(f"""
            <h3 style="margin:0 0 14px 0;color:{cls.PRIMARY_COLOR};font-size:15px;">Vos identifiants de connexion</h3>
            <p style="margin:6px 0;font-size:14px;color:#333;"><strong>Email :</strong>
                <span style="font-family:monospace;color:{cls.HEADER_BG};">{to_email}</span>
            </p>
            <p style="margin:6px 0;font-size:14px;color:#333;"><strong>Mot de passe :</strong>
                <span style="font-family:monospace;color:{cls.HEADER_BG};">{password}</span>
            </p>
            <p style="margin:6px 0;font-size:14px;color:#333;"><strong>Rôle(s) :</strong>
                <span style="font-family:monospace;color:{cls.HEADER_BG};">{roles}</span>
            </p>
        """)}
        {cls._alert_box("""
            <strong>Important :</strong>
            <ul style="margin:8px 0 0 0;padding-left:18px;">
                <li>Changez votre mot de passe dès la première connexion</li>
                <li>Ne partagez jamais vos identifiants</li>
            </ul>
        """, "warning")}
        {cls._cta_button(cls.PLATFORM_URL + "/login", "Se connecter")}
        {cls._signature()}"""

        body = cls._get_base_template("Vos identifiants Global Africa Journal", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_welcome_email(cls, to_email: str, full_name: str, password: str, role: str) -> bool:
        """Email de bienvenue avec identifiants (alias simplifié)."""
        return cls.send_new_user_credentials(to_email, full_name, password, role)

    # ══════════════════════════════════════════════
    # MOT DE PASSE
    # ══════════════════════════════════════════════

    def send_secure_reset_link(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        """Lien de réinitialisation sécurisé (expire en 5 min)."""
        subject = "Réinitialisation de votre mot de passe — Global Africa Journal"
        reset_link = f"{cls.PLATFORM_URL}/reset-password?token={reset_token}"

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        <p style="font-size:15px;line-height:1.6;color:#444;">
            Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte
            <strong>Global Africa Journal</strong>.
        </p>
        {cls._cta_button(reset_link, "Réinitialiser mon mot de passe")}
        {cls._alert_box("<strong>Ce lien expire dans 5 minutes</strong> pour votre sécurité.", "warning")}
        <p style="font-size:13px;color:#888;text-align:center;">
            Si vous n'avez pas effectué cette demande, ignorez cet email.
        </p>
        {cls._signature()}"""

        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_password_reset_email(cls, to_email: str, full_name: str, reset_token: str) -> bool:
        """Lien de réinitialisation standard (expire en 24h)."""
        subject = "Réinitialisation de votre mot de passe — Global Africa Journal"
        reset_link = f"{cls.PLATFORM_URL}/reset-password?token={reset_token}"

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        <p style="font-size:15px;line-height:1.6;color:#444;">
            Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.
        </p>
        {cls._cta_button(reset_link, "Réinitialiser mon mot de passe")}
        {cls._alert_box("<strong>Ce lien est valide pendant 24 heures.</strong><br>Si vous n'avez pas effectué cette demande, ignorez cet email.", "warning")}
        {cls._signature()}"""

        body = cls._get_base_template("Réinitialisation de mot de passe", content)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # GESTION UTILISATEURS (ADMIN)
    # ══════════════════════════════════════════════

    @classmethod
    def send_inactive_user(cls, to_email: str, full_name: str, admin_name: str = None, admin_email: str = None) -> bool:
        """Notification de désactivation de compte."""
        subject = "Votre compte a été désactivé — Global Africa Journal"
        admin_info = f"par <strong>{admin_name}</strong>" if admin_name else "par un administrateur"
        contact = f"<a href='mailto:{admin_email}' style='color:{cls.PRIMARY_COLOR};'>{admin_email}</a>" if admin_email else "l'équipe éditoriale"

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        {cls._alert_box(f"<strong>Information :</strong> Votre compte Global Africa Journal a été désactivé {admin_info}.", "danger")}
        <p style="font-size:15px;line-height:1.6;color:#444;">
            Vous ne pouvez plus vous connecter avec vos identifiants actuels.
            Si vous pensez qu'il s'agit d'une erreur, contactez : {contact}.
        </p>
        {cls._signature()}"""

        body = cls._get_base_template("Désactivation de compte", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_User_update(cls, to_email: str, full_name: str, updated_fields: dict = None, admin_name: str = None) -> bool:
        """Notification de mise à jour de profil par un admin."""
        logger.info(f"send_User_update called: to_email={to_email}, updated_fields={updated_fields}, admin_name={admin_name}")

        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            if field_name == 'password':
                subject = "Votre mot de passe a été réinitialisé — Global Africa Journal"
            elif field_name == 'is_active':
                subject = "Statut de votre compte modifié — Global Africa Journal"
            elif field_name == 'roles':
                subject = "Vos rôles ont été modifiés — Global Africa Journal"
            else:
                subject = f"Votre profil a été mis à jour — Global Africa Journal"
        else:
            subject = "Votre profil a été mis à jour — Global Africa Journal"

        admin_info = f"par <strong>{admin_name}</strong>" if admin_name else "par un administrateur"

        # Construire le contenu des modifications
        changes_html = ""
        if updated_fields:
            if len(updated_fields) == 1:
                field_name = list(updated_fields.keys())[0]
                value = list(updated_fields.values())[0]
                field_display = cls._get_field_display_name(field_name)

                if field_name == 'password':
                    if isinstance(value, str) and value != 'reset':
                        changes_html = f"""
                        <div style="background:{cls.HEADER_BG};padding:20px;border-radius:8px;
                                    text-align:center;margin:20px 0;">
                            <p style="color:#8a9bb8;font-size:13px;margin:0 0 8px 0;">Nouveau mot de passe</p>
                            <span style="font-family:'Courier New',monospace;font-size:20px;
                                         font-weight:700;color:{cls.ACCENT_COLOR};letter-spacing:3px;">
                                {value}
                            </span>
                            <p style="color:#8a9bb8;font-size:12px;margin:10px 0 0 0;">
                                Changez-le dès votre prochaine connexion
                            </p>
                        </div>"""
                    else:
                        changes_html = cls._alert_box("Votre mot de passe a été réinitialisé.", "warning")
                elif field_name == 'is_active':
                    status = "activé" if value else "désactivé"
                    level = "success" if value else "danger"
                    changes_html = cls._alert_box(f"Votre compte a été <strong>{status}</strong>.", level)
                elif field_name == 'roles':
                    roles_text = ", ".join(str(r) for r in value) if isinstance(value, (list, tuple)) and value else str(value or "Aucun rôle")
                    changes_html = cls._info_box(f"<strong>Nouveaux rôles :</strong> {roles_text}")
                else:
                    changes_html = cls._info_box(f"<strong>{field_display} :</strong> {str(value) if value else 'Non défini'}")
            else:
                rows = ""
                for field, value in updated_fields.items():
                    fd = cls._get_field_display_name(field)
                    vs = "Activé" if field == 'is_active' and value else ("Désactivé" if field == 'is_active' else str(value or "—"))
                    rows += f"<li style='margin:6px 0;font-size:14px;'><strong>{fd} :</strong> {vs}</li>"
                changes_html = cls._info_box(f"<ul style='margin:0;padding-left:18px;'>{rows}</ul>")

        if len(updated_fields) == 1:
            field_name = list(updated_fields.keys())[0]
            main_msg = {
                'password': f"Votre mot de passe a été réinitialisé {admin_info}.",
                'is_active': f"Le statut de votre compte a été modifié {admin_info}.",
                'roles': f"Vos rôles ont été mis à jour {admin_info}.",
            }.get(field_name, f"Votre {cls._get_field_display_name(field_name)} a été mis à jour {admin_info}.")
        else:
            main_msg = f"Votre profil a été mis à jour {admin_info}."

        content = f"""
        <p style="font-size:18px;margin-bottom:20px;color:#333;">
            Bonjour <strong>{full_name}</strong>,
        </p>
        {cls._alert_box(f"<strong>Information :</strong> {main_msg}", "info")}
        {changes_html}
        {cls._cta_button(cls.PLATFORM_URL + "/login", "Se connecter à mon compte")}
        {cls._signature()}"""

        body = cls._get_base_template("Mise à jour de votre profil", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def _get_field_display_name(cls, field_name: str) -> str:
        field_mapping = {
            'email': 'email', 'full_name': 'nom complet',
            'profile_photo': 'photo de profil', 'orcid_id': 'ORCID ID',
            'bio': 'biographie', 'position': 'position',
            'institution': 'institution', 'is_active': 'statut du compte',
            'password': 'mot de passe', 'roles': 'rôles'
        }
        return field_mapping.get(field_name, field_name)

    # ══════════════════════════════════════════════
    # SOUMISSION DE MANUSCRIT
    # ══════════════════════════════════════════════

    @classmethod
    def send_author_submission_confirmation_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, submission_date: str, lang: str = "fr"
    ) -> bool:
        """Confirmation de soumission à l'auteur."""
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = f"Confirmation de soumission — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Votre manuscrit a bien été reçu !</strong> Il est maintenant en cours de traitement par notre équipe éditoriale.", "success")}
            {cls._manuscript_card(manuscript_title, f"""
                <p style="margin:8px 0 0 0;font-size:13px;color:#666;">
                    <strong>Référence :</strong> #{manuscript_id} &nbsp;·&nbsp;
                    <strong>Date de soumission :</strong> {submission_date}
                </p>""")}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Prochaines étapes</h3>
            <ol style="font-size:14px;line-height:2;color:#555;padding-left:20px;">
                <li>Vérification initiale de conformité</li>
                <li>Attribution à des évaluateurs experts</li>
                <li>Évaluation par les pairs (double-aveugle)</li>
                <li>Décision éditoriale finale</li>
            </ol>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Suivre mon manuscrit")}
            <p style="font-size:14px;color:#666;">
                Merci pour votre contribution à la recherche scientifique africaine.
            </p>
            {cls._signature()}"""
        else:
            subject = "Submission Confirmation — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Your manuscript has been successfully received!</strong> It is now being processed by our editorial team.", "success")}
            {cls._manuscript_card(manuscript_title, f"""
                <p style="margin:8px 0 0 0;font-size:13px;color:#666;">
                    <strong>Reference:</strong> #{manuscript_id} &nbsp;·&nbsp;
                    <strong>Submission date:</strong> {submission_date}
                </p>""")}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Next Steps</h3>
            <ol style="font-size:14px;line-height:2;color:#555;padding-left:20px;">
                <li>Initial compliance check</li>
                <li>Assignment to expert reviewers</li>
                <li>Double-blind peer review</li>
                <li>Final editorial decision</li>
            </ol>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Track My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Confirmation de soumission" if is_fr else "Submission Confirmation", content
        )
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # DÉCISIONS ÉDITORIALES
    # ══════════════════════════════════════════════

    @classmethod
    def send_manuscript_accepted_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, custom_message: Optional[str] = None, lang: str = "fr"
    ) -> bool:
        """Notification d'acceptation du manuscrit."""
        is_fr = cls._is_french(lang)

        editor_msg = ""
        if custom_message and custom_message.strip():
            label = "Message du comité éditorial" if is_fr else "Editorial Board Message"
            editor_msg = cls._info_box(f"<strong>{label} :</strong><br><em>{custom_message}</em>")

        next_step_fr = cls._alert_box(
            "<strong>Étape suivante :</strong> Veuillez soumettre la version finale de votre manuscrit au format <strong>DOCX / Word</strong> pour la mise en page.", "warning")
        next_step_en = cls._alert_box(
            "<strong>Next Step:</strong> Please submit the final version of your manuscript in <strong>DOCX / Word format</strong> for typesetting.", "warning")

        if is_fr:
            subject = "Manuscrit accepté — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("🎉 <strong>Félicitations !</strong> Votre manuscrit a été <strong>accepté pour publication</strong> dans Global Africa Journal.", "success")}
            {cls._manuscript_card(manuscript_title)}
            {editor_msg}
            {next_step_fr}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Soumettre la version finale")}
            {cls._signature()}"""
        else:
            subject = "Manuscript Accepted — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("🎉 <strong>Congratulations!</strong> Your manuscript has been <strong>accepted for publication</strong> in Global Africa Journal.", "success")}
            {cls._manuscript_card(manuscript_title)}
            {editor_msg}
            {next_step_en}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Submit Final Version")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Manuscrit accepté" if is_fr else "Manuscript Accepted", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_rejected_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, rejection_reason: str = None, lang: str = "fr"
    ) -> bool:
        """Notification de refus du manuscrit."""
        is_fr = cls._is_french(lang)
        logger.info(f"Rejection reason received: {rejection_reason}")

        reason_html = ""
        if rejection_reason:
            label = "Motif de la décision" if is_fr else "Decision Details"
            reason_html = cls._info_box(f"<strong>{label} :</strong><br>{rejection_reason}", "#dc3545")

        if is_fr:
            subject = "Décision éditoriale — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Décision éditoriale :</strong> Votre manuscrit n'a pas été retenu pour publication dans Global Africa Journal.", "danger")}
            {cls._manuscript_card(manuscript_title)}
            {reason_html}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Cette décision ne remet pas en cause la qualité de votre travail.
                Nous vous encourageons à poursuivre vos recherches et à soumettre de nouveaux travaux.
            </p>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir les détails")}
            <p style="font-size:14px;color:#666;">
                Nous vous remercions de l'intérêt que vous portez à notre revue.
            </p>
            {cls._signature()}"""
        else:
            subject = "Editorial Decision — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Editorial Decision:</strong> Your manuscript has not been accepted for publication in Global Africa Journal.", "danger")}
            {cls._manuscript_card(manuscript_title)}
            {reason_html}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                This decision does not reflect on the quality of your work.
                We encourage you to continue your research and submit future contributions.
            </p>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "View Details")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Décision éditoriale" if is_fr else "Editorial Decision", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_published_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, publication_url: str = None,
        custom_message: Optional[str] = None, lang: str = "fr"
    ) -> bool:
        """Notification de publication."""
        is_fr = cls._is_french(lang)
        pub_link = publication_url or f"{cls.PLATFORM_URL}/publications/{manuscript_id}"

        editor_msg = ""
        if custom_message and custom_message.strip():
            label = "Message du comité éditorial" if is_fr else "Editorial Board Message"
            editor_msg = cls._info_box(f"<strong>{label} :</strong><br><em>{custom_message}</em>")

        if is_fr:
            subject = "Votre article est publié — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("🎉 <strong>Félicitations !</strong> Votre article est désormais <strong>publié</strong> et accessible au public dans <em>Global Africa Journal</em>.", "success")}
            {cls._manuscript_card(manuscript_title)}
            {editor_msg}
            <p style="font-size:15px;color:#444;">
                Partagez ce lien avec vos collègues et sur vos réseaux professionnels :
            </p>
            {cls._cta_button(pub_link, "Voir ma publication")}
            <p style="font-size:14px;color:#666;">
                Merci pour votre contribution à la recherche scientifique africaine.
            </p>
            {cls._signature()}"""
        else:
            subject = "Your Article is Published — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("🎉 <strong>Congratulations!</strong> Your article is now <strong>published</strong> and publicly available in <em>Global Africa Journal</em>.", "success")}
            {cls._manuscript_card(manuscript_title)}
            {editor_msg}
            <p style="font-size:15px;color:#444;">
                Share this link with your colleagues and on your professional networks:
            </p>
            {cls._cta_button(pub_link, "View My Publication")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Article publié" if is_fr else "Article Published", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_revision_requested_email(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, revision_comments: str = None, lang: str = "fr"
    ) -> bool:
        """Notification de demande de révision."""
        is_fr = cls._is_french(lang)

        comments_html = ""
        if revision_comments:
            label = "Commentaires du comité éditorial" if is_fr else "Editorial Comments"
            comments_html = cls._info_box(
                f"<strong>{label} :</strong><br><div style='white-space:pre-line;font-size:14px;color:#555;margin-top:8px;'>{revision_comments}</div>",
                "#f9a825")

        if is_fr:
            subject = "Révision demandée — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Révision demandée :</strong> Des modifications sont nécessaires avant que votre manuscrit puisse être accepté pour publication.", "warning")}
            {cls._manuscript_card(manuscript_title)}
            {comments_html}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Veuillez prendre en compte les remarques ci-dessus et soumettre une version révisée.
            </p>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}/revise", "Soumettre ma révision")}
            {cls._signature()}"""
        else:
            subject = "Revisions Requested — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("<strong>Revisions Required:</strong> Modifications are needed before your manuscript can be accepted for publication.", "warning")}
            {cls._manuscript_card(manuscript_title)}
            {comments_html}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Please address the comments above and submit a revised version.
            </p>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}/revise", "Submit My Revision")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Révision demandée" if is_fr else "Revisions Requested", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_auteur_confirmation_docx_file(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = "fr"
    ) -> bool:
        """Confirmation de réception de la version DOCX finale."""
        is_fr = cls._is_french(lang)
        first = (author_name.split()[0] if author_name and author_name.strip()
                 else ("Auteur" if is_fr else "Author"))

        if is_fr:
            subject = "Version finale reçue — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{first}</strong>,
            </p>
            {cls._alert_box("<strong>Votre version finale a bien été reçue !</strong> Elle sera traitée par notre équipe pour la publication.", "success")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir mon manuscrit")}
            <p style="font-size:14px;color:#666;">Merci pour votre confiance.</p>
            {cls._signature()}"""
        else:
            subject = "Final Version Received — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{first}</strong>,
            </p>
            {cls._alert_box("<strong>Your final version has been received!</strong> It will be processed by our team for publication.", "success")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "View My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Version finale reçue" if is_fr else "Final Version Received", content)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # ÉVALUATEURS
    # ══════════════════════════════════════════════

    @classmethod
    def send_evaluation_request_email(
        cls, to_email: str, evaluator_name: str, manuscript_title: str,
        manuscript_pdf_url: str, evaluation_deadline: str, lang: str = "fr"
    ) -> bool:
        """Demande d'évaluation envoyée à un évaluateur."""
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = f"Demande d'évaluation — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{evaluator_name}</strong>,
            </p>
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Le comité éditorial de <strong>Global Africa Journal</strong> sollicite votre expertise
                pour évaluer le manuscrit suivant :
            </p>
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;">Soumis à la revue <strong>Global Africa Journal</strong> — LASPAD</p>')}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Les détails du manuscrit et la grille d'évaluation sont disponibles dans votre espace personnel.
            </p>
            {cls._alert_box(f"<strong>Délai souhaité :</strong> Nous espérons recevoir votre évaluation avant le <strong>{evaluation_deadline}</strong>.", "info")}
            {cls._cta_button(cls.PLATFORM_URL + "/login", "Accéder à mon espace évaluateur")}
            <p style="font-size:14px;color:#666;">
                Dans l'attente de votre retour, veuillez agréer l'expression de notre considération distinguée.
            </p>
            {cls._signature()}"""
        else:
            subject = "Evaluation Request — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{evaluator_name}</strong>,
            </p>
            <p style="font-size:15px;line-height:1.6;color:#444;">
                The editorial board of <strong>Global Africa Journal</strong> kindly requests your expertise
                to review the following manuscript:
            </p>
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;">Submitted to <strong>Global Africa Journal</strong> — LASPAD</p>')}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Manuscript details and the evaluation form are available in your personal dashboard.
            </p>
            {cls._alert_box(f"<strong>Requested deadline:</strong> We would appreciate your evaluation by <strong>{evaluation_deadline}</strong>.", "info")}
            {cls._cta_button(cls.PLATFORM_URL + "/login", "Access My Reviewer Dashboard")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Demande d'évaluation" if is_fr else "Evaluation Request", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_evaluation_reminder_email(
        cls, to_email: str, evaluator_name: str, manuscript_title: str,
        evaluation_deadline: str, lang: str = "fr"
    ) -> bool:
        """Rappel d'évaluation à un évaluateur."""
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = "Rappel — Évaluation en attente | Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{evaluator_name}</strong>,
            </p>
            {cls._alert_box("<strong>Rappel :</strong> Nous n'avons pas encore reçu votre évaluation.", "warning")}
            {cls._manuscript_card(manuscript_title)}
            {cls._alert_box(f"La date limite est fixée au <strong>{evaluation_deadline}</strong>.", "warning")}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                Si vous avez déjà soumis votre évaluation, veuillez ignorer ce message.
                Dans le cas contraire, nous vous serions reconnaissants de bien vouloir procéder dans les meilleurs délais.
            </p>
            {cls._cta_button(cls.PLATFORM_URL + "/login", "Accéder au manuscrit")}
            {cls._signature()}"""
        else:
            subject = "Reminder — Pending Evaluation | Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{evaluator_name}</strong>,
            </p>
            {cls._alert_box("<strong>Reminder:</strong> We have not yet received your evaluation.", "warning")}
            {cls._manuscript_card(manuscript_title)}
            {cls._alert_box(f"The deadline is <strong>{evaluation_deadline}</strong>.", "warning")}
            <p style="font-size:15px;line-height:1.6;color:#444;">
                If you have already submitted your evaluation, please disregard this message.
                Otherwise, we would greatly appreciate your evaluation at the earliest convenience.
            </p>
            {cls._cta_button(cls.PLATFORM_URL + "/login", "Access Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Rappel d'évaluation" if is_fr else "Evaluation Reminder", content)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # NOTIFICATIONS AUTEUR — ÉVALUATEURS
    # ══════════════════════════════════════════════

    @classmethod
    def send_autor_manuscript_assigner_a_evaluator(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = 'fr'
    ) -> bool:
        """Notification à l'auteur : un évaluateur a été assigné."""
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = "Évaluateur assigné — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Cher(e) <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("Un évaluateur expert a été assigné à votre manuscrit. Vous serez notifié(e) dès qu'il aura accepté ou décliné.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Suivre mon manuscrit")}
            {cls._signature()}"""
        else:
            subject = "Reviewer Assigned — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">
                Dear <strong>{author_name}</strong>,
            </p>
            {cls._alert_box("An expert reviewer has been assigned to your manuscript. You will be notified once they accept or decline.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Track My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Évaluateur assigné" if is_fr else "Reviewer Assigned", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_autor_reponse_evalutor_to_assignation(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, accepted: bool, lang: str = 'fr'
    ) -> bool:
        """Notification à l'auteur : réponse de l'évaluateur à l'assignation."""
        is_fr = cls._is_french(lang)

        if accepted:
            if is_fr:
                subject = "Votre manuscrit est en cours d'évaluation — Global Africa Journal"
                content = f"""
                <p style="font-size:18px;margin-bottom:20px;color:#333;">Cher(e) <strong>{author_name}</strong>,</p>
                {cls._alert_box("L'évaluateur a <strong>accepté</strong> d'évaluer votre manuscrit. Le processus de révision par les pairs est en cours.", "success")}
                {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
                {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Suivre mon manuscrit")}
                {cls._signature()}"""
            else:
                subject = "Your Manuscript is Under Review — Global Africa Journal"
                content = f"""
                <p style="font-size:18px;margin-bottom:20px;color:#333;">Dear <strong>{author_name}</strong>,</p>
                {cls._alert_box("The reviewer has <strong>accepted</strong> to evaluate your manuscript. The peer review process is now underway.", "success")}
                {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
                {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Track My Manuscript")}
                {cls._signature(is_fr=False)}"""
        else:
            if is_fr:
                subject = "Recherche d'un nouvel évaluateur — Global Africa Journal"
                content = f"""
                <p style="font-size:18px;margin-bottom:20px;color:#333;">Cher(e) <strong>{author_name}</strong>,</p>
                {cls._alert_box("L'évaluateur précédemment assigné n'a pas pu accepter la mission. Notre équipe est en cours de recherche d'un nouvel expert.", "warning")}
                {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
                <p style="font-size:14px;color:#666;">Vous serez notifié(e) dès qu'un nouvel évaluateur sera assigné.</p>
                {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir le statut")}
                {cls._signature()}"""
            else:
                subject = "Searching for a New Reviewer — Global Africa Journal"
                content = f"""
                <p style="font-size:18px;margin-bottom:20px;color:#333;">Dear <strong>{author_name}</strong>,</p>
                {cls._alert_box("The previously assigned reviewer was unable to accept. Our team is searching for a new expert.", "warning")}
                {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
                <p style="font-size:14px;color:#666;">You will be notified as soon as a new reviewer is assigned.</p>
                {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "View Status")}
                {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Mise à jour évaluation" if is_fr else "Review Update", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_autor_reminder_evalutor(
        cls, to_email: str, author_name: str, manuscript_title: str,
        days_remaining: int, manuscript_id: int = None, lang: str = 'fr'
    ) -> bool:
        """Notification à l'auteur : un rappel a été envoyé à l'évaluateur."""
        is_fr = cls._is_french(lang)
        btn = cls._cta_button(
            f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir mon manuscrit"
        ) if manuscript_id else ""

        if is_fr:
            subject = "Rappel envoyé à l'évaluateur — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Cher(e) <strong>{author_name}</strong>,</p>
            {cls._alert_box(f"Un rappel a été envoyé à l'évaluateur. Il reste environ <strong>{days_remaining} jour(s)</strong> avant la date limite.", "info")}
            {cls._manuscript_card(manuscript_title)}
            {btn}
            {cls._signature()}"""
        else:
            subject = "Reminder Sent to Reviewer — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Dear <strong>{author_name}</strong>,</p>
            {cls._alert_box(f"A reminder has been sent to the reviewer. Approximately <strong>{days_remaining} day(s)</strong> remain until the deadline.", "info")}
            {cls._manuscript_card(manuscript_title)}
            {btn}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Rappel évaluateur" if is_fr else "Reviewer Reminder", content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def evaluator_send_evauation(
        cls, to_email: str, author_name: str, manuscript_title: str,
        manuscript_id: int, lang: str = 'fr'
    ) -> bool:
        """Notification à l'auteur : une évaluation a été soumise."""
        is_fr = cls._is_french(lang)

        if is_fr:
            subject = "Évaluation reçue — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Cher(e) <strong>{author_name}</strong>,</p>
            {cls._alert_box("Un évaluateur vient de soumettre son évaluation pour votre manuscrit.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir mon manuscrit")}
            {cls._signature()}"""
        else:
            subject = "Evaluation Received — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Dear <strong>{author_name}</strong>,</p>
            {cls._alert_box("A reviewer has submitted their evaluation for your manuscript.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "View My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Évaluation reçue" if is_fr else "Evaluation Received", content)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # RE-SOUMISSION
    # ══════════════════════════════════════════════

    @classmethod
    def _get_author_resubmission_confirmation(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        revision_number: int, is_french: bool
    ) -> tuple[str, str]:
        """Confirmation de re-soumission pour l'auteur."""
        first = author_name.split()[0] if author_name else ("Auteur" if is_french else "Author")

        if is_french:
            subject = "Confirmation de re-soumission — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Cher(e) <strong>{first}</strong>,</p>
            {cls._alert_box("<strong>Votre manuscrit révisé a bien été reçu !</strong>", "success")}
            {cls._manuscript_card(manuscript_title, f"""
                <p style="margin:8px 0 0 0;font-size:13px;color:#666;">
                    <strong>Référence :</strong> #{manuscript_id} &nbsp;·&nbsp;
                    <strong>Version :</strong> Révision #{revision_number}
                </p>""")}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Prochaines étapes</h3>
            <ol style="font-size:14px;line-height:2;color:#555;padding-left:20px;">
                <li>Examen des modifications par l'équipe éditoriale</li>
                <li>Nouvelle évaluation si nécessaire</li>
                <li>Décision éditoriale finale</li>
            </ol>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Suivre mon manuscrit")}
            {cls._signature()}"""
        else:
            subject = "Resubmission Confirmation — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Dear <strong>{first}</strong>,</p>
            {cls._alert_box("<strong>Your revised manuscript has been successfully received!</strong>", "success")}
            {cls._manuscript_card(manuscript_title, f"""
                <p style="margin:8px 0 0 0;font-size:13px;color:#666;">
                    <strong>Reference:</strong> #{manuscript_id} &nbsp;·&nbsp;
                    <strong>Version:</strong> Revision #{revision_number}
                </p>""")}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Next Steps</h3>
            <ol style="font-size:14px;line-height:2;color:#555;padding-left:20px;">
                <li>Review of changes by the editorial team</li>
                <li>Additional evaluation if needed</li>
                <li>Final editorial decision</li>
            </ol>
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Track My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Confirmation de re-soumission" if is_french else "Resubmission Confirmation", content)
        return subject, body

    # ══════════════════════════════════════════════
    # MISE À JOUR MANUSCRIT PAR LE STAFF
    # ══════════════════════════════════════════════

    @classmethod
    def send_manuscript_updated_author_notification(
        cls, to_email: str, author_name: str, manuscript_id: int,
        manuscript_title: str, changes: dict, lang: str = "fr"
    ) -> bool:
        """Notification à l'auteur : manuscrit mis à jour par le staff."""
        is_fr = cls._is_french(lang)

        rows = "".join([f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;font-weight:500;color:#555;width:25%;">{field}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;color:#c62828;text-decoration:line-through;width:37%;">
                {old_val or ('Non spécifié' if is_fr else 'Not specified')}
            </td>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;color:#2e7d32;font-weight:500;width:38%;">
                {new_val or ('Non spécifié' if is_fr else 'Not specified')}
            </td>
        </tr>""" for field, (old_val, new_val) in changes.items()])

        table = f"""
        <table style="width:100%;border-collapse:collapse;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;font-size:13px;margin:20px 0;">
            <thead>
                <tr style="background-color:{cls.HEADER_BG};color:#ffffff;">
                    <th style="padding:10px 12px;text-align:left;font-weight:500;">{'Champ' if is_fr else 'Field'}</th>
                    <th style="padding:10px 12px;text-align:left;font-weight:500;">{'Ancienne valeur' if is_fr else 'Old Value'}</th>
                    <th style="padding:10px 12px;text-align:left;font-weight:500;">{'Nouvelle valeur' if is_fr else 'New Value'}</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>"""

        if is_fr:
            subject = f"Votre manuscrit a été mis à jour — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Bonjour <strong>{author_name}</strong>,</p>
            {cls._alert_box("Votre manuscrit a été mis à jour par l'équipe éditoriale.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Référence :</strong> #{manuscript_id}</p>')}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Modifications effectuées</h3>
            {table}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "Voir mon manuscrit")}
            {cls._signature()}"""
        else:
            subject = f"Your Manuscript Has Been Updated — Global Africa Journal"
            content = f"""
            <p style="font-size:18px;margin-bottom:20px;color:#333;">Hello <strong>{author_name}</strong>,</p>
            {cls._alert_box("Your manuscript has been updated by the editorial team.", "info")}
            {cls._manuscript_card(manuscript_title, f'<p style="margin:8px 0 0 0;font-size:13px;color:#666;"><strong>Reference:</strong> #{manuscript_id}</p>')}
            <h3 style="color:{cls.HEADER_BG};font-size:15px;">Changes Made</h3>
            {table}
            {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/author/manuscripts/{manuscript_id}", "View My Manuscript")}
            {cls._signature(is_fr=False)}"""

        body = cls._get_base_template(
            "Mise à jour manuscrit" if is_fr else "Manuscript Updated", content)
        return cls.send_email(to_email, subject, body)

    # ══════════════════════════════════════════════
    # NOTIFICATIONS SYSTÈME
    # ══════════════════════════════════════════════

    @classmethod
    def _system_table(cls, rows_data: list, is_fr: bool = True) -> str:
        """Table de données pour les emails système."""
        rows = "".join([f"""
        <tr>
            <td style="padding:11px 14px;background:#f5f5f5;border:1px solid #ddd;font-weight:600;width:35%;color:#333;">{label}</td>
            <td style="padding:11px 14px;border:1px solid #ddd;color:#444;">{value}</td>
        </tr>""" for label, value in rows_data])
        return f'<table style="width:100%;border-collapse:collapse;margin:20px 0;">{rows}</table>'

    @classmethod
    def send_system_new_submission_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, section_name: str, theme_name: str = None, lang: str = "fr"
    ) -> bool:
        """Notification système : nouvelle soumission."""
        is_fr = cls._is_french(lang)
        subject = f"{'Nouvelle soumission' if is_fr else 'New Submission'} — {manuscript_title[:50]}…"

        rows = [
            ("ID", f"#{manuscript_id}"),
            ("Titre" if is_fr else "Title", f"<strong>{manuscript_title}</strong>"),
            ("Auteur" if is_fr else "Author", f"{author_name} &lt;{author_email}&gt;"),
        ]
        if section_name:
            rows.append(("Rubrique" if is_fr else "Section", section_name))
        if theme_name:
            rows.append(("Appel" if is_fr else "Theme", theme_name))

        label = "Nouvelle soumission reçue" if is_fr else "New Submission Received"
        desc = "Un nouveau manuscrit a été soumis et nécessite votre attention." if is_fr else "A new manuscript has been submitted and requires your attention."

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong><br>{desc}", "info")}
        {cls._system_table(rows, is_fr)}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir le manuscrit" if is_fr else "View Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_system_submitted_docx_file(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, lang: str = "fr"
    ) -> bool:
        """Notification système : version DOCX reçue."""
        is_fr = cls._is_french(lang)
        subject = f"{'Version DOCX reçue' if is_fr else 'DOCX Version Received'} — {manuscript_title[:50]}…"

        rows = [
            ("ID", f"#{manuscript_id}"),
            ("Titre" if is_fr else "Title", f"<strong>{manuscript_title}</strong>"),
            ("Auteur" if is_fr else "Author", f"{author_name} &lt;{author_email}&gt;"),
        ]
        label = "Version DOCX finale reçue" if is_fr else "Final DOCX Version Received"

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", "success")}
        {cls._system_table(rows, is_fr)}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir le manuscrit" if is_fr else "View Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluation_submitted_notification(
        cls, manuscript_id: int, manuscript_title: str, evaluator_name: str,
        evaluator_email: str, evaluation_decision: str, lang: str = "fr"
    ) -> bool:
        """Notification système : évaluation soumise."""
        is_fr = cls._is_french(lang)
        subject = f"{'Évaluation soumise' if is_fr else 'Evaluation Submitted'} — {manuscript_title[:50]}…"

        decision_map = {
            "fr": {"accepter": "Accepté", "accepted": "Accepté", "favorable": "Favorable",
                   "refuser": "Refusé", "rejected": "Refusé", "revision": "Révision demandée",
                   "resubmission_required": "Révision demandée", "mineur": "Révision mineure", "majeur": "Révision majeure"},
            "en": {"accepter": "Accepted", "accepted": "Accepted", "favorable": "Favorable",
                   "refuser": "Rejected", "rejected": "Rejected", "revision": "Revision Requested",
                   "resubmission_required": "Resubmission Required", "mineur": "Minor Revision", "majeur": "Major Revision"}
        }
        dk = evaluation_decision.lower().strip()
        dl = decision_map["fr" if is_fr else "en"].get(dk, evaluation_decision)
        dc = "#2e7d32" if dk in ["accepter", "accepted", "favorable"] else ("#f9a825" if "revision" in dk or "mineur" in dk or "majeur" in dk else "#c62828")

        rows = [
            ("Manuscrit" if is_fr else "Manuscript", f"<strong>{manuscript_title}</strong>"),
            ("ID", f"#{manuscript_id}"),
            ("Évaluateur" if is_fr else "Evaluator", f"{evaluator_name} &lt;{evaluator_email}&gt;"),
            ("Décision" if is_fr else "Decision", f'<strong style="color:{dc};">{dl}</strong>'),
        ]
        label = "Nouvelle évaluation soumise" if is_fr else "New Evaluation Submitted"

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", "info")}
        {cls._system_table(rows, is_fr)}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir l'évaluation" if is_fr else "View Evaluation")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_evaluator_response_notification(
        cls, manuscript_id: int, manuscript_title: str, evaluator_name: str,
        evaluator_email: str, response: str, lang: str = "fr"
    ) -> bool:
        """Notification système : réponse d'un évaluateur à une assignation."""
        is_fr = cls._is_french(lang)
        is_accepted = response.lower() in ["accepted", "accepté", "accepter"]
        status_fr = "accepté" if is_accepted else "refusé"
        status_en = "Accepted" if is_accepted else "Declined"
        level = "success" if is_accepted else "danger"
        subject = f"Demande d'évaluation {status_fr}e" if is_fr else f"Evaluation Request {status_en} — {manuscript_title[:40]}…"

        rows = [
            ("Manuscrit" if is_fr else "Manuscript", f"<strong>{manuscript_title}</strong>"),
            ("ID", f"#{manuscript_id}"),
            ("Évaluateur" if is_fr else "Evaluator", f"{evaluator_name} &lt;{evaluator_email}&gt;"),
            ("Réponse" if is_fr else "Response", f'<strong>{status_fr.upper() if is_fr else status_en.upper()}</strong>'),
        ]
        label = f"Demande {status_fr}e" if is_fr else f"Request {status_en}"
        extra = "" if is_accepted else cls._alert_box(
            "<strong>Action requise :</strong> Il peut être nécessaire d'assigner un autre évaluateur." if is_fr
            else "<strong>Action Required:</strong> You may need to assign another reviewer.", "warning")

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", level)}
        {cls._system_table(rows, is_fr)}
        {extra}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Gérer le manuscrit" if is_fr else "Manage Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)

    @classmethod
    def send_manuscript_resubmitted_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, revision_number: int = 1, lang: str = "fr"
    ) -> bool:
        """Notification système + confirmation auteur : re-soumission."""
        is_fr = cls._is_french(lang)
        subject = f"{'Re-soumission' if is_fr else 'Resubmission'} — {manuscript_title[:50]}…"

        rows = [
            ("ID", f"#{manuscript_id}"),
            ("Titre" if is_fr else "Title", f"<strong>{manuscript_title}</strong>"),
            ("Auteur" if is_fr else "Author", f"{author_name} &lt;{author_email}&gt;"),
            ("Version" if is_fr else "Version", f"Révision #{revision_number}" if is_fr else f"Revision #{revision_number}"),
        ]
        label = "Manuscrit révisé reçu" if is_fr else "Revised Manuscript Received"
        action_msg = "<strong>Action requise :</strong> Veuillez examiner les modifications." if is_fr else "<strong>Action Required:</strong> Please review the changes."

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", "info")}
        {cls._system_table(rows, is_fr)}
        {cls._alert_box(action_msg, "warning")}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir le manuscrit révisé" if is_fr else "View Revised Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        system_ok = cls.send_email(cls.FROM_EMAIL, subject, body)

        author_subject, author_body = cls._get_author_resubmission_confirmation(
            manuscript_id, manuscript_title, author_name, revision_number, is_fr)
        author_ok = cls.send_email(author_email, author_subject, author_body)

        return system_ok and author_ok

    @classmethod
    def send_request_evaluation(
        cls, to_email: str, evaluator_name: str, manuscript_title: str,
        manuscript_id: int, assignment_deadline: str = None, lang: str = "fr"
    ) -> bool:
        """Notification système : évaluateur assigné."""
        is_fr = cls._is_french(lang)
        subject = f"{'Nouvelle assignation' if is_fr else 'New Assignment'} — {manuscript_title[:50]}…"

        rows = [
            ("Manuscrit" if is_fr else "Manuscript", f"<strong>{manuscript_title}</strong>"),
            ("ID", f"#{manuscript_id}"),
            ("Évaluateur" if is_fr else "Evaluator", evaluator_name),
        ]
        if assignment_deadline:
            rows.append(("Date limite" if is_fr else "Deadline", assignment_deadline))

        label = "Nouvelle assignation d'évaluateur" if is_fr else "New Evaluator Assignment"

        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", "success")}
        {cls._system_table(rows, is_fr)}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir le manuscrit" if is_fr else "View Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_manuscript_updated_system_notification(
        cls, manuscript_id: int, manuscript_title: str, author_name: str,
        author_email: str, editor_name: str, changes: dict, lang: str = "fr"
    ) -> bool:
        """Notification système : manuscrit mis à jour par le staff."""
        is_fr = cls._is_french(lang)
        subject = f"{'Manuscrit mis à jour' if is_fr else 'Manuscript Updated'} — {manuscript_title[:50]}…"

        rows_data = [
            ("ID", f"#{manuscript_id}"),
            ("Titre" if is_fr else "Title", f"<strong>{manuscript_title}</strong>"),
            ("Auteur" if is_fr else "Author", f"{author_name} &lt;{author_email}&gt;"),
            ("Modifié par" if is_fr else "Updated by", f"<strong>{editor_name}</strong>"),
        ]

        changes_rows = "".join([f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;font-weight:500;color:#555;width:25%;">{field}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;color:#c62828;text-decoration:line-through;width:37%;">
                {old_val or ('Non spécifié' if is_fr else 'Not specified')}
            </td>
            <td style="padding:10px 12px;border-bottom:1px solid #eee;color:#2e7d32;font-weight:500;width:38%;">
                {new_val or ('Non spécifié' if is_fr else 'Not specified')}
            </td>
        </tr>""" for field, (old_val, new_val) in changes.items()])

        changes_table = f"""
        <table style="width:100%;border-collapse:collapse;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;font-size:13px;margin:16px 0;">
            <thead>
                <tr style="background-color:{cls.HEADER_BG};color:#ffffff;">
                    <th style="padding:10px 12px;text-align:left;">{'Champ' if is_fr else 'Field'}</th>
                    <th style="padding:10px 12px;text-align:left;">{'Ancienne valeur' if is_fr else 'Old Value'}</th>
                    <th style="padding:10px 12px;text-align:left;">{'Nouvelle valeur' if is_fr else 'New Value'}</th>
                </tr>
            </thead>
            <tbody>{changes_rows}</tbody>
        </table>"""

        label = "Mise à jour d'un manuscrit" if is_fr else "Manuscript Update"
        content = f"""
        {cls._alert_box(f"<strong>{label}</strong>", "info")}
        {cls._system_table(rows_data, is_fr)}
        <h3 style="color:{cls.HEADER_BG};font-size:14px;">{'Modifications' if is_fr else 'Changes'}</h3>
        {changes_table}
        {cls._cta_button(f"{cls.PLATFORM_URL}/dashboard/editor/manuscripts/{manuscript_id}", "Voir le manuscrit" if is_fr else "View Manuscript")}
        <p style="font-size:13px;color:#888;text-align:center;">Email automatique — Global Africa Journal</p>"""

        body = cls._get_base_template(label, content)
        return cls.send_email(cls.FROM_EMAIL, subject, body)
