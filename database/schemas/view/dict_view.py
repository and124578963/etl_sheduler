from database.schemas._common import BaseView, Schema

BaseView(
    schema=Schema.DICT,
    name="vm_priority",
    is_materialized=True,
    priority=3,
    select_sql=f"""
        SELECT DISTINCT priority
        FROM {Schema.JIRA}.vm_issue
        ORDER BY priority
       
    """
)

BaseView(
    schema=Schema.DICT,
    name="vm_services",
    is_materialized=True,
    priority=3,
    select_sql=f"""
        SELECT DISTINCT ext_service, project
        FROM {Schema.JIRA}.vm_issue
        ORDER BY project
    """
)
BaseView(
    schema=Schema.DICT,
    name="vm_systems",
    is_materialized=True,
    priority=3,
    select_sql=f"""
        SELECT DISTINCT ext_system, project
        FROM {Schema.JIRA}.vm_issue
        ORDER BY project
    """
)
BaseView(
    schema=Schema.DICT,
    name="vm_projects",
    is_materialized=True,
    priority=3,
    select_sql=f"""
        SELECT p.project
        FROM ( SELECT DISTINCT project
               FROM {Schema.JIRA}.vm_issue_timelog
               UNION
               SELECT DISTINCT project_key AS project
               FROM {Schema.JIRA}.vm_issue) p
        WHERE p.project IS NOT NULL
        ORDER BY p.project
    """
)

BaseView(
    schema=Schema.DICT,
    name="vm_pools",
    is_materialized=True,
    select_sql=f"""
        SELECT DISTINCT cu.pool_name
        FROM {Schema.CUBE}.user cu
        ORDER BY cu.pool_name
    """
)
