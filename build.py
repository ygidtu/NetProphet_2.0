#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u"""
Pack files into NetProphet2.tar.gz
"""
import os
from subprocess import check_call

import patoolib

FILE = "NetProphet2.tar.gz"


def main():
    if os.path.exists(FILE):
        os.remove(FILE)

    tasks = []

    for parent, dirs, files in os.walk("./"):
        for d in dirs:
            if d.startswith("."):
                continue
            tasks.append(os.path.join(parent, d))

        for f in files:
            if f.startswith("."):
                continue
            tasks.append(os.path.join(parent, f))
            
    patoolib.create_archive(FILE, tasks)

    check_call("docker build -t ygidtu/netprophet2 .", shell=True)

if __name__ == '__main__':
    main()
