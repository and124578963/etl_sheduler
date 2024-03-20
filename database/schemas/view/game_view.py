from database.schemas._common import BaseView, Schema

BaseView(
    schema=Schema.GAME,
    name="v_lost_user_achieve",
    select_sql=f"""
    select
        ju.user_name,
        ju.pool_name,
        ac.name as achive_name,
        ac.description,
        ac.type,
        ac.cost,
        axu.get_dttm,
        axu.lost_dttm
    from
        {Schema.CUBE}.user ju
    join {Schema.ARCHIVE}.lost_achive_x_user axu on
        ju.id = axu.user_id
    join {Schema.GAME}.achievements ac on
        axu.achive_id = ac.id;
    """
)


BaseView(
    schema=Schema.GAME,
    name="v_progress_user_achieve",
    select_sql=f"""
    select
        ju.user_name,
        ju.pool_name,
        ac.name as achive_name,
        axu.last_result::double precision / ac.goal::double precision * 100::double precision as progress,
        ac.description,
        ac.type,
        ac.cost,
        axu.update_dttm as get_dttm
    from
        {Schema.CUBE}.user ju
    join {Schema.GAME}.progress_achive_x_user axu on
        ju.id = axu.user_id
    join {Schema.GAME}.achievements ac on
        axu.achive_id = ac.id;
    """
)


BaseView(
    schema=Schema.GAME,
    name="v_user_score",
    select_sql=f"""
    select
        ju.id as user_id,
        ju.user_name,
        ju.pool_name,
        sc.amount_exp,
        sc.amount_cost
    from
       {Schema.CUBE}.user ju
    join {Schema.GAME}.score sc on
        ju.id = sc.user_id
    order by
        sc.amount_cost desc,
        sc.amount_exp desc;
    """
)


BaseView(
    schema=Schema.GAME,
    name="v_user_achieve",
    select_sql=f"""
    select
        ju.user_name,
        ju.pool_name,
        ac.name as achive_name,
        ac.description,
        ac.type,
        ac.cost,
        axu.update_dttm as get_dttm
    from
        {Schema.CUBE}.user ju
    join {Schema.GAME}.achive_x_user axu on
        ju.id = axu.user_id
    join {Schema.GAME}.achievements ac on
        axu.achive_id = ac.id
    union all
    select
        ju.user_name,
        ju.pool_name,
        ac.name as achive_name,
        ac.description,
        ac.type,
        ac.cost,
        null::timestamp without time zone as get_dttm
    from
        {Schema.CUBE}.user ju
    join {Schema.GAME}.pers_achieve pa on
        ju.user_name::text = pa.login::text
    join {Schema.GAME}.achievements ac on
        pa.achievement_name::text = ac.name::text;
    """
)


BaseView(
    schema=Schema.GAME,
    name="v_team_score",
    priority=2,
    select_sql=f"""
    select
        t.team_name,
        round(avg(sc.amount_exp)) as avg_exp,
        round(avg(sc.amount_cost)) as avg_cost
    from
        {Schema.CUBE}.user ju
    join {Schema.GAME}.score sc on
        ju.id = sc.user_id
    join {Schema.CUBE}.v_teams t on
        ju.user_name::text = t.lower_name::text
    group by
        t.team_name
    order by
        (round(avg(sc.amount_cost))) desc,
        (round(avg(sc.amount_exp))) desc;
    """
)
