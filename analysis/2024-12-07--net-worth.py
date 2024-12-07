#!/usr/bin/env python3
import glob
from collections import Counter

categories = {
    "BOA Checking": "liquid",
    "BOA Mortgage": "house",
    "HEAT Loan": "house",
    "HSA": "retirement",
    "House (Zillow)": "house",
    "Jeff Guideline 401k": "retirement",
    "Julia Guideline 401k": "retirement",
    "Jeff Vanguard 401k": "retirement",
    "Vanguard Stocks": "liquid",
    "WF Mortgage": "house",
}

historical_amounts = Counter()

for fname in glob.glob("*.tsv"):
    table = fname.replace(
        "Historical Net Worth - ", "").replace(".tsv", "")
    category = categories[table]
    
    with open(fname) as inf:
        next_date = None
        next_amount = None
        for line in inf:
            date, amount = line.strip().split("\t")
            amount = float(amount.replace("$", "").replace(",",""))

            use_date = date
            use_amount = amount

            # interpolate EOY amounts
            if date.endswith("-01-01"):
                if next_date:
                    assert next_date.endswith("-01-01")
                    use_date = date.replace("-01-01", "-06-01")
                    use_amount = (use_amount + next_amount) / 2
                else:
                    use_date = None
                    use_amount = None

            next_date = date
            next_amount = amount

            if not use_date:
                continue

            yyyy, mm, dd = use_date.split("-")
            assert mm == "06"
            yyyy = int(yyyy)

            historical_amounts[category, yyyy] += use_amount

cpis = {}
with open("CPIAUCSL.csv") as inf:
    for line in inf:
        line = line.strip()
        if not line:
            continue
        date, CPIAUCSL = line.split(",")
        if date == "DATE":
            continue

        CPIAUCSL = float(CPIAUCSL)
        cpis[date] = CPIAUCSL

def deflate(v, yyyy):
    target = "2024-06-01"
    v_date = "%s-06-01" % yyyy

    return cpis[target] / cpis[v_date] * v
        
sorted_categories = list(sorted(set(categories.values())))
print("date", *sorted_categories, sep="\t")
for yyyy in range(2015, 2025):
    print("%s-06" % yyyy, *[
        round(deflate(historical_amounts[category, yyyy], yyyy))
        for category in sorted_categories], sep="\t")
                

        
        
