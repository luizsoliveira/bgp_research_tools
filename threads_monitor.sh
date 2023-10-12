#!/bin/bash
pid=$(ps ax | grep example.py | grep -v grep | head -n1 | cut -d " " -f 1)

if test ! -z "$pid"
then
    ps -T -p $pid      
fi


