
import pandas as pd
from collections import defaultdict


MATCH_RESULTS_PATH = "data/match_results.csv"
MATERIALS_PATH = "data/materials.csv"
OUTPUT_PATH = "data/material_groups.csv"


# Minimum score required to consider two materials
# connected to the same candidate group.
MATCH_THRESHOLD = 0.90


def load_data():
    materials = pd.read_csv(MATERIALS_PATH)
    matches = pd.read_csv(MATCH_RESULTS_PATH)

    return materials, matches


def build_graph(materials, matches):
    """
    Build a graph where every material is a node.

    A strong match between two materials creates an edge.

    Strongly connected materials can then form candidate groups.
    """

    # Every material gets a unique node ID.
    nodes = set(
        materials["material_code"].astype(str)
    )

    graph = defaultdict(set)

    for node in nodes:
        graph[node] = set()

    for _, row in matches.iterrows():

        score = float(row["final_score"])

        classification = str(
            row["classification"]
        )

        # Only strong matches become grouping edges.
        if (
            score >= MATCH_THRESHOLD
            and classification in {
                "IDENTICAL",
                "EQUIVALENT",
            }
        ):

            code_a = str(row["code_a"])
            code_b = str(row["code_b"])

            graph[code_a].add(code_b)
            graph[code_b].add(code_a)

    return graph


def find_connected_components(graph):
    """
    Find connected components using DFS.

    Every connected component becomes a candidate
    common-material group.
    """

    visited = set()
    groups = []

    for node in graph:

        if node in visited:
            continue

        stack = [node]
        component = []

        while stack:

            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            component.append(current)

            for neighbour in graph[current]:

                if neighbour not in visited:
                    stack.append(neighbour)

        groups.append(component)

    return groups


def choose_representative(group, materials):
    """
    Choose a human-readable representative description
    for the candidate master.

    For the prototype we select the shortest description.
    Later we will generate a standardized description.
    """

    group_set = set(group)

    subset = materials[
        materials["material_code"]
        .astype(str)
        .isin(group_set)
    ].copy()

    if subset.empty:
        return "UNKNOWN MATERIAL"

    subset["description_length"] = (
        subset["description"]
        .astype(str)
        .str.len()
    )

    representative = subset.sort_values(
        "description_length"
    ).iloc[0]

    return representative["description"]


def build_group_output(
    groups,
    materials,
):
    """
    Convert groups into a table suitable for display
    and future Django integration.
    """

    rows = []

    for index, group in enumerate(
        groups,
        start=1,
    ):

        # Only keep meaningful groups.
        # A group containing one material isn't a
        # duplicate/harmonization candidate.
        if len(group) < 2:
            continue

        representative = choose_representative(
            group,
            materials,
        )

        group_set = set(group)

        subset = materials[
            materials["material_code"]
            .astype(str)
            .isin(group_set)
        ]

        cpse_codes = []

        for _, material in subset.iterrows():

            cpse_codes.append(
                f"{material['cpse']}:{material['material_code']}"
            )

        rows.append({
            "group_id": f"GROUP-{index:04d}",
            "candidate_description": representative,
            "member_count": len(group),
            "cpse_count": subset["cpse"].nunique(),
            "cpse_mappings": " | ".join(
                cpse_codes
            ),
        })

    return pd.DataFrame(rows)


def main():

    print("Loading material data...")

    materials, matches = load_data()

    print(
        f"Materials loaded: {len(materials)}"
    )

    print(
        f"Pair comparisons loaded: {len(matches)}"
    )

    print("\nBuilding match graph...")

    graph = build_graph(
        materials,
        matches,
    )

    print("Graph created.")

    print("\nFinding candidate groups...")

    groups = find_connected_components(
        graph
    )

    print(
        f"Total connected components: "
        f"{len(groups)}"
    )

    result = build_group_output(
        groups,
        materials,
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"\nSaved groups to: {OUTPUT_PATH}"
    )

    print("\n" + "=" * 90)
    print("CANDIDATE COMMON MATERIAL GROUPS")
    print("=" * 90)

    if result.empty:

        print(
            "\nNo multi-material groups were found."
        )

        return

    for _, row in result.iterrows():

        print("\n" + "-" * 90)

        print(
            f"GROUP: {row['group_id']}"
        )

        print(
            f"Candidate: "
            f"{row['candidate_description']}"
        )

        print(
            f"Materials: "
            f"{row['member_count']}"
        )

        print(
            f"CPSEs: "
            f"{row['cpse_count']}"
        )

        print(
            "Mappings:"
        )

        print(
            row["cpse_mappings"]
        )


if __name__ == "__main__":
    main()

