# Phase I Report

## Entity-Relation Diagram

> Please provide an ER diagram for your DB organization.
see er diagram for just bing chilling,
## DB Organization

> Please provide documentation for your chosen data-base schema, including a discussion of the normalization levels.
        course_id uses the name in the instructions. It is a foreign key that references course_id in Courses.

        user_id is the GWID: ########, which is unique to each student. This is a foreign key that references the Users table.

        semester is the YEAR#, where # is 0 if spring and 1 if fall. This is meant to make it easy to select in ascending order.

        grade is stored as the letter grade (A, A-, B+, B, B-, C+, C, F) as outlined in the instructions. Storing GPA seems
        more convenient, but this attempts to follow the instructions.

        counts refers to whether a course should affect a user's GPA. This attribute is included to address the edge case of
        retaken courses (the same course shouldn't affect GPA twice unless this is desired behavior). counts is 0 or 1.
        If 1, it affects the student's GPA, if 0 it does not.

        We chose to design our form 1 such that the user selects a course from the dropdown of all courses, and can do this
        multiple times. Each time, the course they selected is removed from the dropdown for future cases. The form1 attribute
        represents whether a course the student has taken has been selected. This forces the student to select all courses they
        have taken when they submit the form1. This is only allowed, and required, for courses that have count as 1 (the course should count towards their GPA).
## Testing

> Please detail and document how you test the system. Separately document any unit tests, and manual tests.
> Tested HMTL files for general usage, using different sample insertions in the create file to explore functionality LQ
Manually inspect the user interface to ensure it matches design specifications and is visually appealing.LQ
Verified responsiveness across different devices and screen sizes. on mac os and windows 11 as well
Test UI elements such as buttons, forms, dropdowns, and modals for proper functionality and styling.JS/JH
Navigate through different features and workflows to assess ease of use and intuitiveness.
Identify potential usability issues.JH