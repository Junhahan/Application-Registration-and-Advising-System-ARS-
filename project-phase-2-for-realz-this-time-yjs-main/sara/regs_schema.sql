DROP TABLE IF EXISTS students;
CREATE TABLE students (
  UID           int(8) not null,
  username      varchar(20) not null,
  password      varchar(20) not null,
  fname         varchar(50) not null,
  lname         varchar(50) not null,
  address       varchar(100) not null,
  DOB           int(8) not null,
  email         varchar(50) not null,
  courses       varchar(100), --courses they are taking, can be null for new students
  program       varchar(20) not null,
  primary key (UID),
  foreign key (courses) references courses(CourseID)
);

--students:
INSERT INTO students VALUES
  (88767547, 'sara.almaouf', 'saracourses', 'Sara', 'Almaouf', 'Vienna, VA', 09112004, 'sara.almaouf@gwu.edu', '3, 7, 11, 15, 19', 'Masters Program');
INSERT INTO students VALUES
  (78276378, 'jake.kat', 'jakecourses','Jake', 'Kat', 'Tysons, VA', 07072003, 'jake.kate@gwu.edu', '1, 5, 9, 13, 17', 'PhD');
INSERT INTO students VALUES
  (62736219, 'rohina.saeydie', 'rohinapassword', 'Rohina', 'Saeydie', 'Alexandria, VA', 05072004, 'rohina.saeydie@gwu.edu', '4, 8, 12, 16, 20', 'Masters Program');
INSERT INTO students VALUES
  (89173620, 'emma.holand', 'emmapass', 'Emma', 'Holand', 'Herndon, VA', 04162005, 'emma.holand@gwu.edu', '2, 6, 10, 14, 18', 'PhD');
--created new students through signup route:
--username:rs   password:rs   fname:Rosita   lname:Saeydie   address:Boyds, MD   UID:12345678, rs@email.com

INSERT INTO students VALUES (88888888, 'holiday', 'pass', 'Billie', 'Holiday', 'Washington, D.C.', 10102003, 'holiday@gwu.edu', '2, 3', 'Masters Program');
INSERT INTO students VALUES (99999999, 'krall', 'pass', 'Diana', 'Krall', 'Woodbridge, VA', 01012001, 'krall@gwu.edu', NULL, 'Masters Program');



DROP TABLE IF EXISTS instructors;
CREATE TABLE instructors (
  username      varchar(20) not null,
  password      varchar(20) not null,
  fname         varchar(50) not null,
  lname         varchar(50) not null,
  courses       varchar(100) not null, --courses they are teaching
  email         varchar(50) not null,
  primary key (username),
  foreign key (courses) references courses(CourseID)
);

--instructors:
INSERT INTO instructors VALUES ('Ouska', 'pass1', 'Emily', 'Ouska', '1, 2, 3, 4', 'email1@email.com');
INSERT INTO instructors VALUES ('Edwards', 'pass2', 'Ed', 'Edwards', '5, 6, 7, 8', 'email2@email.com');
INSERT INTO instructors VALUES ('Ross', 'pass3', 'Bob', 'Ross', '9, 10, 11, 12', 'email3@email.com');
INSERT INTO instructors VALUES ('Doubtfire', 'pass3', 'Euphegenia', 'Doubtfire', '13, 14, 15, 16', 'email4@email.com');
INSERT INTO instructors VALUES ('Parmer', 'pass3', 'Gabe', 'Parmer', '17, 18, 19, 20', 'email5@email.com');


DROP TABLE IF EXISTS grad_secretaries;
CREATE TABLE grad_secretaries (
  username      varchar(20) not null,
  password      varchar(20) not null,
  fname         varchar(50) not null,
  lname         varchar(50) not null,
  email         varchar(50) not null,
  primary key (username)
);

--GS:
INSERT INTO grad_secretaries VALUES ('gs', 'gs', 'Razia', 'Yousufi', 'gs@email.com');


DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
  CourseID           int(5) not null,
  dname         varchar(50) not null,
  course_number int(5) not null,
  title         varchar(50) not null,
  credits       int(1) not null,
  course_prereq     varchar(50),
  course_prereq2    varchar(50),
  primary key (CourseID),
  foreign key (dname) references departments(name)
);

