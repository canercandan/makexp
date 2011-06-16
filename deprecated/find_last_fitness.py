#!/usr/bin/env python

import os.path as pa
import shutil

SAMPLES = [
    ("IPC3_STRIPS_DEPOTS_13",
     "/tools/pddl/ipc/IPC3/Tests1/Depots/Strips/Depots.pddl",
     "/tools/pddl/ipc/IPC3/Tests1/Depots/Strips/pfile13"),

    ("IPC3_STRIPS_DRIVERLOG_11",
     "/tools/pddl/ipc/IPC3/Tests1/DriverLog/Strips/driverlog.pddl",
     "/tools/pddl/ipc/IPC3/Tests1/DriverLog/Strips/pfile11"),

    ("IPC6_COST_SCANALYSER_22",
     "/tools/pddl/ipc/ipc2008/seq-sat/scanalyzer-strips/p22-domain.pddl",
     "/tools/pddl/ipc/ipc2008/seq-sat/scanalyzer-strips/p22.pddl"),

    ("IPC6_TEMPO_PARCPRINTER_11",
     "/tools/pddl/ipc/ipc2008/tempo-sat/parcprinter-strips/p11-domain.pddl",
     "/tools/pddl/ipc/ipc2008/tempo-sat/parcprinter-strips/p11.pddl"),

    ("IPC6_SEQ_ELEVATORS_12",
     "/tools/pddl/ipc/ipc2008/seq-sat/elevators-strips/p12-domain.pddl",
     "/tools/pddl/ipc/ipc2008/seq-sat/elevators-strips/p12.pddl"),

    ("IPC6_TEMPO_OPENSTACKS_17",
     "/tools/pddl/ipc/ipc2008/tempo-sat/openstacks-strips/p17-domain.pddl",
     "/tools/pddl/ipc/ipc2008/tempo-sat/openstacks-strips/p17.pddl"),
    ]

POPSIZES = [48, 1152, 2304, 3456, 4608, 5760]
CORESIZES = [48]
NRUNS = 21
BINARIES = ['dae-sm']
DYNAMIC = True
RESTART = True
PATTERN = "%(SAMPLE)s_%(SCHEMA)s_%(BINARY)s_%(DYNAMIC)s_S%(POPSIZE)d_C%(CORESIZE)d.soln.%(NUMRUN)d.%(SUFFIX)s"

for sample,domain,pfile in SAMPLES:
    for size in POPSIZES:
        for binary in BINARIES:
            for core in CORESIZES:
                for num in xrange(1, NRUNS+1):
                    i = 1

                    while 1:

                        dico = {'SAMPLE': sample,
                                'POPSIZE': size,
                                'CORESIZE': core,
                                'NUMRUN': num,
                                'SUFFIX': i,
                                'BINARY': binary,
                                'SCHEMA': "RESTART" if RESTART else "",
                                'DYNAMIC': "DYNAMIC" if DYNAMIC else "STATIC",
                                }

                        if pa.isfile(PATTERN % dico):
                            i += 1
                            continue

                        dico['SUFFIX'] = i-1

                        print 'the last one is: %s' % PATTERN % dico

                        src = PATTERN % dico
                        dico['SUFFIX'] = 'last'
                        dst = PATTERN % dico
                        shutil.copy(src, dst)

                        break
