#!/usr/bin/env python

#  Copyright 2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""\
This is a tool that helps you to profile where the most of the time in your test cases is consumed.
This is helpful for example in situations where you want to optimise the test execution times.
"""

from robot.api import ExecutionResult

try:
    from robot.api import ResultVisitor
except ImportError:    # Not exposed via robot.api in RF 2.7
    from robot.result.visitor import ResultVisitor

import math, re
import argparse


class KeywordTimes(ResultVisitor):

    VAR_PATTERN = re.compile(r'^(\$|\@)\{[^\}]+\}(, \$\{[^\}]+\})* = ')

    def __init__(self):
        self.keywords = {}

    def end_keyword(self, keyword):
        name = self._get_name(keyword)
        if name not in self.keywords:
           self.keywords[name] = KeywordsTime(name)
        self.keywords[name].elapsedtimes += [keyword.elapsedtime]

    def _get_name(self, keyword):
        name = keyword.name
        m = self.VAR_PATTERN.search(name)
        if m:
           return name[m.end():]
        return name


class KeywordsTime(object):

    def __init__(self, name):
        self.name = name
        self.elapsedtimes = []

    @property
    def elapsed(self):
        return float(sum(self.elapsedtimes))/1000

    @property
    def calls(self):
        return len(self.elapsedtimes)

    @property
    def average_time(self):
        return round(float(self.elapsed)/self.calls, 3)

    @property
    def median_time(self):
        s = sorted(self.elapsedtimes)
        half = float(len(s)-1) / 2
        half_low = int(math.floor(half))
        half_high = int(math.ceil(half))
        return round(float(s[half_low]+s[half_high])/2000, 3)

    @property
    def variance(self):
        squares = [(float(i)/1000)**2 for i in self.elapsedtimes]
        return sum(squares)/len(squares)-(self.elapsed/self.calls)**2

    @property
    def standard_deviation(self):
        return round(self.variance**0.5, 3)

    @property
    def stdev_per_avgtime(self):
        if self.average_time == 0:
            return 0
        return round(100*self.standard_deviation/self.average_time, 2)

    def __cmp__(self, other):
        return cmp(other.elapsed, self.elapsed)


def _print_results(times, shown_keywords, limit):
    s = sorted(times.keywords.values())
    print 'Total time (s) |   Calls | avg time (s) | median time (s) | stdev (s) | stdev/avg time % | Keyword name'
    shown = 0
    for k in s:
        if shown == shown_keywords:
            break
        if limit is not None and k.stdev_per_avgtime > limit:
            continue
        shown += 1
        print str(k.elapsed).rjust(14)+' | '+str(k.calls).rjust(7)+ ' | ' + \
                str(k.average_time).rjust(12) + ' | ' + str(k.median_time).rjust(15) + \
                ' | ' + str(k.standard_deviation).rjust(9) + ' | ' + str(k.stdev_per_avgtime).rjust(16) + (' | "%s"' % k.name)
    print 'Showing %d of total keywords %d' % (shown, len(times.keywords))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', '-l', type=float, help='Filter out keywords with larger percentage'
            ' of stdev/avg time than LIMIT. This helps by filtering out most used "primitive" keywords'
            ' such as Sleep and Run Keyword If etc. and let\'s you focus on the keywords that very often'
            ' take a lot of time to execute (in other words are most fruitful places to focus optimisation effort).')
    parser.add_argument('--show', '-s', default=100, type=int, help='Max number of shown keywords. Default is 100.')
    parser.add_argument('source', help='output from a Robot Framework execution to analyze')
    args = parser.parse_args()
    try:
      resu = ExecutionResult(args.source)
      times = KeywordTimes()
      resu.visit(times)
      _print_results(times, args.show, args.limit)
    except:
        print __doc__
        raise
