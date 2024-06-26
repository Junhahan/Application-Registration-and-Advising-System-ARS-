# Phase I Report

## Entity-Relation Diagram

> Please provide an ER diagram for your DB organization.
![ER Diagram](/assets/ER%20Diagram.png)
## DB Organization

> Please provide documentation for your chosen data-base schema, including a discussion of the normalization levels.

- For our chosen data-base schema, we split our information into eight different tables: users, applicants, academicinformation, personal information, recommendations, checkstatus, facultymembers, and reviewform. We decided to use uid as our primary key and foreign key to link most of our tables together. 
- Faculty members had data in faculty members and users, but not in the other tables to differentiate the specific data from applicants.
- Information for applicants went into users, academicinformation, personalinformation, and checkstatus as their specific information. Review and recommendation data was linked to the applicant after a faculty reviewer made a review for that applicant. Some choices were made to put the MS major (if one existed) and BS/BA major into the personalinformation table while other academic info went into the academicinformation table.
- Certain data was only available to other users based on the permissions they had (Graduate Secretary and CAC/Chair for example).
- Admin has access to almost all data.
- We decided to omit recommended advisor for the final decision from our database 

# Normalization
- The schema is primarily based on 
- First Normal Form (1NF): Since each table in our schema has a primary key and every field has atomic values without repeated groups of columns, our design satisfies the requirements of the 1NF. This guarantees that the structure of the data improves data integrity and query performance.
- Second Normal Form (2NF): Additionally, the design follows the 2NF. Partial dependencies are eliminated because every non-primary key field depends entirely on the primary key. In the "academicinformation" table, for instance, all non-key characteristics are directly reliant on the primary key "uid", guaranteeing that no non-key attribute is based on any subset of the primary key.
- Third Normal Form (3NF): Because the schema does not create transitive dependencies between the tables, it also seems to be in compliance with the third normal form. Non-key fields in the "personalinformation" table, like "SSID," "contact_info," and so on, rely solely on the primary key uid and not on any other non-primary key columns. This demonstrates data consistency and cuts down on redundancy.

# Design Choices
- An applicant's account and uid get created when they submit their initial application along with their academic and personal information. With applicants, we decided to make it so they can only view their current status, and submit recommendations if they didn't submit one yet. If they submitted a recommendation, the data that would be entered would be the recommender's data. Their status would be labeled as 'Application Incomplete' if they had both recommendations and transcript missing, would have shown up as 'Application Incomplete - transcript missing' or 'Application Incomplete - recommendations missing' if they had one or the other missing from the database. When both recommendations and the transcript have been marked as received, the status would be changed to say the application was complete and would reflect so on the applicant's status page. For faculty reviewers, they could only review applicants that had their application marked as complete and when they reviewed a specific applicant, they would see all of their relevant data and recommendations then give a rating of the application which would be submitted to the database. For the Graduate Secretary, we made it so they confirmed that a applicant's transcript was received by entering the applicant's uid and that they could see all of the data regarding the applicant including the review data on the final decision page. We also made it so that the CAC could see the same type of pages as Faculty Reviewers and Graduate Secretary except for the accepted transcript page. For the System Administrator, we chose to make it so they could see all list of users, all applicants with their status, and create new users. For final decision, only the GS and CAC are able to make the decision, but we also decided to omit the recommended advisor if an applicant was admitted. 

# List of Assumptions
- Using MySQL, we design the relational schema which will effectively handle and relate the applicant data, reviews and final decisions.
- On the other hand, Applicants, reviews, recommendation letters, users etc are examples of the key tables. We used python flask, we will be able to manage requests and communicate the MySQL database.
- We assumed that there would be only one recommendation letter and one review done by the faculty for an applicant. 
- Applicants are able to handle and submit their applications through the creation of personal user accounts. It is the responsibility of applicants to enter accurate academic and personal data. Following their initial data entry, each candidate is automatically granted a unique student number (UID).
- The graduate secretary manually updates the system with the receipt of each transcript, which is presumed to have been mailed. 
- Following completion, each applicant is examined by a committee or a faculty member.
- Review form is based on applicant's submitted data is filled out with ratings and recommendations as part of the process.
- For Chair of Admissions Committee is not present, the graduate secretary may enter final judgements and update he status of applications. 
- We assumed an applicant would create their account on the application page
- Faculty reviewers will be able to see and evaluate the applications but won't choose who gets admitted.
- CAC decide on admissions and make final decision.

