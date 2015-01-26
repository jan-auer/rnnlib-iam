set -e

if [ $# -ne 2 ]; then
	echo "Usage: ./$FILE <mode> <dataset>"
	exit
fi

CDL_FILES=(
	header.cdl
	seqTags.cdl
	labels.cdl
	wordTargetStrings.cdl
	targetStrings.cdl
	seqLengths.cdl
	seqDims.cdl
	inputs.cdl
)

./iam_$1.py $2
cat ${CDL_FILES[@]} > combined.cdl
echo '}' >> combined.cdl

echo "Generating $2.nc"
ncgen -o $2.nc combined.cdl
rm ${CDL_FILES[@]} combined.cdl

