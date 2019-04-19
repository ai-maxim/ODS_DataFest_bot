# Generated by Django 2.1.7 on 2019-04-19 06:17
from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies = [
        ('backend', '0011_auto_20190415_2105'),
    ]
    operations = [
        migrations.CreateModel(
            name='RandomBeerUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tg_user_id', models.IntegerField(unique=True)),
                ('tg_nickname', models.TextField(default=None, null=True)),
                ('ods_nickname', models.TextField(default=None, null=True)),
                ('social_network_link', models.TextField(default=None, null=True)),
                ('random_beer_try', models.IntegerField(default=None, null=True)),
                ('prev_pair', models.IntegerField(default=None, null=True)),
                ('accept_rules', models.BooleanField(default=False)),
                ('is_busy', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='tguser',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),
    ]