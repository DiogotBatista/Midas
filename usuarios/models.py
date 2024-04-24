from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class CustomuserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo Email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    first_name = models.CharField("Nome", max_length=40)
    last_name = models.CharField('Sobrenome', max_length=40, db_index=True)
    data_cadastro = models.DateField('Data de cadastro', auto_now_add=True, editable=False, blank=True)
    last_access = models.DateTimeField('Último Acesso', blank=True, null=True)


    objects = CustomuserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def is_in_equipe_group(self):
        return self.groups.filter(name='usuario').exists()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email

class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    ordenacao = models.IntegerField('Ordenação')

    class Meta:
        ordering = ['ordenacao']

    def __str__(self):
        return self.titulo
