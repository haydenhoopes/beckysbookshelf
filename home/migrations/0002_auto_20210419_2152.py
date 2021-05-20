# Generated by Django 3.2 on 2021-04-20 03:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authors',
            name='PrimaryTopic',
            field=models.ForeignKey(db_column='PrimaryTopic', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.topics'),
        ),
        migrations.AlterField(
            model_name='books',
            name='AuthorID',
            field=models.ForeignKey(db_column='AuthorID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.authors'),
        ),
        migrations.AlterField(
            model_name='books',
            name='PublisherID',
            field=models.ForeignKey(db_column='PublisherID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.publishers'),
        ),
        migrations.AlterField(
            model_name='books',
            name='SeriesID',
            field=models.ForeignKey(db_column='SeriesID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.series'),
        ),
        migrations.AlterField(
            model_name='books',
            name='TopicID',
            field=models.ForeignKey(db_column='TopicID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.topics'),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='BookID',
            field=models.ForeignKey(db_column='BookID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.books'),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='ConditionID',
            field=models.ForeignKey(db_column='ConditionID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.conditions'),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='CoverID',
            field=models.ForeignKey(db_column='CoverID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.covertype'),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='CustomerID',
            field=models.ForeignKey(db_column='CustomerID', db_constraint=False, on_delete=django.db.models.deletion.CASCADE, to='home.customers'),
        ),
    ]