--courses:
INSERT INTO courses VALUES
  (1, 'CSCI', 6221, 'SW Paradigms', 3, null, null);
INSERT INTO courses VALUES
  (2, 'CSCI', 6461, 'Computer Architecture', 3, null, null);
INSERT INTO courses VALUES
  (3, 'CSCI', 6212, 'Algorithms', 3, null, null);
INSERT INTO courses VALUES
  (4, 'CSCI', 6232, 'Networks 1', 3, null, null);
INSERT INTO courses VALUES
  (5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', null);
INSERT INTO courses VALUES
  (6, 'CSCI', 6241, 'Database 1', 3, null, null);
INSERT INTO courses VALUES
  (7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', null);
INSERT INTO courses VALUES
  (8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212');
INSERT INTO courses VALUES
  (9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', null);
INSERT INTO courses VALUES
  (10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', null);
INSERT INTO courses VALUES
  (11, 'CSCI', 6260, 'Multimedia', 3, null, null);
INSERT INTO courses VALUES
  (12, 'CSCI', 6262, 'Graphics 1', 3, null, null);
INSERT INTO courses VALUES
  (13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', null);
INSERT INTO courses VALUES
  (14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', null);
INSERT INTO courses VALUES
  (15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232');
INSERT INTO courses VALUES
  (16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', null);
INSERT INTO courses VALUES
  (17, 'ECE', 6241, 'Communication Theory', 3, null, null);
INSERT INTO courses VALUES
  (18, 'ECE', 6242, 'Information Theory', 2, null, null);
INSERT INTO courses VALUES
  (19, 'MATH', 6210, 'Logic', 2, null, null);
INSERT INTO courses VALUES
  (20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212');

DROP TABLE IF EXISTS student_courses;
CREATE TABLE student_courses (
  student_UID                   int(8) not null,
  student_fname                 varchar(50),
  student_lname                 varchar(50),
  IP_course_ID                  int(5) not null,
  IP_course_dname               varchar(50) not null,
  IP_course_number              int(5) not null,
  IP_course_title               varchar(50) not null,  
  grade                         varchar(2) not null,
  IP_instructor_username        varchar(50) not null,
  foreign key (student_UID) references students(UID),
  foreign key (student_fname) references students(fname),
  foreign key (student_lname) references students(lname),
  foreign key (IP_course_ID) references courses_schedule(course_ID),
  foreign key (IP_course_dname) references courses_schedule(course_dname),
  foreign key (IP_course_number) references courses_schedule(course_number),
  foreign key (IP_course_title) references courses_schedule(course_title),
  foreign key (IP_instructor_username) references courses_schedule(instructor_username),
  primary key (student_UID, IP_course_ID)
);


-- IP (in progress) courses for a specific student:
-- new student's do not have IP courses
-- default grade is IP (in progress) but can be changed by the instructor teaching the course.
INSERT INTO student_courses VALUES (88767547, 'Sara', 'Almaouf', 3, 'CSCI', 6212, 'Algorithms', 'IP', 'Choi');
INSERT INTO student_courses VALUES (88767547, 'Sara', 'Almaouf', 7, 'CSCI', 6242, 'Database 2', 'IP', 'Edwards');
INSERT INTO student_courses VALUES (88767547, 'Sara', 'Almaouf', 11, 'CSCI', 6260, 'Multimedia', 'IP', 'Ross');
INSERT INTO student_courses VALUES (88767547, 'Sara', 'Almaouf', 15, 'CSCI', 6286, 'Network Security', 'IP', 'Doubtfire');
INSERT INTO student_courses VALUES (88767547, 'Sara', 'Almaouf', 19, 'MATH', 6210, 'Logic', 'IP', 'Parmer');


INSERT INTO student_courses VALUES (62736219, 'Rohina', 'Saeydie', 4, 'CSCI', 6232, 'Networks 1', 'IP', 'Ouska');
INSERT INTO student_courses VALUES (62736219, 'Rohina', 'Saeydie', 8, 'CSCI', 6246, 'Compilers', 'IP', 'Edwards');
INSERT INTO student_courses VALUES (62736219, 'Rohina', 'Saeydie', 12, 'CSCI', 6262, 'Graphics 1', 'IP', 'Ross');
INSERT INTO student_courses VALUES (62736219, 'Rohina', 'Saeydie', 16, 'CSCI', 6384, 'Cryptography 2', 'IP', 'Doubtfire');
INSERT INTO student_courses VALUES (62736219, 'Rohina', 'Saeydie', 20, 'CSCI', 6339, 'Embedded Systems', 'IP', 'Parmer');


INSERT INTO student_courses VALUES (78276378, 'Jake', 'Kat', 1, 'CSCI', 6221, 'SW Paradigms', 'IP', 'Ouska');
INSERT INTO student_courses VALUES (78276378, 'Jake', 'Kat', 5, 'CSCI', 6233, 'Networks 2', 'IP', 'Edwards');
INSERT INTO student_courses VALUES (78276378, 'Jake', 'Kat', 9, 'CSCI', 6251, 'Cloud Computing', 'IP', 'Ross');
INSERT INTO student_courses VALUES (78276378, 'Jake', 'Kat', 13, 'CSCI', 6283, 'Security 1', 'IP', 'Doubtfire');
INSERT INTO student_courses VALUES (78276378, 'Jake', 'Kat', 17, 'ECE', 6241, 'Communication Theory', 'IP', 'Parmer');


INSERT INTO student_courses VALUES (89173620, 'Emma', 'Holand', 2, 'CSCI', 6461, 'Computer Architecture', 'IP', 'Narahari');
INSERT INTO student_courses VALUES (89173620, 'Emma', 'Holand', 6, 'CSCI', 6241, 'Database 1', 'IP', 'Edwards');
INSERT INTO student_courses VALUES (89173620, 'Emma', 'Holand', 10, 'CSCI', 6254, 'SW Engineering', 'IP', 'Ross');
INSERT INTO student_courses VALUES (89173620, 'Emma', 'Holand', 14, 'CSCI', 6284, 'Cryptography', 'IP', 'Doubtfire');
INSERT INTO student_courses VALUES (89173620, 'Emma', 'Holand', 18, 'ECE', 6242, 'Information Theory', 'IP', 'Parmer');


INSERT INTO student_courses VALUES (88888888, 'Billie', 'Holiday', 2, 'CSCI', 6461, 'Computer Architecture', 'IP', 'Narahari');
INSERT INTO student_courses VALUES (88888888, 'Billie', 'Holiday', 3, 'CSCI', 6212, 'Algorithms', 'IP', 'Choi');



DROP TABLE IF EXISTS previous_courses;
CREATE TABLE previous_courses (
  student_UID                   int(8) not null,
  student_fname                 varchar(50),
  student_lname                 varchar(50),
  course_ID                     int(5) not null,
  course_dname                  varchar(50) not null,
  course_number                 int(5) not null,
  course_title                  varchar(50) not null,  
  grade                         varchar(2) not null,
  instructor_username           varchar(50) not null,
  foreign key (student_UID) references students(UID),
  foreign key (student_fname) references students(fname),
  foreign key (student_lname) references students(lname),
  foreign key (course_ID) references courses_schedule(course_ID),
  foreign key (course_dname) references courses_schedule(course_dname),
  foreign key (course_number) references courses_schedule(course_number),
  foreign key (course_title) references courses_schedule(course_title),
  foreign key (instructor_username) references courses_schedule(instructor_username),
  primary key (student_UID, course_ID)
);
--sara 6241, 6283, 6232, 6212
INSERT INTO previous_courses VALUES (88767547, 'Sara', 'Almaouf', 6, 'CSCI', 6241, 'Database 1', 'A', 'Edwards');
INSERT INTO previous_courses VALUES (88767547, 'Sara', 'Almaouf', 13, 'CSCI', 6283, 'Security 1', 'A', 'Doubtfire');
INSERT INTO previous_courses VALUES (88767547, 'Sara', 'Almaouf', 4, 'CSCI', 6232, 'Networks 1', 'A', 'Ouska');
INSERT INTO previous_courses VALUES (88767547, 'Sara', 'Almaouf', 3, 'CSCI', 6212, 'Algorithms', 'A', 'Choi');
--rohina 6461, 6212, 6284
INSERT INTO previous_courses VALUES (62736219, 'Rohina', 'Saeydie', 2, 'CSCI', 6461, 'Computer Architecture', 'A', 'Narahari');
INSERT INTO previous_courses VALUES (62736219, 'Rohina', 'Saeydie', 3, 'CSCI', 6212, 'Algorithms', 'A', 'Choi');
INSERT INTO previous_courses VALUES (62736219, 'Rohina', 'Saeydie', 14, 'CSCI', 6284, 'Cryptography', 'A', 'Doubtfire');
--jake kat 6232, 6461, 6212
INSERT INTO previous_courses VALUES (78276378, 'Jake', 'Kat', 4, 'CSCI', 6232, 'Networks 1', 'A', 'Ouska');
INSERT INTO previous_courses VALUES (78276378, 'Jake', 'Kat', 2, 'CSCI', 6461, 'Computer Architecture', 'B+', 'Narahari');
INSERT INTO previous_courses VALUES (78276378, 'Jake', 'Kat', 3, 'CSCI', 6212, 'Algorithms', 'C+', 'Choi');
--emma 6221, 6212
INSERT INTO previous_courses VALUES (89173620, 'Emma', 'Holand', 1, 'CSCI', 6221, 'SW Paradigms', 'A-', 'Ouska');
INSERT INTO previous_courses VALUES (89173620, 'Emma', 'Holand', 3, 'CSCI', 6212, 'Algorithms', 'B', 'Choi');

DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
  id        int(5) not null,
  name      varchar(50) not null
);

--departments:
INSERT INTO departments VALUES (12345, 'CSCI');
INSERT INTO departments VALUES (67853, 'MATH');
INSERT INTO departments VALUES (09471, 'ECE');


DROP TABLE IF EXISTS courses_schedule;
CREATE TABLE courses_schedule (
  semester                   varchar(20) not null,
  course_ID                  int(5) not null,
  course_dname               varchar(50) not null,
  course_number              int(5) not null,
  course_title               varchar(50) not null,
  course_credits             int(1) not null,
  section_number             int(1) not null,
  meeting_time               varchar(50) not null,
  instructor_username        varchar(50) not null,
  primary key (semester, course_ID),
  foreign key (course_ID) references courses(Course_ID),
  foreign key (course_dname) references courses(dname),
  foreign key (course_number) references courses(course_number),
  foreign key (course_title) references courses(title),
  foreign key (course_credits) references courses(credits),
  foreign key (instructor_username) references instructors(username)
);

--courses_schedule:
INSERT INTO courses_schedule VALUES ('Spring 2024', 1, 'CSCI', 6221, 'SW Paradigms', 3, 1, 'M 1500—1730', 'Ouska');
INSERT INTO courses_schedule VALUES ('Spring 2024', 2, 'CSCI', 6461, 'Computer Architecture', 3, 1, 'T 1500—1730', 'Ouska');
INSERT INTO courses_schedule VALUES ('Spring 2024', 3, 'CSCI', 6212, 'Algorithms', 3, 1, 'W 1500—1730', 'Ouska');
INSERT INTO courses_schedule VALUES ('Spring 2024', 4, 'CSCI', 6232, 'Networks 1', 3, 1, 'M 1800—2030', 'Ouska');

INSERT INTO courses_schedule VALUES ('Spring 2024', 5, 'CSCI', 6233, 'Networks 2', 3, 1, 'T 1800—2030', 'Edwards');
INSERT INTO courses_schedule VALUES ('Spring 2024', 6, 'CSCI', 6241, 'Database 1', 3, 1, 'W 1800—2030', 'Edwards');
INSERT INTO courses_schedule VALUES ('Spring 2024', 7, 'CSCI', 6242, 'Database 2', 3, 1, 'R 1800—2030', 'Edwards');
INSERT INTO courses_schedule VALUES ('Spring 2024', 8, 'CSCI', 6246, 'Compilers', 3, 1, 'T 1500—1730', 'Edwards');

INSERT INTO courses_schedule VALUES ('Spring 2024', 9, 'CSCI', 6251, 'Cloud Computing', 3, 1, 'M 1800—2030', 'Ross');
INSERT INTO courses_schedule VALUES ('Spring 2024', 10, 'CSCI', 6254, 'SW Engineering', 3, 1, 'M 1530—1800', 'Ross');
INSERT INTO courses_schedule VALUES ('Spring 2024', 11, 'CSCI', 6260, 'Multimedia', 3, 1, 'R 1800—2030', 'Ross');
INSERT INTO courses_schedule VALUES ('Spring 2024', 12, 'CSCI', 6262, 'Graphics 1', 3, 1, 'W 1800—2030', 'Ross');

INSERT INTO courses_schedule VALUES ('Spring 2024', 13, 'CSCI', 6283, 'Security 1', 3, 1, 'T 1800—2030', 'Doubtfire');
INSERT INTO courses_schedule VALUES ('Spring 2024', 14, 'CSCI', 6284, 'Cryptography', 3, 1, 'M 1800—2030', 'Doubtfire');
INSERT INTO courses_schedule VALUES ('Spring 2024', 15, 'CSCI', 6286, 'Network Security', 3, 1, 'W 1800—2030', 'Doubtfire');
INSERT INTO courses_schedule VALUES ('Spring 2024', 16, 'CSCI', 6384, 'Cryptography 2', 3, 1, 'W 1500—1730', 'Doubtfire');

INSERT INTO courses_schedule VALUES ('Spring 2024', 17, 'ECE', 6241, 'Communication Theory', 3, 1, 'M 1800—2030', 'Parmer');
INSERT INTO courses_schedule VALUES ('Spring 2024', 18, 'ECE', 6242, 'Information Theory', 2, 1, 'T 1800—2030', 'Parmer');
INSERT INTO courses_schedule VALUES ('Spring 2024', 19, 'MATH', 6210, 'Logic', 2, 1, 'W 1800-2030', 'Parmer');
INSERT INTO courses_schedule VALUES ('Spring 2024', 20, 'CSCI', 6339, 'Embedded Systems', 3, 1, 'R 1600--1830', 'Parmer');


DROP TABLE IF EXISTS catalog;
CREATE TABLE catalog (
  department        varchar(50) not null,
  course_number     int(5) not null,
  course_title      varchar(50) not null,
  course_credits    int(1) not null,
  course_prereq     varchar(50),
  course_prereq2    varchar(50),
  foreign key (department) references courses_schedule(course_dname),
  foreign key (course_number) references courses_schedule(course_number),
  foreign key (course_title) references courses_schedule(course_title),
  foreign key (course_credits) references courses_schedule(course_credits),
  foreign key (course_prereq) references courses(course_prereq),
  foreign key (course_prereq2) references courses(course_prereq2)
);

--catalog:
INSERT INTO catalog VALUES ('CSCI', 6221, 'SW Paradigms', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6461, 'Computer Architecture', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6212, 'Algorithms', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6220, 'Machine Learning', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6232, 'Networks 1', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL);
INSERT INTO catalog VALUES ('CSCI', 6241, 'Database 1', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL);
INSERT INTO catalog VALUES ('CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212');
INSERT INTO catalog VALUES ('CSCI', 6260, 'Multimedia', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', NULL);
INSERT INTO catalog VALUES ('CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', NULL);
INSERT INTO catalog VALUES ('CSCI', 6262, 'Graphics 1', 3, NULL, NULL);
INSERT INTO catalog VALUES ('CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL);
INSERT INTO catalog VALUES ('CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL);
INSERT INTO catalog VALUES ('CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232');
INSERT INTO catalog VALUES ('CSCI', 6325, 'Algorithms 2', 3, 'CSCI 6212', NULL);
INSERT INTO catalog VALUES ('CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212');
INSERT INTO catalog VALUES ('CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', NULL);
INSERT INTO catalog VALUES ('ECE', 6241, 'Communication Theory', 3, NULL, NULL);
INSERT INTO catalog VALUES ('ECE', 6242, 'Information Theory', 2, NULL, NULL);
INSERT INTO catalog VALUES ('MATH', 6210, 'Logic', 2, NULL, NULL);

DROP TABLE IF EXISTS registrations;
CREATE TABLE registrations (
  registration_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id        int(8) not null,
  course_id         int(5) not null,
  foreign key (student_id) references students(UID),
  foreign key (course_id) references courses_schedule(course_ID)
);