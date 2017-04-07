#! /usr/bin/env python2
from datetime import date, timedelta, datetime
import dateutil.parser
import time
import getpass
from getpass import getuser
import smtplib
import argparse
import re

# import xlutils

from xlrd import open_workbook
from xlutils.copy import copy

import config
from utils import *
from queries import *
import auth

class SDL():
    issue_path = "https://adc.luxoft.com/jira/browse/%s"
    server = "http://adc.luxoft.com/jira"

    def __init__(self, sprint, developers_on_vacation=[],
                 developers = config.developers, print_queries=False):
        self.jira = auth.jira_login(self.server)
        self.on_vacation = developers_on_vacation
        self.developers = developers
        self.sdl = self.jira.project('APPLINK')
        self.sprint = "SDL_RB_B3.42"
        self.print_queries = print_queries
        versions = self.jira.project_versions(self.sdl)
        for v in versions:
            if v.name == self.sprint:
                self.sprint = v
                break

    def Query(self, query, maxResults=50):
        if (self.print_queries):
            print(query)
        issues = self.jira.search_issues(query, maxResults=maxResults)
        return issues

    def get_asignee(self, issue):
        return issue.raw['fields']['assignee']['displayName']

    def workload(self, user, report=[]):
        # query = 'assignee = %s AND status not in (Suspended, Closed, Resolved) AND fixVersion in("%s")'
        query = workload_query % (user, self.sprint)
        issues = self.Query(query)
        res = 0
        for issue in issues:
            if issue.fields.timeestimate:
                res += to_h(issue.fields.timeestimate)
                report.append((issue, to_h(issue.fields.timeestimate)))
        return res

    def calc_overload(self):
        report = []
        # for user in self.developers:

        users = 'oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich'

        for user in users.split(', '):
            load = self.workload(user)
            today = time.strftime("%Y-%m-%d")
            days_left = calc_diff_days(today, self.sprint.releaseDate)
            hours_left = days_left * 8
            overload = hours_left - load
            #res = "OK"
            print("%s workload : %s/%s" % (user, load, hours_left))
            if (overload < 0):
                res = "OVERLOAD : %s" % (-overload)
                report_str = "%s/%s : %s" % (load, hours_left, res)
                report.append((user, report_str))
        return report

    def issues_without_due_date(self):
        report = []
        # for user in self.developers:
            # query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s")  AND status not in (Closed, Resolved, Suspended) AND duedate is EMPTY '''

        user = '(oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich)'
        query = issues_without_due_date_query % (user, self.sprint)
        issues = self.Query(query)
        for issue in issues:
            report.append((self.get_asignee(issue), self.issue_path % issue))
            # print issue.raw['fields']['assignee']['displayName']

            # for issue in issues:
            #     today = date.today()
            #     print today.strftime('%m')

            #     add_3_days = date.today() + timedelta(3)
            #     print add_3_days.strftime('%Y-%m-%d')
            #     print add_3_days.strftime('%m')

            #     this_month = today.strftime('%m')
            #     add_3_days_month = add_3_days.strftime('%m')

            #     if this_month != add_3_days_month:
            #         issue.update(fields={'fixVersions' : [{'name': 'SDL_RB_B3.41'}]})

            #     new_due_date = add_3_days.strftime('%Y-%m-%d')
            #     issue.update(fields={'duedate' : new_due_date})
        return report


    def issues_with_expired_due_date(self):
        report = []
        user = '(oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich)'
        
        # for user in self.developers:
            # query = ''' assignee = %s and status not in (closed, resolved, Approved) AND duedate < startOfDay()'''
        query = issues_with_expired_due_date_query % (user)
        issues = self.Query(query)
        for issue in issues:
            report.append((self.get_asignee(issue), self.issue_path % issue))

            # for issue in issues:
            #     print issue.raw['fields']['duedate']
            #     add_3_days = date.today() + timedelta(3)
            #     print add_3_days.strftime('%Y-%m-%d')
            #     new_due_date = add_3_days.strftime('%Y-%m-%d')
            #     issue.update(fields={'duedate' : new_due_date})

        return report


    def expired_in_progress(self):
        report = []
        # for user in self.developers:
            # query = '''assignee = %s AND status in ("In Progress", "Analyze") AND (updated < -2d OR fixVersion = Backlog)'''


        user = '(oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich)'
        

        query = expired_in_progress_query % (user)
        issues = self.Query(query)
        for issue in issues:
            report.append((self.get_asignee(issue), self.issue_path % issue))
        return report


    def without_correct_estimation(self):
        report = []

        user = '(oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich)'
        
        # for user in self.developers:
            # query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s") AND status not in (Closed, Resolved, Suspended) AND (remainingEstimate = 0 OR remainingEstimate is EMPTY)'''
        query = without_correct_estimation_query % (user, self.sprint)
        issues = self.Query(query)
        for issue in issues:
            report.append((self.get_asignee(issue), self.issue_path % issue))

            # for issue in issues:
            #     # print issue.raw['fields']
            #     if not 'timetracking' in issue.raw['fields']:
            #         issue.update(fields={'timetracking' : {"originalEstimate": "2d"}})
        return report

    def expired_code_review(self):
        report = []
        gh = auth.login()
        repo = gh.repository('CustomSDL', 'sdl_panasonic')
        open_pulls = auth.open_pull_request_for_repo(repo)
        for pull in open_pulls:
            if pull.days_old > 2:
                developer = config.get_developer_by_github_user_name(pull.developer)
                if developer in self.developers:
                    report.append((developer, "has review %d days old: %s : %s"%(pull.days_old, pull.caption, pull.url)))
        return report

    def wrong_due_date(self):
        report = []
        for user in self.developers:
            # query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s") AND (duedate < "%s" OR duedate > "%s") AND status not in (resolved, closed)'''
            query = wrong_due_date_query % (user, self.sprint, self.sprint.startDate, self.sprint.releaseDate)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report


    def wrong_fix_version(self):
        report = []

        user = '(oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich)'
        
        # for user in self.developers:
            # query = '''assignee = %s AND fixversion not in ("%s") and (labels is EMPTY OR labels != exclude_from_metrics) AND status not in (closed, resolved) AND duedate > "%s" AND duedate <= "%s" '''
        query = wrong_fix_version_query % (user, self.sprint, self.sprint.startDate, self.sprint.releaseDate)
        issues = self.Query(query)
        for issue in issues:
            report.append((self.get_asignee(issue), self.issue_path % issue))

            # for issue in issues:
            #     print issue.raw['fields']['fixVersions'][0]['name']
            #     issue.update(fields={'fixVersions' : [{'name': 'SDL_RB_B3.40'}]})
        return report

    def absence_in_progress(self):
        report = []
        # for user in self.developers:
        # if user in self.on_vacation:
        #         continue
            # query = '''assignee = %s AND status = "In Progress" '''


        users = 'oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich'


        for user in users.split(', '):
            print user

        for user in users.split(', '):        
            issues = self.Query(absence_in_progress_query % user)
            if (len(issues) == 0):
                report.append((user, None))
        return report


    def not_logged_vacation(self):
        report = []
        vacation_issue_key = "FORDUSSDL-16"
        work_logs = self.jira.worklogs(vacation_issue_key)
        yesterday_work_logs = []
        yesterday = date.today() - timedelta(1)
        for work_log in work_logs:
            date_started = dateutil.parser.parse(work_log.started).date
            if yesterday == date_started:
                yesterday_work_logs.append(date_started)
        for user in self.on_vacation:
            logged = False
            for work_log in yesterday_work_logs:
                if worklog.author.name == user:
                    logged = True
            if not logged:
                report.append((user, " Not logged vacation for " + yesterday.strftime('%Y-%m-%d')))
        return report

    def not_logged_work(self):
        report = []
        user_logged = {}


        users = 'oherasym, akozoriz, agaliuzov, akutsan, aoleynik, anosach, vveremjova, abyzhynar, vprodanov, vlantonov, okozlov, slevchenko, vlambova, omehmedov, pvasilev, dcherniev, atymchenko, istoilov, tkireva, ilytvynenko, pdmytriiev, akalinich'

        for user in users.split(', '):
            user_logged[user] = 0

        # for developer in self.developers:
        #     user_logged[developer.lower()] = 0
        today = date.today()
        last_work = last_work_day()
        query = '''key in workedIssues("%s","%s", "APPLINK Developers")''' % (last_work.strftime("%Y-%m-%d"),
                                                                              today.strftime("%Y-%m-%d"))
        issues = self.Query(query, maxResults=1000)
        for issue in issues:
            work_logs = self.jira.worklogs(issue.key)
            for work_log in work_logs:
                date_started = dateutil.parser.parse(work_log.started).date()
                if date_started == last_work:
                    time_spent = work_log.timeSpent
                    author = work_log.updateAuthor.name
                    if author in user_logged.keys():
                        user_logged[author] += time_spent_from_str(time_spent)
                    # if author in self.developers:
                    #     user_logged[author] += time_spent_from_str(time_spent)
        for developer in user_logged:
            if (user_logged[developer.lower()] < 8):
                report.append(
                    (developer, "Logged for %s : %sh" % (last_work.strftime("%Y/%m/%d"), user_logged[str(developer)])))
        return report

    def daily_metrics(self):
        report = {}
        report['1. Tickets with incorrect or empty due date (except ongoing activities)'] = self.issues_without_due_date()
        # report['2. Tickets with expired due dates'] = self.issues_with_expired_due_date()
        # report['3. Absence of "in progress" or "analyze"'] = self.absence_in_progress()
        # report['4. Tickets "in progress" without updating during last 2 days'] = self.expired_in_progress()
        # report['5. Open issues without correct estimation'] = self.without_correct_estimation()
        # report['6. Open code reviews with age more 2 days'] = self.expired_code_review()
        # report['7. Overload : '] = self.calc_overload()
        # report['8. Previous day work time logging'] = self.not_logged_work()
        # report['9. Not logged vacation/traning'] = self.not_logged_vacation()
        # report['10. Wrong FixVersion'] = self.wrong_fix_version()

        # report['11. Wrong due date'] = self.wrong_due_date()
        return report


