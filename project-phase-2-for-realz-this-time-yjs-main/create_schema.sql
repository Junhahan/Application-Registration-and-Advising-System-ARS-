use university;
SET foreign_key_checks = 0;

DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS reviewform;
DROP TABLE IF EXISTS checkstatus;
DROP TABLE IF EXISTS recommendations;
DROP TABLE IF EXISTS personalinformation;
DROP TABLE IF EXISTS academicinformation;
DROP TABLE IF EXISTS catalog;
DROP TABLE IF EXISTS courses_schedule;
DROP TABLE IF EXISTS form1;
DROP TABLE IF EXISTS instructors;
DROP TABLE IF EXISTS student_course;
DROP TABLE IF EXISTS alumni;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS applicants_info;
DROP TABLE IF EXISTS applicants;
DROP TABLE IF EXISTS facultymembers;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS advisor_assignments;
DROP TABLE IF EXISTS form1_requests;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS graduation_requests;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  user_id     INT AUTO_INCREMENT,
  username    VARCHAR(20) NOT NULL,
  password    VARCHAR(20) NOT NULL,
  fname       VARCHAR(50) NOT NULL,
  lname       VARCHAR(50) NOT NULL,
  address     VARCHAR(100),
  DOB         DATE,
  email       VARCHAR(50) NOT NULL,
  user_type   VARCHAR(20) NOT NULL,
  uid         VARCHAR(50) NOT NULL,
  PRIMARY KEY (user_id),
  INDEX idx_username (username)
);

CREATE TABLE applicants (
  uid            varchar(50) not null,
  password       varchar(50) not null,
  name           varchar(50) not null,
  address        varchar(50) not null,
  gender         varchar(50) not null,
  program        varchar(50) not null,
  semester       varchar(50) not null,
  year           varchar(4) not null,
  degree_program varchar(100) not null,
  status         varchar(5),
  PRIMARY KEY (uid)
);

