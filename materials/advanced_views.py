import math
import re
from typing import Any, Dict, List

from django.http import JsonResponse
from django.shortcuts import render

# =========================================================
# DEMO MATERIALS
# =========================================================

DEMO_MATERIALS = [
    {
        "code": "ONGC-1001",
        "cpse": "ONGC",
        "description": "HEX BOLT M10 X 50 SS304",
        "category": "BOLT",
        "material": "SS304",
        "diameter": 10,
        "length": 50,
        "unit_price": 18.5,
    },
    {
        "code": "NTPC-4401",
        "cpse": "NTPC",
        "description": "HEXAGONAL BOLT M10 X 50 MM SS304",
        "category": "BOLT",
        "material": "SS304",
        "diameter": 10,
        "length": 50,
        "unit_price": 21.5,
    },
    {
        "code": "SAIL-3101",
        "cpse": "SAIL",
        "description": "HEX BOLT M10*50 STAINLESS STEEL 304",
        "category": "BOLT",
        "material": "SS304",
        "diameter": 10,
        "length": 50,
        "unit_price": 19.8,
    },
    {
        "code": "HPCL-2008",
        "cpse": "HPCL",
        "description": "SS316 FLANGED BALL VALVE 2 INCH 150 PSI",
        "category": "BALL_VALVE",
        "material": "SS316",
        "diameter": 50,
        "pressure": 150,
        "unit_price": 32000,
    },
    {
        "code": "BHEL-7781",
        "cpse": "BHEL",
        "description": "SEAMLESS SS304 PIPE OD 50 MM WT 3 MM",
        "category": "PIPE",
        "material": "SS304",
        "diameter": 50,
        "wall_thickness": 3,
        "unit_price": 2800,
    },
]


# =========================================================
# COMPLIANCE RULES MATRIX (EXPANDED FOR 13 CLASSES & 11 CONDITIONS)
# =========================================================

COMPLIANCE_MATERIAL_CLASSES = [
    {"value": "BALL_VALVE", "label": "Ball Valve"},
    {"value": "GATE_VALVE", "label": "Gate Valve"},
    {"value": "GLOBE_VALVE", "label": "Globe Valve"},
    {"value": "PIPE", "label": "Seamless / Welded Pipe"},
    {"value": "FLANGE", "label": "Flange (WNRF / Blind / Slip-on)"},
    {"value": "BOLT", "label": "Bolt & Fasteners (SS / High-Tensile)"},
    {"value": "BEARING", "label": "Bearing (Deep Groove / Roller)"},
    {"value": "GASKET", "label": "Gasket (Spiral Wound / RTJ / PTFE)"},
    {"value": "PUMP", "label": "Centrifugal / Process Pump"},
    {"value": "COMPRESSOR", "label": "Compressor (Gas / Air)"},
    {"value": "PRESSURE_VESSEL", "label": "Pressure Vessel / Column"},
    {"value": "FITTING", "label": "Fitting (Elbow / Tee / Reducer)"},
    {"value": "MECHANICAL_SEAL", "label": "Mechanical Seal (Cartridge / API 682)"},
]

COMPLIANCE_CONDITIONS = [
    {"value": "SOUR_GAS", "label": "Sour Gas Service (H₂S Present)"},
    {"value": "HIGH_PRESSURE", "label": "High Pressure (> 100 bar / Class 600+)"},
    {"value": "HIGH_TEMPERATURE", "label": "High Temperature (> 250°C)"},
    {"value": "CORROSIVE_SERVICE", "label": "Corrosive Medium (Wet CO₂ / Acid / Alkali)"},
    {"value": "CRITICAL_SERVICE", "label": "Critical Process Safety / Lethal Service"},
    {"value": "ROTATING_EQUIPMENT", "label": "Rotating Equipment Dynamic Duty"},
    {"value": "OFFSHORE_SERVICE", "label": "Offshore / Marine Saline Environment"},
    {"value": "HYDROGEN_SERVICE", "label": "High-Pressure Hydrogen (Embrittlement Risk)"},
    {"value": "CRYOGENIC_SERVICE", "label": "Cryogenic Service (LNG / Sub-zero <-46°C)"},
    {"value": "STEAM_SERVICE", "label": "Superheated High-Pressure Steam"},
    {"value": "CHEMICAL_SERVICE", "label": "Aggressive Chemical Service"},
]

