from django.db import models
from django.contrib.auth.models import User

class Xray(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="xrays")

    image = models.ImageField(upload_to="xrays/%Y/%m/%d/")
    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("done", "Done"), ("failed", "Failed")],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Xray #{self.id} - {self.user.username} - {self.created_at:%Y-%m-%d %H:%M}"



class Prediction(models.Model):
    xray = models.ForeignKey(
        "Xray",
        on_delete=models.CASCADE,
        related_name="predictions"
    )

    label = models.CharField(max_length=120)          # Hastalık adı
    region = models.CharField(max_length=120, blank=True)
    score = models.FloatField()                        # 0–100 arası güven skoru

    # YOLO bounding box (opsiyonel)
    x1 = models.FloatField(null=True, blank=True)
    y1 = models.FloatField(null=True, blank=True)
    x2 = models.FloatField(null=True, blank=True)
    y2 = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.label} - %{self.score:.1f}"

