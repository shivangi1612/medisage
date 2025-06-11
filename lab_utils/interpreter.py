import re

def interpret_lab_results(lab_results_json):
    import json
    try:
        lab_results = json.loads(lab_results_json)
    except json.JSONDecodeError:
        return "❌ Failed to parse extracted lab results. Please check formatting."

    interpreted_results = []

    for test in lab_results:
        test_name = test.get("test_name")
        value = extract_float(test.get("value"))
        unit = test.get("unit")
        ref_range = test.get("reference_range")

        interpretation = "Unknown"

        if ref_range and value is not None:
            low, high = parse_reference_range(ref_range)
            if low is not None and high is not None:
                if value < low:
                    interpretation = "Low"
                elif value > high:
                    interpretation = "High"
                else:
                    interpretation = "Normal"

        interpreted_results.append({
            "test_name": test_name,
            "value": value,
            "unit": unit,
            "reference_range": ref_range,
            "interpretation": interpretation
        })

    return interpreted_results


def parse_reference_range(ref_range):
    match = re.findall(r"[\d\.]+", ref_range)
    if len(match) >= 2:
        return float(match[0]), float(match[1])
    return None, None

def extract_float(value):
    try:
        return float(re.findall(r"[\d\.]+", str(value))[0])
    except:
        return None
