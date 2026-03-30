
#first line is always empty (magic python bs)

#statements & loops

#if = switch case: define cases
#else = for multiple cases
#elif = same priority
#for = iteration
#file = holds data permanently (ex: google docs)



#run command prompt command: \domain> python3 filename
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


    print(f"{args.name} has math scores of {math_index}, along with english scores of {english_index}")
    print(f"{args.name}'s math average is {statistics.mean(math_index)}, and their english average is {statistics.mean(english_index)}")
