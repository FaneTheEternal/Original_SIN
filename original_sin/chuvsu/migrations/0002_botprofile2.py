# Generated by Django 3.1.7 on 2021-08-30 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chuvsu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotProfile2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_guid', models.TextField()),
                ('current', models.TextField(default='')),
                ('back', models.TextField(default='', help_text='work as stack', verbose_name='cls1;cls2')),
            ],
        ),
    ]
