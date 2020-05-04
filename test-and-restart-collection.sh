
cd `dirname $0`
logfile=`basename -s .sh $0`.log

for tracker in track-*.txt
do
    if [[ ! `pgrep -f $tracker` ]]
    then
	# if the process is dead
	time=`date "+%F %T"`
	echo "$time: Restarting Twitter collection: $tracker" >> $logfile
	nohup python3 collect_tweets.py $tracker >> ${tracker/.txt/.nohup.out} &
    fi
done