COMPLIANCE_RULES = [
    # ---------------- BALL VALVE ----------------
    {
        "material_class": "BALL_VALVE",
        "condition": "SOUR_GAS",
        "requirement": "NACE MR0175 / ISO 15156 Certification",
        "severity": "BLOCKING",
        "rule_text": "Sour-service ball valves require certified SSC/SCC resistant body, trim, and Bolting per NACE MR0175. Standard SS304/SS316 without HRC < 22 heat treatment cannot be substituted.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME B16.34 / API 6D Pressure Rating Verification",
        "severity": "BLOCKING",
        "rule_text": "Valve body wall thickness and seat design must conform to ASME Class 600/900/1500 shell test limits before equivalence approval.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "HIGH_TEMPERATURE",
        "requirement": "Seat/Seal Material Rating (PTFE Limit 200°C)",
        "severity": "BLOCKING",
        "rule_text": "Soft-seated ball valves degrade rapidly above 200°C. Metal-seated (Stellite/tungsten carbide) construction is mandatory for service > 250°C.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "OFFSHORE_SERVICE",
        "requirement": "Inconel / Duplex Trim & Marine Coating ISO 12944-C5M",
        "severity": "WARNING",
        "rule_text": "External marine atmospheric corrosion requires C5-M protective coating and 316SS or duplex stainless hardware.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "HYDROGEN_SERVICE",
        "requirement": "Hydrogen Embrittlement & Fugitive Emission API 641",
        "severity": "BLOCKING",
        "rule_text": "Hydrogen service requires low-hardness base alloys and low-leakage certified stem seals to prevent micro-fissuring and explosive leakage.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "CRYOGENIC_SERVICE",
        "requirement": "BS 6364 Extended Bonnet & Impact Testing at -196°C",
        "severity": "BLOCKING",
        "rule_text": "Cryogenic valves require extended vapor-space bonnets and Charpy V-notch impact validation to avert brittle stem seizure.",
    },
    {
        "material_class": "BALL_VALVE",
        "condition": "CORROSIVE_SERVICE",
        "requirement": "Wetted Parts Medium Compatibility Check",
        "severity": "WARNING",
        "rule_text": "Material compatibility with process fluid (PREn index) must be checked against corrosion allowance.",
    },

    # ---------------- GATE VALVE ----------------
    {
        "material_class": "GATE_VALVE",
        "condition": "SOUR_GAS",
        "requirement": "NACE MR0175 Compliance",
        "severity": "BLOCKING",
        "rule_text": "Wedge, seat ring, and stem must comply with hardness restrictions under NACE MR0175/ISO 15156.",
    },
    {
        "material_class": "GATE_VALVE",
        "condition": "STEAM_SERVICE",
        "requirement": "ASME B16.34 & Stellite #6 Hardfacing",
        "severity": "BLOCKING",
        "rule_text": "High-pressure steam service mandates Stellite facing on wedge/seat to withstand wire-drawing erosion.",
    },
    {
        "material_class": "GATE_VALVE",
        "condition": "HIGH_PRESSURE",
        "requirement": "API 600 / API 602 Hydrostatic Shell Proof",
        "severity": "BLOCKING",
        "rule_text": "Shell wall thickness and bonnet bolting must meet minimum API 600 structural thresholds.",
    },

    # ---------------- GLOBE VALVE ----------------
    {
        "material_class": "GLOBE_VALVE",
        "condition": "CRITICAL_SERVICE",
        "requirement": "API 623 / ISO 15848-1 Tightness Class AH",
        "severity": "BLOCKING",
        "rule_text": "Critical throttling service requires anti-cavitation trim and low-emission graphite stem packing.",
    },
    {
        "material_class": "GLOBE_VALVE",
        "condition": "HIGH_TEMPERATURE",
        "requirement": "ASTM A217 Gr. WC9 / C12A Alloy Verification",
        "severity": "BLOCKING",
        "rule_text": "Standard carbon steel body suffers creep above 425°C. Chrome-moly alloy casting is required.",
    },

    # ---------------- PIPE ----------------
    {
        "material_class": "PIPE",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME B31.3 Schedule & Min Wall Thickness",
        "severity": "BLOCKING",
        "rule_text": "Pipe schedule (e.g., SCH 40 vs SCH 80 / SCH 160) determines burst rating. Lower schedule pipes cannot replace higher schedule lines.",
    },
    {
        "material_class": "PIPE",
        "condition": "SOUR_GAS",
        "requirement": "NACE TM0177 / TM0284 HIC & SSC Testing",
        "severity": "BLOCKING",
        "rule_text": "Carbon steel and stainless piping must have certified Hydrogen Induced Cracking (HIC) resistance test certificates.",
    },
    {
        "material_class": "PIPE",
        "condition": "CRYOGENIC_SERVICE",
        "requirement": "ASTM A333 Grade 6 / 304L Austenitic Impact Test",
        "severity": "BLOCKING",
        "rule_text": "Standard carbon steel pipes undergo ductile-to-brittle transition below -29°C. Cryogenic certified pipe is mandatory.",
    },
    {
        "material_class": "PIPE",
        "condition": "CORROSIVE_SERVICE",
        "requirement": "Corrosion Allowance & Material Grade Match",
        "severity": "WARNING",
        "rule_text": "Verify corrosion rate against design life before substituting SS304 with standard carbon steel.",
    },

    # ---------------- FLANGE ----------------
    {
        "material_class": "FLANGE",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME B16.5 / B16.47 Pressure-Temp Class",
        "severity": "BLOCKING",
        "rule_text": "Class 150 vs Class 300 vs Class 600 flange bolt circles, bolt hole diameters, and face thicknesses are dimensionally incompatible.",
    },
    {
        "material_class": "FLANGE",
        "condition": "OFFSHORE_SERVICE",
        "requirement": "Duplex UNS S31803 / 316L RTJ Facing Verification",
        "severity": "BLOCKING",
        "rule_text": "Offshore subsea and topside hydrocarbon flanges require Ring Type Joint (RTJ) face and saline pit-resistant alloy.",
    },

    # ---------------- BOLT & FASTENERS ----------------
    {
        "material_class": "BOLT",
        "condition": "HIGH_TEMPERATURE",
        "requirement": "ASTM A193 Gr. B7 / B16 High Temp Alloy",
        "severity": "BLOCKING",
        "rule_text": "Commercial Grade 8.8 or SS304 bolts relax tension rapidly at temperatures > 300°C. ASTM A193 B7/B16 alloy studs required.",
    },
    {
        "material_class": "BOLT",
        "condition": "CRITICAL_SERVICE",
        "requirement": "Grade & Proof Load Certification (ISO 898-1)",
        "severity": "BLOCKING",
        "rule_text": "Fastener tensile class and material chemistry (SS304 vs SS316 vs B7) must strictly match pressure vessel design calculations.",
    },
    {
        "material_class": "BOLT",
        "condition": "SOUR_GAS",
        "requirement": "ASTM A193 Gr. B7M / NACE MR0175 Max Hardness 22 HRC",
        "severity": "BLOCKING",
        "rule_text": "Standard B7 bolts crack catastrophically in sour environments. B7M bolts with controlled hardness (< 22 HRC) are strictly required.",
    },

    # ---------------- BEARING ----------------
    {
        "material_class": "BEARING",
        "condition": "ROTATING_EQUIPMENT",
        "requirement": "ISO 281 Dynamic Load & Clearance C3 / C4",
        "severity": "BLOCKING",
        "rule_text": "Internal radial clearance (CN vs C3) and cage material (pressed steel vs machined brass) must match operating thermal expansion.",
    },
    {
        "material_class": "BEARING",
        "condition": "HIGH_TEMPERATURE",
        "requirement": "High-Temp Grease & Viton / Metallic Seals",
        "severity": "BLOCKING",
        "rule_text": "Standard rubber seals (NBR) melt above 120°C. Fluoroelastomer (FKM) or labyrinth metal seals with synthetic polyurea grease required.",
    },

    # ---------------- GASKET ----------------
    {
        "material_class": "GASKET",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME B16.20 Spiral Wound with Inner/Outer Ring",
        "severity": "BLOCKING",
        "rule_text": "Compressed non-asbestos fiber gaskets fail under high pressure surges. Metallic spiral wound or kammprofile gaskets required.",
    },
    {
        "material_class": "GASKET",
        "condition": "CORROSIVE_SERVICE",
        "requirement": "PTFE / Flexible Graphite Filler Chemistry Check",
        "severity": "WARNING",
        "rule_text": "Filler material must be chemically inert to strong oxidizing or acidic process chemicals.",
    },

    # ---------------- PUMP ----------------
    {
        "material_class": "PUMP",
        "condition": "ROTATING_EQUIPMENT",
        "requirement": "API 610 Heavy-Duty Hydrocarbon Pump Class",
        "severity": "BLOCKING",
        "rule_text": "Centrifugal pumps in hydrocarbon or hazardous service must strictly follow API 610 (OH2/BB2/BB3) casing and vibration criteria.",
    },
    {
        "material_class": "PUMP",
        "condition": "SOUR_GAS",
        "requirement": "API 610 Table H.1 Materials Class S-6 / S-8 / C-6",
        "severity": "BLOCKING",
        "rule_text": "Pump impeller, casing, and wear rings must meet NACE MR0175 and API 610 sour metallurgy.",
    },

    # ---------------- COMPRESSOR ----------------
    {
        "material_class": "COMPRESSOR",
        "condition": "HYDROGEN_SERVICE",
        "requirement": "API 618 Reciprocating / API 617 Centrifugal H₂ Spec",
        "severity": "BLOCKING",
        "rule_text": "Hydrogen compressor cylinders and packing rings require specialized low-molecular-weight sealing and anti-permeation alloys.",
    },

    # ---------------- PRESSURE VESSEL ----------------
    {
        "material_class": "PRESSURE_VESSEL",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME Boiler & Pressure Vessel Code Section VIII Div 1/2",
        "severity": "BLOCKING",
        "rule_text": "Pressure boundary plate thickness, weld joint efficiency, and Post-Weld Heat Treatment (PWHT) must meet ASME code stamp criteria.",
    },

    # ---------------- FITTING ----------------
    {
        "material_class": "FITTING",
        "condition": "HIGH_PRESSURE",
        "requirement": "ASME B16.9 Butt-Weld / B16.11 Forged Socket 3000#",
        "severity": "BLOCKING",
        "rule_text": "Fitting pressure class (2000# vs 3000# vs 6000#) and wall schedule must equal or exceed mating pipe rating.",
    },

    # ---------------- MECHANICAL SEAL ----------------
    {
        "material_class": "MECHANICAL_SEAL",
        "condition": "CRITICAL_SERVICE",
        "requirement": "API 682 4th Ed. Category 2/3 Dual Cartridge Seal",
        "severity": "BLOCKING",
        "rule_text": "Lethal or flammable services require pressurized dual barrier fluid seal plans (API Plan 53A/53B) to eliminate zero atmosphere leakage.",
    },
]


