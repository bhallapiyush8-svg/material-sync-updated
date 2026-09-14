
from itertools import combinations

from django.core.management.base import BaseCommand

from materials.models import (
    Material,
    MaterialMatch,
)

# Import the AI matching engine from our ML prototype.
from ml.matcher import compare_materials


class Command(BaseCommand):
    help = "Run AI-based material harmonization on Django materials."

    def handle(self, *args, **options):

        materials = list(
            Material.objects.select_related("cpse").all()
        )

        total_materials = len(materials)

        if total_materials == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No materials found in the database."
                )
            )
            return

        self.stdout.write(
            f"Materials loaded: {total_materials}"
        )

        created_matches = 0
        skipped_same_cpse = 0

        # -----------------------------------------------------
        # Compare every cross-CPSE pair
        # -----------------------------------------------------

        for material_a, material_b in combinations(
            materials,
            2,
        ):

            # Only compare records belonging to different CPSEs.
            if material_a.cpse_id == material_b.cpse_id:
                skipped_same_cpse += 1
                continue

            result = compare_materials(
                material_a.description,
                material_b.description,
            )

            # Avoid duplicate database entries if the command
            # is executed again.
            _, created = (
                MaterialMatch.objects.update_or_create(
                    material_a=material_a,
                    material_b=material_b,
                    defaults={
                        "semantic_score":
                            result["semantic_score"],

                        "attribute_score":
                            result["attribute_score"],

                        "final_score":
                            result["final_score"],

                        "critical_mismatch":
                            result["critical_mismatch"],

                        "classification":
                            result["classification"],

                        "explanation": {
                            "attributes_a":
                                result["attributes_a"],

                            "attributes_b":
                                result["attributes_b"],
                        },
                    },
                )
            )

            if created:
                created_matches += 1

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "\nHarmonization matching complete."
            )
        )

        self.stdout.write(
            f"Total materials        : {total_materials}"
        )

        self.stdout.write(
            f"New match records      : {created_matches}"
        )

        self.stdout.write(
            f"Same-CPSE pairs skipped: {skipped_same_cpse}"
        )

        self.stdout.write(
            f"Total DB matches       : "
            f"{MaterialMatch.objects.count()}"
        )
