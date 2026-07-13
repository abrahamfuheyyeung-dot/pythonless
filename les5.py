
#run command prompt command: cd domain, should turn into: \domain> python3 filename
import argparse
import sys
import csv
import statistics


'''
background work we don't see here:
 - made a spreadsheet
 - imported into computer as csv file
 - when we type into command prompt the --readcsv, we are reading the csv file we have:
      f.e: python3 les5.py --readcsv fromsheet.csv

'''

#{Dictionary: [list, list, list]}
#test_scores = {"Name" : ["Ann", "Bob" , "Chris" , "Derek"], "Math" : [[70, 80, 90], [82,62,92], [73,73,73], [54, 94, 94]], "Eng" : [[20,80,70], [52, 82, 92], [93,73,33], [44,74,54]]}

parser = argparse.ArgumentParser(prog='test_results', description = 'here are some test scores')


parser.add_argument('--name', help= 'have no fear, help is here', action ='store', default = '')

parser.add_argument('--readcsv', help="", action="store", default=int )
args = parser.parse_args()
#here is the whole list
#"r" is the file handler, it is opening as a Read ability (write would be W)
emptyscores = []
with open(args.readcsv, "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        #append edits list
        emptyscores.append(row)



#reading list here
testscores = {"Name":[], "Math" :[], "Eng" :[]}
'''
we are going to append the values in math1,2,3, etc... to their own list, then append the list into the dictionary
this fixes the formatting issue where all math values are in one list, not sets of list
'''
for row in emptyscores:
    testscores["Name"].append(row["Name"])
    appendmath = []
    appendmath.append(int(row["Math 1"]))
    appendmath.append(int(row["Math 2"]))
    appendmath.append(int(row["Math 3"]))
    testscores["Math"].append(appendmath)
   
    appendeng = []
    appendeng.append(int(row["Eng 1"]))
    appendeng.append(int(row["Eng 2"]))
    appendeng.append(int(row["Eng 3"]))
    testscores["Eng"].append(appendeng)


#back to the good ol days


print("Query for " + args.name + "...")
if args.name == '' or (args.name not in testscores ["Name"] and args.name != 'all'): 
    # specific formatting in the conditional here
        print("Error: Not in system")
        sys.exit(1)
          
else:
     
     field_names = testscores.keys()
#CSV is comma separated text
     name_list = testscores ["Name"]
     name_index = name_list.index(args.name)
     name_math = testscores ["Math"]
     math_index = name_math[name_index]

     name_english = testscores ["Eng"]
     english_index = name_english[name_index]
#using function here

     print(f"{args.name} has math scores of {math_index}, along with english scores of {english_index}")
     print(f"{args.name}'s math average is {statistics.mean(math_index)}, and their english average is {statistics.mean(english_index)}")

