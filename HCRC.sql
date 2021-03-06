create table invite_codes
(
    code               text
        constraint invite_codes_pk
            primary key,
    generate_user_name text,
    used_user_name     text
);

create table new_players
(
    player_id          integer
        constraint new_players_pk
            primary key autoincrement,
    player_name        text,
    password           text,
    register_timestamp int,
    invitor_username   text,
    phone_number       text
);

create table ip_sms_record
(
    ip_addr       integer
        constraint ip_message_record_pk
            primary key,
    last_msg_time integer,
    req_count     integer
);

create unique index ip_message_record_ip_addr_uindex
    on ip_sms_record (ip_addr);

