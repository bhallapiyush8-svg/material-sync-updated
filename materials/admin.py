
from django.contrib import admin

from .models import (
    CPSE,
    Material,
    MaterialMatch,
    MaterialGroup,
    MaterialGroupMember,
    NationalMaterial,
    NationalMaterialMapping,
    Approval,
    AuditLog,
)


@admin.register(CPSE)
class CPSEAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "created_at",
    )

    search_fields = (
        "name",
        "code",
    )


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "material_code",
        "cpse",
        "description",
        "unit",
        "created_at",
    )

    list_filter = (
        "cpse",
        "unit",
    )

    search_fields = (
        "material_code",
        "description",
    )


@admin.register(MaterialMatch)
class MaterialMatchAdmin(admin.ModelAdmin):
    list_display = (
        "material_a",
        "material_b",
        "semantic_score",
        "attribute_score",
        "final_score",
        "classification",
        "critical_mismatch",
    )

    list_filter = (
        "classification",
        "critical_mismatch",
    )


@admin.register(MaterialGroup)
class MaterialGroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_code",
        "candidate_description",
        "confidence",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "group_code",
        "candidate_description",
    )


@admin.register(MaterialGroupMember)
class MaterialGroupMemberAdmin(admin.ModelAdmin):
    list_display = (
        "group",
        "material",
        "match_confidence",
        "created_at",
    )


@admin.register(NationalMaterial)
class NationalMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "national_code",
        "standardized_description",
        "category",
        "status",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
    )

    search_fields = (
        "national_code",
        "standardized_description",
    )


@admin.register(NationalMaterialMapping)
class NationalMaterialMappingAdmin(admin.ModelAdmin):
    list_display = (
        "national_material",
        "material",
        "mapping_confidence",
        "created_at",
    )


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "reviewer",
        "material_group",
        "national_material",
        "created_at",
    )

    list_filter = (
        "action",
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "entity_type",
        "entity_id",
        "user",
        "created_at",
    )

    list_filter = (
        "action",
        "entity_type",
    )

    search_fields = (
        "entity_id",
        "user",
    )

