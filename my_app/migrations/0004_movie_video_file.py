# Generated migration to add video_file field to Movie model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0003_movie_telegram_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='video_file',
            field=models.FileField(blank=True, help_text='Yoki video faylni yuklang (mp4, mkv va b.)', null=True, upload_to='movies/videos/'),
        ),
    ]

