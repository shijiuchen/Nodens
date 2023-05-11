#!/bin/bash

service=$1
echo $service
ids=($(kubectl get pods | grep $service | awk '{print $1}'))

rm uid.txt

echo $ids



for id in "${ids[@]}"
do
    
    echo $id
    x='"'$id'"'
    y='"'
    command="crictl ps -o json | jq  '.[][].labels | select (.["$y"io.kubernetes.pod.name"$y"] == "$x") | .["$y"io.kubernetes.pod.uid"$y"]' | uniq) "
    uid=$(crictl ps -o json | jq  '.[][].labels | select (.["io.kubernetes.pod.name"] == '$x') | .["io.kubernetes.pod.uid"]' | uniq)
    echo $uid >> uid.txt

done