# Missing functionality
- In our program design, when the Graduate Secretary views transcripts, our dialog box should include some basic information of the latest applicants, such as name, UID, and date of birth. This will greatly ensure that our information and data are matched, saving time on searching for student information by UID.
- Our program also lacks a confirmation message. After a recommendation letter is sent, we should have a screen to display that the recommendation letter has been sent, and a warning prompt asking applicants to send it from their personal email to the recommender to check to prevent the email from going into the spam folder.
- On our admin homepage, we should've not set up a create a new user option only for faculty itself; this is a flaw in our design. We should have made it so the admin could create all applicants and faculty accounts.

# Division of work
Nathan: Database schema creation, Homepage, System Admin pages, Applicant backend, Transcript updates, Faculty pages, Final decision, Debugging, MySQL migration, Unit/Manual testing, README file, report_phase1.md

Teresa: Database Schema Creation, Applicant frontend and backend, Transcript updates, Status frontend and backend, Recommendation frontend and backend, Final Decision, CSS files, Unit/Manual Testing, README.md, report_phase1.md, Debugging necessary files.

Yan: Database schema creation, Login page, Review form frontend and backend, Final Decision, CSS files, Unit/Manual Testing,  README.md, report_phase1.md, Debugging necessary files.

## Testing
- For Testing, we will be using a seperate python file to do our testing.
- We ensure that each function works as expected. Therefore, we used setUp method to create table for users, applicants and relevant data, before each test which initiliazes a SQLite memory database and set up the necessary structure. By creating new testing environment for each and every test case, this would ensure that we avoid data persistence across tests. It is essential to preserve the autonomy and integrity of each test seperately.
- Following the completion of each test method, the tearDown method is called, and it is in charge of shutting down the database connection and tidying up the test environment. In another words, this would guarantee that every test execute unhindered by earlier tests and in clean state. It stops data from leaking between the tests is essentia; to preserve test correctness and dependibility.
- For the test_insert_user_and_applicant, it verifies that entries can be appropriately inserted and retrieved across linked tables in the database. The process entails putting test data into several tables, followed by assertions to verify the accuracy and integrity of the data. Through the use of the realistic simulations, the system's ability to handle user and applicant data within the database is tested. 

> Please detail and document how you test the system. Separately document any unit tests, and manual tests.
Unit testing:
In our code, we have a test called 'test_insert_user_and_applicant'
what is does: It checks if we can add a new user and a new applicant into our system.
How it works: 1.We create a pretend database to work with.
              2.We set up tables in this pretend database that our code will use ('users', 'applicants',etc)
              3.We add a new user(admin)and a new applicant(person applying for) to the pretend database.
              4.We add more details about the applicant,like their personal information and academic information. 
              5.We pretend to check the status of the applicant at different stages of the applican process.
              6.We check if everything was added correctly and if the status checks work as expected.
What it checks:
             It makes sure the user and applicant are added correctly.
             It checks if our system can handle different stages of the application process properly.
Manual Testing:
How it works:
             1. A applicant applies using the apply link from the homepage.
             2. The applicant can login and check their status.
             3. The applicant submits a request for a recommendation letter which changes the recommendation status to received.
             4. The Graduate Secretary confirms a applicant's transcript has been received by UID.
             5. If both transcript and recommendation have been received, the application is marked complete and a faculty reviewer can review.
             6. The faculty reviewer submits their review, they get returned to their homepage after the review.
             7. The Graduate Secretary or CAC/Chair makes the final decision.
             8. The applicant receives their final decision on their status page.

After the test: We clean up and get rid of the pretend database.