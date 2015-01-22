set -e

./iam_${1}.py $2
cat header.cdl seqTags.cdl labels.cdl wordTargetStrings.cdl targetStrings.cdl seqLengths.cdl seqDims.cdl inputs.cdl > $2.cdl
echo '}' >> $2.cdl

echo "Generating $2.nc"
ncgen -o $2.nc $2.cdl
rm ./*.cdl

