from collections import defaultdict
from math import log

def readNgramsAsDict (filename):
	grams = defaultdict (int)
	with open (filename) as fin:
		for line in fin:
			parts = line.strip().split ("\t")
			grams[tuple(parts[0].split())] = int(parts[1])
	return grams

def segmentIntoTwoWords (token):
	for i,_ in enumerate (word):
		part1, part2 = word[:i], word[i:]
		if part1 != "" and part2 != "":
			yield part1, part2

def getStandardized (ratios, token, threshold=1):
	bc1, bc2, bratio = max (ratios, key=lambda x:x[2])
	standardized = token
	if bratio > threshold:
		standardized = " ".join ([bc1, bc2])

	return standardized

def P (num, denom, V, s=1):
	return (num + s) / (denom + (V*s))

def Pint(probs, lambdas):
	return sum([lambdas[i]*probs[i] for i in range (len(probs))])

def logP (num, denom, V, s=1):
	return log (num+s) - log (denom + (V*s))
