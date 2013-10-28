# called from update_happiness.sh
#
# given a file with lines like:
#   1381228301 6 bed computer  [2013.10.08 06:31:41 Tue]
#   1381228369  [2013.10.08 06:32:49 Tue]
#   1381230590 bed computer 5  [2013.10.08 07:09:50 Tue]
#
# produce a file like:
#   [[1381228301, 6],
#    [1381230590, 5]]

IN=/home/jefftk/jtk/tagtime.log
OUT=/home/jefftk/jtk/happiness.log

echo "[" > $OUT
cat $IN | \
  while read ts rest
  do 
    echo "[$ts, $(echo " $rest " | grep -o ' [0-9] ' | sed 's/ //g')],"
  done | grep -v ', ],$' | sed 's/,$/\n,/' >> $OUT
# remove trailing comma
sed -i '$ d' $OUT

echo "]" >> $OUT