def evaluate_compliance(material_class: str, condition: str):
    """
    Evaluates engineering compliance rules.
    Returns: (checks, blocked, review_count, pass_count, summary_text)
    """
    material_class = material_class.upper().strip()
    condition = condition.upper().strip()

    checks = []
    for rule in COMPLIANCE_RULES:
        if rule["material_class"] == material_class and rule["condition"] == condition:
            checks.append({
                **rule,
                "passed": rule["severity"] == "WARNING",
            })

    # If no specific rule for this exact combination, check general material class rules
    if not checks:
        for rule in COMPLIANCE_RULES:
            if rule["material_class"] == material_class:
                checks.append({
                    **rule,
                    "passed": True,
                })
                if len(checks) >= 2:
                    break

    # If still empty, add default baseline verification check
    if not checks:
        checks.append({
            "material_class": material_class,
            "condition": condition,
            "requirement": "General Engineering Specification Baseline (IS / ASTM / ASME)",
            "severity": "WARNING",
            "rule_text": "General dimensional and metallurgical standards review recommended for non-critical duty.",
            "passed": True,
        })

    blocked = any(not check["passed"] and check["severity"] == "BLOCKING" for check in checks)
    review_count = sum(1 for check in checks if check["severity"] == "WARNING")
    pass_count = sum(1 for check in checks if check["passed"])

    if blocked:
        summary_text = (
            f"MATCH BLOCKED: Engineering standards requirement not satisfied. "
            f"Equivalence substitution between materials in {condition.replace('_', ' ').title()} "
            f"requires mandatory technical certification under international safety standards."
        )
    elif review_count > 0:
        summary_text = (
            f"REVIEW REQUIRED: Materials exhibit technical compatibility, but site-specific "
            f"operating conditions and corrosion allowances require sign-off by the Lead Discipline Engineer."
        )
    else:
        summary_text = "PASS: All standardized engineering compliance criteria satisfied for normal operating parameters."

    return checks, blocked, review_count, pass_count, summary_text


# =========================================================
# MULTI-CPSE INVENTORY DATASET (SAVINGS SIMULATOR)
# =========================================================

