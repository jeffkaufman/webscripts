# ./update_happiness.sh timepie.log
#
# Every so often, on your phone, have tagtime send you it's log.  Then
# run the log through this program, which will take the new lines and
# put them in tagtime.log.  This also runs extract_happiness.sh to
# create happiness.log which is used by /happiness_graph

if [ $# -ne 1 ]
then
  echo "usage: $0 timepie.log"
  exit 2
fi

IN="$1"
OUT=/home/jefftk/jtk/tagtime.log
OUT_T=/home/jefftk/jtk/tagtime.log.tmp

cp $OUT $OUT_T

cat "$IN" | \
  while read ts rest
  do
    grep "$ts" $OUT > /dev/null || echo "$ts $rest" >> $OUT_T
  done

diff $OUT $OUT_T
echo -n "look good? [y/n] "
read q
if [ "$q" == "y" ]
then
  cp $OUT_T $OUT
  /home/jefftk/bin/extract_happiness.sh
else
  echo "no change made"
fi
