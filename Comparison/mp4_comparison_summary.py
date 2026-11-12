# "Method", "Threshold","Resolution", "frame", "Average total time per frame", "Average frame conversion", "Theoretical fps"

def rounded_average(l):
    return round(sum(l) / len(l), 2)

results_per_method = {}

with open("mp4_results.csv", "r") as f:
    f.readline()        # Skip first line

    for line in f:
        result = line.split(",")
        if result[0] not in results_per_method:                     # Unique dictionary for each technique used, based on method name
            results_per_method[result[0]] = ([],[],[])

        results_per_method[result[0]][0].append(float(result[5]))   # Average total time per frame
        results_per_method[result[0]][1].append(float(result[6]))   # Average frame conversion
        results_per_method[result[0]][2].append(float(result[7]))   # Theoretical fps


for method, results in results_per_method.items():
    print(method)
    print(f"Average total time per frame:\t{rounded_average(results[0])}")
    print(f"Average frame conversion:\t\t{rounded_average(results[1])}")
    print(f"Theoretical fps:\t\t\t\t{rounded_average(results[2])}")
    print()
