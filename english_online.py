#!/usr/bin/env python

import glob, sys, os, re
from optparse import OptionParser
from xml.dom.minidom import parse

# NetCDF variables and dimensions for RNNlib
labels = set()
numSeqs = 0
numDims = 1
numTimesteps = 0
inputPattSize = 3 # x, y and pen-up
maxSeqTagLength = 0
maxTargStringLength = 0
maxWordTargStringLength = 0

# Internal stuff
first = True

def createCdl(name, delimiter=''):
	f = open(name + '.cdl', 'w')
	f.write(' ' + name + ' =\n  ' + delimiter)
	return f

def closeCdl(f, delimiter=''):
	f.write(delimiter + ' ;\n\n')
	f.close()

if len(sys.argv) != 3:
	print "Usage: english_online.py <std_file> <dataset_name>"
	exit(1)

print "Loading statistical distribution"
with open(sys.argv[1], 'r') as stdFile:
	inputMeans = [ float(i) for i in stdFile.readline().split(' ') ]
	inputStds = [ float(i) for i in stdFile.readline().split(' ') ]

# Intermediate files (*.cdl) for NetCDF generation
seqTagsFile = createCdl('seqTags', '"')
seqDimsFile = createCdl('seqDims')
seqLengthsFile = createCdl('seqLengths')
targetStringsFile = createCdl('targetStrings', '"')
wordTargetStringsFile = createCdl('wordTargetStrings', '"')
inputsFile = createCdl('inputs')
labelsFile = createCdl('labels', '"')

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
numLabels = len(labels)
labelStrings = [ label.replace('"','\\"').replace("'","\\'") for label in labels ]
maxLabelLength = len(max(labelStrings, key=len))
labelsFile.write('",\n  "'.join(labelStrings))

# Process all active samples in the current training set
for sample in file(sys.argv[2] + '.txt').readlines():
	basePath = re.sub(r'^(((\w+)-\d+)\w?)$', '\g<3>/\g<2>/\g<1>', sample.strip())

	# Check whether the sample files exist
	asciiPath = 'ascii/%s.txt' % basePath
	if not os.path.exists(asciiPath):
		print 'ERROR: Sample %s does not exist!' % basePath
		continue

	print "Processing sample", basePath

	# Read the plain text of the sample
	with open(asciiPath, 'r') as asciiFile:
		text = re.sub(r'.*[\r\n]+CSR:\s*[\r\n]+', '', asciiFile.read(), 1, re.DOTALL)
		lines = re.split(r'[\r\n]+', text.strip())

	# Process each line in the text separately
	for i in range(0, len(lines)):
		line = lines[i].strip()
		linePath = 'lineStrokes/%s-%02d.xml' % (basePath, i + 1)
		if not os.path.exists(linePath):
			print 'ERROR: Strokes %s do not exist!' % linePath
			continue

		# Process all characters and build the target sequence
		targetString = ''
		for char in line:
			label = '#_' if char == ' ' else '_' + char
			targetString += label + ' '

		# Load all stroke points for the current line as inputs
		inputs = []
		for stroke in parse(linePath).getElementsByTagName('Stroke'):
			for point in stroke.getElementsByTagName('Point'):
				x = (float(point.getAttribute('x')) - inputMeans[0]) / inputStds[0]
				y = (float(point.getAttribute('y')) - inputMeans[1]) / inputStds[1]
				inputs += [x, y, 0]
			inputs[-1] = 1

		# Update CDL variables
		numSeqs += 1
		numTimesteps += len(inputs) / inputPattSize
		
		# Normalise values for CDL output
		targetString = targetString.strip().replace('"','\\"').replace("'","\\'")
		wordTargetString = line.replace('"','\\"').replace("'","\\'")
		inputString = ',\n  '.join([ str(inp) for inp in inputs ])
		seqLength = str(len(inputs) / inputPattSize)
		
		# Update CDL parameters
		maxSeqTagLength = max(maxSeqTagLength, len(linePath))
		maxTargStringLength = max(maxTargStringLength, len(targetString))
		maxWordTargStringLength = max(maxWordTargStringLength, len(wordTargetString))

		# Write delimiters to the previous data points
		if first:
			first = False
		else:
			seqTagsFile.write('",\n  "')
			seqDimsFile.write(',\n  ')
			seqLengthsFile.write(',\n  ')
			targetStringsFile.write('",\n  "')
			wordTargetStringsFile.write('",\n  "')
			inputsFile.write(',\n  ')

		# Write all data out to the CDL files
		seqTagsFile.write(linePath)
		seqDimsFile.write(seqLength)
		seqLengthsFile.write(seqLength)
		targetStringsFile.write(targetString)
		wordTargetStringsFile.write(wordTargetString)
		inputsFile.write(inputString)

# Finalize all files
closeCdl(seqTagsFile, '"')
closeCdl(seqDimsFile)
closeCdl(seqLengthsFile)
closeCdl(targetStringsFile, '"')
closeCdl(wordTargetStringsFile, '"')
closeCdl(inputsFile)
closeCdl(labelsFile, '"')

# Write the CDL file header
with open('header.cdl', 'w') as headerFile:
	headerFile.write('netcdf latin {\ndimensions:\n')
	headerFile.write('	numSeqs = ' + str(numSeqs) + ' ;\n')
	headerFile.write('	numDims = ' + str(numDims) + ' ;\n')
	headerFile.write('	numLabels = ' + str(numLabels) + ' ;\n')
	headerFile.write('	numTimesteps = ' + str(numTimesteps) + ' ;\n')
	headerFile.write('	inputPattSize = ' + str(inputPattSize) + ' ;\n')
	headerFile.write('	maxSeqTagLength = ' + str(maxSeqTagLength + 1) + ' ;\n')
	headerFile.write('	maxWordTargStringLength = ' + str(maxWordTargStringLength + 1) + ' ;\n')
	headerFile.write('	maxTargStringLength = ' + str(maxTargStringLength + 1) + ' ;\n')
	headerFile.write('	maxLabelLength = ' + str(maxLabelLength) + ' ;\n')
	headerFile.write('variables:\n')
	headerFile.write('	char seqTags(numSeqs, maxSeqTagLength) ;\n')
	headerFile.write('		seqTags:longname = "sequence tags" ;\n')
	headerFile.write('	char labels(numLabels, maxLabelLength) ;\n')
	headerFile.write('		labels:longname = "labels" ;\n')
	headerFile.write('	char wordTargetStrings(numSeqs, maxWordTargStringLength) ;\n')
	headerFile.write('		wordTargetStrings:longname = "target strings" ;\n')
	headerFile.write('	char targetStrings(numSeqs, maxTargStringLength) ;\n')
	headerFile.write('		targetStrings:longname = "target strings" ;\n')
	headerFile.write('	int seqLengths(numSeqs) ;\n')
	headerFile.write('		seqLengths:longname = "sequence lengths" ;\n')
	headerFile.write('	int seqDims(numSeqs, numDims) ;\n')
	headerFile.write('		seqDims:longname = "sequence dimensions" ;\n')
	headerFile.write('	float inputs(numTimesteps, inputPattSize) ;\n')
	headerFile.write('		inputs:longname = "input patterns" ;\n')
	headerFile.write('data:\n\n')

