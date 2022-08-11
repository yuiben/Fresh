alter table users drop foreign key position_id;
alter table users 
drop column phone_number,
drop column date_of_birth,
drop column image,
drop colum address;


create table profile
(
    id        int auto_increment
	primary key,
    first_name varchar(255),
    last_name varchar(255),
    phone_number varchar(20) not null,
    date_of_birth date not null,
    image varchar(255) default null,
    position_id int not null,
    user_id int not null,
    foreign key (position_id) references positions(id) on delete cascade,
    unique foreign key (user_id) references users(id) on delete cascade,
    deleted_at date default null,
    created_at datetime(6),
    updated_at datetime(6)

);

