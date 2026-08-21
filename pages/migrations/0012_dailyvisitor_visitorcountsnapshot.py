from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0011_sitesettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyVisitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.DateField()),
                ('visitor_id', models.CharField(max_length=64)),
                ('first_seen_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VisitorCountSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('checked_at', models.DateTimeField(auto_now_add=True)),
                ('visitor_count', models.PositiveIntegerField()),
            ],
            options={'ordering': ('-checked_at',)},
        ),
        migrations.AddConstraint(
            model_name='dailyvisitor',
            constraint=models.UniqueConstraint(fields=('day', 'visitor_id'), name='unique_daily_visitor'),
        ),
    ]