from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class MyUserManager(BaseUserManager):

  def create_user(self, username, phone_number, email=None, password=None):
    if not username:
      raise ValueError('کاربران باید حتماً نام کاربری داشته باشند.')
    if not phone_number:
      raise ValueError('کاربران باید حتماً شماره تلفن داشته باشند.')

    user = self.model(
        username=username,
        phone_number=phone_number,
        email=self.normalize_email(email) if email else None,
    )
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(
      self, username, phone_number, email=None, password=None
  ):
    user = self.create_user(
        username=username,
        phone_number=phone_number,
        email=email,
        password=password,
    )
    user.is_admin = True
    user.save(using=self._db)
    return user


class MyUser(AbstractBaseUser):
  username = models.CharField(max_length=150, unique=True)
  email = models.EmailField(max_length=254, unique=True, blank=True, null=True)
  phone_number = models.CharField(max_length=11, unique=True)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)

  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['phone_number']

  objects = MyUserManager()

  def __str__(self):
    return self.username

  def has_perm(self, perm, obj=None):
    return self.is_admin

  def has_module_perms(self, app_label):
    return self.is_admin

  @property
  def is_staff(self):
    return self.is_admin

class Profile(models.Model):
    user = models.OneToOneField(
    MyUser,
    on_delete=models.CASCADE,
    related_name='profile',
    verbose_name='کاربر',
)
    avatar = models.ImageField(upload_to='avatars',blank=True)
    bio = models.TextField(blank=True)
    full_name = models.CharField(max_length=150,blank=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"
@receiver(post_save, sender=MyUser)
def create_user_profile(sender, instance, created, **kwargs):
  if created:
    Profile.objects.create(user=instance)
