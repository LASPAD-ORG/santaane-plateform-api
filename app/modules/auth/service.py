"""
Auth module - Business logic service
Handles authentication business logic including OTP verification and password reset
"""
import random
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from app.modules.auth.error_codes import AuthErrorCode
from app.core.security import hash_password, verify_password, create_access_token
from app.core.logging import get_logger
from app.core.email import EmailService

logger = get_logger(__name__)


class AuthService:
    """Service for authentication business logic"""

    def __init__(self, repository: AuthRepository):
        self.repository = repository

    def _get_utc_now(self):
        """
        Helper to get current UTC time as a naive datetime object.
        Essential for compatibility with PostgreSQL TIMESTAMP WITHOUT TIME ZONE.
        """
        return datetime.now(timezone.utc).replace(tzinfo=None)

    async def register_user(self, user_data: UserCreate) -> str:
        """Register a new user and send initial OTP code"""
        logger.info(f"Registration attempt for email: {user_data.email}")

        if await self.repository.user_exists(user_data.email):
            logger.warning(f"Registration failed: email '{user_data.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AuthErrorCode.EMAIL_ALREADY_EXISTS
            )

        # Génération du code OTP initial
        otp_code = str(random.randint(100000, 999999))
        hashed_password = hash_password(user_data.password)
        
        now = self._get_utc_now()
        user = await self.repository.create_user(
            email=user_data.email,
            full_name=user_data.fullName,
            hashed_password=hashed_password,
            profile_photo=user_data.profilePhoto,
            orcid_id=user_data.orcidId,
            otp_code=otp_code,
            # On met 2 heures pour compenser les décalages de fuseaux horaires locaux/UTC
            otp_expires_at=now + timedelta(hours=2),
            otp_send_count=1,
            last_otp_sent_at=now,
            is_active=False 
        )

        logger.info(f"User registered successfully: {user.email}. Sending OTP.")
        EmailService.send_otp_email(user.email, otp_code)
        
        await self.set_default_user_role(user.id)
        return "Compte créé. Veuillez vérifier votre boîte mail pour le code de validation."

    async def verify_otp(self, email: str, code: str) -> bool:
        """Verify OTP code and activate user account"""
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        if user.otp_code != code.strip():
            raise HTTPException(status_code=400, detail="Code OTP invalide")

        if not user.otp_expires_at:
            raise HTTPException(status_code=400, detail="Aucun code n'a été généré")

        now = self._get_utc_now()
        db_expires = user.otp_expires_at.replace(tzinfo=None) if user.otp_expires_at.tzinfo else user.otp_expires_at
        
        # On compare en laissant une marge de sécurité
        if db_expires < (now - timedelta(hours=1)):
            raise HTTPException(status_code=400, detail="Code OTP expiré")

        user.is_active = True
        user.email_verified = True
        user.otp_code = None
        await self.repository.update_user(user)
        
        logger.info(f"User {email} verified and activated via OTP")
        return True

    async def resend_otp(self, email: str) -> str:
        """Resend OTP code with a limit of 5 per day"""
        user = await self.repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

        now = self._get_utc_now()
        today = now.date()
        
        last_sent = user.last_otp_sent_at.replace(tzinfo=None) if user.last_otp_sent_at and user.last_otp_sent_at.tzinfo else user.last_otp_sent_at

        if last_sent and last_sent.date() == today:
            if user.otp_send_count >= 5:
                logger.warning(f"OTP limit reached for {email}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
                    detail="Limite de 5 codes par jour atteinte."
                )
            user.otp_send_count += 1
        else:
            user.otp_send_count = 1

        new_otp = str(random.randint(100000, 999999))
        user.otp_code = new_otp
        user.otp_expires_at = now + timedelta(hours=2) # Marge de sécurité
        user.last_otp_sent_at = now
        
        await self.repository.update_user(user)
        EmailService.send_otp_email(user.email, new_otp)
        
        return "Un nouveau code a été envoyé."

    async def request_password_reset(self, email: str) -> str:
        """Request password reset with expiration token"""
        user = await self.repository.get_user_by_email(email)
        if not user:
            return "Si cet email existe, un lien a été envoyé."

        now = self._get_utc_now()
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        # Augmenté à 2h pour éviter l'expiration immédiate due au décalage serveur/DB
        user.reset_token_expires_at = now + timedelta(hours=2)
        
        await self.repository.update_user(user)
        EmailService.send_password_reset_email(user.email, user.full_name, reset_token)
        
        return "Lien de réinitialisation envoyé."

    async def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """Confirm password reset using token"""
        user = await self.repository.get_user_by_reset_token(token)
        
        if not user:
             raise HTTPException(status_code=400, detail="Lien invalide")
             
        now = self._get_utc_now()
        db_reset_expires = user.reset_token_expires_at.replace(tzinfo=None) if user.reset_token_expires_at.tzinfo else user.reset_token_expires_at
        
        # On vérifie si l'heure actuelle n'a pas dépassé l'heure d'expiration
        if db_reset_expires < now:
            logger.error(f"Token expiré: DB={db_reset_expires} VS NOW={now}")
            raise HTTPException(status_code=400, detail="Lien expiré")

        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None
        
        await self.repository.update_user(user)
        logger.info(f"Password reset successful for user: {user.email}")
        return True

    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """Authenticate user and return JWT token"""
        logger.info(f"Login attempt for email: {credentials.email}")
        user = await self.repository.get_user_by_email(credentials.email)

        if not user or not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.INVALID_CREDENTIALS
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Veuillez valider votre compte avec le code OTP."
            )

        access_token = create_access_token(data={"sub": user.email})
        return TokenResponse(access_token=access_token, token_type="bearer")

    async def set_default_user_role(self, user_id: int):
        """Assign default role to newly registered user"""
        default_role_id = 4
        await self.repository.assign_default_role_to_user(user_id, default_role_id)

    async def get_current_user(self, user_id: int) -> UserResponse:
        """Get current authenticated user details"""
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        roles = await self.repository.get_user_roles(user_id)
        return UserResponse(
            id=user.id, email=user.email, fullName=user.full_name,
            profilePhoto=user.profile_photo, orcidId=user.orcid_id,
            bio=user.bio, position=user.position, institution=user.institution,
            roles=roles, createdAt=user.created_at, updatedAt=user.updated_at
        )