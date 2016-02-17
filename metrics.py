#! /usr/bin/env python2
import jira_auth
from datetime import date, timedelta
import dateutil.parser
import time
import getpass
from getpass import getuser
import smtplib
import argparse
import re

import github
import config

# TODO:
#   Calculate current sprint automatically
#	Weekly project metrics
#	Monthly project metrics


def is_holiday(day):
    return day.weekday() > 4


def time_spent_from_str(time_spent):
    res = 0
    minutes = re.search("([0-9]+)m", time_spent)
    hours = re.search("([0-9]+)h", time_spent)
    days = re.search("([0-9]+)d", time_spent)
    if days:
        res += int(days.groups()[0]) * 8.0
    if hours:
        res += int(hours.groups()[0])
    if minutes:
        res += int(minutes.groups()[0]) / 60.0
    return res


def calc_diff_days(from_date, to_date):
    from_date = from_date.split("-")
    to_date = to_date.split("-")
    from_date = date(int(from_date[0]), int(from_date[1]), int(from_date[2]))
    to_date = date(int(to_date[0]), int(to_date[1]), int(to_date[2]))
    day_generator = (from_date + timedelta(x + 1) for x in range((to_date - from_date).days))
    return sum(1 for day in day_generator if not is_holiday(day))


def last_work_day():
    day = date.today() - timedelta(1)
    while is_holiday(day):
        day -= timedelta(1)
    return day


def to_h(val):
    return val / 60.0 / 60.0


class SDL():
    issue_path = "https://adc.luxoft.com/jira/browse/%s"

    def __init__(self, sprint, developers_on_vacation=[],
                 developers = config.developers, print_queries=False):
        self.jira = jira_auth.login(config.server)
        self.on_vacation = developers_on_vacation
        self.developers = developers
        self.sdl = self.jira.project('APPLINK')
        self.sprint = "SDL_RB_B3.28"
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

    def workload(self, user, report=[]):
        query = 'assignee = %s AND status not in (Suspended, Closed, Resolved) AND fixVersion in("%s")'
        query = query % (user, self.sprint)
        issues = self.Query(query)
        res = 0
        for issue in issues:
            if issue.fields.timeestimate:
                res += to_h(issue.fields.timeestimate)
                report.append((issue, to_h(issue.fields.timeestimate)))
        return res

    def calc_overload(self):
        report = []
        for user in self.developers:
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
        for user in self.developers:
            query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s")  AND status not in (Closed, Resolved, Suspended) AND duedate is EMPTY '''
            query = query % (user, self.sprint)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report


    def issues_with_expired_due_date(self):
        report = []
        for user in self.developers:
            query = ''' assignee = %s and status not in (closed, resolved, Approved) AND duedate < startOfDay()'''
            query = query % (user)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report


    def expired_in_progress(self):
        report = []
        for user in self.developers:
            query = '''assignee = %s AND status in ("In Progress", "Analyze") AND (updated < -2d OR fixVersion = Backlog)'''
            query = query % (user)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report


    def without_correct_estimation(self):
        report = []
        for user in self.developers:
            query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s") AND status not in (Closed, Resolved, Suspended) AND (remainingEstimate = 0 OR remainingEstimate is EMPTY)'''
            query = query % (user, self.sprint)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report

    def expired_code_review(self):
        report = []
        gh = github.login()
        repo = gh.repository('CustomSDL', 'sdl_panasonic')
        open_pulls = github.open_pull_request_for_repo(repo)
        for pull in open_pulls:
            if pull.days_old > 2:
                developer = config.get_developer_by_github_user_name(pull.developer)
                if developer in self.developers:
                    report.append((developer, "has review %d days old: %s : %s"%(pull.days_old, pull.caption, pull.url)))
        return report

    def wrong_due_date(self):
        report = []
        for user in self.developers:
            query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s") AND (duedate < "%s" OR duedate > "%s") AND status not in (resolved, closed)'''
            query = query % (user, self.sprint, self.sprint.startDate, self.sprint.releaseDate)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report


    def wrong_fix_version(self):
        report = []
        for user in self.developers:
            query = '''assignee = %s AND fixversion not in ("%s") and (labels is EMPTY OR labels != exclude_from_metrics) AND status not in (closed, resolved) AND duedate > "%s" AND duedate <= "%s" '''
            query = query % (user, self.sprint, self.sprint.startDate, self.sprint.releaseDate)
            issues = self.Query(query)
            for issue in issues:
                report.append((user, self.issue_path % issue))
        return report

    def absence_in_progress(self):
        report = []
        for user in self.developers:
            if user in self.on_vacation:
                continue
            query = '''assignee = %s AND status = "In Progress" '''
            issues = self.Query(query % user)
            if (len(issues) == 0):
                report.append((user, None))
        return report

    def not_implemented_yet(self):
        report = []
        report.append((None, "ERROR:  Feature is not implemented yet"))
        return report

    def not_logged_vacation(self):
        report = []
        vacation_issue_key = "APPLINK-13266"
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
        for developer in self.developers:
            user_logged[developer.lower()] = 0
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
                    if author in self.developers:
                        user_logged[author] += time_spent_from_str(time_spent)
        for developer in user_logged:
            if (user_logged[developer.lower()] < 8):
                report.append(
                    (developer, "Logged for %s : %sh" % (last_work.strftime("%Y/%m/%d"), user_logged[str(developer)])))
        return report

    def daily_metrics(self):
        report = {}
        report['1. Tickets with incorrect or empty due date (except ongoing activities)'] = self.issues_without_due_date()
        report['2. Tickets with expired due dates'] = self.issues_with_expired_due_date()
        report['3. Absence of "in progress" issues assigned to each team member report'] = self.absence_in_progress()
        report['4. Tickets "in progress" without updating during last 2 days'] = self.expired_in_progress()
        report['5. Open issues without correct estimation'] = self.without_correct_estimation()
        report['6. Open code reviews with age more 2 days'] = self.expired_code_review()
        report['7. Overload : '] = self.calc_overload()
        report['9. Not logged vacation'] = self.not_logged_vacation()
        report['10. Tickets with wrong FixVersion'] = self.wrong_fix_version()
        report['11. Wrong due date'] = self.wrong_due_date()
        report['8. Previous day work time logging'] = self.not_logged_work()
        return report


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

    on_vacation = []
    if args.vacation:
        on_vacation = args.vacation
    sdl = SDL(sprint=args.sprint, developers_on_vacation=on_vacation, developers=developers,
              print_queries=args.verbose)
    daily_report = sdl.daily_metrics()
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
    if (args.send_mail):
        print(email_list)
        sender = "mailer@zln-ford-01.luxoft.com"
        smtpObj = smtplib.SMTP('localhost')
        smtpObj.sendmail(sender, email_list, config.message_template % (";".join(email_list), report_str))

    return 0


if __name__ == "__main__":
    main()