CPSE_INVENTORY_POOL = [
    {
        "id": "INV-001",
        "material_code": "N-MAT-BLT-SS304-M10-L050",
        "description": "Hex Bolt M10 x 50 mm SS304 Full Thread",
        "category": "FASTENERS",
        "source_cpse": "ONGC",
        "source_plant": "Hazira Gas Complex, Gujarat",
        "dest_cpse": "NTPC",
        "dest_plant": "Ramagundam Thermal Power Station, Telangana",
        "source_stock": 2500,
        "dest_requirement": 800,
        "unit_price": 24.50,
        "distance_km": 1180,
        "weight_per_unit_kg": 0.048,
    },
    {
        "id": "INV-002",
        "material_code": "N-MAT-VLV-BL-SS316-D050-P150",
        "description": "Flanged Ball Valve 2 Inch (50mm) Class 150 SS316 Body/Trim",
        "category": "VALVES",
        "source_cpse": "IOCL",
        "source_plant": "Panipat Refinery, Haryana",
        "dest_cpse": "BPCL",
        "dest_plant": "Kochi Refinery, Kerala",
        "source_stock": 140,
        "dest_requirement": 45,
        "unit_price": 34500.00,
        "distance_km": 2450,
        "weight_per_unit_kg": 9.2,
    },
    {
        "id": "INV-003",
        "material_code": "N-MAT-PIP-SML-SS304-D050-T3",
        "description": "Seamless SS304 Pipe OD 50mm WT 3mm (6 Meter Length)",
        "category": "PIPING",
        "source_cpse": "SAIL",
        "source_plant": "Bhilai Steel Plant, Chhattisgarh",
        "dest_cpse": "BHEL",
        "dest_plant": "Tiruchirappalli Boiler Unit, Tamil Nadu",
        "source_stock": 350,
        "dest_requirement": 120,
        "unit_price": 18200.00,
        "distance_km": 1390,
        "weight_per_unit_kg": 21.5,
    },
    {
        "id": "INV-004",
        "material_code": "N-MAT-BRG-DGR-6205-2RS-C3",
        "description": "Deep Groove Ball Bearing 6205-2RS C3 Synthetic Sealed",
        "category": "BEARINGS",
        "source_cpse": "NTPC",
        "source_plant": "Singrauli Super Thermal, UP",
        "dest_cpse": "GAIL",
        "dest_plant": "Pata Petrochemical Complex, UP",
        "source_stock": 850,
        "dest_requirement": 300,
        "unit_price": 2200.00,
        "distance_km": 420,
        "weight_per_unit_kg": 0.13,
    },
    {
        "id": "INV-005",
        "material_code": "N-MAT-GSK-SPW-SS316-2IN-150",
        "description": "Spiral Wound Gasket 2 Inch Class 150 SS316/Graphite Ring",
        "category": "GASKETS",
        "source_cpse": "HPCL",
        "source_plant": "Visakhapatnam Refinery, Andhra Pradesh",
        "dest_cpse": "ONGC",
        "dest_plant": "Mumbai Offshore Base, Maharashtra",
        "source_stock": 1800,
        "dest_requirement": 600,
        "unit_price": 850.00,
        "distance_km": 1350,
        "weight_per_unit_kg": 0.35,
    },
]


def calculate_savings_model(transfer_item_id: str = None, custom_qty: int = None):
    """
    Calculates detailed financial and carbon savings for inter-CPSE transfers.
    Formula:
      - Avoided Purchase = transfer_qty * dest_unit_price
      - Transport Cost = fixed_base (₹2,500) + (distance_km * total_weight_tons * ₹4.20/ton-km)
      - Net Financial Savings = Avoided Purchase - Transport Cost
      - Avoided Virgin Metal CO₂ = total_weight_kg * 2.89 kg CO₂e/kg
      - Transport CO₂ = total_weight_tons * distance_km * 0.092 kg CO₂e/ton-km
      - Net CO₂ Avoided = max(0, Avoided Virgin CO₂ - Transport CO₂) in tCO₂e
    """
    selected_item = CPSE_INVENTORY_POOL[0]
    if transfer_item_id:
        for item in CPSE_INVENTORY_POOL:
            if item["id"] == transfer_item_id:
                selected_item = item
                break

    transfer_qty = custom_qty if custom_qty and custom_qty > 0 else min(selected_item["source_stock"], selected_item["dest_requirement"])

    avoided_purchase = transfer_qty * selected_item["unit_price"]
    total_weight_kg = transfer_qty * selected_item["weight_per_unit_kg"]
    total_weight_tons = max(0.05, total_weight_kg / 1000.0)

    freight_rate_per_ton_km = 4.50
    transport_cost = round(2500 + (selected_item["distance_km"] * total_weight_tons * freight_rate_per_ton_km), 2)
    net_savings = max(0.0, avoided_purchase - transport_cost)

    # Carbon calculations
    avoided_manufacturing_co2_kg = total_weight_kg * 2.89  # Stainless / Engineering Alloy emissions factor
    transport_emissions_co2_kg = total_weight_tons * selected_item["distance_km"] * 0.092
    net_co2_avoided_tons = round(max(0.0, (avoided_manufacturing_co2_kg - transport_emissions_co2_kg) / 1000.0), 3)

    return {
        "item": selected_item,
        "transfer_qty": transfer_qty,
        "avoided_purchase": avoided_purchase,
        "transport_cost": transport_cost,
        "net_savings": net_savings,
        "total_weight_kg": round(total_weight_kg, 1),
        "distance_km": selected_item["distance_km"],
        "co2_avoided_tons": net_co2_avoided_tons,
        "all_opportunities": CPSE_INVENTORY_POOL,
    }


# =========================================================
# PROCUREMENT INTELLIGENCE & PRICE VARIANCE DATA
# =========================================================

