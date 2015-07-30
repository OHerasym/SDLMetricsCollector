# JiraMetricMetter
Script for collecting metrics according to https://adc.luxoft.com/confluence/display/APPLINK/2015/06/25/Developers+team+metrics
Dependency:
https://pypi.python.org/pypi/jira

Currently suports only daily metrics
Can send email to developers, that have fails in metrics. (use -m option for this)


For help use :
./metrics.py -h
[code]
usage: metrics.py [-h] [-m] [-v VACATION [VACATION ...]]
                  [-d DEVELOPERS [DEVELOPERS ...]]

optional arguments:
  -h, --help            show this help message and exit
  -m, --send_mail       Sent emails about result
  -v VACATION [VACATION ...], --vacation VACATION [VACATION ...]
                        Developer on vacation
  -d DEVELOPERS [DEVELOPERS ...], --developers DEVELOPERS [DEVELOPERS ...]
                        Custom developers list
[/code]
