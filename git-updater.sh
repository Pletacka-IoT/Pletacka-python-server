#!/usr/bin/env bash

set -e # Stop on error

while :
do
    date
    git fetch
    git reset --hard origin/master
    git clean -f

    # Restart your services here

    while :
    do
        sleep 60
        git fetch
        if git status | grep 'behind'
        then
            break
        fi
    done
done  