PROCUREMENT_BENCHMARKS = [
    {
        "code": "N-MAT-BRG-6205-2RS",
        "description": "Deep Groove Ball Bearing 6205-2RS C3 (SKF / FAG Equivalent)",
        "category": "BEARINGS",
        "prices": [
            {"cpse": "ONGC", "price": 15000, "po_date": "2024-03-12", "po_num": "ONGC/PO/44810", "qty": 50},
            {"cpse": "IOCL", "price": 18500, "po_date": "2024-06-20", "po_num": "IOCL/MAT/88391", "qty": 120},
            {"cpse": "NTPC", "price": 22000, "po_date": "2024-01-15", "po_num": "NTPC/GEN/12093", "qty": 80},
            {"cpse": "BPCL", "price": 38000, "po_date": "2024-08-04", "po_num": "BPCL/PROC/55012", "qty": 30},
        ],
        "min_price": 15000,
        "max_price": 38000,
        "avg_price": 23375,
        "variance_pct": 153.3,
        "status": "HIGH_VARIANCE",
        "annual_volume": 450,
        "potential_joint_savings": 4250000,
        "explanation": "The same normalized bearing specification exhibits a 153.3% price disparity across CPSE purchase orders. BPCL procured in low spot volumes while ONGC leveraged frame agreements.",
    },
    {
        "code": "N-MAT-VLV-BL-SS316-2IN",
        "description": "SS316 Flanged Ball Valve 2 Inch Class 150 Full Bore (Fire-Safe API 607)",
        "category": "VALVES",
        "prices": [
            {"cpse": "ONGC", "price": 32000, "po_date": "2024-02-18", "po_num": "ONGC/OFFSHORE/992", "qty": 200},
            {"cpse": "NTPC", "price": 34500, "po_date": "2024-05-11", "po_num": "NTPC/PO/5521", "qty": 75},
            {"cpse": "SAIL", "price": 41000, "po_date": "2024-04-29", "po_num": "SAIL/STORE/1102", "qty": 60},
            {"cpse": "BHEL", "price": 54000, "po_date": "2024-07-16", "po_num": "BHEL/PUR/3391", "qty": 25},
        ],
        "min_price": 32000,
        "max_price": 54000,
        "avg_price": 40375,
        "variance_pct": 68.8,
        "status": "HIGH_VARIANCE",
        "annual_volume": 680,
        "potential_joint_savings": 5700000,
        "explanation": "High price variance driven by differing vendor inspection scopes and non-consolidated procurement batches.",
    },
    {
        "code": "N-MAT-PIP-SML-SS304-50MM",
        "description": "Seamless Pipe SS304 OD 50mm WT 3mm (Per Meter)",
        "category": "PIPING",
        "prices": [
            {"cpse": "ONGC", "price": 2800, "po_date": "2024-01-22", "po_num": "ONGC/PIPE/1029", "qty": 1500},
            {"cpse": "IOCL", "price": 2950, "po_date": "2024-04-14", "po_num": "IOCL/REF/7732", "qty": 800},
            {"cpse": "NTPC", "price": 3100, "po_date": "2024-06-05", "po_num": "NTPC/MAT/4410", "qty": 650},
            {"cpse": "BPCL", "price": 3750, "po_date": "2024-08-19", "po_num": "BPCL/STORE/912", "qty": 200},
        ],
        "min_price": 2800,
        "max_price": 3750,
        "avg_price": 3150,
        "variance_pct": 33.9,
        "status": "MODERATE_VARIANCE",
        "annual_volume": 4200,
        "potential_joint_savings": 1470000,
        "explanation": "Moderate price variance correlated directly with purchase order tonnage volumes.",
    },
    {
        "code": "N-MAT-BLT-SS304-M10-50",
        "description": "Hex Bolt M10 x 50 mm SS304 with Nut & Spring Washer (Per 100 Units)",
        "category": "FASTENERS",
        "prices": [
            {"cpse": "ONGC", "price": 1850, "po_date": "2024-02-10", "po_num": "ONGC/FAST/8812", "qty": 500},
            {"cpse": "SAIL", "price": 1980, "po_date": "2024-05-18", "po_num": "SAIL/PUR/5541", "qty": 400},
            {"cpse": "NTPC", "price": 2150, "po_date": "2024-03-30", "po_num": "NTPC/PO/1289", "qty": 350},
            {"cpse": "BHEL", "price": 2400, "po_date": "2024-07-22", "po_num": "BHEL/INV/6631", "qty": 200},
        ],
        "min_price": 1850,
        "max_price": 2400,
        "avg_price": 2095,
        "variance_pct": 29.7,
        "status": "CONTROLLED_VARIANCE",
        "annual_volume": 12500,
        "potential_joint_savings": 3062500,
        "explanation": "Standard commodity fastener with consistent national distribution channels.",
    },
]


# =========================================================
# CAD / 3D MATCHER DEMO DATA
# =========================================================

