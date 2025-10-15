#!/usr/bin/env python3

import csv
from collections import Counter

CURRENT="I currently attend BIDA:"
OPTIONAL="If we started requiring masks at all our dances, I would attend:"
REQUIRED="If we stopped requiring masks at any of our dances, I would attend:"

GLYCOL="If BIDA added Glycol Vapors, my attendance would"

def to_annual(s):
    # Convert a string describing expected attendance into a number of times
    # they'd come per year.  We take off August, and otherwise dance 3x/month.

    s = s.strip()
    
    if s == "About monthly":
        return 11
    if s in ["Almost every time", "Every time"]:
        return 11*3
    if s in [
            "I don't attend, but I would if you had different covid policies",
            "Not at all"]:
        return 0
    if s == "About quarterly":
        return 4
    if s == "About yearly":
        return 1

    # Manual parsing of specific responses, added by Claude Sonnet 4.5 with a
    # few manual corrections.
    
    # Current attendance
    if s == "whenever I'm in town!":
        return 4  # quarterly-ish
    if s == "I just moved to the area and plan to start attending this fall":
        return 11  # monthly
    if s == "Whenever I'm in town":
        return 4  # quarterly
    if s == "Used to attend (prepandemic) and would like to come back":
        return 0  # not currently attending
    if s == "I don't attend, and there isn't currently anything that would make me comfortable attending":
        return 0
    if s == "I have yet to come but only due to scheduling conflicts":
        return 4
    if s == "Whenever possible based on masking requirements and my ability to travel from NYC.  Ideally, every time masks are required.":
        return 6
    if s == "I am planning on attending for the first time soon!":
        return 0  # not yet attending
    if s == "I basically cannot contradance with a mask on. So, if I am free and I remember that there is a bida dance, the chance that it will be mask-optional vs mask-required is 50-50. this means that I end up showing up about once a quarter.":
        return 4  # quarterly
    if s == "Rarely, as I live out of town, but attend when I can":
        return 1
    if s == "varies":
        return 11  # assume monthly average
    if s == "I have been a few times, but I intend to come more often":
        return 11  # monthly intention
    if s == "i don't attend, and I'm a bit far away... but the fact that you care about masking makes me want to attend!":
        return 0
    if s == "Not in the area, just sharing a COVID cautious perspective":
        return 0
    if s == "I’m currently not local but I am covid conscious":
        return 0
    if s == "":
        return None  # skip empty responses
    
    # Optional (mask-optional) attendance
    if s == "only for special occasions":
        return 4  # quarterly
    if s == "I would still attend as a musician as long as they weren’t required while playing. If that changes I woyluld probably stop participating in open band.":
        return 4
    if s == "Less than I do normally":
        return 2  # they were 4
    if s == "More often than I currently do, but still subject to the rest of my schedule that means I might not make every dance":
        return 8 # was 4
    if s == "I would probably still come to play, but not to dance":
        return 2
    if s == "more often than I do now, probably either every time or about monthly":
        return 11*2  # split the difference
    if s == "maybe 2/3 of the time? more than monthly most likely!":
        return 11*2  # about 2x per month
    if s == "I think masks should be required during respiratory illness waves":
        return 4 # previously quarterly
    if s == "Range from monthly to quarterly":
        return 8  # between quarterly and monthly
    if s == "Almost every time, like I do now":
        return 11*3
    if s == "Every time I could conceivably travel there!":
        return 11
    if s == "less, unless it was a dance I thought was worth coming into town for":
        return 2  # was 4
    if s == "Every other week":
        return 11*1.5  # roughly 16-17 times
    if s == "less often":
        return 11  # was almost every time
    if s == "As many as I can fit into my schedule!":
        return 22
    
    # Required (mask-required) attendance
    if s == "I would probably go more in this scenario.":
        return 11  # was 4
    if s == "in the early fall and late spring, avoiding flu/covid seasons largely.":
        return 11
    if s == "As often as I can":
        return 11*3
    if s == "Still the same, not in town regularly enough":
        return 4  # was 4
    if s == "If there were a particularly large spike in covid rates and masks were not required, I might attend less":
        return 16
    if s == "Monthly, if not more":
        return 14
    if s == "If there was no masking, it would depend on what I am doing":
        return 11  # monthly average
    if s == "Almost every time, like I do now":
        return 11*3
    if s == "it's hard to say, but if bida was mask optional as a rule, chances are I'd show up way more often because it would be on my radar as \"a thing I could go to if I was free\". I am guessing that would average out to about monthly, with twice a month occasionally.":
        return 11*1.5  # between monthly and twice monthly
    if s == "when I'm in town (once every year or two)":
        return 1  # yearly
    if s == "when I could/have energy for it":
        return 11  # monthly
    if s == "not sure, but probably much less than I have been":
        return 4  # was 11*3
    if s == "I would keep coming, but would be really sad about it":
        return 11*3  # was 11*3
    if s == "Maybe quarterly or so, but if I ended up being the only one masked, I would stop attending entirely":
        return 4  # quarterly
    
    return None

def parse_glycol(s):
    if s == "Increase":
        return "increase"
    if s == "Decrease":
        return "decrease"
    if s == "Glycol Vapors won't change how likely I am to attend":
        return "same"
    return None
    
    

total = 0
total_complete = 0

counts = Counter()

with open("responses.tsv") as inf:
    for row in csv.DictReader(inf, delimiter="\t"):
        if (row[CURRENT].startswith("Not in the area") or
            row[CURRENT].startswith("I’m currently not local")):
            continue
        
        current = to_annual(row[CURRENT])
        optional = to_annual(row[OPTIONAL])
        required = to_annual(row[REQUIRED])
        glycol = parse_glycol(row[GLYCOL])

        total += 1
        if current is None or optional is None or required is None:
            continue

        if glycol is None:
            continue
        
        total_complete += 1

        
        if optional == current == required:
            mask_status = "no change"
        elif optional >= current >= required:
            mask_status = "prefer less"
        elif required >= current >= optional:
            mask_status = "prefer more"
        else:
            print("Inconsistent:")
            print("  current", current, row[CURRENT])
            print("  optional", optional, row[OPTIONAL])
            print("  required", required, row[REQUIRED])
            print()
            mask_status = "inconsistent"

        counts[mask_status, glycol] += 1
            
print(f"Limiting to non-other responses dropped us from "
      f"{total} to {total_complete}")

print("glycol", "prefer less","no change","prefer more","inconsistent", sep="\t")
for glycol in "increase", "same", "decrease":
    print(glycol,
          counts["prefer less", glycol],
          counts["no change", glycol],
          counts["prefer more", glycol],
          counts["inconsistent", glycol],
          sep="\t")
