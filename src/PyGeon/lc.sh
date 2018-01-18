s=0;
for i in `ls */*py`
do
#echo `wc $i -l|grep -Po '[0-9]*'` $i
s=$((s + `wc $i -l|grep -Po '^[0-9]*'`))
done
echo $s


