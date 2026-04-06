from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0005_movieepisode_video_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='home_featured_order',
            field=models.PositiveSmallIntegerField(default=0, help_text="Kichik raqam avval ko'rsatiladi"),
        ),
        migrations.AddField(
            model_name='movie',
            name='is_home_featured',
            field=models.BooleanField(default=False, help_text="Bosh sahifa hero fonida ko'rsatish uchun belgilang"),
        ),
    ]
