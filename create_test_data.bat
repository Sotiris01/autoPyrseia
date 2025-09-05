@echo off
echo Creating test data folders for autoPyrseia...
echo.

REM Clean up existing test folders
if exist "test_data" rmdir /s /q "test_data"
mkdir "test_data"
cd "test_data"

REM Test 1: Simple case with 1 recipient, no attachments
echo Creating Test 1: Simple case with 1 recipient...
mkdir "test1"
cd "test1"

REM Create test PDF content for test 1
(
echo R 123456Z JAN 25
echo FM COMMAND CENTER ALPHA
echo TO ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: TEST MESSAGE ONE
echo ΣΧΕΤ. : NONE
echo.
echo This is a test message for autoPyrseia testing.
echo No classified information contained.
echo Test content only - not real military data.
echo.
) > temp_content.txt

REM Create proper PDF using Python helper
echo Creating pyrseia_server.pdf for test 1...
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
if not exist pyrseia_server.pdf (
    echo Fallback: copying as text file...
    copy temp_content.txt pyrseia_server.pdf > nul
)
del temp_content.txt

cd ..

REM Test 2: Multiple recipients with 1 attachment
echo Creating Test 2: Multiple recipients with 1 attachment...
mkdir "test2"
cd "test2"

(
echo P 234567Z FEB 25
echo FM COMMAND CENTER BETA
echo TO ΣΤΡΑΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΛΑΦ ΙΩΑΝΝΙΝΩΝ
echo INVALID_RECIPIENT_ALPHA
echo ΣΠ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: TEST MESSAGE TWO WITH ATTACHMENTS
echo ΣΧΕΤ. : TEST REFERENCE
echo.
echo This is test case two with multiple recipients.
echo Contains one attachment file.
echo Should filter out INVALID_RECIPIENT_ALPHA.
echo Test content only - not real military data.
echo.
echo 1 συνημμένα αρχεία:
echo 1. test_document.docx
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
echo This is a test document attachment > test_document.docx
del temp_content.txt

cd ..

REM Test 3: TO/INFO format with 2 attachments
echo Creating Test 3: TO/INFO format with 2 attachments...
mkdir "test3"
cd "test3"

(
echo R 345678Z MAR 25
echo FM COMMAND CENTER CHARLIE
echo TO ΣΥ ΗΠΕΙΡΟΥ
echo FAKE_UNIT_BRAVO
echo INFO 4501 ΠΜΥ
echo UNKNOWN_COMMAND_CENTER
echo ΝΑΥΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: TEST MESSAGE THREE INFO CASE
echo ΣΧΕΤ. : MULTIPLE REFERENCES
echo.
echo This is test case three using TO/INFO format.
echo Contains two attachment files.
echo Should filter out FAKE_UNIT_BRAVO and UNKNOWN_COMMAND_CENTER.
echo Test content only - not real military data.
echo.
echo 2 συνημμένα αρχεία:
echo 1. report_sample.xlsx
echo 2. image_test.png
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
echo Sample,Test,Data > report_sample.xlsx
echo PNG_TEST_IMAGE_DATA > image_test.png
del temp_content.txt

cd ..

REM Test 4: Complex case with special characters and 5 recipients
echo Creating Test 4: Complex case with 5 recipients...
mkdir "test4"
cd "test4"

(
echo P 456789Z APR 25
echo FM COMMAND CENTER DELTA
echo TO ΑΕΡΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo TEST_RECIPIENT_CHARLIE
echo ΣΤΡΑΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo INFO ΛΑΦ ΙΩΑΝΝΙΝΩΝ
echo NONEXISTENT_UNIT_DELTA
echo ΣΠ ΙΩΑΝΝΙΝΩΝ
echo FICTIONAL_COMMAND_ECHO
echo ΘΕΜΑ: TEST MESSAGE FOUR - COMPLEX CASE WITH SPECIAL CHARS
echo.
echo This is test case four with complex formatting.
echo Contains special characters and formatting tests.
echo Should filter out TEST_RECIPIENT_CHARLIE, NONEXISTENT_UNIT_DELTA, and FICTIONAL_COMMAND_ECHO.
echo Numbers: 123, 456, 789
echo Symbols: / - . _ 
echo Test content only - not real military data.
echo.
echo 1 συνημμένα αρχεία:
echo 1. complex_test_file.pdf
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
echo PDF_TEST_ATTACHMENT_CONTENT > complex_test_file.pdf
del temp_content.txt

cd ..

REM Test 5: Edge case with no ΣΧΕΤ section
echo Creating Test 5: Edge case without ΣΧΕΤ section...
mkdir "test5"
cd "test5"

(
echo R 567890Z MAY 25
echo FM COMMAND CENTER ECHO
echo TO ΣΥ ΗΠΕΙΡΟΥ
echo INVALID_UNIT_FOXTROT
echo 4501 ΠΜΥ
echo INFO
echo ΝΑΥΤΟΔΙΚΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo BOGUS_RECIPIENT_GOLF
echo ΘΕΜΑ: TEST EDGE CASE WITH MISSING REFERENCES
echo.
echo This is test case five - edge case with ΘΕΜΑ but no ΣΧΕΤ.
echo Tests the fallback mechanisms of the parser.
echo Should filter out INVALID_UNIT_FOXTROT and BOGUS_RECIPIENT_GOLF.
echo Content continues without standard format.
echo Should test recipient extraction limits.
echo Test content only - not real military data.
echo.
echo 2 συνημμένα αρχεία:
echo 1. edge_case_doc.txt
echo 2. backup_file.zip
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
echo Edge case test document content > edge_case_doc.txt
echo ZIP_BACKUP_TEST_DATA > backup_file.zip
del temp_content.txt

cd ..

REM Test 6: Duplicate detection test with minimal content difference
echo Creating Test 6: Duplicate detection test with minimal difference...
mkdir "test6"
cd "test6"

REM Create first signal
mkdir "signal_a"
cd "signal_a"

(
echo R 999888Z JUN 25
echo FM DUPLICATE TEST COMMAND
echo TO ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: DUPLICATE TEST SIGNAL
echo ΣΧΕΤ. : DUPLICATE_TEST_REF
echo.
echo This is the first version of the duplicate test signal.
echo The content is almost identical except for one character.
echo This tests autoPyrseia's duplicate detection capabilities.
echo Test marker: A
echo Test content only - not real military data.
echo.
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
del temp_content.txt

cd ..

REM Create second signal - identical except one character different
mkdir "signal_b"
cd "signal_b"

(
echo R 999888Z JUN 25
echo FM DUPLICATE TEST COMMAND
echo TO ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: DUPLICATE TEST SIGNAL
echo ΣΧΕΤ. : DUPLICATE_TEST_REF
echo.
echo This is the first version of the duplicate test signal.
echo The content is almost identical except for one character.
echo This tests autoPyrseia's duplicate detection capabilities.
echo Test marker: B
echo Test content only - not real military data.
echo.
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
del temp_content.txt

cd ..
cd ..

REM Test 7: Long attachment filename spanning two lines
echo Creating Test 7: Long attachment filename test...
mkdir "test7"
cd "test7"

(
echo R 777999Z JUL 25
echo FM COMMAND CENTER FOXTROT
echo TO ΦΡΟΥΡΑΡΧΕΙΟ ΙΩΑΝΝΙΝΩΝ
echo ΣΠ ΙΩΑΝΝΙΝΩΝ
echo ΘΕΜΑ: TEST MESSAGE SEVEN - LONG FILENAME TEST
echo ΣΧΕΤ. : LONG_FILENAME_TEST_REF
echo.
echo This is test case seven with very long attachment filename.
echo Tests autoPyrseia's ability to handle filenames that span multiple lines.
echo The attachment filename below exceeds normal line length limits.
echo Test content only - not real military data.
echo.
echo 1 συνημμένα αρχεία:
echo 1. very_long_attachment_filename_that_exceeds_
echo    in_the_display_system_test_document_with_additional_descriptive_text.docx
) > temp_content.txt

copy temp_content.txt pyrseia_server.pdf > nul
python ..\..\create_pdf_helper.py temp_content.txt pyrseia_server.pdf
echo This is a test document with a very long filename that spans multiple lines > very_long_attachment_filename_that_exceeds_in_the_display_system_test_document_with_additional_descriptive_text.docx
del temp_content.txt

cd ..

echo.
echo ================================
echo Test data creation completed!
echo ================================
echo.
echo Created 7 test folders:
echo - test1: 1 recipient, 0 attachments
echo - test2: 3 recipients, 1 attachment  
echo - test3: 3 recipients, 2 attachments ^(TO/INFO format^)
echo - test4: 5 recipients, 1 attachment ^(complex case^)
echo - test5: 3 recipients, 2 attachments ^(edge case^)
echo - test6: 2 identical signals, 1 char difference ^(duplicate detection test^)
echo - test7: 2 recipients, 1 attachment ^(long filename test^)
echo.
echo Each folder contains:
echo - pyrseia_server.pdf ^(test signal file^)
echo - Various attachment files ^(0-2 per test^)
echo.
echo Test 6 special note:
echo - Contains signal_a and signal_b subfolders
echo - Both have identical ID, FM, and recipient
echo - Only difference: "Test marker: A" vs "Test marker: B"
echo - Perfect for testing duplicate detection system
echo.
echo Test 7 special note:
echo - Tests very long attachment filenames
echo - Filename exceeds normal line length limits
echo - Tests parsing capabilities for multi-line filenames
echo.
echo All content is TEST DATA ONLY - no real military information.
echo.
echo To use: Copy contents of any test folder to your downloads folder
echo and run autoPyrseia to test different scenarios.
echo For test6: Copy signal_a first, process, then copy signal_b to test duplicates.
echo For test7: Tests attachment filename parsing with exceptionally long names.
echo.
pause
