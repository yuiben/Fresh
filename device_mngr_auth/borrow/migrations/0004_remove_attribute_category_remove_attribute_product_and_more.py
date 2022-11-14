# Generated by Django 4.1 on 2022-10-01 15:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0003_attribute_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attribute',
            name='category',
        ),
        migrations.RemoveField(
            model_name='attribute',
            name='product',
        ),
        migrations.RemoveField(
            model_name='attribute',
            name='value',
        ),
        migrations.CreateModel(
            name='AttributeValue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('deleted_at', models.DateTimeField(default=None, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('value', models.CharField(default=None, max_length=100, null=True)),
                ('attribue', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attribue', to='borrow.attribute')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='borrow.product')),
            ],
            options={
                'db_table': 'AttributeValue',
            },
        ),
    ]
