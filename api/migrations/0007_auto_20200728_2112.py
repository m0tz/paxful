# Generated by Django 3.0.8 on 2020-07-28 21:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_auto_20200728_2059"),
    ]

    operations = [
        migrations.RemoveField(model_name="statictics", name="transactions",),
        migrations.AddField(model_name="statictics", name="total_transactions", field=models.IntegerField(default=0),),
    ]
