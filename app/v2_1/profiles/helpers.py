from typing import Any


def deepmerge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deepmerge(result[key], value)
            else:
                raise ValueError()
        else:
            result[key] = value
    return result
