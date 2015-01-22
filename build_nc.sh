set -e

./english_online.py $1
cat header.cdl seqTags.cdl labels.cdl wordTargetStrings.cdl targetStrings.cdl seqLengths.cdl seqDims.cdl inputs.cdl > $1.cdl
echo '}' >> $1.cdl

echo "Generating $1.nc"
ncgen -o $1.nc $1.cdl
rm ./*.cdl

