import statistics
import time

#time

timea = time.time()
print(time.localtime())
#lists
a = [92, 95, 82, 12, 11]
b = [12, 13, 14, 15, 16]
score = {"math" : a, "english" :b }

#code
print(score["math"])
print(statistics.mean(score["math"]))
c = sum(score["math"]) / len(score["math"])
print(c)


#time operator - IMPORTANT


timeb = time.time()
timediff = timeb-timea
print(timediff)
print(timeb)

z = timediff * 1000000000
print(f" {z} nanoseconds")

print(time.localtime())
