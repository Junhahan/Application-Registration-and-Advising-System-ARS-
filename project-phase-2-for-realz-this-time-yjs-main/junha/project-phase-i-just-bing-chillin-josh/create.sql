-- SQLBook: Code
use mydb;

SET FOREIGN_KEY_CHECKS = 0;


DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS prereqs;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS form1;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS form1_requests;



DROP TABLE IF EXISTS courses;
CREATE TABLE courses (
    course_id VARCHAR(255),
    title VARCHAR(255),
    credits INT(8),
    PRIMARY KEY(course_id)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id VARCHAR(255),
    user_type VARCHAR(255),
    password VARCHAR(255),
    fname VARCHAR(255),
    lname VARCHAR(255),
    email VARCHAR(255),
    address VARCHAR(255),
    PRIMARY KEY(user_id)
);


CREATE TABLE IF NOT EXISTS alumni (
    user_id VARCHAR(255) PRIMARY KEY,
    grad_year INT,
    degree VARCHAR(255),
    major VARCHAR(255),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS prereqs;
CREATE TABLE prereqs (
    required_for VARCHAR(255),
    prereq VARCHAR(255),
    PRIMARY KEY(required_for, prereq),
    FOREIGN KEY(required_for) REFERENCES courses(course_id),
    FOREIGN KEY(prereq) REFERENCES courses(course_id)
);

DROP TABLE IF EXISTS student_courses;
CREATE TABLE student_courses (
    course_id VARCHAR(255),
    user_id VARCHAR(255),
    semester INT(8),
    grade enum('IP', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F'),
    counts enum('T', 'F') DEFAULT 'F' NOT NULL,
    form1 enum('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY(course_id, user_id, semester),
    FOREIGN KEY(course_id) REFERENCES courses(course_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students (
    user_id VARCHAR(255),
    grad_status enum('T', 'F') DEFAULT 'F' NOT NULL,
    thesis TEXT,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS advisor_assignments;
CREATE TABLE advisor_assignments (
    student_id VARCHAR(255),
    faculty_id VARCHAR(255),
    PRIMARY KEY(student_id, faculty_id),
    FOREIGN KEY(student_id) REFERENCES users(user_id),
    FOREIGN KEY(faculty_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS form1;
CREATE TABLE form1 (
    user_id VARCHAR(255),
    course_id VARCHAR(255),
    PRIMARY KEY(user_id, course_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(course_id) REFERENCES courses(course_id)
);

DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS form1_requests;
CREATE TABLE form1_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(255) NOT NULL,
    faculty_advisor_id VARCHAR(255) NOT NULL,
    status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
    FOREIGN KEY(student_id) REFERENCES users(user_id),
    FOREIGN KEY(faculty_advisor_id) REFERENCES users(user_id)
);


SET FOREIGN_KEY_CHECKS = 1; 

-- COURSE DATA
INSERT INTO courses (course_id, title, credits)
VALUES 
    ("CSCI6221", "SW Paradigms", 3),
    ("CSCI6262", "Graphics 1", 3),
    ("CSCI6461", "Computer Architecture", 3),
    ("CSCI6212", "Algorithms", 3),
    ("CSCI6220", "Machine Learning", 3),
    ("CSCI6232", "Networks 1", 3),
    ("CSCI6233", "Networks 2", 3),
    ("CSCI6241", "Database 1", 3),
    ("CSCI6242", "Database 2", 3),
    ("CSCI6246", "Compilers", 3),
    ("CSCI6260", "Multimedia", 3),
    ("CSCI6251", "Cloud Computing", 3),
    ("CSCI6254", "SW Engineering", 3),
    ("CSCI6283", "Security 1", 3),
    ("CSCI6284", "Cryptography", 3),
    ("CSCI6286", "Network Security", 3),
    ("CSCI6325", "Algorithms 2", 3),
    ("CSCI6339", "Embedded Systems", 3),
    ("CSCI6384", "Cryptography 2", 3),
    ("ECE6241", "Communication Theory", 3),
    ("ECE6242", "Information Theory", 2),
    ("MATH6210", "Logic", 2);



-- USER DATA
INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES
    ("12222222", "MS", "password", "john", "lname", "someemail@email.com", "some address"),
    ("13333333", "MS", "password", "jone", "lname", "someemail@email.com", "some address"),
    ("52222222", "PHD", "password", "jane", "lname", "someemail@email.com", "some address"),
    ("53333333", "PHD", "password", "janesse", "lname", "someemail@email.com", "some address"),
    ("21111111", "FA", "password", "jine", "smith1", "someemail@email.com", "some address"),
    ("22222222", "FA", "password", "june", "smith2", "someemail@email.com", "some address"),
    ("31111111", "GS", "password", "jene", "lname", "someemail@email.com", "some address"),
    ("41111111", "AL", "pass2", "jojo", "number1", "alum1@email.com", "address 1"),
    ("51111111", "AD", "password", "Junha", "Han", "example@email.com", "111 random st");


-- TAKEN COURSES DATA

INSERT INTO student_courses VALUES ("CSCI6221", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6262", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6461", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6212", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6220", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6232", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6233", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6241", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6242", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6246", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6260", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6251", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6254", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6283", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6284", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6286", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6325", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6339", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6384", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("ECE6241", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("ECE6242", "12222222", 20240, "A-", "T", "F");
INSERT INTO student_courses VALUES ("MATH6210", "12222222", 20240, "A-", "T", "F");

INSERT INTO student_courses VALUES ("MATH6210", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("ECE6242", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("ECE6241", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6384", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6339", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6325", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6221", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6262", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6461", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6212", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6220", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6232", "41111111", 20240, "B-", "T", "F");
INSERT INTO student_courses VALUES ("CSCI6233", "41111111", 20240, "B-", "T", "F");








-- PREREQ DATA
INSERT INTO prereqs (required_for, prereq)
VALUES
    ("CSCI6233", "CSCI6232"),
    ("CSCI6242", "CSCI6241"),
    ("CSCI6246", "CSCI6212"),
    ("CSCI6251", "CSCI6461"),
    ("CSCI6254", "CSCI6221"),
    ("CSCI6283", "CSCI6212"),
    ("CSCI6284", "CSCI6212"),
    ("CSCI6286", "CSCI6283"),
    ("CSCI6286", "CSCI6232"),
    ("CSCI6325", "CSCI6212"),
    ("CSCI6339", "CSCI6461"),
    ("CSCI6339", "CSCI6212"),
    ("CSCI6384", "CSCI6284");

-- STUDENT DATA
INSERT INTO students VALUES ('12222222', 0, "MY THESIS MY THESIS MY THESIS MY THESIS");
INSERT INTO students VALUES ('13333333', 0, NULL);
INSERT INTO students VALUES ('52222222', 0, NULL);
INSERT INTO students VALUES ('53333333', 0, NULL);




-- ADVISOR PAIR DATA
INSERT INTO advisor_assignments(student_id, faculty_id)
VALUES 
    ("12222222", "21111111"),
    ("13333333", "21111111");



INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('55555555', 'MS', 'paulPass', 'Paul', 'McCartney', 'paul@university.edu', '123 Abbey Road');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('66666666', 'MS', 'georgePass', 'George', 'Harrison', 'george@university.edu', '456 Penny Lane');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('88888888', 'PHD', 'ringoPass', 'Ringo', 'Starr', 'ringo@university.edu', '789 Strawberry Fields');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('77777777', 'AL', 'ericPass', 'Eric', 'Clapton', 'eric@alumni.university.edu', '1010 Layla St');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('99999991', 'FA', 'narahariPass', 'Narahari', '', 'narahari@university.edu', 'Faculty Office 1');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('99999992', 'FA', 'parmerPass', 'Parmer', '', 'parmer@university.edu', 'Faculty Office 2');

INSERT INTO users (user_id, user_type, password, fname, lname, email, address)
VALUES ('99999999', 'GS', 'gsPass', 'GS', 'Account', 'gs@university.edu', 'Graduate School Office');






INSERT INTO student_courses (course_id, user_id, semester, grade)
VALUES 
    ('CSCI6221', '55555555', 202401, 'A'),
    ('CSCI6212', '55555555', 202401, 'A'),
    ('CSCI6461', '55555555', 202401, 'A'),
    ('CSCI6232', '55555555', 202401, 'A'),
    ('CSCI6233', '55555555', 202401, 'A'),
    ('CSCI6241', '55555555', 202402, 'B'),
    ('CSCI6246', '55555555', 202402, 'B'),
    ('CSCI6262', '55555555', 202402, 'B'),
    ('CSCI6283', '55555555', 202402, 'B'),
    ('CSCI6242', '55555555', 202402, 'B');

INSERT INTO student_courses (course_id, user_id, semester, grade)
VALUES 
    ('ECE6242', '66666666', 202403, 'C'),
    ('CSCI6221', '66666666', 202401, 'B'),
    ('CSCI6461', '66666666', 202401, 'B'),
    ('CSCI6212', '66666666', 202401, 'B'),
    ('CSCI6232', '66666666', 202401, 'B'),
    ('CSCI6233', '66666666', 202401, 'B'),
    ('CSCI6241', '66666666', 202402, 'B'),
    ('CSCI6242', '66666666', 202402, 'B'),
    ('CSCI6283', '66666666', 202402, 'B'),
    ('CSCI6284', '66666666', 202402, 'B');


INSERT INTO student_courses (course_id, user_id, semester, grade)
VALUES 
    ('CSCI6221', '88888888', 202401, 'A'),
    ('CSCI6461', '88888888', 202401, 'A'),
    ('CSCI6212', '88888888', 202401, 'A'),
    ('CSCI6232', '88888888', 202401, 'A'),
    ('CSCI6233', '88888888', 202401, 'A'),
    ('CSCI6241', '88888888', 202401, 'A'),
    ('CSCI6242', '88888888', 202401, 'A'),
    ('CSCI6283', '88888888', 202401, 'A'),
    ('CSCI6284', '88888888', 202401, 'A'),
    ('CSCI6286', '88888888', 202401, 'A'),
    ('CSCI6246', '88888888', 202401, 'A'),
    ('CSCI6262', '88888888', 202401, 'A');

INSERT INTO student_courses (course_id, user_id, semester, grade)
VALUES 
    ('CSCI6221', '77777777', 201301, 'B'),
    ('CSCI6212', '77777777', 201301, 'B'),
    ('CSCI6461', '77777777', 201301, 'B'),
    ('CSCI6232', '77777777', 201301, 'B'),
    ('CSCI6233', '77777777', 201301, 'B'),
    ('CSCI6241', '77777777', 201302, 'B'),
    ('CSCI6242', '77777777', 201302, 'B'),
    ('CSCI6283', '77777777', 201302, 'A'),
    ('CSCI6284', '77777777', 201302, 'A'),
    ('CSCI6286', '77777777', 201302, 'A');

INSERT INTO advisor_assignments (student_id, faculty_id)
VALUES 
    ('55555555', '99999991'),
    ('66666666', '99999992'),
    ('88888888', '99999992');


INSERT INTO alumni (user_id, grad_year, degree, major)
VALUES ('77777777', 2014, 'MS', 'Computer Science');