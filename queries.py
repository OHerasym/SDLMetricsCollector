
workload_query = '''assignee = %s and fixversion in ("%s")'''
issues_without_due_date_query = ''' assignee in (%s) and type not in (Question,"Document Approval") AND fixversion in ("%s")  AND status not in (Analyze, "Suspended Progress", Closed, Resolved, Suspended) AND (duedate is EMPTY OR duedate < "2017/4/01" OR duedate > "2017/4/30") '''
issues_with_expired_due_date_query = ''' assignee in (%s) and status not in (closed, resolved, Approved) AND duedate < startOfDay()'''
expired_in_progress_query = '''assignee in (%s) AND status in ("In Progress", "Analyze") AND (updated < -2d OR fixVersion = Backlog)'''
without_correct_estimation_query = ''' assignee in (%s) and type not in (Question,"Document Approval") AND fixversion in ("%s") AND status not in (Analyze, Closed, Resolved) AND (remainingEstimate = 0 OR remainingEstimate is EMPTY)'''
wrong_due_date_query = ''' assignee = %s and type not in (Question) AND fixversion in ("%s") AND (duedate < "%s" OR duedate > "%s") AND status not in (resolved, closed)'''
wrong_fix_version_query = '''assignee in (%s) AND fixversion not in ("%s", PASA_RB_E3.42) and (labels is EMPTY OR labels != exclude_from_metrics) AND status not in (closed, resolved) AND duedate > "%s" AND duedate <= "%s" '''
absence_in_progress_query = '''assignee = %s AND status in ("In Progress",Analyze) '''