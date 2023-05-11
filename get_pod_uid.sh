#!/bin/bash
service=$1
echo $service
ids=($(kubectl get pods | grep $service | awk '{print $1}'))

rm uid.txt

echo $ids

if [ $service = "search" ]
then 
    target="frontend"
    for id in "${ids[@]}"
    do
        if [[ $id == *$target* ]]
        then
            echo 'yyyyyy'
        else
            echo $id
            x='"'$id'"'
            y='"'
            uid=$(kubectl get pods -A -o custom-columns=NodeName:.spec.nodeName,PodName:.metadata.name,PodUID:.metadata.uid | grep $id | awk '{print $3}')
            echo $uid >> uid.txt
        fi
    done
else
    target1="mongo"
    target2="memcached"
    if [[ $service == *$target1* ]] || [[ $service == *$target2* ]]
    then
        for id in "${ids[@]}"
        do
            echo $id
            x='"'$id'"'
            y='"'
            uid=$(kubectl get pods -A -o custom-columns=NodeName:.spec.nodeName,PodName:.metadata.name,PodUID:.metadata.uid | grep $id | awk '{print $3}')
            echo $uid >> uid.txt
        done
    else
        for id in "${ids[@]}"
        do
            if [[ $id == *$target1* ]] || [[ $id == *$target2* ]]
            then
                echo 'xxxxx'
            else
                echo $id
                x='"'$id'"'
                y='"'
                uid=$(kubectl get pods -A -o custom-columns=NodeName:.spec.nodeName,PodName:.metadata.name,PodUID:.metadata.uid | grep $id | awk '{print $3}')
                echo $uid >> uid.txt
            fi
        done
    fi
fi