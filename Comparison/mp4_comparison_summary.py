# "Method", "Threshold","Resolution", "frame", "Average total time per frame", "Average frame conversion", "Theoretical fps"
import csv

def rounded_average(l):
    return round(sum(l) / len(l), 2)

results_per_method = {}

with open("mp4_results.csv", "r") as f:
    reader = csv.DictReader(f)

    for line in reader:
        method_name = line["Method"]
        if method_name not in results_per_method:                     # Unique dictionary for each technique used, based on method name
            results_per_method[method_name] = ([],[],[])


        results_per_method[method_name][0].append(float(line["Average total time per frame"]))   # Average total time per frame
        results_per_method[method_name][1].append(float(line["Average frame conversion"]))   # Average frame conversion
        results_per_method[method_name][2].append(float(line["Theoretical fps"]))   # Theoretical fps


for method, results in results_per_method.items():
    print(method)
    print(f"Average total time per frame:\t{rounded_average(results[0])}")
    print(f"Average frame conversion:\t\t{rounded_average(results[1])}")
    print(f"Theoretical fps:\t\t\t\t{rounded_average(results[2])}")
    print()
