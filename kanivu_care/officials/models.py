from django.db import models
from django.contrib.auth.models import User

class ReportRequest(models.Model):
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="report_requests")
    requested_to_role = models.CharField(max_length=20, choices=(("coordinator", "Coordinator"), ("convenier", "Convenor")))
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    report_file = models.FileField(upload_to="reports/", null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Report: {self.title} by {self.requested_by.username}"

class FundRequest(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_fund_requests")
    title = models.CharField(max_length=255)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_fund_requests")
    submitted_at = models.DateTimeField(auto_now_add=True)
    action_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Fund Request: {self.title} - {self.amount}"
