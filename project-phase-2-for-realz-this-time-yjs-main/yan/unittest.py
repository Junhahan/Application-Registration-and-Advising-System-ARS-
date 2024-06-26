import sqlite3
import unittest
# seperate python file unit test 
class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.connection = sqlite3.connect(':memory:')
        self.cur = self.connection.cursor()
    
        self.cur.executescript("""
            CREATE TABLE users (
            username    varchar(50) not null,
            password    varchar(50) not null,
            type        varchar(50) not null,
            uid         varchar(50) not null,
            PRIMARY KEY (uid)
            );
            CREATE TABLE applicants (
              uid        varchar(50) not null PRIMARY KEY,
              name       varchar(50) not null,
              address    varchar(50) not null,
              gender     varchar(50) not null,
              program    varchar(50) not null,
              semester   varchar(50) not null,
              FOREIGN KEY (uid) REFERENCES users(uid)
            );
            CREATE TABLE academicinformation (
              uid              varchar(50) not null,
              MS_GPA           DECIMAL(1,2),
              BS_BA_GPA        DECIMAL(1,2) NOT NULL,
              MS_year          INTEGER,
              BS_BA_year       INTEGER NOT NULL,
              MS_uni           varchar(50),
              BS_uni           varchar(50) NOT NULL,
              GRE_verbal       INTEGER not null,
              GRE_quantitative INTEGER not null,
              GRE_examyear     INTEGER not null,
              GRE_advanced     INTEGER,
              GRE_subject      varchar(50),
              TOEFL            INTEGER,
              TOEFL_date       varchar(50),
              recommendations  BOOLEAN not null,
              transcript       BOOLEAN not null,
              PRIMARY KEY (uid),
              FOREIGN KEY (uid) REFERENCES applicants(uid)
            );
            CREATE TABLE personalinformation (
              uid           varchar(50) not null,
              SSID          varchar(50) not null,
              contact_info  varchar(50) not null,
              MS_major      varchar(50),
              BS_BA_major   varchar(50) not null,
              interests     varchar(50) not null,
              experience    varchar(50) not null,
              PRIMARY KEY (uid),
              FOREIGN KEY (uid) REFERENCES applicants(uid)
            );
            CREATE TABLE recommendations (
              uid             varchar(50) NOT NULL,
              rec_name        varchar(50) NOT NULL,
              rec_email       varchar(50) NOT NULL,
              rec_prof        varchar(50) NOT NULL,
              rec_affiliation varchar(50) NOT NULL,
              PRIMARY KEY (uid),
              FOREIGN KEY (uid) REFERENCES applicants(uid)
            );
            CREATE TABLE checkstatus (
              uid         varchar(50) NOT NULL,
              status      varchar(50) NOT NULL,
              PRIMARY KEY (uid),
              FOREIGN KEY (uid) REFERENCES applicants(uid)
            );
            CREATE TABLE facultymembers (
              uid      varchar(50) not null,
              role     varchar(50) not null,
              name     varchar(50) not null,
              permissions      varchar(50) not null,
              finalDecision    varchar(50) not null,
              PRIMARY KEY (role),
              FOREIGN KEY (uid) REFERENCES users(uid)
            );
            CREATE TABLE reviewform (
              uid                     varchar(50) not null,
              recommendation1rating   integer,
              recommendation1generic  char(1),
              recommendation1credible char(1),
              recommendation1from     varchar(100) not NULL,
              gac_rating              varchar(50),
              deficiencycourses       varchar(255),
              reasonsforrejection     varchar(255),
              reviewer_comments       varchar(40),
              PRIMARY KEY (uid),
              FOREIGN KEY (uid) REFERENCES applicants(uid)
            );
        """)

    def tearDown(self):
        self.connection.close()

    def test_insert_user_and_applicant(self):
        self.cur.execute("INSERT INTO users (username, password, type, uid) VALUES (?, ?, ?, ?)",
                         ('SystemAdmin', 'Op-!2234AC', 'admin', '11112222'))

        self.cur.execute("INSERT INTO applicants (uid, name, address, gender, program, semester) VALUES (?, ?, ?, ?, ?, ?)",
                         ('11112233', 'John Doe', '123 Main St', 'male', 'MS', 'Fall 2024'))
        
        # Insert into personalinformation
        self.cur.execute("INSERT INTO personalinformation (uid, SSID, contact_info, BS_BA_major, interests, experience) VALUES (?, ?, ?, ?, ?, ?)",
                         ('11112233', '123-45-6789', 'john.doe@example.com', 'Computer Science', 'AI Research', '2 years at XYZ Corp'))

        # Insert into academicinformation
        self.cur.execute("INSERT INTO academicinformation (uid, BS_BA_GPA, GRE_verbal, GRE_quantitative, GRE_examyear, recommendations, transcript) VALUES (?, ?, ?, ?, ?, ?, ?)",
                         ('11112233', 3.5, 150, 160, 2023, 1, 1))

        # Insert into checkstatus
        self.cur.execute("INSERT INTO checkstatus (uid, status) VALUES (?, ?)",
                         ('11112233', 'Application Complete and Under Review'))
        self.cur.execute("INSERT INTO reviewform (uid, recommendation1rating, recommendation1generic, recommendation1credible, recommendation1from, gac_rating, reviewer_comments) VALUES (?, ?, ?, ?, ?, ?)",
                         ('11112233', '5', 'N', 'Y', 'Senior Software at Google', '3', 'Has research work potential'))
                         
        # Select all information for a applicant based on complete application
        self.cur.execute("SELECT a.*, pi.*, ai.*, cs.status FROM applicants a JOIN personalinformation pi ON a.uid = pi.uid JOIN academicinformation ai ON a.uid = ai.uid JOIN checkstatus cs ON a.uid = cs.uid WHERE cs.status = 'Application Complete and Under Review'")
        complete_application = self.cur.fetchone()

        # Select all information for a applicant based on review complete
        self.cur.execute("SELECT a.*, pi.*, ai.*, rf.*, cs.status FROM applicants a JOIN personalinformation pi ON a.uid = pi.uid JOIN academicinformation ai ON a.uid = ai.uid JOIN reviewform rf ON a.uid = rf.uid JOIN checkstatus cs ON a.uid = cs.uid WHERE cs.status = 'Review Complete'")
        review_complete = self.cur.fetchone()

        # Select all information for a applicant based on final decision complete
        self.cur.execute("SELECT a.*, pi.*, ai.*, fm.*, cs.status FROM applicants a JOIN personalinformation pi ON a.uid = pi.uid JOIN academicinformation ai ON a.uid = ai.uid JOIN facultymembers fm ON a.uid = fm.uid JOIN checkstatus cs ON a.uid = cs.uid WHERE cs.status = 'Final Decision Made'")
        final_decision_complete = self.cur.fetchone()

        self.connection.commit()

        self.cur.execute("SELECT * FROM users WHERE uid = 11112233 ")
        user = self.cur.fetchone()
        
        self.cur.execute("SELECT * FROM applicants WHERE uid = 11112233",)
        applicant = self.cur.fetchone()


        self.assertIsNotNone(user)
        self.assertEqual(user[0], 'SystemAdmin')

        self.assertIsNotNone(applicant)
        self.assertEqual(applicant[1], 'John Doe')

if __name__ == '__main__':
    unittest.main()