def try_again(user):
    return user[1:]



def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None


def remove_developer_name(developers):

    devs = []

    for developer in developers:
        surname, name = developer.split(' ')
        devs.append(surname)

    return devs



def get_current_day():
    return datetime.now().day

def set_1_metric(metircs_list, developers, wb, rb):


    developers = remove_developer_name(developers)

    print(developers)
    print(metircs_list)

    devs_fails = [metric[0].split(' ')[1].lower() for metric in metircs_list]

    print("Current day", get_current_day())

    print(devs_fails)

    for metric in metircs_list:
        name, surname = metric[0].split(' ')
        index = find_element_in_list(surname.lower(), developers)
        count = devs_fails.count(surname.lower())
        print("fails")
        print(surname)
        print(count)

        if index:
            print(index)


            wb.write(index + 2, get_current_day() - 1, count)
        else:
            print("None value")



def get_list_developers(rb):

    user = 'vlantonov'
    second_name = user[1:]

    excel_developers = []

    for developer in xrange(2,24,1):
        excel_developers.append(rb.sheets()[1].cell(developer,1).value.lower())

    for developer in excel_developers:
        print(developer)


    # +25
    print(second_name in rb.sheets()[1].cell(2,1).value.lower())
    print(second_name in rb.sheets()[1].cell(27,1).value.lower())
    print(second_name in rb.sheets()[1].cell(52,1).value.lower())
    print(second_name in rb.sheets()[1].cell(77,1).value.lower())

    print(try_again(second_name) in rb.sheets()[1].cell(2,1).value.lower())
    print(try_again(second_name) in rb.sheets()[1].cell(27,1).value.lower())
    print(try_again(second_name) in rb.sheets()[1].cell(52,1).value.lower())
    print(try_again(second_name) in rb.sheets()[1].cell(77,1).value.lower())

    return excel_developers


