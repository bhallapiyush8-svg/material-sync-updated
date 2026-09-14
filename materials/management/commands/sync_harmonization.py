import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from materials.models import (
    AuditLog,
    Material,
    MaterialGroup,
    MaterialGroupMember,
    NationalMaterial,
    NationalMaterialMapping,
)


class Command(BaseCommand):
    help = (
        "Sync generated material groups and national material "
        "master records into Django."
    )

    def handle(self, *args, **options):
        base_dir = Path.cwd()
        groups_path = base_dir / "data" / "material_groups.csv"
        national_path = base_dir / "data" / "national_master.csv"

        if not groups_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Missing file: {groups_path}"
                )
            )
            return

        if not national_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Missing file: {national_path}"
                )
            )
            return

        with transaction.atomic():
            groups_created = 0
            groups_updated = 0
            members_created = 0
            national_created = 0
            national_updated = 0
            mappings_created = 0
            audit_created = 0

            # -------------------------------------------------
            # 1. Sync candidate material groups
            # -------------------------------------------------

            with groups_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:
                    group_code = (
                        str(row["group_id"])
                        .strip()
                    )

                    candidate_description = (
                        str(row["candidate_description"])
                        .strip()
                    )

                    group, created = (
                        MaterialGroup.objects.update_or_create(
                            group_code=group_code,
                            defaults={
                                "candidate_description":
                                    candidate_description,
                                "status":
                                    "PENDING_REVIEW",
                            },
                        )
                    )

                    if created:
                        groups_created += 1
                    else:
                        groups_updated += 1

                    mappings_text = str(
                        row.get("cpse_mappings", "")
                    ).strip()

                    if not mappings_text:
                        continue

                    # Example:
                    # ONGC:ONGC-1001 |
                    # BHEL:BHEL-2201

                    for mapping in mappings_text.split("|"):
                        mapping = mapping.strip()

                        if ":" not in mapping:
                            continue

                        cpse_code, material_code = (
                            mapping.split(":", 1)
                        )

                        cpse_code = cpse_code.strip()
                        material_code = material_code.strip()

                        try:
                            material = Material.objects.get(
                                cpse__code=cpse_code,
                                material_code=material_code,
                            )
                        except Material.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    "Material not found: "
                                    f"{cpse_code}:{material_code}"
                                )
                            )
                            continue

                        _, member_created = (
                            MaterialGroupMember.objects
                            .get_or_create(
                                group=group,
                                material=material,
                                defaults={
                                    "match_confidence": 0.0,
                                },
                            )
                        )

                        if member_created:
                            members_created += 1

            # -------------------------------------------------
            # 2. Sync national material master
            # -------------------------------------------------

            with national_path.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as file:

                reader = csv.DictReader(file)

                for row in reader:
                    national_code = (
                        str(
                            row["national_material_code"]
                        ).strip()
                    )

                    standardized_description = (
                        str(
                            row[
                                "standardized_description"
                            ]
                        ).strip()
                    )

                    category = (
                        str(
                            row.get("category") or
                            "UNKNOWN"
                        ).strip()
                    )

                    status = (
                        str(
                            row.get("status") or
                            "PENDING_APPROVAL"
                        ).strip()
                    )

                    attributes = {
                        "material": row.get("material"),
                        "diameter_mm": row.get(
                            "diameter_mm"
                        ),
                        "length_mm": row.get(
                            "length_mm"
                        ),
                        "size_mm": row.get(
                            "size_mm"
                        ),
                        "pressure_rating_psi": row.get(
                            "pressure_rating_psi"
                        ),
                        "connection_type": row.get(
                            "connection_type"
                        ),
                        "bearing_number": row.get(
                            "bearing_number"
                        ),
                        "seal_type": row.get(
                            "seal_type"
                        ),
                        "wall_thickness_mm": row.get(
                            "wall_thickness_mm"
                        ),
                        "pipe_type": row.get(
                            "pipe_type"
                        ),
                    }

                    national_material, created = (
                        NationalMaterial.objects
                        .update_or_create(
                            national_code=national_code,
                            defaults={
                                "standardized_description":
                                    standardized_description,
                                "category": category,
                                "attributes": attributes,
                                "status": status,
                            },
                        )
                    )

                    if created:
                        national_created += 1
                    else:
                        national_updated += 1

                    # -------------------------------------------------
                    # 3. Create national-material mappings
                    # -------------------------------------------------

                    mappings_text = str(
                        row.get("cpse_mappings", "")
                    ).strip()

                    for mapping in mappings_text.split("|"):
                        mapping = mapping.strip()

                        if ":" not in mapping:
                            continue

                        cpse_code, material_code = (
                            mapping.split(":", 1)
                        )

                        cpse_code = cpse_code.strip()
                        material_code = material_code.strip()

                        try:
                            material = Material.objects.get(
                                cpse__code=cpse_code,
                                material_code=material_code,
                            )
                        except Material.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    "National mapping skipped; "
                                    "material not found: "
                                    f"{cpse_code}:"
                                    f"{material_code}"
                                )
                            )
                            continue

                        _, mapping_created = (
                            NationalMaterialMapping.objects
                            .get_or_create(
                                national_material=
                                    national_material,
                                material=material,
                                defaults={
                                    "mapping_confidence": 0.0,
                                },
                            )
                        )

                        if mapping_created:
                            mappings_created += 1

                    # -------------------------------------------------
                    # 4. Audit
                    # -------------------------------------------------

                    AuditLog.objects.create(
                        action="NATIONAL_MASTER_SYNC",
                        entity_type="NationalMaterial",
                        entity_id=str(
                            national_material.id
                        ),
                        user="system",
                        details={
                            "national_code":
                                national_code,
                            "source_group":
                                row.get("source_group"),
                            "member_count":
                                row.get("member_count"),
                        },
                    )

                    audit_created += 1

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Harmonization database sync complete."
            )
        )

        self.stdout.write(
            f"Groups created       : {groups_created}"
        )

        self.stdout.write(
            f"Groups updated       : {groups_updated}"
        )

        self.stdout.write(
            f"Group members created: {members_created}"
        )

        self.stdout.write(
            f"National materials created: "
            f"{national_created}"
        )

        self.stdout.write(
            f"National materials updated: "
            f"{national_updated}"
        )

        self.stdout.write(
            f"National mappings created: "
            f"{mappings_created}"
        )

        self.stdout.write(
            f"Audit logs created   : {audit_created}"
        )