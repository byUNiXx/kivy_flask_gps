

CREATE TABLE phone (
	pid CHAR(36) NOT NULL, 
	PRIMARY KEY (pid)
);


CREATE TABLE alarm (
	aid INTEGER NOT NULL, 
	name VARCHAR(15) NOT NULL, 
	description VARCHAR(1024), 
	PRIMARY KEY (aid)
);


CREATE TABLE moving (
	pid CHAR(36) NOT NULL, 
	ip VARCHAR(36) NOT NULL, 
	type VARCHAR(11) NOT NULL, 
	utc VARCHAR(6) NOT NULL, 
	lat DECIMAL(9, 6), 
	lon DECIMAL(9, 6), 
	alt DECIMAL(9, 3), 
	timestamp DATETIME, 
	PRIMARY KEY (pid), 
	FOREIGN KEY(pid) REFERENCES phone (pid), 
	CONSTRAINT types CHECK (type IN ('car', 'bike', 'truck', 'skate', 'other_heavy', 'other_light'))
);


CREATE TABLE phone_alarm (
	phone_id CHAR(36) NOT NULL, 
	alarm_id INTEGER NOT NULL, 
	timestamp DATETIME, 
	status BOOLEAN, 
	PRIMARY KEY (phone_id, alarm_id), 
	FOREIGN KEY(phone_id) REFERENCES phone (pid), 
	FOREIGN KEY(alarm_id) REFERENCES alarm (aid), 
	CHECK (status IN (0, 1))
);

CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