def rara(metrics):
    rb = open_workbook("metrics.xls", formatting_info=True)


    developers = get_list_developers(rb)


    wb = copy(rb)
    s = wb.get_sheet(1)
    print('Sheet name ' + s.name)

    set_1_metric(metrics['1. Tickets with incorrect or empty due date (except ongoing activities)'], developers, s, rb)

    s.write(5,5,'A1123123123')
    wb.save('names.xls')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--send_mail", action="store_true",
                        help="Send emails about result")
    parser.add_argument("-v", "--vacation", action="store", nargs='+',
                        help="Developer on vacation")
    parser.add_argument("-d", "--developers", action="store", nargs='+',
                        help="Custom developers list")
    parser.add_argument("-V", "--verbose", action="store_true",
                        help="Print queries")
    parser.add_argument("-s", "--sprint",
                        help="Set sprint version")
    args = parser.parse_args()
    developers = config.developers
    if args.developers:
        developers = []
        for arg_dev in args.developers:
            developer = config.get_developer_by_luxoft_user_name(arg_dev)
            if (developer):
                developers.append(developer)
            else:
                print("{0} not found ", arg_dev)

    on_vacation = ['akutsan']
    if args.vacation:
        on_vacation = args.vacation
    sdl = SDL(sprint=args.sprint, developers_on_vacation=on_vacation, developers=developers,
              print_queries=args.verbose)
    daily_report = sdl.daily_metrics()


    print(daily_report)


    email_list = []
    email_template = "%s@luxoft.com"
    report_str = ""
    for metric in daily_report:
        temp = "%s : \n" % metric
        report_str += temp
        fails = daily_report[metric]
        for fail in fails:
            temp = "\t%s : %s \n" % (fail[0], fail[1])
            report_str += temp
            if fail[0]:
                email = email_template % (fail[0])
                if email not in email_list:
                    email_list.append(email)
    print(report_str)



    temp_user = 'oherasym'
    second_name = temp_user[1:]
    print("Current user: "+ temp_user)
    print("user2: " + second_name)




    # try:
    rara(daily_report)
        # rb = open_workbook("metrics.xls", formatting_info=True)


        # get_list_developers(rb)

        # wb = copy(rb)
        # s = wb.get_sheet(1)
        # print('Sheet name ' + s.name)


        # s.write(5,5,'A1123123123')
        # wb.save('names.xls')

        # print([s.name for s in sheets].index(sheetname))
    # except:
        # print('ERROR: metrics file not found!')




    #if (args.send_mail):
    #    print(email_list)
    #    sender = "mailer@zln-ford-01.luxoft.com"
    #    smtpObj = smtplib.SMTP('localhost')
    #    smtpObj.sendmail(sender, email_list, config.message_template % (";".join(email_list), report_str))

    return 0


if __name__ == "__main__":
    main()
