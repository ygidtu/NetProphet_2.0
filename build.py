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
    # if os.path.exists(FILE):
    #     os.remove(FILE)
    #
    # tasks = []
    #
    # for parent, dirs, files in os.walk("./"):
    #     if "bak" in parent:
    #         continue
    #
    #     if ".cpan" in parent:
    #         continue
    #
    #     if parent.endswith("__") or os.path.basename(parent).startswith("__"):
    #         continue
    #
    #     for d in dirs:
    #         if d.startswith("."):
    #             continue
    #
    #         if d.startswith("__"):
    #             continue
    #
    #         tasks.append(os.path.join(parent, d))
    #
    #     for f in files:
    #
    #         if f.startswith(".") or f == "NetProphet_2.0-master-cad8020.zip":
    #             continue
    #         tasks.append(os.path.join(parent, f))
    #
    # patoolib.create_archive(FILE, tasks)
    check_call("docker build -t ygidtu/netprophet2 .", shell=True)


if __name__ == '__main__':
    main()
