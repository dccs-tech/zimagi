# Generated by Django 2.1.3 on 2019-02-24 15:23

from django.db import migrations, models
import django.db.models.deletion
import systems.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='config',
            field=systems.models.fields.EncryptedDataField(default={}),
        ),
        migrations.AddField(
            model_name='group',
            name='state_config',
            field=systems.models.fields.EncryptedDataField(default={}),
        ),
        migrations.AddField(
            model_name='group',
            name='type',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='variables',
            field=systems.models.fields.EncryptedDataField(default={}),
        ),
        migrations.AlterField(
            model_name='group',
            name='environment',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='environment.Environment'),
        ),
    ]