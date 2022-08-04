create table auth_group
(
    id   int auto_increment
        primary key,
    name varchar(150) not null,
    constraint name
        unique (name)
);

create table auth_user
(
    id        int auto_increment
        primary key,
    email     varchar(500) not null,
    password  varchar(255) not null,
    role      int          not null,
    user_code varchar(10)  not null,
    constraint email
        unique (email)
);

create table django_content_type
(
    id        int auto_increment
        primary key,
    app_label varchar(100) not null,
    model     varchar(100) not null,
    constraint django_content_type_app_label_model_76bd3d3b_uniq
        unique (app_label, model)
);

create table auth_permission
(
    id              int auto_increment
        primary key,
    name            varchar(255) not null,
    content_type_id int          not null,
    codename        varchar(100) not null,
    constraint auth_permission_content_type_id_codename_01ab375a_uniq
        unique (content_type_id, codename),
    constraint auth_permission_content_type_id_2f476e4b_fk_django_co
        foreign key (content_type_id) references django_content_type (id)
);

create table auth_group_permissions
(
    id            bigint auto_increment
        primary key,
    group_id      int not null,
    permission_id int not null,
    constraint auth_group_permissions_group_id_permission_id_0cd325b0_uniq
        unique (group_id, permission_id),
    constraint auth_group_permissio_permission_id_84c5c92e_fk_auth_perm
        foreign key (permission_id) references auth_permission (id),
    constraint auth_group_permissions_group_id_b120cbf9_fk_auth_group_id
        foreign key (group_id) references auth_group (id)
);

create table django_migrations
(
    id      bigint auto_increment
        primary key,
    app     varchar(255) not null,
    name    varchar(255) not null,
    applied datetime(6)  not null
);

create table token_blacklist_outstandingtoken
(
    id         bigint auto_increment
        primary key,
    token      longtext     not null,
    created_at datetime(6)  null,
    expires_at datetime(6)  not null,
    user_id    int          null,
    jti        varchar(255) not null,
    constraint token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq
        unique (jti),
    constraint token_blacklist_outs_user_id_83bc629a_fk_auth_user
        foreign key (user_id) references auth_user (id)
);

create table token_blacklist_blacklistedtoken
(
    id             bigint auto_increment
        primary key,
    blacklisted_at datetime(6) not null,
    token_id       bigint      not null,
    constraint token_id
        unique (token_id),
    constraint token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk
        foreign key (token_id) references token_blacklist_outstandingtoken (id)
);

