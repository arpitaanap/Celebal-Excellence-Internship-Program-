import json
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

METADATA_FILE = (
    BASE_DIR
    / "vector_store"
    / "metadata.json"
)


# ============================================================
# LOAD METADATA
# ============================================================

with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as file:

    metadata = json.load(file)


# ============================================================
# FIND MAHINDRA ENTRIES
# ============================================================

print("\n" + "=" * 70)
print("METADATA VALUE CHECK")
print("=" * 70)

print(
    f"\nTotal chunks: {len(metadata)}"
)

print(
    "\nMahindra entries:"
)

print("-" * 70)

found = 0

seen = set()

for item in metadata:

    brand = str(
        item.get("brand", "")
    ).strip()

    model = str(
        item.get("model", "")
    ).strip()

    if "mahindra" in brand.lower():

        combination = (
            brand,
            model
        )

        if combination in seen:
            continue

        seen.add(combination)

        print(
            f"Brand: {brand!r}"
        )

        print(
            f"Model: {model!r}"
        )

        print()

        found += 1


print("-" * 70)

print(
    f"\nUnique Mahindra brand/model combinations: "
    f"{found}"
)