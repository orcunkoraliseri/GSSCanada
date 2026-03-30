FILE HANDLE MICRO1 /NAME = 'C:\PATH TO DATA\c24episode_withno_bootstrap.dat' /recform=fixed /lrecl=76.
DATA LIST FILE=MICRO1
/RECID          00001 - 00005
EPINO          00006 - 00007
WGHT_EPI       00008 - 00017  (4)
DDAY           00018 - 00018
TOTEPISO       00019 - 00020
ACTCODE        00021 - 00025  (1)
STARTIME       00026 - 00029  (A) 
ENDTIME        00030 - 00033  (A)
STARTMIN       00034 - 00037
ENDMIN         00038 - 00041
DURATION       00042 - 00045
PLACE          00046 - 00047
ALONE          00048 - 00048
SPOUSE         00049 - 00049
CHILDHSD       00050 - 00050
PARHSD         00051 - 00051
MEMBHSD        00052 - 00052
NHSDCL15       00053 - 00053
NHSDC15P       00054 - 00054
NHSDPAR        00055 - 00055
OTHFAM         00056 - 00056
FRIENDS        00057 - 00057
OTHERS         00058 - 00058
SACT1          00059 - 00060
SACT2          00061 - 00062
SACT3          00063 - 00064
SACT1DUR       00065 - 00068
SACT2DUR       00069 - 00072
SACT3DUR       00073 - 00076.
EXECUTE.
VARIABLE LABELS
RECID        "Record identification."
EPINO        "Sequential episode number."
WGHT_EPI     "Episode weight."
DDAY         "Designated day of interview."
TOTEPISO     "Total number of episodes during the reference day."
ACTCODE      "Activity code of the episode."
STARTIME     "Start time of the episode."
ENDTIME      "End time of the episode."
STARTMIN     "Start time of the episode in minutes."
ENDMIN       "End time of the episode in minutes."
DURATION     "Duration (in minutes) of the episode."
PLACE        "Location of the episode."
ALONE        "Social contacts - alone?"
SPOUSE       "Social contacts - with spouse/partner?"
CHILDHSD     "Social contacts - with children of the household less than 1"
PARHSD       "Social contacts - with parent(s) or parent(s) in-law living"
MEMBHSD      "Social contacts - with other member(s) of the household (inc"
NHSDCL15     "Social contacts - with child(ren) of the respondent living o"
NHSDC15P     "Social contacts - with child(ren) of the respondent living o"
NHSDPAR      "Social contacts - with parent(s) or parent(s) in-law living"
OTHFAM       "Social contacts - with other family member(s) living outside"
FRIENDS      "Social contacts - with friends living outside the household?"
OTHERS       "Social contacts - with others living outside the household?"
SACT1        "First Simultaneous Activity code."
SACT2        "Second Simultaneous Activity code."
SACT3        "Third Simultaneous Activity code."
SACT1DUR     "Duration (in minutes) of the first simultaneous activity."
SACT2DUR     "Duration (in minutes) of the second simultaneous activity."
SACT3DUR     "Duration (in minutes) of the third simultaneous activity.".
EXECUTE.
VALUE LABELS
/DDAY
                           1 "Sunday"
                           2 "Monday"
                           3 "Tuesday"
                           4 "Wednesday"
                           5 "Thursday"
                           6 "Friday"
                           7 "Saturday"
/PLACE
                           01 "Respondent's home"
                           02 "Work place"
                           03 "Someone else's home"
                           04 "Restaurant/bar"
                           05 "Place of worship"
                           06 "Grocery store"
                           07 "Other store/Mall"
                           08 "School"
                           09 "Outdoors away from home"
                           10 "Library"
                           11 "Other place"
                           12 "Car (driver)"
                           13 "Car (passenger)"
                           14 "Walk"
                           15 "Bus (includes street cars)"
                           16 "Subway/Train (includes commuter trains)"
                           17 "Bicycle"
                           18 "Boat/Ferry"
                           19 "Taxi/Limousine Service"
                           20 "Airplane"
                           21 "Other"
                           97 "Not stated for refused information"
                           98 "Not stated"
                           99 "Don't know"
/ALONE
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.0"
                           8 "Not stated"
                           9 "Personal activity"
