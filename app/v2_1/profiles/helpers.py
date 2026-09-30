from typing import Any


def deepmerge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Merge two sidecar mappings. Profiles pass their own fields first and the
    common fields second; the key order decides the element order in the sidecar.
    A key present in both (other than a nested dict) is a mapping error.
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deepmerge(result[key], value)
            else:
                raise ValueError(f"Duplicate sidecar key {key!r}")
        else:
            result[key] = value
    return result
