
import argparse
import sys

'''
Currency Converter
USD, RMB, YEN, NTD, WON
USD ->RMB is 6.8
USD -> YEN is 160
USD -> NTD is 31.8
USD -> WON is 1490
Add a "NOT CONVERTABLE" Message for non-mentioned currencies
--from
--to
--amount
'''
#list
ccc = {"Currency" : ["USD", "RMB","YEN", "NTD", "WON"], "Rate" : [ 1, 6.8, 160, 31.8, 1490]}

#create parser commands for my thing
parser = argparse.ArgumentParser(prog = "currency converter", description = "currency converter")
parser.add_argument('--amount', help="", action="store", type = float, default = "0.0")
parser.add_argument('--to', help="", action="store", default="USD", dest = "to_currency")
parser.add_argument('--from',action="store",default = "USD",dest='from_currency')

args = parser.parse_args()

#if statement
print("currency converter")
if args.from_currency not in ccc["Currency"]:
    print ("not in system, try again")
    sys.exit(1)

if args.to_currency not in ccc ["Currency"]:
    print ("NOt in system, try again")
    sys.exit(1)

#conversion rate


ccname = ccc["Currency"]
ccrate = ccc["Rate"]
ccamount = float(args.amount)

ccfindx= ccname.index(args.from_currency)
ccfrate = ccrate[ccfindx]

cctox = ccname.index(args.to_currency)
cctorate = ccrate[cctox]


ccfstandard = 1/ccfrate

cctstandard = ccfstandard * cctorate


ccdone = args.amount * cctstandard

print(round(ccdone, 2))