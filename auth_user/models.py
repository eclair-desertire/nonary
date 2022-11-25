from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from imagekit.models import ProcessedImageField

from utils.models import BaseModel
from utils.tokens import create_verification_code, generate_password


class UserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """
        if not phone_number:
            raise ValueError('The given phone_number must be set')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('verification_code', create_verification_code())
        if password is None:
            password = generate_password()
        return self._create_user(phone_number, password, **extra_fields)

    def create_staff(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        email = email.lower()
        return self._create_user(email, password, **extra_fields)

    def create_admin(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=70, blank=True, null=True)
    new_email = models.EmailField(max_length=70, blank=True, null=True)
    phone_number = models.CharField(max_length=70, unique=True)
    first_name = models.CharField(max_length=500, blank=True, null=True)
    last_name = models.CharField(max_length=500, blank=True, null=True)
    middle_name = models.CharField(max_length=500, blank=True, null=True)
    city = models.ForeignKey('location.City', on_delete=models.SET_NULL, blank=True, null=True)
    old_phone_number = models.CharField(max_length=70, blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    avatar = ProcessedImageField(upload_to='avatars', processors=[], format='WEBP', options={'quality': 60},
                                 null=True, blank=True, verbose_name='Аватар')

    updated_at = models.DateTimeField(auto_now=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    selected_card = models.ForeignKey('auth_user.UserCard', on_delete=models.SET_NULL, null=True, related_name='users')
    is_common = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number'

    @property
    def full_name(self):
        first_name = self.first_name if self.first_name else ''
        last_name = self.last_name if self.last_name else ''
        middle_name = self.middle_name if self.middle_name else ''
        full_name = f"{last_name} {first_name} {middle_name}".strip()
        return full_name if len(full_name) > 0 else 'Данные не заполнены!'

    objects = UserManager()

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class BadSMS(BaseModel):
    phone_number = models.CharField(max_length=200)
    is_called = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    code = models.IntegerField()


class QuestionCategory(BaseModel):
    name = models.CharField(max_length=2000, verbose_name='Название')
    icon = ProcessedImageField(upload_to='question_categories', processors=[], format='ico', options={'quality': 60},
                               null=True, blank=True, verbose_name='Иконка')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию вопросов'
        verbose_name_plural = 'Категории вопросов'
        ordering = ('position', )


class Question(BaseModel):
    question = models.TextField(verbose_name='Вопрос')
    category = models.ForeignKey(QuestionCategory, on_delete=models.CASCADE, related_name='questions',
                                 verbose_name='Категория вопросов', null=True)
    answer = models.TextField(verbose_name='Ответ')

    class Meta:
        verbose_name = 'Вопросы и ответы'
        verbose_name_plural = 'Вопросы и ответы'
        ordering = ('position', )


class UsefulQuestion(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='useful_questions')
    is_useful = models.BooleanField(default=True)


class FavouriteProduct(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE, related_name='favourites')


class UserCard(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    pan = models.CharField(max_length=250)
    brand = models.CharField(max_length=250, blank=True)
    card_token = models.TextField()
