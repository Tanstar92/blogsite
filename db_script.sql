create database blogs;
use blogs;

create table users(
	id int unsigned auto_increment primary key,
    email varchar(50) not null unique,
    pass varchar(100) not null,
    full_name varchar(40) not null,
    reg_date datetime not null default now()
);

create table post(
	id int unsigned auto_increment primary key,
    content varchar(100) not null,
    image varchar(200) not null,
    created_on datetime not null default now(),
    creator int unsigned not null,
    foreign key (creator) references users(id)
);
