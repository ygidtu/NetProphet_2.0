#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u"""
Created at 2020.01.02

A python wrapper for running the netprophet
"""
import os
import sys
from subprocess import check_call
from argparse import ArgumentParser, ArgumentError


if __name__ == '__main__':
    parser = ArgumentParser(description="NetProphet 2.0")

    parser.add_argument("-c", "--config", type=str, required=True, help="Path to config file")
    parser.add_argument("-p", "--processes", type=int, default=1, help="How many cpu to use")

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        try:
            arg = parser.parse_args(sys.argv[1:])
        except ArgumentError as err:
            print(err)
            parser.print_help()

        if not os.path.exists(arg.config) or not os.path.isfile(arg.config):
            print("Please set the correct path to config file")
            exit(1)

        root_dir = os.path.abspath(os.path.dirname(__file__))
        config = os.path.abspath(arg.config)

        if arg.processes <= 0:
            processes = 1
        else:
            processes = arg.processes

        check_call("snakemake --cores {} --latency-wait 30 --nolock --configfile {} -s {}/run_serial.Snakefile all".format(processes, config, root_dir), shell=True)
