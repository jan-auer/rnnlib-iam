#!/usr/bin/env python
import math, glob, sys, os, re
from xml.dom.minidom import parse

def avg(l): 
	return math.fsum(l) / len(l)

def var(l):
	a = avg(l)
	return reduce(lambda s, x: s + (x - a) ** 2, l) / len(l)

def std(l):
	return math.sqrt(var(l))

# Stores all values for x, y coordinates
x = []
y = []

# Process all active samples in the current training set
TRAIN_FILE = 'trainset.txt'
for sample in file(TRAIN_FILE).readlines():
	basePath = re.sub(r'^(((\w+)-\d+)\w?)$', '\g<3>/\g<2>/\g<1>', sample.strip())
	print "Processing sample", basePath

	# Load all stroke points for the current line as inputs
	linePath = 'lineStrokes/%s-*.xml' % basePath
	for strokesFile in glob.glob(linePath):
		for point in parse(strokesFile).getElementsByTagName('Point'):
			x.append(float(point.getAttribute('x')))
			y.append(float(point.getAttribute('y')))

# Calculate the mean and stdev values
means = [ avg(x), avg(y) ]
stds  = [ std(x), std(y) ]

# Write them to the stdev file
print 'Writing mean and stdev to trainset.std'
stdFile = open('trainset.std', 'w')
stdFile.write(' '.join([ str(m) for m in means ]) + '\n')
stdFile.write(' '.join([ str(s) for s in stds  ])  + '\n')
stdFile.close()
