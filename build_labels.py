#!/usr/bin/env python

import glob, sys, os, re
from optparse import OptionParser
from xml.dom.minidom import parse

# NetCDF variables and dimensions for RNNlib
labels = set()

# Batch load ALL labels (not only for this training set)
print "Loading labels"
for fileName in glob.glob('ascii/*/*/*.txt'):
	asciiFile = open(fileName, 'r')
	text = re.sub(r'.*[\r\n]+CSR:\s*[\r\n]+', '', asciiFile.read(), 1, re.DOTALL)
	for char in text:
		if char == '\n' or char == '\r': continue
		label = '#_' if char == ' ' else '_' + char
		labels.add(label)
	asciiFile.close()

# Write all labels
labelStrings = [ ' ' if label == '#_' else label[1] for label in labels ]
print ''.join(labelStrings)

