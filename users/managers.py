from django.contrib.auth.base_user import BaseUserManager
import logging
logger = logging.getLogger("mylogger")


class AccountManager(BaseUserManager):
    def create_user(self, email, name=None, password=None, **extra_fields):
        logger.info(extra_fields)
        fb_auth = False
        if not email:
            raise ValueError("Users must have an email address.")
        if not name:
            raise ValueError("Users must have a name.")

        if fb_auth:
            user = self.model(
                email=self.normalize_email(email),
                # name=kwargs.get('name')
            )
        else:
            user = self.model(
                email=self.normalize_email(email),
                name=name
            )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            name=name
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user