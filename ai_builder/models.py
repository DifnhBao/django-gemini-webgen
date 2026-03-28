from django.conf import settings
from django.db import models
from django.utils import timezone


class GeneratedWebsite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_websites')
    topic = models.CharField(max_length=255)
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def __str__(self):
        return f"{self.topic} by {self.user.username}"
