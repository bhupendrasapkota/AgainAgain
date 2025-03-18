# Generated by Django 5.1.6 on 2025-03-17 13:48

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(help_text='Upload a photo (JPG, JPEG, PNG, GIF)', upload_to='photos/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])]),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['user'], name='photos_phot_user_id_f39ddb_idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['is_public'], name='photos_phot_is_publ_2d152c_idx'),
        ),
    ]