/SPOUSE
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/CHILDHSD
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/PARHSD
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/MEMBHSD
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/NHSDCL15
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/NHSDC15P
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/NHSDPAR
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/OTHFAM
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/FRIENDS
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/OTHERS
                           1 "Yes"
                           2 "No"
                           7 "Not asked for activity code 002.2"
                           8 "Not stated"
                           9 "Personal activity"
/SACT1
                           11 "Talking, conversation (not on phone)"
                           12 "Radio listening"
                           13 "Watching television, rented movies"
                           14 "Eating and drinking"
                           15 "Domestic work (meal prep and cleanup, cleaning, laundry)"
                           16 "Reading (books, newspapers)"
                           17 "Childcare"
                           18 "Listening to MP3 players, CD's, cassette tapes or records"
                           19 "Talking on the phone"
                           20 "Computer use (excluding email, chat groups, social networkin"
                           21 "E-mail, chat groups, social networking"
                           22 "Sending or receiving text messages"
                           23 "Adult care"
                           24 "Work and school-related activities"
                           25 "Other"
                           26 "Pet care / interaction"
                           27 "Personal care personal activities"
                           28 "Games, cards, puzzles"
                           29 "Relaxing, thinking, resting, smoking"
                           30 "Household management / organization"
                           31 "Errands"
                           32 "Physical exercise / Outdoor Excursions"
                           33 "Sleeping"
                           34 "Praying, meditation, bible reading"
                           35 "Hobbies and home craft"
                           36 "Socializing"
                           96 "No simultaneous activity reported"
                           97 "Not asked"
                           98 "Not stated"
                           99 "Don't know"
/SACT2
                           11 "Talking, conversation (not on phone)"
                           12 "Radio listening"
                           13 "Watching television, rented movies"
                           14 "Eating and drinking"
                           15 "Domestic work (meal prep and cleanup, cleaning, laundry)"
                           16 "Reading (books, newspapers)"
                           17 "Childcare"
                           18 "Listening to MP3 players, CD's, cassette tapes or records"
                           19 "Talking on the phone"
                           20 "Computer use (excluding email, chat groups, social networkin"
                           21 "E-mail, chat groups, social networking"
                           22 "Sending or receiving text messages"
                           23 "Adult care"
                           24 "Work and school-related activities"
                           25 "Other"
                           26 "Pet care / interaction"
                           27 "Personal care personal activities"
                           28 "Games, cards, puzzles"
                           29 "Relaxing, thinking, resting, smoking"
                           30 "Household management / organization"
                           31 "Errands"
                           32 "Physical exercise / Outdoor Excursions"
                           33 "Sleeping"
                           34 "Praying, meditation, bible reading"
                           35 "Hobbies and home craft"
                           36 "Socializing"
                           96 "No simultaneous activity reported"
                           97 "Not asked"
                           98 "Not stated"
                           99 "Don't know"
/SACT3
                           11 "Talking, conversation (not on phone)"
                           12 "Radio listening"
                           13 "Watching television, rented movies"
                           14 "Eating and drinking"
                           15 "Domestic work (meal prep and cleanup, cleaning, laundry)"
                           16 "Reading (books, newspapers)"
                           17 "Childcare"
                           18 "Listening to MP3 players, CD's, cassette tapes or records"
                           19 "Talking on the phone"
                           20 "Computer use (excluding email, chat groups, social networkin"
                           21 "E-mail, chat groups, social networking"
                           22 "Sending or receiving text messages"
                           23 "Adult care"
                           24 "Work and school-related activities"
                           25 "Other"
                           26 "Pet care / interaction"
                           27 "Personal care personal activities"
                           28 "Games, cards, puzzles"
                           29 "Relaxing, thinking, resting, smoking"
                           30 "Household management / organization"
                           31 "Errands"
                           32 "Physical exercise / Outdoor Excursions"
                           33 "Sleeping"
                           34 "Praying, meditation, bible reading"
                           35 "Hobbies and home craft"
                           36 "Socializing"
                           96 "No simultaneous activity reported"
                           97 "Not asked"
                           98 "Not stated"
                           99 "Don't know"
/SACT1DUR
                           9997 "Not asked"
                           9998 "Not stated"
                           9999 "Don't know"
/SACT2DUR
                           9997 "Not asked"
                           9998 "Not stated"
                           9999 "Don't know"
/SACT3DUR
                           9997 "Not asked"
                           9998 "Not stated"
                           9999 "Don't know" .
EXECUTE.
