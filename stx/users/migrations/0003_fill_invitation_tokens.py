import uuid
from django.db import migrations

def fill_invitation_tokens(apps, schema_editor):
    CustomUser = apps.get_model('users', 'CustomUser')
    for user in CustomUser.objects.filter(invitation_token__isnull=True):
        user.invitation_token = uuid.uuid4()
        user.save(update_fields=['invitation_token'])

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_invitation_token_no_unique'),
    ]

    operations = [
        migrations.RunPython(fill_invitation_tokens),
    ]
