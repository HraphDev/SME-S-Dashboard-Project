import uuid
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_fill_invitation_tokens'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='invitation_token',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True),
        ),
    ]
