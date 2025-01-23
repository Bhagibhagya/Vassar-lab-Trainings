from django.db import models
from uuid import uuid4
# Create your models here.

class ComplianceReport(models.Model):
    report_id = models.UUIDField(primary_key=True, default=uuid4(), editable=False)  # Primary key
    customer_uuid = models.UUIDField(null=True, blank=True) 
    project_id = models.CharField(max_length=45, null=True, blank=True)
    report = models.JSONField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'compliance_report'