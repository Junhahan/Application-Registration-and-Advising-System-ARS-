# Phase I Report

## Entity-Relation Diagram

> Please provide an ER diagram for your DB organization.
![ER_Diagram](https://github.com/gwu-cs-db-s24-grading/project-phase-i-rrss/assets/142900774/39bb99ee-472b-46c4-ac88-bd8680a5f9a6)


## DB Organization

> Please provide documentation for your chosen data-base schema, including a discussion of the normalization levels. 

Students Table: has attributes UID, username, password, first name, last name, address, date of birth, email, courses student is taking, and program. The primary key is UID, and courses references CourseID in courses table. This table is in Third Normal Form (3NF), satisfying both 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary key (UID), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds all of the student's data. 

Instructors Table: has attributes username, password, first name, last name, courses they are teaching, and email. Primary key is username, and courses references CourseID in courses table. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF. This is because each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary key (UID), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds all data for an instructor. 

Grad Secretaries Table: has attributes username, password, first name, last name, and email. The primary key is username. This table is in Third Normal Form (3NF)and satisfies the levels 1NF and 2NF, because each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary key (username), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds information about GSs

Courses Table: has attributes courseID, department name, course number, title, credits, course preqrequisite 1, course preqrequisite 2. Primary key is courseID and department name references name in departments table. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary key (CourseID), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds everything related to the courses. 

Student Courses Table: has attributes student_UID, student's first name, student's last name, In Progress courseID, In Progress course department name, In Progress course number, In Progress course title, grade, In Progress course's instructor's username. The primary key is student_UID and In Progress courseID. This table is in 1NF as it contains atomic values, but it is not in 2NF nor 3NF because of partial and transitive dependencies. The student first name and last name, and the instructor username are dependent on student_UID and IP_course_ID but not on each other. This table is to track the courses that the student has taken/is taking. 

Departments Table: has attributes id and name. The primary key is id. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary key (id), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds information for the three different departments that the courses are part of. 

Course Schedule Table: has attributes semester, course_ID, course's department name, course number, course title, course credits, section number, meeting time, and instructor username. The primary key is semester and course_ID. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary keys (semester and course_ID), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds information about the courses that are available to register into (offered during a semester).

Catalog Table: has attributes department, course number, course title, course credits, course prerequisite 1, and course prerequisite 2. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary keys (department and course number), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table hold information about ALL courses that the system offers, whether available or not during a specific semester. 

Registration Table: has attributes registration ID, student ID, and course ID. This table is in Third Normal Form (3NF), satisfying 1NF and 2NF, since each attribute has atomic values, no partial dependencies exist, all non-prime attributes are fully dependent on the primary keys (registration ID), no transitive dependencies exist, and there are no non-prime attributes that depend on other non-prime attributes. This table holds information about past registration for a student, and will hold future insertions of courses when a student registers for a course. 


## Testing

> Please detail and document how you test the system. Separately document any unit tests, and manual tests.

The way we tested our system was through various manual tests to ensure all functionality is working properly:
1) Creating a new student account by signing up, then using the username and password created in the signup, to log in. (login and signup functionality)
2) Logging into student account, clicking "Student Profile" to view student's data, and editing the data to update the student profile information. Logging out and logging back in to check that the update was saved. (editing and updating student profile functionality)
3) Logging into student account, clicking "Schedule" to view the course schedule, going back and clicking "Course Catalog" to view the course catalog of all courses offered by the system. (vewing courses)
4) Logging into student account, clicking "Registration", using the dropdown menu to select a course to register for, then clicking "Transcript" to check that the registration was successful. (registration functionality)
5) Registering for a course, then registering for a course with the same meeting time as the previous course, to check that registration will fail for the second course.  (testing time conflict functionality)
6) Registering for a course, then registering for the same course again, to check that registration will fail for the second attempt, and the course will be displayed once only in transcript. (testing 'already taking course' functionality)
7) Logging in as student, clicking Drop Courses, and dropping a course registered for, using the "Remove" button. (drop course functionality)
8) Logging out using the Actions drop down menu at the top of Home page (logout functionality)
9) Logging in using all created usernames and passwords 
10) Logging in as student, clicking Transcript and putting in student UID, to view classes registered, and grades recieved by instructor. (testing viewing transcript)
11) Logging in as instructor, clicking Assign Grades, entering a student's UID along with courses taught by logged in instructor, and assign a grade. submit grade assignement and check that it successfully updated transcript. Log into student's account and check that the grade is visible on the student's end.(grade assignment functionality)
12) Logging in as instructor, clicking Transcript, entering a student's UID, and veiwing the student's transcript along with assigned grades. (viewing transcripts functionality)
13) Logging out as instructor. (logout functionality)
14) Logging in as a grade secretary, clicking Assign Grade, entering student UID, along with any courses they are taking, and assign a grade. Hit submit and ensure grade is displayed on student's transcript, and student is able to view grade on their end. (grade assignement to any course functionality)
15) Logging in as a grade secretary, clicking Transcript, entering student UID, and viewing student's transcript with grades and courses in progress. (veiwing student transcripts functionality)
16) Logging out as grade secretary. (logout functionality)
17) Clicking the "Reset" button in the home page of our system to check info reset. 
18) Viewing schedule of classes and course catalog without needing to be logged in as student, instructor, or GS.

## Design Choices

We created a clean and organized UI layout that is easy to navigate when it comes to students, instructors, or GSs. There is clear navigation and sections designed for easy access, and an easy registration process for students. We also made sure to create clear navigation for instructors and grade secrataries to assign grades, view transcripts, and logout of their accounts. We focused on our design and making sure it presents a well organized layout throughout all pages of the students, instructors, and grade secratries accounts. We connected our design with our database which was carefully created ensuring we satisfy 3NF for most of the tables created. We included efficient data in our database and made sure everything was well tested. We also made sure to include pop-up messages for when students face a registration error, or for when instructors/grade secrataries face a grade assignement issue, to ensure that the user is well aware of their actions and the reason behind the system's responses. This addition creates a user-friendly environment for the students, instructors, and grade secrataries using the university system. We added the Home button to every page that the user accesses, in order to easily go back to the home page and navigate. 

We used Bootstrap for our html styling. Source: https://getbootstrap.com/docs/5.3/components/navbar/ 

## Design Assumptions


## Missing Functionality


## Key Responsibilities
