#/bin/bash

set -e
cmd="cafebot.py --version"
cmd2="barista version cafe"
for i in {4..256};
  do
  if [ $i -gt 255 ]; then
    echo "[ERROR]: IP address is greater than 255, exit"
  #  break;
  else
    host="10.245.243.$i"
    echo $host
    ansible all -a "$cmd2" -i hosts_info

  fi
done



#host="192.168.37.106"
#cmd="cafebot.py --version"

#ansible $host -a "$cmd"

execute() {
    var=`$1`
    #ls -l
    local status=$?
    if [ $status -ne 0 ]; then
        echo "[FAIL]: when executing '$1'" >&2
        echo "***Exit***" >&2
        exit -1
    else
        echo "[PASS]: executed '$1'"
    fi
    return $status
}

#execute "ansible $host -a $cmd"

