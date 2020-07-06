# Generated by Django 3.0.8 on 2020-07-03 23:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import utils.custom_fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', utils.custom_fields.FarsiCharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', utils.custom_fields.FarsiCharField(blank=True, max_length=30, verbose_name='last name')),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True, verbose_name='mobile number')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='birth date')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='users/avatars/%Y/%m/', verbose_name='Avatar')),
                ('avatar_thumbnail', models.ImageField(blank=True, editable=False, upload_to='users/avatars-thumbnails/%Y/%m/', verbose_name='avatar thumbnail')),
                ('key', models.CharField(blank=True, max_length=50, unique=True, verbose_name='key')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselected this instead of deleting accounts.', verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('referral', models.OneToOneField(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='UserScoreTransaction',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('type', models.CharField(choices=[('Profile', 'Profile'), ('Referral', 'Referral')], max_length=10)),
                ('point', models.PositiveIntegerField(default=0, verbose_name='point')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_score_transactions', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'user scores transaction',
                'verbose_name_plural': 'users scores transactions',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserScore',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('type', models.CharField(choices=[('Profile', 'Profile'), ('Referral', 'Referral')], max_length=10)),
                ('point', models.PositiveIntegerField(default=0, verbose_name='point')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_score', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'user scores',
                'verbose_name_plural': 'users scores',
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Creation On')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Modified On')),
                ('address', utils.custom_fields.FarsiTextField(max_length=300, verbose_name='address')),
                ('coordinates', models.CharField(blank=True, max_length=50, null=True, verbose_name='Coordinates')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_addresses', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'user addresses',
                'verbose_name_plural': 'users addresses',
            },
        ),
        migrations.AddConstraint(
            model_name='userscore',
            constraint=models.UniqueConstraint(fields=('user', 'type'), name='user_score_type'),
        ),
    ]
