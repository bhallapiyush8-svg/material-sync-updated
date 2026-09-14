
from django.db import models


class CPSE(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
    )

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.name} ({self.code})"


class Material(models.Model):
    cpse = models.ForeignKey(
        CPSE,
        on_delete=models.CASCADE,
        related_name="materials",
    )

    material_code = models.CharField(
        max_length=100,
    )

    description = models.TextField()

    unit = models.CharField(
        max_length=50,
        blank=True,
    )

    normalized_description = models.TextField(
        blank=True,
    )

    attributes = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cpse", "material_code"],
                name="unique_cpse_material_code",
            )
        ]

    def __str__(self):
        return f"{self.cpse.code} - {self.material_code}"


class MaterialMatch(models.Model):
    material_a = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="matches_as_a",
    )

    material_b = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="matches_as_b",
    )

    semantic_score = models.FloatField()

    attribute_score = models.FloatField()

    final_score = models.FloatField()

    critical_mismatch = models.BooleanField(
        default=False,
    )

    classification = models.CharField(
        max_length=50,
    )

    explanation = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.material_a.material_code} "
            f"<-> "
            f"{self.material_b.material_code}"
        )


class MaterialGroup(models.Model):
    group_code = models.CharField(
        max_length=100,
        unique=True,
    )

    candidate_description = models.TextField()

    confidence = models.FloatField(
        default=0.0,
    )

    status = models.CharField(
        max_length=50,
        default="PENDING_REVIEW",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.group_code


class MaterialGroupMember(models.Model):
    group = models.ForeignKey(
        MaterialGroup,
        on_delete=models.CASCADE,
        related_name="members",
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="group_memberships",
    )

    match_confidence = models.FloatField(
        default=0.0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["group", "material"],
                name="unique_group_material",
            )
        ]


class NationalMaterial(models.Model):
    national_code = models.CharField(
        max_length=150,
        unique=True,
    )

    standardized_description = models.TextField()

    category = models.CharField(
        max_length=100,
    )

    attributes = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=50,
        default="PENDING_APPROVAL",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.national_code} - "
            f"{self.standardized_description}"
        )


class NationalMaterialMapping(models.Model):
    national_material = models.ForeignKey(
        NationalMaterial,
        on_delete=models.CASCADE,
        related_name="cpse_mappings",
    )

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="national_mappings",
    )

    mapping_confidence = models.FloatField(
        default=0.0,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["national_material", "material"],
                name="unique_national_material_mapping",
            )
        ]


class Approval(models.Model):
    ACTION_CHOICES = [
        ("APPROVE", "Approve"),
        ("REJECT", "Reject"),
        ("MODIFY", "Modify"),
    ]

    material_group = models.ForeignKey(
        MaterialGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approvals",
    )

    national_material = models.ForeignKey(
        NationalMaterial,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="approvals",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )

    reviewer = models.CharField(
        max_length=200,
    )

    comments = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.action} by {self.reviewer}"


class AuditLog(models.Model):
    action = models.CharField(
        max_length=100,
    )

    entity_type = models.CharField(
        max_length=100,
    )

    entity_id = models.CharField(
        max_length=100,
    )

    user = models.CharField(
        max_length=200,
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.action} - "
            f"{self.entity_type} - "
            f"{self.entity_id}"
        )



# Create your models here.