CREATE TABLE students (
  user_id     INT(8) NOT NULL,
  program     VARCHAR(20) NOT NULL,
  thesis      TEXT,
  grad_status ENUM('T', 'F') DEFAULT 'F' NOT NULL,
  grad_semester VARCHAR(20) NOT NULL,
  grad_year VARCHAR(10) NOT NULL,
  uaf VARCHAR(1) NOT NULL,
  PRIMARY KEY (user_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE enrollments (
  user_id     INT(8) NOT NULL,
  course_id   INT(5) NOT NULL,
  PRIMARY KEY (user_id, course_id),
  FOREIGN KEY (user_id) REFERENCES students(user_id),
  FOREIGN KEY (course_id) REFERENCES courses(CourseID)
);

CREATE TABLE alumni (
  user_id int(8) not null,
  grad_year int(4) not null,
  degree varchar(50) not null,
  major varchar(50) not null,
  primary key (user_id)
);

CREATE TABLE applicants_info (
  uid VARCHAR(50) NOT NULL,
  MS_GPA DECIMAL(3,2),
  BS_BA_GPA DECIMAL(3,2) NOT NULL,
  MS_year INTEGER,
  BS_BA_year INTEGER NOT NULL,
  MS_uni VARCHAR(50),
  BS_uni VARCHAR(50) NOT NULL,
  GRE_verbal INTEGER NOT NULL,
  GRE_quantitative INTEGER NOT NULL,
  GRE_examyear INTEGER NOT NULL,
  GRE_advanced INTEGER,
  GRE_subject VARCHAR(50),
  TOEFL INTEGER,
  TOEFL_date VARCHAR(50),
  recommendations BOOLEAN NOT NULL,
  transcript BOOLEAN NOT NULL,
  PRIMARY KEY (uid)
);


CREATE TABLE student_course (
  student_id int(8) NOT NULL,
  IP_course_ID int(5) NOT NULL,
  dname varchar(50) NOT NULL,
  course_number int(5) NOT NULL,
  title varchar(50) NOT NULL,
  credits int(1) NOT NULL,
  course_prereq varchar(50),
  course_prereq2 varchar(50),
  grade varchar(2) NOT NULL,
  counts enum('T', 'F') DEFAULT 'F' NOT NULL,
  form1 enum('T', 'F') DEFAULT 'F' NOT NULL,
  PRIMARY KEY (student_id, IP_course_ID),
  FOREIGN KEY (student_id) REFERENCES students(user_id)
);

CREATE TABLE instructors (
  user_id   INT(8) NOT NULL, 
  course_ID INT(5) NOT NULL,
  PRIMARY KEY (user_id, course_ID),
  FOREIGN KEY (course_ID) REFERENCES courses(CourseID),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE courses_schedule (
  semester              VARCHAR(20) NOT NULL,
  course_ID             INT(5) NOT NULL,
  course_dname          VARCHAR(50) NOT NULL,
  course_number         INT(5) NOT NULL,
  course_title          VARCHAR(50) NOT NULL,
  course_credits        INT(1) NOT NULL,
  section_number        INT(1) NOT NULL,
  meeting_time          VARCHAR(50) NOT NULL,
  instructor_username   VARCHAR(50) NOT NULL,
  PRIMARY KEY (semester, course_ID),
  INDEX idx_course_ID (course_ID),
  INDEX idx_dname (course_dname),
  INDEX idx_course_number (course_number),
  INDEX idx_course_title (course_title),
  INDEX idx_course_credits (course_credits),
  FOREIGN KEY (instructor_username) REFERENCES users(username)
);

CREATE TABLE academicinformation (
  uid VARCHAR(50) NOT NULL,
  MS_GPA DECIMAL(3,2),
  BS_BA_GPA DECIMAL(3,2) NOT NULL,
  MS_year INTEGER(4),
  BS_BA_year INTEGER(4) NOT NULL,
  MS_uni VARCHAR(50),
  BS_uni VARCHAR(50) NOT NULL,
  GRE_verbal INTEGER(3) NOT NULL,
  GRE_quantitative INTEGER(3) NOT NULL,
  GRE_examyear INTEGER(4) NOT NULL,
  GRE_advanced INTEGER(3),
  GRE_subject VARCHAR(50),
  TOEFL INTEGER(3),
  TOEFL_date VARCHAR(50),
  recommendations BOOLEAN NOT NULL,
  transcript BOOLEAN NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

CREATE TABLE personalinformation (
  uid varchar(50) not null,
  SSID varchar(50) not null,
  contact_info varchar(50) not null,
  MS_major varchar(50),
  BS_BA_major varchar(50) not null,
  interests varchar(50) not null,
  experience varchar(50) not null,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

CREATE TABLE recommendations (
  rec_id SERIAL PRIMARY KEY,
  uid varchar(50) NOT NULL,
  rec_name varchar(50) NOT NULL,
  rec_email varchar(100) NOT NULL,
  rec_prof varchar(50) NOT NULL,
  rec_affiliation varchar(100) NOT NULL,
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

CREATE TABLE checkstatus (
  uid varchar(50) NOT NULL,
  status varchar(50) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

CREATE TABLE reviewform (
  uid  varchar(50) not null,
  recommendation1rating integer(1),
  recommendation1generic char(1),
  recommendation1credible char(1),
  recommendation1from varchar(100) not NULL,
  gac_rating varchar(50),
  deficiencycourses varchar(255),
  reasonsforrejection varchar(255),
  reviewer_comments varchar(40),
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

CREATE TABLE facultymembers (
  user_id INT(8) NOT NULL,
  role VARCHAR(50) NOT NULL,
  name VARCHAR(50) NOT NULL,
  permissions VARCHAR(50) NOT NULL,
  finalDecision VARCHAR(50) NOT NULL,
  PRIMARY KEY (role),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE registrations (
  registration_id INTEGER PRIMARY KEY AUTO_INCREMENT,
  student_id INT(8) NOT NULL,
  course_id INT(5) NOT NULL,
  FOREIGN KEY (student_id) REFERENCES users(user_id),
  FOREIGN KEY (course_id) REFERENCES courses_schedule(course_ID)
);

CREATE TABLE catalog (
  department VARCHAR(50) NOT NULL,
  course_number INT(5) NOT NULL,
  course_title VARCHAR(50) NOT NULL,
  course_credits INT(1) NOT NULL,
  course_prereq VARCHAR(50),
  course_prereq2 VARCHAR(50),
  FOREIGN KEY (department) REFERENCES courses_schedule(course_dname),
  FOREIGN KEY (course_number) REFERENCES courses_schedule(course_number),
  FOREIGN KEY (course_title) REFERENCES courses_schedule(course_title),
  FOREIGN KEY (course_credits) REFERENCES courses_schedule(course_credits)
);

CREATE TABLE courses (
  CourseID        INT(5) NOT NULL,
  dname           VARCHAR(50) NOT NULL,
  course_number   INT(5) NOT NULL,
  title           VARCHAR(50) NOT NULL,
  credits         INT(1) NOT NULL,
  course_prereq   VARCHAR(50),
  course_prereq2  VARCHAR(50),
  PRIMARY KEY (CourseID)
);

CREATE TABLE form1 (
    user_id INT,
    course_id INT(5),
    PRIMARY KEY(user_id, course_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(course_id) REFERENCES courses(CourseID)
);

CREATE TABLE advisor_assignments (
    student_id INT(8),
    faculty_id INT(8),
    PRIMARY KEY(student_id, faculty_id),
    FOREIGN KEY(student_id) REFERENCES users(user_id),
    FOREIGN KEY(faculty_id) REFERENCES users(user_id)
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE form1_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    faculty_advisor_id INT NOT NULL,
    status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (faculty_advisor_id) REFERENCES users(user_id)
);

CREATE TABLE graduation_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    faculty_advisor_id INT NOT NULL,
    status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
    FOREIGN KEY (student_id) REFERENCES users(user_id),
    FOREIGN KEY (faculty_advisor_id) REFERENCES users(user_id)
);

INSERT INTO users (user_id, username, password, fname, lname, address, DOB, email, user_type, uid) VALUES
(88767547, 'sara.almaouf', 'pass', 'Sara', 'Almaouf', 'Vienna, VA', '2004-09-11', 'sara.almaouf@gwu.edu', 'applicant', ''),

(78276378, 'jake.kat', 'pass', 'Jake', 'Kat', 'Tysons, VA', '2003-07-07', 'jake.kate@gwu.edu', 'student', ''),
(78307381, 'kate.joe', 'pass', 'Kate', 'Joe', 'Alexandia, VA', '2005-05-20', 'kate@gwu.edu', 'student', ''),
(88888888, 'holiday', 'pass', 'Billie', 'Holiday', 'Washington, D.C.', '2003-10-10', 'holiday@gwu.edu', 'student', ''),
(99999999, 'krall', 'pass', 'Diana', 'Krall', 'Woodbridge, VA', '2001-01-01', 'krall@gwu.edu', 'student', ''),

(72801643, 'Ouska', 'pass', 'Emily', 'Ouska', NULL, NULL, 'email1@email.com', 'instructor', ''),
(09526719, 'Edwards', 'pass', 'Ed', 'Edwards', NULL, NULL, 'email2@email.com', 'instructor', ''),
(78153610, 'Ross', 'pass', 'Bob', 'Ross', NULL, NULL, 'email3@email.com', 'instructor', ''),
(98145283, 'Doubtfire', 'pass', 'Euphegenia', 'Doubtfire', NULL, NULL, 'email4@email.com', 'instructor', ''),
(56283619, 'Parmer', 'pass', 'Gabe', 'Parmer', NULL, NULL, 'email5@email.com', 'instructor', ''),
(17826492, 'N', 'pass', 'Bhagirath', 'Narahari', NULL, NULL, 'narahari@gwu.edu', 'instructor', ''),
(96732691, 'C', 'pass', 'HyeongAh', 'Choi', NULL, NULL, 'choi@gwu.edu', 'instructor', ''),

(63736329, 'review.faculty', 'pass', 'Faculty', 'Reviewer', 'TESt, MA', '2000-04-07', 'test2@gwu.edu', 'reviewer', ''),
(63736319, 'roh.justin', 'pass', 'Justin', 'Roh', 'TESt, MA', '2000-05-07', 'test@gwu.edu', 'faculty', ''),
(73736319, 'kim.david', 'pass', 'David', 'Kim', 'Add, VA', '2000-04-07', 'david@gwu.edu', 'faculty', ''),
(83736319, 'Johnson.Liam', 'pass', 'Liam', 'Johnson', 'Boston, MA', '2002-01-27', 'liam@gwu.edu', 'faculty', ''),
(89173620, 'emma.holand', 'pass', 'Emma', 'Holand', 'Herndon, VA', '2005-04-16', 'emma.holand@gwu.edu', 'admin', ''),
(74742839, 'GradSec', 'pass', 'Grad', 'Sec', 'Fairfax, VA', '2002-08-02', 'GradSec@gwu.edu', 'secretary', ''),
(89234234, 'Alumni', 'pass', 'Alu', 'Mni', 'Arlington, VA', '2003-05-04', 'Alumni@gwu.edu', 'alumni', ''),
(82341508, 'AdCAC', 'pass', 'Ad', 'CAC', 'woodbridge, VA', '2003-07-02', 'AdCAC@gwu.edu', 'CAC/Chair', ''),

(12345678, 'new.student1', 'newpass1', 'New', 'Student1', '123 Fake St, Springfield', '1995-08-01', 'new.student1@university.edu', 'student', ''),
(23456789, 'new.student2', 'newpass2', 'New', 'Student2', '321 Fake St, Springfield', '1996-09-02', 'new.student2@university.edu', 'student', ''),
(55555555, 'mccartney', 'pass', 'Paul', 'McCartney', '789 Penny Lane, Liverpool', '2002-06-18', 'mccartney@gwu.edu', 'student', ''),
(66666666, 'harrison', 'pass', 'George', 'Harrison', '321 Abbey Road, London', '2001-02-25', 'harrison@gwu.edu', 'student', ''),
(44444444, 'starr', 'pass', 'Ringo', 'Starr', '654 Yellow Submarine St, Liverpool', '2000-07-07', 'starr@gwu.edu', 'student', ''),
(77777777, 'clapton', 'pass', 'Eric', 'Clapton', '456 Layla Ln, Surrey', '1999-03-30', 'clapton@gwu.edu', 'alumni', '');

INSERT INTO students (user_id, program, grad_status, grad_semester, grad_year, uaf) VALUES 
(78276378, 'Masters Program', 'T', 'Fall', '2026','F'),
(78307381, 'PhD', 'T', 'Fall','2026','T'),
(88888888, 'Masters Program', 'T','Summer','2027','T'),
(99999999, 'Masters Program', 'T','Fall','2027','T'),
(12345678, 'PhD', 'T', 'Fall', '2026','T'),
(23456789, 'Masters Program', 'T', 'Summer', '2026','T'),
(55555555, 'Masters Program', 'F', 'Fall', '2024', 'F'),
(66666666, 'Masters Program', 'F', 'Fall', '2024', 'F'),
(44444444, 'PhD', 'F', 'Fall', '2026', 'F');

INSERT INTO enrollments (user_id, course_id) VALUES 
(78276378, 1),
(78276378, 5),
(78276378, 9),
(78276378, 13),
(78276378, 17),
(78307381, 2),
(78307381, 6),
(78307381, 10),
(78307381, 14),
(78307381, 18),
(88888888, 2),
(88888888, 3);

INSERT INTO alumni (user_id, grad_year, degree, major) VALUES
(89234234, 2022, 'MS', 'Data Analytics'),
(77777777, 2014, 'MS', 'Computer Science');

INSERT INTO applicants (uid, password, name, address, gender, program, semester, year, degree_program, status) VALUES
('A0000001', 'appPass1', 'Tom Smith', '1234 Elm St, Springfield', 'Male', 'Computer Science', 'Fall', '2024', 'PhD',''),
('A0000002', 'appPass2', 'Jane Doe', '5678 Oak St, Springfield', 'Female', 'Electrical Engineering', 'Fall', '2024', 'Masters',''),
('12312312', 'lennon', 'John Lennon', '123 Penny Lane, Liverpool', 'Male', 'Computer Science', 'Fall', '2024', 'PhD', 'completed'),  
('66666667', 'starr', 'Ringo Starr', '456 Abbey Road, London', 'Male', 'Computer Science', 'Fall', '2024', 'Masters', 'incomplete'),
('A0000003', 'appPass3', 'Alice Johnson', '123 Apple St, Metropolis', 'Female', 'Mechanical Engineering', 'Fall', '2024', 'Masters', 'accepted'),
('A0000004', 'appPass4', 'Bob Franklin', '456 Pear St, Metropolis', 'Male', 'Physics', 'Fall', '2024', 'PhD', 'rejected'),
('A0000005', 'appPass5', 'Carol White', '789 Banana St, Metroville', 'Female', 'Biology', 'Fall', '2024', 'Masters', ''),
('A0000006', 'appPass6', 'David Green', '321 Kiwi Ln, Smalltown', 'Male', 'Chemistry', 'Fall', '2024', 'PhD', ''),
('A0000007', 'appPass7', 'Erica Brown', '654 Melon St, Bigtown', 'Female', 'Mathematics', 'Fall', '2024', 'Masters', ''),
('A0000008', 'appPass8', 'Frank Maple', '987 Grape St, Rivertown', 'Male', 'Environmental Science', 'Fall', '2024', 'PhD', ''),
('A0000009', 'appPass9', 'Grace Pine', '369 Cherry Ln, Lakecity', 'Female', 'Statistics', 'Fall', '2024', 'Masters', 'accepted'),
('A0000010', 'appPass10', 'Henry Oak', '258 Plum St, Hilltown', 'Male', 'Astronomy', 'Fall', '2024', 'PhD', ''),
('A0000011', 'appPass11', 'Isla Cedar', '147 Peach St, Beachtown', 'Female', 'Philosophy', 'Fall', '2024', 'Masters', 'rejected'),
('A0000012', 'appPass12', 'Jason Birch', '963 Apple St, Metropolis', 'Male', 'Mechanical Engineering', 'Fall', '2024', 'PhD', ''),
('A0000013', 'appPass13', 'Kelly Spruce', '784 Pear St, Metropolis', 'Female', 'Physics', 'Fall', '2024', 'Masters', ''),
('A0000014', 'appPass14', 'Liam Teak', '321 Banana St, Metroville', 'Male', 'Biology', 'Fall', '2024', 'PhD', ''),
('A0000015', 'appPass15', 'Monica Fir', '456 Kiwi Ln, Smalltown', 'Female', 'Chemistry', 'Fall', '2024', 'Masters', 'accepted'),
('A0000016', 'appPass16', 'Noah Elm', '789 Melon St, Bigtown', 'Male', 'Mathematics', 'Fall', '2024', 'PhD', ''),
('A0000017', 'appPass17', 'Olivia Pine', '321 Grape St, Rivertown', 'Female', 'Environmental Science', 'Fall', '2024', 'Masters', ''),
('A0000018', 'appPass18', 'Peter Ash', '654 Cherry Ln, Lakecity', 'Male', 'Statistics', 'Fall', '2024', 'PhD', 'rejected'),
('A0000019', 'appPass19', 'Quinn Willow', '987 Plum St, Hilltown', 'Female', 'Astronomy', 'Fall', '2024', 'Masters', ''),
('A0000020', 'appPass20', 'Ryan Hazel', '369 Peach St, Beachtown', 'Male', 'Philosophy', 'Fall', '2024', 'PhD', ''),
('A0000021', 'appPass21', 'Sophia Mahogany', '258 Apple St, Metropolis', 'Female', 'Mechanical Engineering', 'Fall', '2024', 'Masters', ''),
('A0000022', 'appPass22', 'Tyler Redwood', '147 Pear St, Metropolis', 'Male', 'Physics', 'Fall', '2024', 'PhD', '');

INSERT INTO applicants_info (uid, MS_GPA, BS_BA_GPA, MS_year, BS_BA_year, MS_uni, BS_uni, GRE_verbal, GRE_quantitative, GRE_examyear, GRE_advanced, GRE_subject, TOEFL, TOEFL_date, recommendations, transcript) VALUES
('A0000001', NULL, 3.85, NULL, 2018, NULL, 'GWU', 160, 168, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000002', NULL, 3.60, NULL, 2019, NULL, 'GWU', 158, 170, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000003', NULL, 3.70, NULL, 2020, NULL, 'MIT', 155, 165, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000004', 3.50, 3.90, 2020, 2020, 'Stanford', 'Stanford', 160, 162, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000005', NULL, 3.80, NULL, 2021, NULL, 'Harvard', 158, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000006', 3.60, 3.65, 2020, 2020, 'Caltech', 'Caltech', 155, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000007', NULL, 3.75, NULL, 2020, NULL, 'Princeton', 150, 155, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000008', 3.80, 3.90, 2021, 2021, 'Yale', 'Yale', 162, 170, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000009', NULL, 3.85, NULL, 2021, NULL, 'Columbia', 159, 167, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000010', 3.45, 3.50, 2020, 2020, 'UChicago', 'UChicago', 154, 159, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000011', NULL, 3.95, NULL, 2020, NULL, 'UPenn', 161, 169, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000012', 3.70, 3.80, 2021, 2021, 'Duke', 'Duke', 156, 163, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000013', NULL, 3.60, NULL, 2020, NULL, 'Northwestern', 152, 158, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000014', 3.55, 3.65, 2021, 2021, 'JHU', 'JHU', 157, 161, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000015', NULL, 3.80, NULL, 2020, NULL, 'WashU', 160, 165, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000016', 3.90, 3.95, 2020, 2020, 'Cornell', 'Cornell', 163, 168, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000017', NULL, 3.70, NULL, 2021, NULL, 'Brown', 155, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000018', 3.85, 3.90, 2021, 2021, 'Dartmouth', 'Dartmouth', 159, 164, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000019', NULL, 3.60, NULL, 2020, NULL, 'Vanderbilt', 154, 159, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000020', 3.50, 3.55, 2020, 2020, 'Rice', 'Rice', 152, 158, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000021', NULL, 3.75, NULL, 2021, NULL, 'Notre Dame', 158, 166, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
('A0000022', 3.80, 3.85, 2020, 2020, 'Emory', 'Emory', 160, 167, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE);

INSERT INTO student_course VALUES 
(78307381, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'IP', 'F', 'F'),
(78307381, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'IP', 'F', 'F'),
(78307381, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'IP', 'F', 'F'),
(78307381, 16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', NULL, 'IP', 'F', 'F'),
(78307381, 20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212', 'IP', 'F', 'F'),
(78276378, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'IP', 'F', 'F'),
(78276378, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'IP', 'F', 'F'),
(78276378, 9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', NULL, 'IP', 'F', 'F'),
(78276378, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'IP', 'F', 'F'),
(78276378, 17, 'ECE', 6241, 'Communication Theory', 3, NULL, NULL, 'IP', 'F', 'F'),
(89173620, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'IP', 'F', 'F'),
(89173620, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'IP', 'F', 'F'),
(89173620, 10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', NULL, 'IP', 'F', 'F'),
(89173620, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'IP', 'F', 'F'),
(89173620, 18, 'ECE', 6242, 'Information Theory', 2, NULL, NULL, 'IP', 'F', 'F'),
(88888888, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'IP', 'F', 'F'),
(88888888, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'IP', 'F', 'F'),
(55555555, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'A', 'F', 'F'),
(55555555, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'A', 'F', 'F'),
(55555555, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'A', 'F', 'F'),
(55555555, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'A', 'F', 'F'),
(55555555, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'A', 'F', 'F'),
(55555555, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
(55555555, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
(55555555, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'B', 'F', 'F'),
(55555555, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'B', 'F', 'F'),
(55555555, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
(66666666, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'B', 'F', 'F'),
(66666666, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'B', 'F', 'F'),
(66666666, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'B', 'F', 'F'),
(66666666, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'B', 'F', 'F'),
(66666666, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'B', 'F', 'F'),
(66666666, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
(66666666, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
(66666666, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
(66666666, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
(66666666, 18, 'ECE', 6242, 'Information Theory', 2, NULL, NULL, 'C', 'F', 'F'),
(44444444, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'A', 'F', 'F'),
(44444444, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'A', 'F', 'F'),
(44444444, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'A', 'F', 'F'),
(44444444, 9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', NULL, 'A', 'F', 'F'),
(44444444, 10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', NULL, 'A', 'F', 'F'), 
(44444444, 11, 'CSCI', 6260, 'Multimedia', 3, NULL, NULL, 'A', 'F', 'F'),
(44444444, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'A', 'F', 'F'),
(77777777, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'B', 'F', 'F'),
(77777777, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'B', 'F', 'F'),
(77777777, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'B', 'F', 'F'), 
(77777777, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'B', 'F', 'F'),
(77777777, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'B', 'F', 'F'),
(77777777, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
(77777777, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
(77777777, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'A', 'F', 'F'),  
(77777777, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'A', 'F', 'F'),
(77777777, 15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232', 'A', 'F', 'F');

INSERT INTO instructors VALUES 
(72801643, 1),
(72801643, 2),
(72801643, 3),
(72801643, 4),
(09526719, 5),
(09526719, 6),
(09526719, 7),
(09526719, 8),
(78153610, 9),
(78153610, 10),
(78153610, 11),
(78153610, 12),
(98145283, 13),
(98145283, 14),
(98145283, 15),
(98145283, 16),
(56283619, 17),
(56283619, 18),
(56283619, 19),
(56283619, 20),
(17826492, 2),
(96732691, 3),
(63736319, 1),
(63736319, 2),
(63736319, 3);

INSERT INTO courses (CourseID, dname, course_number, title, credits, course_prereq, course_prereq2) VALUES
  (1, 'CSCI', 6221, 'SW Paradigms', 3, null, null),
  (2, 'CSCI', 6461, 'Computer Architecture', 3, null, null),
  (3, 'CSCI', 6212, 'Algorithms', 3, null, null),
  (4, 'CSCI', 6232, 'Networks 1', 3, null, null),
  (5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', null),
  (6, 'CSCI', 6241, 'Database 1', 3, null, null),
  (7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', null),
  (8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212'),
  (9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', null),
  (10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', null),
  (11, 'CSCI', 6260, 'Multimedia', 3, null, null),
  (12, 'CSCI', 6262, 'Graphics 1', 3, null, null),
  (13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', null),
  (14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', null),
  (15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232'),
  (16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', null),
  (17, 'ECE', 6241, 'Communication Theory', 3, null, null),
  (18, 'ECE', 6242, 'Information Theory', 2, null, null),
  (19, 'MATH', 6210, 'Logic', 2, null, null),
  (20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212');

INSERT INTO form1 (user_id, course_id) VALUES
(78276378, 1),
(78276378, 3),
(78307381, 2),
(78307381, 4);

INSERT INTO advisor_assignments (student_id, faculty_id) VALUES
(78276378, 63736319),
(78307381, 73736319),
(88888888, 73736319),
(99999999, 63736319),
(12345678, 83736319),
(23456789, 83736319),
(55555555, 17826492),
(66666666, 56283619),
(44444444, 56283619);
