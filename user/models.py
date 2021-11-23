from django.db import models

from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField
import uuid
from django.dispatch import receiver


class MyUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password, profile_pic):
        if not email:
            raise ValueError("Email Required")
        if not first_name:
            raise ValueError("First Name Required")
        if not last_name:
            raise ValueError("Last Name Required")
        
        
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            username=username,
            profile_pic=profile_pic,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, first_name, last_name, password):
        user = self.create_user(email, username, first_name, last_name, password)
        user.admin = True
        user.staff = True
        user.superuser = True
        user.save(using=self._db)
        return user




class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = CharField(max_length=25, unique=True)
    first_name = CharField(max_length=70)
    last_name = CharField(max_length=70)
    profile_pic = models.ImageField(null=True)

    
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email'] # Email & Password are required by default.

    objects = MyUserManager()
    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin
    
    @property
    def is_superuser(self):
        "Is the user a admin member?"
        return self.admin
    