CAD_COMPARISON_PAIRS = [
    {
        "id": "CAD-PAIR-01",
        "name": "Weld Neck Flange 2\" Class 150 vs DIN EN 1092-1 PN16",
        "part_a": "ANSI B16.5 2\" 150# WNRF (ONGC Standard)",
        "part_b": "DIN EN 1092-1 DN50 PN16 (NTPC Spec)",
        "shape_type": "FLANGE",
        "similarity_score": 94.7,
        "geometry_score": 92.0,
        "mounting_score": 100.0,
        "decision": "GEOMETRIC MATCH",
        "confidence": "HIGH",
        "mesh_points_a": "12,450 vertices / 24,800 facets",
        "mesh_points_b": "12,180 vertices / 24,300 facets",
        "bounding_box_a": "152.4 x 152.4 x 63.5 mm",
        "bounding_box_b": "152.0 x 152.0 x 63.0 mm",
        "bolt_circle_a": "120.7 mm PCD / 4 Holes x 19 mm",
        "bolt_circle_b": "120.0 mm PCD / 4 Holes x 18 mm",
        "explanation": "3D geometric scan and bolt hole pattern match within 0.5% tolerance. Flange face thickness and raised face height align for cross-compatibility under PN16/Class 150 envelopes.",
    },
    {
        "id": "CAD-PAIR-02",
        "name": "Centrifugal Pump Impeller Variant A vs Variant B",
        "part_a": "Enclosed 6-Vane Impeller OD 210mm (IOCL Refinery)",
        "part_b": "Enclosed 6-Vane Impeller OD 212mm (BPCL Standard)",
        "shape_type": "IMPELLER",
        "similarity_score": 88.3,
        "geometry_score": 86.0,
        "mounting_score": 94.0,
        "decision": "LIKELY EQUIVALENT",
        "confidence": "MEDIUM-HIGH",
        "mesh_points_a": "34,200 vertices / 68,100 facets",
        "mesh_points_b": "33,900 vertices / 67,400 facets",
        "bounding_box_a": "210.0 x 210.0 x 42.0 mm",
        "bounding_box_b": "212.0 x 212.0 x 42.0 mm",
        "bolt_circle_a": "Keyed Shaft Bore 32.0 mm",
        "bolt_circle_b": "Keyed Shaft Bore 32.0 mm",
        "explanation": "Hub mounting dimensions and vane curvature profile match. Outer diameter varies by 2mm (trim allowance). Can be skimmed on lathe for exact hydraulic curve equivalence.",
    },
    {
        "id": "CAD-PAIR-03",
        "name": "90° Long Radius Pipe Bend vs Short Radius Elbow",
        "part_a": "90° Long Radius Butt-Weld Bend R=1.5D (SAIL)",
        "part_b": "90° Short Radius Butt-Weld Elbow R=1.0D (BHEL)",
        "shape_type": "ELBOW",
        "similarity_score": 58.1,
        "geometry_score": 52.0,
        "mounting_score": 68.0,
        "decision": "DIFFERENT (FLOW RESTRICTION)",
        "confidence": "HIGH",
        "mesh_points_a": "8,400 vertices / 16,700 facets",
        "mesh_points_b": "7,900 vertices / 15,600 facets",
        "bounding_box_a": "180.0 x 180.0 x 60.3 mm",
        "bounding_box_b": "125.0 x 125.0 x 60.3 mm",
        "bolt_circle_a": "Beveled Weld End 60.3 mm OD",
        "bolt_circle_b": "Beveled Weld End 60.3 mm OD",
        "explanation": "Significant centerline radius variance (1.5D vs 1.0D). While mating diameter is identical, substituting short radius will increase pressure drop by 42% and fails hydraulic piping stress specs.",
    },
    {
        "id": "CAD-PAIR-04",
        "name": "Valve Body Casting vs Fabricated Pipe Elbow",
        "part_a": "Cast Steel Globe Valve Body DN50 (HPCL)",
        "part_b": "Forged 90° Reducing Elbow DN50x40 (GAIL)",
        "shape_type": "VALVE_VS_ELBOW",
        "similarity_score": 21.4,
        "geometry_score": 18.0,
        "mounting_score": 25.0,
        "decision": "NON-MATCH",
        "confidence": "CERTAIN",
        "mesh_points_a": "28,500 vertices / 56,800 facets",
        "mesh_points_b": "9,100 vertices / 18,100 facets",
        "bounding_box_a": "230.0 x 165.0 x 280.0 mm",
        "bounding_box_b": "115.0 x 115.0 x 75.0 mm",
        "bolt_circle_a": "Flanged Inlet/Outlet + Bonnet Cavity",
        "bolt_circle_b": "Socket Weld Ends",
        "explanation": "Completely disparate component topologies. Negative baseline test case accurately rejected by volumetric octree scanner.",
    },
]


# =========================================================
# MULTILINGUAL INGESTION DEMO DATA
# =========================================================

MULTILINGUAL_PRESETS = [
    {
        "id": "LANG-HI-01",
        "language": "Hindi (हिन्दी)",
        "script": "Devanagari",
        "source_text": "स्टेनलेस स्टील हेक्स बोल्ट १० मिमी x ५० मिमी (एसएस ३०४)",
        "cpse_origin": "NTPC Singrauli Stores",
        "detected_lang": "Hindi (hi)",
        "confidence": 98.4,
        "translated_en": "STAINLESS STEEL HEX BOLT 10 MM X 50 MM (SS304)",
        "normalized_identity": "BOLT / SS304 / M10 / 50 MM / FULL THREAD",
        "attributes": {
            "component": "Hex Bolt",
            "material_grade": "SS304",
            "diameter": "10 mm (M10)",
            "length": "50 mm",
            "standard": "Metric ISO",
        },
    },
    {
        "id": "LANG-TA-02",
        "language": "Tamil (தமிழ்)",
        "script": "Tamil",
        "source_text": "துருப்பிடிக்காத எஃகு பைப் 50 மிமீ தடிமன் 3 மிமீ (SS304)",
        "cpse_origin": "BHEL Trichy Receiving Store",
        "detected_lang": "Tamil (ta)",
        "confidence": 97.2,
        "translated_en": "STAINLESS STEEL PIPE 50 MM WALL THICKNESS 3 MM (SS304)",
        "normalized_identity": "PIPE / SS304 / OD 50 MM / WT 3 MM / SEAMLESS",
        "attributes": {
            "component": "Seamless Pipe",
            "material_grade": "SS304",
            "outer_diameter": "50 mm",
            "wall_thickness": "3 mm",
            "standard": "ASTM A312",
        },
    },
    {
        "id": "LANG-TE-03",
        "language": "Telugu (తెలుగు)",
        "script": "Telugu",
        "source_text": "స్టెయిన్లెస్ స్టీల్ బాల్ వాల్వ్ 2 అంగుళాలు 150 పౌండ్లు (SS316)",
        "cpse_origin": "HPCL Visakhapatnam Materials",
        "detected_lang": "Telugu (te)",
        "confidence": 96.8,
        "translated_en": "STAINLESS STEEL BALL VALVE 2 INCH 150 LB (SS316)",
        "normalized_identity": "BALL VALVE / SS316 / 2 IN (50MM) / CLASS 150 / FLANGED",
        "attributes": {
            "component": "Ball Valve",
            "material_grade": "SS316",
            "nominal_size": "2 Inch (50 mm)",
            "pressure_class": "150 PSI / Class 150",
            "end_connection": "Flanged WNRF",
        },
    },
    {
        "id": "LANG-GU-04",
        "language": "Gujarati (ગુજરાતી)",
        "script": "Gujarati",
        "source_text": "સ્ટેનલેસ સ્ટીલ ફ્લેંજ ૨ ઇંચ ક્લાસ ૧૫૦ વેલ્ડ નેક (SS316L)",
        "cpse_origin": "ONGC Hazira Complex",
        "detected_lang": "Gujarati (gu)",
        "confidence": 98.1,
        "translated_en": "STAINLESS STEEL FLANGE 2 INCH CLASS 150 WELD NECK (SS316L)",
        "normalized_identity": "FLANGE / SS316L / 2 IN / CLASS 150 / WELD NECK",
        "attributes": {
            "component": "Weld Neck Flange",
            "material_grade": "SS316L",
            "nominal_size": "2 Inch (DN50)",
            "pressure_class": "Class 150 (PN20)",
            "facing": "Raised Face (RF)",
        },
    },
    {
        "id": "LANG-MR-05",
        "language": "Marathi (मराठी)",
        "script": "Devanagari",
        "source_text": "डीप ग्रूव्ह बॉल बेअरिंग ६२०५-२आरएस सी३ हाय टेम्परेचर",
        "cpse_origin": "BPCL Mumbai Refinery Store",
        "detected_lang": "Marathi (mr)",
        "confidence": 97.9,
        "translated_en": "DEEP GROOVE BALL BEARING 6205-2RS C3 HIGH TEMPERATURE",
        "normalized_identity": "BEARING / DEEP GROOVE / 6205-2RS / C3 CLEARANCE",
        "attributes": {
            "component": "Deep Groove Ball Bearing",
            "bearing_number": "6205",
            "seal_type": "2RS (Dual Rubber Contact)",
            "clearance": "C3 Radial Clearance",
            "application": "High Temp Rotating Equipment",
        },
    },
]


