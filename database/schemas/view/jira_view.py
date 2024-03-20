
# Здесь, т.к. зависит от cube.vm_issue_timelog
from database.schemas import Schema
from database.schemas._common import BaseView

BaseView(
    schema=Schema.JIRA,
    name="vm_issue",
    is_materialized=True,
    priority=2,
    select_sql=f"""
        SELECT issue.issue_key,
            issue.summary,
            issue.description,
            COALESCE(NULLIF(issue.c_priority::text, 'NaN'::text), '0.Не указано'::text) AS priority,
            issue.status,
            issue.project_key,
            issue.resolution,
            issue.id_assigne,
            issue.id_reporter,
            issue.creator,
            issue.created,
            issue.updated,
            issue.resolved,
            issue.due_date,
            COALESCE(NULLIF(TRIM(BOTH ' '::text FROM split_part(issue.c_ext_system::text, '->'::text, 1)), 'NaN'::text), NULLIF(issue.security_level::text, 'NaN'::text), '0.Не указано'::text) AS ext_system,
            COALESCE(NULLIF(TRIM(BOTH ' '::text FROM split_part(issue.c_ext_system::text, '->'::text, 2)), ''::text), '0.Не указано'::text) AS ext_service,
            issue.time_response,
            issue.time_resolution,
            vit.time_worked_days,
            TRIM(BOTH ' '::text FROM split_part(issue.issue_key::text, '-'::text, 1)) AS project
        FROM {Schema.JIRA}.issue
        LEFT JOIN {Schema.JIRA}.vm_issue_timelog vit ON issue.issue_key::text = vit.issue_key::text
    """
)


BaseView(
    schema=Schema.JIRA,
    name="vm_issue_timelog",
    is_materialized=True,
    select_sql=f"""
        SELECT COALESCE(xc.issue_key, t.issue_id) AS issue_key,
            t.issue_summary,
            round(sum(t.time_worked_days)::numeric, 2) AS time_worked_days,
            string_agg((t.user_name::text || ': '::text) || round(t.time_worked_days::numeric, 2)::text, chr(10) 
                       ORDER BY t.user_name) AS details,
            TRIM(BOTH ' '::text FROM split_part(COALESCE(xc.issue_key, t.issue_id)::text, '-'::text, 1)) AS project
        FROM ( SELECT user_timelog.issue_id,
                    user_timelog.issue_summary,
                    user_timelog.user_name,
                    sum(user_timelog.time_worked_days) AS time_worked_days
               FROM {Schema.CUBE}.user_timelog
                GROUP BY user_timelog.issue_id, user_timelog.user_name, user_timelog.issue_summary
              ) t
        LEFT JOIN {Schema.JIRA}.issue_x_clone xc ON xc.clone_key::text = t.issue_id::text
        GROUP BY xc.issue_key, t.issue_id, t.issue_summary
    """
)
