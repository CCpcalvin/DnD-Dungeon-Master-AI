# Generated by Django 5.2.2 on 2025-06-29 11:33

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('theme', models.CharField(blank=True, max_length=255, null=True)),
                ('current_floor', models.IntegerField(default=0)),
                ('game_state', models.CharField(choices=[('Player Creation', 'Player Creation'), ('In Progress', 'In Progress'), ('Waiting for Next Floor', 'Waiting For Next Floor'), ('Completed', 'Completed')], default='In Progress', max_length=25)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('Player', 'Player'), ('Narrator', 'Narrator'), ('System', 'System')], max_length=20)),
                ('content', models.TextField()),
                ('suggested_actions', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='api.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='FloorHistoryModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.JSONField()),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='floor_history', to='api.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='NonCombatFloorModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('floor_type', models.CharField(choices=[('Treasure', 'Treasure'), ('Treasure with Trap', 'Treasure With Trap'), ('Hidden Trap', 'Hidden Trap'), ('NPC Encounter', 'Npc Encounter')], default='Treasure', max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('penalty', models.FloatField(default=0)),
                ('completion_rate', models.IntegerField(default=0)),
                ('floor_history_model', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='non_combat_floor_model', to='api.floorhistorymodel')),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='non_combat_floor_model', to='api.gamesession')),
            ],
        ),
        migrations.CreateModel(
            name='PlayerInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_name', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField()),
                ('current_health', models.IntegerField(default=10)),
                ('max_health', models.IntegerField(default=10)),
                ('strength', models.IntegerField(blank=True, null=True)),
                ('dexterity', models.IntegerField(blank=True, null=True)),
                ('constitution', models.IntegerField(blank=True, null=True)),
                ('intelligence', models.IntegerField(blank=True, null=True)),
                ('wisdom', models.IntegerField(blank=True, null=True)),
                ('charisma', models.IntegerField(blank=True, null=True)),
                ('session', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player', to='api.gamesession')),
            ],
        ),
    ]
