/* This is a complete overhaul of the old annotation system */
create table if not exists quantity_types (id integer primary key not null auto_increment, name varchar (30));
create table if not exists units (id integer primary key not null auto_increment, name varchar (30), full_name varchar(30));
create table if not exists change_types (id integer primary key not null auto_increment, name varchar(30), description varchar(100), quantity_type_id integer not null references quantity_types, unit_id integer not null default 1 references units);
create table if not exists system_changes (id integer primary key not null auto_increment, system_uid varchar(40) not null, time datetime not null, change_type_id integer not null references change_types, amount_int integer, amount_decimal decimal(13, 10));

insert into units (id, name) values (1, 'none');

insert into quantity_types (id, name) values (1, 'none');
insert into quantity_types (id, name) values (2, 'integer');
insert into quantity_types (id, name) values (3, 'decimal');
insert into quantity_types (id, name) values (4, 'volume');
insert into quantity_types (id, name) values (5, 'concentration');

insert into change_types (name, description, quantity_type_id) values ('add_base', 'Added Base', 4);
insert into change_types (name, description, quantity_type_id) values ('add_acid', 'Added Acid', 4);
insert into change_types (name, description, quantity_type_id) values ('harvest_fish', 'Harvested Fish', 2);
insert into change_types (name, description, quantity_type_id) values ('harvest_plant', 'Harvested Plants', 2);
insert into change_types (name, description, quantity_type_id) values ('add_fish', 'Added Fish', 2);
insert into change_types (name, description, quantity_type_id) values ('add_plant', 'Added Plants', 2);
insert into change_types (name, description, quantity_type_id) values ('add_bacteria', 'Added Bacteria', 4);
insert into change_types (name, description, quantity_type_id) values ('clean_tank', 'Cleaned Tank', 1);
insert into change_types (name, description, quantity_type_id) values ('reproduction', 'Fish Reproduced', 1);
