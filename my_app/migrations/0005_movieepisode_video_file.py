# Generated migration to add video_file field to MovieEpisode model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_movie_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='movieepisode',
            name='video_file',
            field=models.FileField(blank=True, help_text='Yoki video faylni yuklang (mp4, mkv va b.)', null=True, upload_to='videos/'),
        ),
    ]

