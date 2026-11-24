# Method, Threshold, Resolution, frames, Average time per frame, FPS captured, Unprocessed stream displayed, Processed stream displayed

import csv

def rounded_average(l):
    return round(sum(l) / len(l), 2)

results_per_method = {}

with open("picamera_results.csv", "r") as f:
    reader = csv.DictReader(f)

    for line in reader:
        method_name = line["Method"]
        if method_name not in results_per_method:                     # Unique dictionary for each technique used, based on method name
            results_per_method[method_name] = ([],[], [], [], [])


        results_per_method[method_name][0].append(float(line["Average time per frame"]))   # Average total time per frame
        results_per_method[method_name][1].append(float(line["FPS captured"]))   # FPS captured
        results_per_method[method_name][2].append(float(line["Average capture time per frame"]))   # Average total time per frame
        results_per_method[method_name][3].append(float(line["Average conversion time per frame"]))   # FPS captured
        results_per_method[method_name][4].append(float(line["Average display time per frame"]))   # FPS captured

for method, results in results_per_method.items():
    print(method)
    print(f"Average total time per frame:\t{rounded_average(results[0])}")
    print(f"Theoretical fps:\t\t\t\t{rounded_average(results[1])}")
    print(f"Capture: {rounded_average(results[2])}\nConversion: {rounded_average(results[3])}\nDisplay: {rounded_average(results[4])}")
    print()
