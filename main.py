#!/usr/bin/env python3
# -*- coding:utf-8 -*-
u"""
Created at 2020.01.02

A python wrapper for running the netprophet to replace snakemake
"""
import os
import sys
import json
import logging

from argparse import ArgumentParser, ArgumentError
from multiprocessing import Pool
from shutil import rmtree
from subprocess import check_call, CalledProcessError

from tqdm import tqdm

from CODE import prepare_resources
from CODE import weighted_avg_similar_dbds
from CODE import build_motif_network
from CODE import combine_networks
from CODE import convert_fire2meme
from CODE import parse_network_scores
from CODE import parse_motif_summary
from CODE import parse_quantized_bins


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s")


def call(cmd):
    u"""

    :param cmd:
    :return:
    """
    with open(os.devnull, "w+") as w:
        check_call(cmd, shell=True, stdout=w, stderr=w)


class SnakeMakePipe(object):
    u"""

    """

    def __init__(self, path: str, processes: int=1):
        u"""
        path to config file
        :param path:
        :param processes
        """
        self.processes = processes
        # self.__root__ = os.path.abspath(os.path.dirname(__file__))
        self.__root__ = "/opt/NetProphet_2.0"

        if not os.path.exists(path) or not os.path.isfile(path):
            raise FileNotFoundError("Cannot find config file at %s" % path)

        with open(path) as r:
            self.config = json.load(r)

        self.progress = os.path.join(self.config["NETPROPHET2_DIR"], "progress.json")

        if self.check_progress(11):
            logging.info("Please remove {} before re-run this pipeline".format(self.progress))

    def check_progress(self, step):
        u"""

        :param step:
        :return:
        """

        progress = []
        if os.path.exists(self.progress):
            with open(self.progress) as r:
                progress = json.load(r)

        return step in progress

    def log_progress(self, step):
        progress = []
        if os.path.exists(self.progress):
            with open(self.progress) as r:
                progress = json.load(r)

        if step not in progress:
            progress.append(step)

        with open(self.progress, "w+") as w:
            json.dump(progress, w, indent=4)

    def step1(self):
        u"""
        STEP 1 to create output dir or files
        :return:
        """
        logging.info("STEP1: make_directories")

        if self.check_progress(1):
            logging.info("STEP1: skipped")
            return

        paths = [
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["RESOURCES_DIR"],
                "tmp"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "networks/"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "motif_inference/"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "motif_inference/network_scores/"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "motif_inference/network_bins/"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "motif_inference/motifs_pfm/"
            ),
            os.path.join(
                self.config["NETPROPHET2_DIR"],
                self.config["OUTPUT_DIR"],
                "motif_inference/motifs_score/"
            )
        ]

        for i in paths:
            if not os.path.exists(i):
                logging.info("Create %s" % i)
                os.makedirs(i)
            else:
                logging.info("%s exists" % i)
        self.log_progress(1)

    def step2(self):
        u"""

        :return:
        """
        logging.info("STEP2: prepare_resources")

        if not self.check_progress(1):
            raise FileNotFoundError("Please run STEP1 before run STEP2")
        else:

            if not self.check_progress(2):
                prepare_resources.main([
                    "-g", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_GENES"]
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-e", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_EXPRESSION_DATA"]
                    ),
                    "-c", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_SAMPLE_CONDITIONS"]
                    ),
                    "-or", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/rdata.expr"
                    ),
                    "-of", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/data.fc.tsv"
                    ),
                    "-oa", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/allowed.adj"
                    ),
                    "-op1", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/data.pert.adj"
                    ),
                    "-op2", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/data.pert.tsv"
                    ),
                ])

                self.log_progress(2)

    def step3(self):
        u"""

        :return:
        """
        logging.info("STEP3: map_np_network")
        if not self.check_progress(2):
            raise FileNotFoundError("Please run STEP2 before run STEP3")
        else:
            if not self.check_progress(3):
                check_call(
                    "bash {program} -m -u {input_u} -t {input_t} -r {input_r} -a {input_a} -p {input_p} -d {input_d} -g {input_g} -f {input_f} -o {input_o} -n {output_n}".format(**{
                        "program": os.path.join(self.__root__, "SRC/NetProphet1/netprophet"),
                        "input_u": os.path.join(
                            self.config["NETPROPHET2_DIR"], "SRC/NetProphet1/"),
                        "input_t": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            self.config["FILENAME_EXPRESSION_DATA"]),
                        "input_r": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            "tmp/rdata.expr"
                        ),
                        "input_a": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            "tmp/allowed.adj"
                        ),
                        "input_p": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            "tmp/data.pert.adj"
                        ),
                        "input_d": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            self.config["FILENAME_DE_ADJMTR"]
                        ),
                        "input_g": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            self.config["FILENAME_GENES"]
                        ),
                        "input_f": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["RESOURCES_DIR"],
                            self.config["FILENAME_REGULATORS"]
                        ),
                        "input_o": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["OUTPUT_DIR"],
                            "networks/"
                        ),
                        "output_n": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["OUTPUT_DIR"],
                            "networks/np.adjmtr"
                        )
                    }),
                    shell=True
                )

                self.log_progress(3)

    def step4(self):
        u"""

        data_fc_expr=${1}
        pert_matrix=${2}
        tf_names=${3}
        output_adjmtr=${4}
        use_serial=${5}

        :return:
        """

        logging.info("STEP4: map_bart_network")

        if not self.check_progress(3):
            raise FileNotFoundError("Please run STEP3 before run STEP4")
        else:
            if not self.check_progress(4):
                check_call("Rscript --vanilla {program} fcFile={data_fc_expr} isPerturbedFile={pert_matrix} tfNameFile={tf_names} saveTo={output_adjmtr}.tsv mpiBlockSize={processes}".format(**{
                    "program": os.path.join(self.__root__, "CODE/build_bart_network.r"),
                    "data_fc_expr": os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/data.fc.tsv"
                    ),
                    "pert_matrix": os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        "tmp/data.pert.adj"
                    ),
                    "tf_names": os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "output_adjmtr": os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/bn.adjmtr"
                    ),
                    "processes": self.processes
                }), shell=True)

                # 推测，这里只是单纯的去除行名和列名
                o = os.path.join(self.config["NETPROPHET2_DIR"], self.config["OUTPUT_DIR"], "networks/bn.adjmtr")
                with open(o, "w+") as w:
                    with open(o + ".tsv") as r:
                        for idx, line in enumerate(r):
                            if idx > 0:
                                lines = line.split()
                                if len(lines) > 0:
                                    w.write("\t".join(lines[1:]) + "\n")

                self.log_progress(4)

    def step5(self):
        u"""

        :return:
        """

        logging.info("STEP5: weighted_average_np_network")

        if not self.check_progress(4):
            raise FileNotFoundError("Please run STEP4 before run STEP5")
        else:
            if not self.check_progress(5):
                weighted_avg_similar_dbds.main([
                    "-n", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/np.adjmtr"
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-a", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["DBD_PID_DIR"]
                    ),
                    "-d", "50", "-t", "single_dbds",
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/npwa.adjmtr"
                    )
                ])

                self.log_progress(5)

    def step6(self):
        u"""

        :return:
        """
        logging.info("STEP6: weighted_average_bart_network")

        if not self.check_progress(5):
            raise FileNotFoundError("Please run STEP5 before run STEP6")
        else:
            if not self.check_progress(6):
                weighted_avg_similar_dbds.main([
                    "-n", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/bn.adjmtr"
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-a", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["DBD_PID_DIR"]
                    ),
                    "-d", "50", "-t", "single_dbds",
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/bnwa.adjmtr"
                    )
                ])

                self.log_progress(6)

    def step7(self):
        u"""

        :return:
        """
        logging.info("STEP7: combine_npwa_bnwa")

        if not self.check_progress(6):
            raise FileNotFoundError("Please run STEP6 before run STEP7")
        else:
            if not self.check_progress(7):
                check_call(
                    "Rscript {program} {input_n} {input_b} {output_o}".format(**{
                        "program": os.path.join(self.__root__, "CODE/quantile_combine_networks.r"),
                        "input_n": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["OUTPUT_DIR"],
                            "networks/npwa.adjmtr"
                        ),
                        "input_b": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["OUTPUT_DIR"],
                            "networks/bnwa.adjmtr"
                        ),
                        "output_o": os.path.join(
                            self.config["NETPROPHET2_DIR"],
                            self.config["OUTPUT_DIR"],
                            "networks/npwa_bnwa.adjmtr"
                        )
                    }),
                    shell=True
                )

                self.log_progress(7)

    def step8(self):
        u"""

        ## Check if all motifs are ready
        bash CODE/check_inference_status.sh ${OUTPUT_DIR}/motif_inference/motif_inference.log $REGULATORS $FLAG

        :return:
        """
        logging.info("STEP8: infer_motifs")

        if not self.check_progress(7):
            raise FileNotFoundError("Please run STEP7 before run STEP8")
        else:
            if not self.check_progress(8):
                logging.info("Binning promoters based on network scores ... ")

                parse_network_scores.main([
                    "-a", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/npwa_bnwa.adjmtr"
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-t", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_GENES"]
                    ),
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "motif_inference/network_scores"
                    )
                ])

                parse_quantized_bins.main([
                    "-n", "20",
                    "-i", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "motif_inference/network_scores"
                    ),
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "motif_inference/network_bins"
                    ),
                ])

                logging.info("Done")

                promoter = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["RESOURCES_DIR"],
                    self.config["FILENAME_PROMOTERS"]
                )
                out_dir = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["OUTPUT_DIR"]
                )

                tasks = []
                with open(os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"])
                ) as r:
                    for regulator in r:
                        regulator = regulator.strip()

                        tasks.append(
                            "perl {FIREDIR}/fire.pl --expfiles={OUTDIR} --exptype=discrete --fastafile_dna={PROMOTER} --k=7 --jn=20 --jn_t=16 --nodups=1 --dorna=0 --dodnarna=0".format(**{
                                "FIREDIR": os.getenv("FIREDIR"),
                                "OUTDIR": os.path.join(out_dir, "motif_inference/network_bins", regulator),
                                "PROMOTER": promoter
                            })
                        )

                try:
                    with Pool(self.processes) as p:
                        list(tqdm(p.imap(call, tasks), total=len(tasks)))
                except CalledProcessError as err:
                    logging.error(err)
                    exit(1)

                self.log_progress(8)

    def step9(self):
        u"""

        :return:
        """
        logging.info("STEP9: score_motifs")

        if not self.check_progress(8):
            raise FileNotFoundError("Please run STEP8 before run STEP9")
        else:
            if not self.check_progress(9):
                OUTPUT_DIR = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["OUTPUT_DIR"]
                )
                MOTIFS_DIR = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["OUTPUT_DIR"],
                    "motif_inference/network_bins/"
                )
                REGULATORS = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["RESOURCES_DIR"],
                    self.config["FILENAME_REGULATORS"]
                )
                PROMOTERS = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["RESOURCES_DIR"],
                    self.config["FILENAME_PROMOTERS"]
                )
                MOTIFS_LIST = os.path.join(
                    self.config["NETPROPHET2_DIR"],
                    self.config["OUTPUT_DIR"], "motif_inference/motifs.txt"
                )

                logging.info("Parsing motif inference results ... ")
                parse_motif_summary.main([
                    "-a", "True",
                    "-i", MOTIFS_DIR,
                    "-o", MOTIFS_LIST
                ])
                convert_fire2meme.main([
                    "-i", MOTIFS_LIST,
                    "-o", os.path.join(OUTPUT_DIR, "motif_inference/motifs_pfm/")
                ])
                logging.info("Done")

                # score_motifs $  $PROMOTERS $ ${OUTPUT_DIR}/motif_inference/motif_scoring.log

                FN_TF_PWM = os.path.join(OUTPUT_DIR, "motif_inference/motifs_pfm/")  # directory of tf pwm
                FN_PROMOTERS = PROMOTERS  # promoter sequence file
                OUT_FIMO = os.path.join(OUTPUT_DIR, "motif_inference/motifs_score")  # directory of fimo alignment output

                tasks1, tasks2, tasks3 = [], [], []
                with open(REGULATORS) as r:
                    for regulator in r:
                        regulator = regulator.strip()

                        if not os.path.exists(os.path.join(FN_TF_PWM, regulator)):
                            continue

                        if os.path.exists(os.path.join(OUT_FIMO, regulator)):
                            rmtree(os.path.join(OUT_FIMO, regulator))
                        os.makedirs(os.path.join(OUT_FIMO, regulator))

                        tasks1.append("{fimo} -o {OUT_FIMO}/{regulator} --thresh 5e-3 {FN_TF_PWM}/{regulator} {FN_PROMOTERS}".format(**{
                            "OUT_FIMO": OUT_FIMO,
                            "regulator": regulator,
                            "FN_TF_PWM": FN_TF_PWM,
                            "FN_PROMOTERS": FN_PROMOTERS,
                            "fimo": os.path.join(self.__root__, "SRC/meme/bin/fimo")
                        }))

                        tasks2.append("sed '1d' {OUT_FIMO}/{regulator}/fimo.txt | cut -f 1,2,7 > {OUT_FIMO}/{regulator}/temp.txt".format(**{
                            "OUT_FIMO": OUT_FIMO,
                            "regulator": regulator,
                        }))

                        tasks3.append("ruby {program} -i {OUT_FIMO}/{regulator}/temp.txt > {OUT_FIMO}/{regulator}.summary".format(**{
                            "OUT_FIMO": OUT_FIMO,
                            "regulator": regulator,
                            "program": os.path.join(self.__root__, "CODE/estimate_affinity.rb")
                        }))

                with Pool(self.processes) as p:
                    try:
                        list(tqdm(p.imap(call, tasks1), total=len(tasks1)))
                    except CalledProcessError as err:
                        pass
                    try:
                        list(tqdm(p.imap(call, tasks2), total=len(tasks2)))
                        list(tqdm(p.imap(call, tasks3), total=len(tasks3)))
                    except CalledProcessError as err:
                        logging.error(err)
                        exit(1)

                self.log_progress(9)

    def step10(self):
        u"""
        :return:
        """

        logging.info("STEP10: build_motif_network")

        if not self.check_progress(9):
            raise FileNotFoundError("Please run STEP9 before run STEP10")
        else:
            if not self.check_progress(10):
                build_motif_network.main([
                    "-i", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "motif_inference/motifs.txt"
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-g", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_GENES"]
                    ),
                    "-f", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "motif_inference/motifs_score/"
                    ),
                    "-t", "robust",
                    "-v", str(self.config["MOTIF_THRESHOLD"]),
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/mn.adjmtr"
                    )
                ])

                self.log_progress(10)

    def step11(self):
        u"""
        :return:
        """
        logging.info("STEP11: assemble_final_network")
        if not self.check_progress(10):
            raise FileNotFoundError("Please run STEP10 before run STEP11")
        else:
            if not self.check_progress(11):
                combine_networks.main([
                    "-s", "resort",
                    "-n", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/npwa_bnwa.adjmtr"
                    ),
                    "-b", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/mn.adjmtr"
                    ),
                    "-od", os.path.join(self.config["NETPROPHET2_DIR"], self.config["OUTPUT_DIR"], "networks/"),
                    "-om", "npwa_bnwa_mn.adjmtr"
                ])

                weighted_avg_similar_dbds.main([
                    "-n", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        "networks/", "npwa_bnwa_mn.adjmtr"
                    ),
                    "-r", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["FILENAME_REGULATORS"]
                    ),
                    "-a", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["RESOURCES_DIR"],
                        self.config["DBD_PID_DIR"]
                    ),
                    "-d", "50", "-f", "single_dbds",
                    "-o", os.path.join(
                        self.config["NETPROPHET2_DIR"],
                        self.config["OUTPUT_DIR"],
                        self.config["FILENAME_NETPROPHET2_NETWORK"]
                    )
                ])

                self.log_progress(11)


if __name__ == '__main__':
    parser = ArgumentParser(description="NetProphet 2.0")

    parser.add_argument("-c", "--config", type=str, required=True, help="Path to config file")
    parser.add_argument("-p", "--processes", type=int, default=1, help="How many cpu to use")

    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        try:
            args = parser.parse_args(sys.argv[1:])

            if not os.path.exists(args.config) or not os.path.isfile(args.config):
                print("Please set the correct path to config file")
                exit(1)

            root_dir = os.path.abspath(os.path.dirname(__file__))
            config = os.path.abspath(args.config)

            if args.processes <= 0:
                processes = 1
            else:
                processes = args.processes

            runner = SnakeMakePipe(args.config, args.processes)

            runner.step1()
            runner.step2()
            runner.step3()
            runner.step4()
            runner.step5()
            runner.step6()
            runner.step7()
            runner.step8()
            runner.step9()
            runner.step10()
            runner.step11()

        except ArgumentError as err:
            print(err)
            parser.print_help()