# =========================================================
# DATA LINEAGE GRAPH DEMO DATA
# =========================================================

LINEAGE_CLUSTER = {
    "target_national_code": "NATIONAL-MAT-00421",
    "target_description": "HEX BOLT M10 X 50 MM STAINLESS STEEL SS304 FULL THREAD METRIC ISO",
    "category": "FASTENERS / BOLTS",
    "standard_assigned": "ISO 4017 / DIN 933 / IS 1364",
    "harmonization_date": "2024-08-15 11:32:00 IST",
    "confidence_score": 96.4,
    "audit_hash": "sha256:7f89d3a4b6c1e9203847f9e8a7d6c5b4e3f2a1098b7c6d5e4f3a2b1c0d9e8f7a",
    "approver_role": "Shri R. K. Verma, CGM (Materials), ONGC & Member Secretary, Inter-CPSE Harmonization Council (DPE)",
    "e_office_ref": "E-Office File No: DPE/CPSE-STD/2024/7791 (Note #14)",
    "source_nodes": [
        {
            "cpse": "ONGC",
            "legacy_code": "ONGC-1001",
            "raw_text": "HEX BOLT M10 X 50 SS304",
            "erp_source": "SAP ERP ECC 6.0 (Hazira Plant)",
            "ingested_at": "2024-08-10 09:15:22",
            "similarity_to_master": 95.4,
            "mapping_status": "CONFIRMED_IDENTICAL",
        },
        {
            "cpse": "NTPC",
            "legacy_code": "NTPC-4401",
            "raw_text": "HEXAGONAL BOLT M10 X 50 MM SS304",
            "erp_source": "Oracle ERP Cloud (Ramagundam)",
            "ingested_at": "2024-08-10 10:44:11",
            "similarity_to_master": 97.8,
            "mapping_status": "CONFIRMED_IDENTICAL",
        },
        {
            "cpse": "SAIL",
            "legacy_code": "SAIL-3101",
            "raw_text": "HEX BOLT M10*50 STAINLESS STEEL 304",
            "erp_source": "In-house CoreERP (Bhilai)",
            "ingested_at": "2024-08-11 14:20:05",
            "similarity_to_master": 94.2,
            "mapping_status": "CONFIRMED_IDENTICAL",
        },
        {
            "cpse": "IOCL",
            "legacy_code": "IOCL-STORE-2388",
            "raw_text": "SS304 FASTENER BOLT HEX M10-50 MM",
            "erp_source": "SAP S/4HANA (Panipat)",
            "ingested_at": "2024-08-12 16:02:40",
            "similarity_to_master": 92.9,
            "mapping_status": "CONFIRMED_IDENTICAL",
        },
        {
            "cpse": "BPCL",
            "legacy_code": "BPCL-SAP-7712",
            "raw_text": "BOLT HEX FULL THRD SS 304 M10X50MM",
            "erp_source": "SAP ERP ECC 6.0 (Kochi)",
            "ingested_at": "2024-08-13 11:18:19",
            "similarity_to_master": 96.1,
            "mapping_status": "CONFIRMED_IDENTICAL",
        },
    ],
    "pipeline_steps": [
        {"step": "01", "name": "Raw ERP Ingestion", "desc": "Ingested 5 distinct item masters with divergent text conventions."},
        {"step": "02", "name": "OCR & Linguistic Normalization", "desc": "Cleaned delimiters (*, x, mm, spaces) and standard unit expansion."},
        {"step": "03", "name": "Attribute Extraction", "desc": "Parsed structured dimensions: Grade=SS304, Dia=10mm, Length=50mm, Head=Hex."},
        {"step": "04", "name": "Sentence-BERT Embedding", "desc": "High semantic affinity vector computed (>88% text vector cosine)."},
        {"step": "05", "name": "Engineering Rule Validation", "desc": "100% attribute equivalence confirmed under ISO 4017 bolt schema."},
        {"step": "06", "name": "National Master Mapping", "desc": "Bound 5 CPSE legacy codes into single unified entity NATIONAL-MAT-00421."},
    ],
}


# =========================================================
# ADVANCED VIEWS (INDIVIDUAL DEDICATED ROUTES)
# =========================================================

