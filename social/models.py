from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='sent')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
    
    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("You cannot send a friend request to yourself.")

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"
