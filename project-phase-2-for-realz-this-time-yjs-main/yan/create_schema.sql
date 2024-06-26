-- SQLBook: Code
PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  username        varchar(50) not null,
  password        varchar(50) not null,
  type            varchar(50) not null,
  uid             varchar(50) not null,
  PRIMARY KEY (uid)
);
DROP TABLE IF EXISTS applicants;
CREATE TABLE applicants (
  uid          varchar(50) not null PRIMARY KEY,
  name         varchar(50) not null,
  address      varchar(50) not null,
  gender       varchar(50) not null,
  program      varchar(50) not null,
  semester     varchar(50) not null,
  foreign key (uid) references users(uid)
);
DROP TABLE IF EXISTS academicinformation;
CREATE TABLE academicinformation (
  uid          varchar(50) not null,
  MS_GPA         DECIMAL(1,2),
  BS_BA_GPA         DECIMAL(1,2) NOT NULL,
  MS_year           INTEGER(4),
  BS_BA_year       INTEGER(4) NOT NULL,
  MS_uni           varchar(50),
  BS_uni          varchar(50) NOT NULL,
  GRE_verbal           INTEGER(3) not null,
  GRE_quantitative      INTEGER(3) not null,
  GRE_examyear        INTEGER(4) not null,
  GRE_advanced          INTEGER(3),
  GRE_subject          varchar(50),
  TOEFL        INTEGER(3),
  TOEFL_date   varchar(50),
  recommendations    BOOLEAN not null,
  transcript         BOOLEAN not null,
  PRIMARY KEY (uid),
  foreign key (uid) references applicants(uid)
);
DROP TABLE IF EXISTS personalinformation;
CREATE TABLE personalinformation (
  uid          varchar(50) not null,
  SSID         varchar(50) not null,
  contact_info      varchar(50) not null,
  MS_major             varchar(50),
  BS_BA_major varchar(50) not null,
  interests varchar(50) not null,
  experience varchar(50) not null,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);
DROP TABLE IF EXISTS recommendations;
CREATE TABLE recommendations (
  uid varchar(50) NOT NULL,
  rec_name varchar(50) NOT NULL,
  rec_email varchar(50) NOT NULL,
  rec_prof varchar(50) NOT NULL,
  rec_affiliation varchar(50) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);
DROP TABLE IF EXISTS checkstatus;
CREATE TABLE checkstatus (
  uid varchar(50) NOT NULL,
  status varchar(50) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);
DROP TABLE IF EXISTS facultymembers;
CREATE TABLE facultymembers (
  uid     varchar(50) not null,
  role     varchar(50) not null,
  name     varchar(50) not null,
  permissions   varchar(50) not null,
  finalDecision varchar(50) not null,
  PRIMARY KEY (role),
  FOREIGN KEY (uid) REFERENCES users(uid)
);
DROP TABLE IF EXISTS reviewform;
CREATE TABLE reviewform (
  uid  varchar(50) not null,
  recommendation1rating integer(1),
  recommendation1generic char(1),
  recommendation1credible char(1),
  recommendation1from varchar(100) not NULL,
  gac_rating   varchar(50),
  deficiencycourses     varchar(255),
  reasonsforrejection   varchar(255),
  reviewer_comments   varchar(40),

  PRIMARY KEY (uid),
  FOREIGN KEY (uid) REFERENCES applicants(uid)
);

INSERT INTO users VALUES('SystemAdmin', 'Op-!2234AC', 'admin', '11112222');

 -- insert Graduate Secretary
INSERT INTO users VALUES('GradSec', 'A4-kjNE687', 'faculty', '22121234');
INSERT INTO facultymembers VALUES('22121234', 'GS', 'GradSec', 'AcceptTranscript', 'Yes');

-- insert CAC/Chair
INSERT INTO users VALUES('AdCAC', 'WL$09a2ef', 'faculty', '11234532');
INSERT INTO facultymembers VALUES('11234532', 'CAC', 'Chair', 'Review', 'Yes');

-- insert Faculty Reviewers
INSERT INTO users VALUES('FacRev1', 'DLR243-86H', 'faculty', '11132346');
INSERT INTO facultymembers VALUES('11132346', 'Faculty', 'Nathan', 'Review', 'No');