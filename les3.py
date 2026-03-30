
#first line is always empty (magic python bs)

#statements & loops

#if = switch case: define cases
#else = for multiple cases
#elif = same priority
#for = iteration
#file = holds data permanently (ex: google docs)

''' 
how to do functions (aka subroutine for fancy schmucks)

def function_name(parameter1, paramter2):
  function body, perform tasks
  return result

the result gives you the temporary variable provided by the function
if the function has c = average, b = sum, and your result is c, it will only give average

return is mainly used for storing variables temporarily, and will be wiped upon recalling the function
print will still print upon running the function

to call function:
 result = function_name(value1, value2)
'''



#run command prompt command: cd domain, should turn into: \domain> python3 filename
import argparse
import sys
import csv
import statistics


#{Dictionary: [list, list, list]}
test_scores = {"Name" : ["Ann", "Bob" , "Chris" , "Derek"], "Math" : [[70, 80, 90], [82,62,92], [73,73,73], [54, 94, 94]], "Eng" : [[20,80,70], [52, 82, 92], [93,73,33], [44,74,54]]}

#how to recall value in dictionary in list
#    print(test_scores["Name"][0])


#variable parser is calling argparse import, the object ArgumentParser, 
parser = argparse.ArgumentParser(prog='test_results', description = 'here are some test scores')
'''
this adds the argument parser, where:
the calling function is called name
help is the prompt
it performs the storing action
there is no default
'''

parser.add_argument('--name', help= 'have no fear, help is here', action ='store', default = '')

#part of useless junk
parser.add_argument('--writecsv', help="", action="store_true", default=False)

args = parser.parse_args()

print("Query for " + args.name + "...")
if args.name == '' or args.name not in test_scores ["Name"]: 
        print("Error: Not in system")
        sys.exit(1)
else:
    print(args.name + " is in the system!")
    name_list = test_scores ["Name"]
    name_index = name_list.index(args.name)
    # f denotes a mixed between str and int, otherwise need a bunch of +
    print(f"{args.name} is in position {name_index}")

    name_math = test_scores ["Math"]
    math_index = name_math[name_index]

    name_english = test_scores ["Eng"]
    english_index = name_english[name_index]
#using function here

    def average(a):
          c = statistics.mean(a)
          return c
    print(f"{args.name} has math scores of {math_index}, along with english scores of {english_index}")
    print(f"{args.name}'s math average is {average(math_index)}, and their english average is {average(english_index)}")

    def chaos(name, test_scores):
        name = args.name
        scores = {}
        scores["Name"] = args.name
        scores["Math"] = math_index
        scores["Eng"] = english_index
        return scores
    print(f"  Here's the whole list: {chaos(args, test_scores)}")








#csv is the function for opening a new file, and having the ability to edit it. (Think like a google docs)

field_names = test_scores.keys()
#CSV is comma separated text

if args.writecsv:
        write_score = chaos(test_scores, args.name)
        print(type(test_scores))
        with open("myfile.csv", "w", newline="") as csvfile:
                field_names = test_scores.keys()
                writer = csv.DictWriter (csvfile, fieldnames=field_names)
                writer.writeheader()
                writer.writerow(write_score)

#needs a "reader" function to actually show me the csv file. Above just saves it to the csv
        print("\nContents of myfile.csv:")
        with open("myfile.csv", "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)

print("Program completed correctly")

#import os
#os.startfile()
