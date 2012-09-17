#!/usr/bin/env python3

import optparse, logging, sys, os
import common, parser as p
import browsers_variables as b
import stats_variables as s
import tracers_variables as t

logger = logging.getLogger("use_variables")

class ExecutePlan(b.Browser):
    def __init__(self, parser, stat=None):
        b.Browser.__init__(self, parser, stat=stat)

    def browse(self, options, tree):
        tree['MANGLENAME'] = '%(MANGLENAME_PATTERN)s' % tree % tree
        tree['TIME_FILENAME'] = '%(TIMEFILENAME_PATTERN)s' % tree % tree
        tree['RES_FILENAME'] = '%(RESFILENAME_PATTERN)s' % tree % tree
        tree['PLAN_FILENAME'] = '%(PLANFILENAME_PATTERN)s' % tree % tree
        tree['PROCESS_COMMAND'] = '%(COMMAND_PATTERN)s' % tree % tree

        self.logger.debug('%(PROCESS_COMMAND)s' % tree)

        if tree['EXECUTE']:
            p = subprocess.Popen('%(PROCESS_COMMAND)s' % tree, shell=True)
            p.wait()

        self.browseAll(tree)

class SampleDomain(b.Browser):
    def __init__(self, parser, browser=None):
        b.Browser.__init__(self, parser, browser)

    def browse(self, options, tree):
        tree['PROGRESSBAR_SIZE'] *= len(tree['SAMPLES'])

        for tree['NAME'], tree['DOMAIN'], tree['INSTANCE'] in tree['SAMPLES']:
            self.browseAll(tree)

def main():

    parser = p.Parser()

    do = b.Do(parser)
    cmd = b.Command(parser)
    rang = b.Range(parser)
    schema = b.Dynamic(parser)
    pop = b.Pop(parser)
    core = b.Core(parser)
    sample = b.Sample(parser)
    execute = ExecutePlan(parser)
    start = b.Restart(parser)

    evaluationTimeTracer = t.Easy(parser)
    evaluationTimeStat = s.EvaluationTime(parser, evaluationTimeTracer)

    variationTimeTracer = t.Easy(parser)
    variationTimeStat = s.VariationTime(parser, variationTimeTracer)

    replaceTimeTracer = t.Easy(parser)
    replaceTimeStat = s.ReplaceTime(parser, replaceTimeTracer)

    globalTimeTracer = t.Easy(parser)
    globalTimeStat = s.GlobalTime(parser, globalTimeTracer)

    speedupTracer = t.Easy(parser)
    speedupStat = s.TimeSpeedUp(parser, speedupTracer)

    efficiencyTracer = t.Easy(parser)
    efficiencyStat = s.TimeEfficiency(parser, efficiencyTracer)

    makespanTracer = t.Easy(parser, title='makespan', ylabel='Makespan')
    makespanStat = s.MakeSpan(parser, makespanTracer)

    totalcostTracer = t.Easy(parser, title='totalcost', ylabel='Total cost')
    totalcostStat = s.TotalCost(parser, totalcostTracer)

    operatorsTimeTracer = t.OperatorsTimeProportions(parser)
    globalAbsoluteTimeTracer = t.GlobalAbsoluteTime(parser)
    globalTimeSpeedupTracer = t.GlobalTimeSpeedup(parser)
    globalEfficiencyTracer = t.GlobalEfficiency(parser, ybound=(0,1))

    options = parser()

    do\
        .add(start)\
        \
        .add(sample)\
        .add(cmd)\
        .add(schema)\
        .add(core)\
        \
        .add(pop)\
        .add(rang)\
        .add(execute)

    rang.addStats([
            # evaluationTimeStat, variationTimeStat,
            # replaceTimeStat, globalTimeStat,
            #speedupStat,
            efficiencyStat,
            # makespanStat, totalcostStat,
            ])

    pop.addTracers([
            # evaluationTimeTracer, variationTimeTracer,
            # replaceTimeTracer, globalTimeTracer,
            # speedupTracer, efficiencyTracer,
            # makespanTracer, totalcostTracer,
            ])

    do.addTracers([
            #operatorsTimeTracer,
            #globalAbsoluteTimeTracer,
            #globalTimeSpeedupTracer,
            globalEfficiencyTracer,
            ])

    do()

# when executed, just run main():
if __name__ == '__main__':
    logger.debug('### script started ###')
    main()
    logger.debug('### script ended ###')
