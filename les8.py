

import argparse
import sys
import csv
import statistics

parser = argparse.ArgumentParser(prog='test_results', description = 'here are some test scores')


parser.add_argument('--age', help= 'have no fear, help is here', action ='store', default = '')

parser.add_argument('--readcsv', help="", action="store", default="dog_scores.csv" )
args = parser.parse_args()
#here is the whole list
#"r" is the file handler, it is opening as a Read ability (write would be W)
emptyscores = []
with open(args.readcsv, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #append edits list
        emptyscores.append(row)

dogscores = {"Dog Age":[], "Human year":[]}
'''
we are going to append the values in math1,2,3, etc... to their own list, then append the list into the dictionary
this fixes the formatting issue where all math values are in one list, not sets of list
'''
for row in emptyscores:
    dogscores["Dog Age"].append(row["Dog"])
    appenddog = []
    appenddog.append(int(row["s"]))
    appenddog.append(int(row["m"]))
    appenddog.append(int(row["l"]))
    appenddog.append(int(row["g"]))
    dogscores["Human year"].append(appenddog)


print("Query for " + args.age + "...")
if args.age == '' or (args.age not in dogscores ["Dog Age"]): 
    # specific formatting in the conditional here
        print("Error: Not in system")
        sys.exit(1)
          
else:
     
     field_names = dogscores.keys()
#CSV is comma separated text
     dog_index = dogscores["Dog Age"].index(args.age)
     human_index = dogscores["Human year"][dog_index]
#using function here

     mean = statistics.mean(human_index)
     print(f"{args.age} has human range of of {human_index}, so the average age of the dog in human years is {mean}")
