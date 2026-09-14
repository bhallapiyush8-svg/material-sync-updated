
import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from materials.models import CPSE, Material


class Command(BaseCommand):
    help = "Import material master data from data/materials.csv"

    def handle(self, *args, **options):

        # -----------------------------------------------------
        # Locate the project root
        # -----------------------------------------------------

        project_root = Path(
            __file__
        ).resolve().parents[3]

        csv_path = (
            project_root
            / "data"
            / "materials.csv"
        )

        if not csv_path.exists():

            self.stdout.write(
                self.style.ERROR(
                    f"CSV file not found:\n{csv_path}"
                )
            )

            return

        # -----------------------------------------------------
        # Counters
        # -----------------------------------------------------

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # -----------------------------------------------------
        # Read CSV
        # -----------------------------------------------------

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            required_columns = {
                "cpse",
                "material_code",
                "description",
                "unit",
            }

            actual_columns = set(
                reader.fieldnames or []
            )

            missing_columns = (
                required_columns
                - actual_columns
            )

            if missing_columns:

                self.stdout.write(
                    self.style.ERROR(
                        "Missing CSV columns: "
                        + ", ".join(
                            sorted(
                                missing_columns
                            )
                        )
                    )
                )

                return

            # -------------------------------------------------
            # Import each row
            # -------------------------------------------------

            for row in reader:

                cpse_code = row[
                    "cpse"
                ].strip()

                material_code = row[
                    "material_code"
                ].strip()

                description = row[
                    "description"
                ].strip()

                unit = row[
                    "unit"
                ].strip()

                # ---------------------------------------------
                # Basic validation
                # ---------------------------------------------

                if not cpse_code:
                    skipped_count += 1
                    continue

                if not material_code:
                    skipped_count += 1
                    continue

                if not description:
                    skipped_count += 1
                    continue

                # ---------------------------------------------
                # CPSE
                # ---------------------------------------------

                cpse, _ = (
                    CPSE.objects.get_or_create(
                        code=cpse_code,
                        defaults={
                            "name": cpse_code,
                        },
                    )
                )

                # ---------------------------------------------
                # Material
                # ---------------------------------------------

                material, created = (
                    Material.objects.update_or_create(
                        cpse=cpse,
                        material_code=material_code,
                        defaults={
                            "description":
                                description,

                            "unit":
                                unit,
                        },
                    )
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        # -----------------------------------------------------
        # Final output
        # -----------------------------------------------------

        self.stdout.write(
            self.style.SUCCESS(
                "\nMaterial import completed."
            )
        )

        self.stdout.write(
            f"Created : {created_count}"
        )

        self.stdout.write(
            f"Updated : {updated_count}"
        )

        self.stdout.write(
            f"Skipped : {skipped_count}"
        )
