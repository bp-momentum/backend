# Generated by Django 3.2.9 on 2021-11-29 15:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('BPBackendDjango', '0003_auto_20211119_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='exerciseinplan',
            name='date',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AddField(
            model_name='exerciseinplan',
            name='repeats_per_set',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='exerciseinplan',
            name='sets',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trainer',
            name='email_address',
            field=models.CharField(default='', max_length=254),
        ),
        migrations.AddField(
            model_name='user',
            name='email_address',
            field=models.CharField(default='', max_length=254),
        ),
        migrations.AlterField(
            model_name='doneexercises',
            name='date',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='user',
            name='trainer',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='BPBackendDjango.trainer'),
        ),
    ]