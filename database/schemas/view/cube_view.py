from database.schemas._common import BaseView, Schema


BaseView(
    schema=Schema.CUBE,
    name="vm_users",
    is_materialized=True,
    select_sql=f"""
        SELECT cu.login,
            cc.login AS curator_key,
            cu.pool_name,
            cu.status
        FROM {Schema.CUBE}.user cu
        LEFT JOIN {Schema.CUBE}.user cc ON cc.user_name::text = cu.curator_name::text
        WHERE cu.office::text <> 'Не сотрудник GBC'::text
    """
)


BaseView(
    schema=Schema.CUBE,
    name="v_teams",
    select_sql=F"""
        select
            t1.user_name as full_name,
            t1.login as lower_name,
            teams.team_name
        from
            {Schema.CUBE}.user t1
        left join {Schema.CUBE}.user t2 on
            t2.user_name::text = t1.curator_name::text
        left join {Schema.CUBE}.user t3 on
            t3.user_name::text = t2.curator_name::text
        join (
            select
                ku.user_name as team_lead,
                initcap("substring"(ku.login::text,
                '[[:alpha:]]*$'::text)) || ' Team'::text as team_name
            from
                {Schema.CUBE}.user ku
            where
                ku.curator_name::text = 'Халин Игорь Витальевич'::text) teams on
            teams.team_lead::text = t1.curator_name::text
            or teams.team_lead::text = t1.user_name::text
            or t2.curator_name::text = teams.team_lead::text
            or t3.curator_name::text = teams.team_lead::text
        where
            t1.pool_name::text = 'Команда MM.SUP'::text
            and t1.status::text = 'Работает'::text
        order by
            teams.team_name;
    """
)