def compliance_view(request):
    """Dedicated Compliance Twin interface."""
    material_class = request.POST.get("material_class", "BALL_VALVE") if request.method == "POST" else request.GET.get("class", "BALL_VALVE")
    condition = request.POST.get("condition", "SOUR_GAS") if request.method == "POST" else request.GET.get("condition", "SOUR_GAS")

    checks, blocked, review_count, pass_count, summary_text = evaluate_compliance(material_class, condition)

    return render(
        request,
        "materials/compliance.html",
        {
            "selected_class": material_class,
            "selected_condition": condition,
            "material_classes": COMPLIANCE_MATERIAL_CLASSES,
            "conditions": COMPLIANCE_CONDITIONS,
            "checks": checks,
            "blocked": blocked,
            "review_count": review_count,
            "pass_count": pass_count,
            "summary_text": summary_text,
            "total_rules": len(COMPLIANCE_RULES),
        },
    )


def savings_view(request):
    """Dedicated Financial Savings & Carbon Simulator."""
    selected_id = request.GET.get("item", "INV-001")
    custom_qty = None
    if request.method == "POST":
        selected_id = request.POST.get("item_id", selected_id)
        try:
            custom_qty = int(request.POST.get("transfer_qty", 0))
        except (ValueError, TypeError):
            custom_qty = None

    savings_data = calculate_savings_model(selected_id, custom_qty)

    # Compute overall pool totals for executive aggregate view
    total_avoided_pool = sum(item["source_stock"] * item["unit_price"] for item in CPSE_INVENTORY_POOL)
    total_potential_savings = sum(
        max(0, (item["dest_requirement"] * item["unit_price"]) - (2500 + item["distance_km"] * (item["dest_requirement"] * item["weight_per_unit_kg"] / 1000) * 4.5))
        for item in CPSE_INVENTORY_POOL
    )
    total_co2_pool = sum(
        (item["dest_requirement"] * item["weight_per_unit_kg"] * 2.89) / 1000.0
        for item in CPSE_INVENTORY_POOL
    )

    return render(
        request,
        "materials/savings.html",
        {
            "savings": savings_data,
            "selected_id": selected_id,
            "total_avoided_pool": total_avoided_pool,
            "total_potential_savings": total_potential_savings,
            "total_co2_pool": round(total_co2_pool, 1),
            "inventory_pool": CPSE_INVENTORY_POOL,
        },
    )


def procurement_view(request):
    """Dedicated Procurement Intelligence & Price Variance dashboard."""
    selected_code = request.GET.get("code", "N-MAT-BRG-6205-2RS")
    selected_item = next((item for item in PROCUREMENT_BENCHMARKS if item["code"] == selected_code), PROCUREMENT_BENCHMARKS[0])

    total_procurement_savings = sum(item["potential_joint_savings"] for item in PROCUREMENT_BENCHMARKS)
    high_variance_count = sum(1 for item in PROCUREMENT_BENCHMARKS if item["status"] == "HIGH_VARIANCE")

    return render(
        request,
        "materials/procurement.html",
        {
            "benchmarks": PROCUREMENT_BENCHMARKS,
            "selected_item": selected_item,
            "total_procurement_savings": total_procurement_savings,
            "high_variance_count": high_variance_count,
        },
    )


def cad_view(request):
    """Dedicated CAD / 3D Matcher demonstration."""
    selected_id = request.GET.get("pair", "CAD-PAIR-01")
    selected_pair = next((pair for pair in CAD_COMPARISON_PAIRS if pair["id"] == selected_id), CAD_COMPARISON_PAIRS[0])

    return render(
        request,
        "materials/cad.html",
        {
            "pairs": CAD_COMPARISON_PAIRS,
            "selected_pair": selected_pair,
        },
    )


def multilingual_view(request):
    """Dedicated Multilingual Ingestion module."""
    selected_preset_id = request.GET.get("preset", "LANG-HI-01")
    custom_input = ""
    result = None

    if request.method == "POST":
        custom_input = request.POST.get("custom_text", "").strip()
        if custom_input:
            # Deterministic parsing for demo custom input
            result = {
                "id": "CUSTOM-01",
                "language": "Auto-Detected (Indic)",
                "script": "Regional UTF-8",
                "source_text": custom_input,
                "cpse_origin": "Custom CPSE Regional Submission",
                "detected_lang": "Indic NLP Pipeline",
                "confidence": 94.6,
                "translated_en": custom_input.upper(),
                "normalized_identity": f"NORMALIZED / {custom_input.upper()}",
                "attributes": {
                    "raw_tokens": custom_input,
                    "normalized_state": "Processed via Bhashini / IndicBERT normalizer",
                    "status": "Ready for Comparator",
                },
            }
        else:
            selected_preset_id = request.POST.get("preset_id", selected_preset_id)

    if not result:
        result = next((p for p in MULTILINGUAL_PRESETS if p["id"] == selected_preset_id), MULTILINGUAL_PRESETS[0])

    return render(
        request,
        "materials/multilingual.html",
        {
            "presets": MULTILINGUAL_PRESETS,
            "selected_preset": result,
            "custom_input": custom_input,
        },
    )


def lineage_view(request):
    """Dedicated Data Lineage visualizer."""
    return render(
        request,
        "materials/lineage.html",
        {
            "lineage": LINEAGE_CLUSTER,
        },
    )


def advanced_center(request):
    """Advanced Material Intelligence Suite Hub."""
    return render(request, "materials/advanced_center.html")


def erp_duplicate_api(request):
    """ERP API duplicate search endpoint."""
    query = request.GET.get("q", "").strip().upper()
    if not query:
        return JsonResponse({"query": query, "matches": []})

    results = []
    for material in DEMO_MATERIALS:
        description = material["description"].upper()
        query_tokens = set(re.findall(r"[A-Z0-9]+", query))
        desc_tokens = set(re.findall(r"[A-Z0-9]+", description))
        if not query_tokens:
            continue
        overlap = len(query_tokens & desc_tokens) / max(len(query_tokens), 1)
        score = min(100, round(overlap * 100, 1))
        if score >= 25:
            results.append({
                "code": material["code"],
                "cpse": material["cpse"],
                "description": material["description"],
                "score": score,
                "warning": score >= 55,
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return JsonResponse({"query": query, "matches": results[:5]})