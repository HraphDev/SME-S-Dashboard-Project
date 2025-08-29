from datetime import timedelta
from django.utils import timezone 
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    full_name = models.CharField(max_length=150)  
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_login = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    invitation_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email' 
    REQUIRED_FIELDS = ['full_name', 'role']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if not self.invitation_token:
            self.invitation_token = uuid.uuid4()
            self.token_expiry = timezone.now() + timedelta(days=2)
        super().save(*args, **kwargs)
        
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:20]}"        