# Generated by Django 4.1 on 2022-10-01 15:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('borrow', '0004_remove_attribute_category_remove_attribute_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributevalue',
            name='attribue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='attribues', to='borrow.attribute'),
        ),
    ]