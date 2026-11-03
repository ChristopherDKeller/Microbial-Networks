import re

from .metadata_rules import RULES


TABLE_NAME = "agp_metadata"

EXCLUDED_COLUMNS = {
    "#SampleID",
    "sample_name",
}


def quote_identifier(name: str) -> str:
    """Escape SQL identifiers such as column names."""
    return '"' + name.replace('"', '""') + '"'


def get_categories(con) -> list[str]:
    """Read column names from DuckDB, excluding sample identifiers."""
    columns = con.execute(
        f"DESCRIBE {quote_identifier(TABLE_NAME)}"
    ).fetchdf()["column_name"].tolist()

    return [
        c for c in columns
        if c not in EXCLUDED_COLUMNS
    ]


def classify_category(category: str) -> str:
    """Assign the first matching RULES group."""
    name = category.casefold()

    for group, patterns in RULES:
        if any(re.search(pattern, name) for pattern in patterns):
            return group

    return "other"


def get_group_order() -> dict[str, int]:
    """Preserve the group order defined by RULES."""
    order = {
        group: index
        for index, (group, _) in enumerate(RULES)
    }
    order["other"] = len(order)

    return order