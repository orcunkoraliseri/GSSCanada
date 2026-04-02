* Encoding: windows-1252.
/* The following line should contain the complete path and name of your raw data file */
/* The last line of this file contains the path to your output '.sav' file */

FILE HANDLE DATA / NAME=".\data_donnees_2016_hier.dat" LRECL=489 .

DATA LIST FILE=DATA/
   HH_ID 1-6                EF_ID 7-13               CF_ID 14-21           
   PP_ID 22-31              WEIGHT 32-47             WT1 48-63            
   WT2 64-79                WT3 80-95                WT4 96-111           
   WT5 112-127              WT6 128-143              WT7 144-159          
   WT8 160-175              WT9 176-191              WT10 192-207          
   WT11 208-223             WT12 224-239             WT13 240-255          
   WT14 256-271             WT15 272-287             WT16 288-303          
   ABOID 304                AGEGRP 305-306           AGEIMM 307-308        
   ATTSCH 309               BEDRM 310                BFNMEMB 311           
   BUILT 312-313            CF_RP 314                CFSTAT 315-316        
   CFSTRUCT 317             CIP2011 318-319          CITIZEN 320           
   CITOTH 321               CMA 322-324              CONDO 325             
   COW 326                  DIST 327                 DTYPE 328             
   DUR 329                  EF_RP 330                EFDECILE 331-332      
   EFDIMBM 333-340          EMPIN 341-348            ETHDER 349-350        
   FCOND 351-358            FOL 359                  FPTWK 360             
   GENSTAT 361              GTRFS 362-369            HDGREE 370-371        
   HHMAINP 372              HLAEN 373                HLAFR 374             
   HLANO 375-376            HLBEN 377                HLBFR 378             
   HLBNO 379                HRSWRK 380-381           IMMSTAT 382           
   INCTAX 383-390           KOL 391                  LEAVE 392             
   LFTAG 393-394            LOC_ST_RES 395           LOCSTUD 396-397       
   LOLICOA 398              LOLICOB 399              LOLIMA 400            
   LOLIMB 401               LOMBM 402                LSTWRK 403            
   LWAEN 404                LWAFR 405                LWANO 406             
   LWBEN 407                LWBFR 408                LWBNO 409             
   MarStH 410               Mob1 411                 Mob5 412              
   MODE 413                 MRKINC 414-421           MTNEn 422             
   MTNFr 423                MTNNO 424-425            NAICS 426-427         
   NOCS 428-429             NOL 430-431              NOS 432               
   OCC 433                  POB 434                  POBF 435              
   POBM 436                 POWST 437                PR 438-439            
   PR1 440-441              PR5 442-443              PRESMORTG 444         
   PRIHM 445                PWPR 446-447             REGIND 448            
   REPAIR 449               ROOM 450-451             SEX 452               
   SHELCO 453-456           SSGRAD 457-458           SUBSIDY 459           
   TENUR 460                TOTINC 461-468           TOTINC_AT 469-476     
   VALUE 477-484            VISMIN 485               WKSWRK 486            
   WRKACT 487-488           YRIMM 489 .           


FORMATS
  WEIGHT (F17.13) /        WT1 (F17.11) /           WT2 (F17.11) /        
  WT3 (F17.11) /           WT4 (F17.11) /           WT5 (F17.11) /        
  WT6 (F17.11) /           WT7 (F17.11) /           WT8 (F17.11) /        
  WT09 (F17.11) /          WT10 (F17.11) /          WT11 (F17.11) /        
  WT12 (F17.11) /          WT13 (F17.11) /          WT14 (F17.11) /        
  WT15 (F17.11) /          WT16 (F17.11) / .
    
VARIABLE LABELS
ABOID "Aboriginal: Aboriginal identity – Detailed"                                                                                                                                                      
AGEGRP "Age"                                                                                                                                                                                            
AGEIMM "Immigration: Age at Immigration"                                                                                                                                                                
ATTSCH "Education: School attendance"                                                                                                                                                                   
BEDRM "Bedrooms"                                                                                                                                                                                        
BFNMEMB "Aboriginal: Membership in a First Nation or Indian band"                                                                                                                                       
BUILT "Period of construction"                                                                                                                                                                          
CFSTAT "Household living arrangements of person, simple version"                                                                                                                                        
CFSTRUCT "Census family structure, simple version"                                                                                                                                                      
CF_ID "Key for census family table"
CF_RP "Census family reference person"                                                                                                                                                                  
CIP2011 "Education: Major field of study, primary groupings (based on CIP Canada 2016)"                                                                                                                 
CITIZEN "Citizenship: Citizenship status and type – Summary"                                                                                                                                            
CITOTH "Citizenship: Other country of citizenship"                                                                                                                                                      
CMA "Census metropolitan area or census agglomeration of current residence (2016)"                                                                                                                      
CONDO "Condominium status"                                                                                                                                                                              
COW "Labour: Class of worker (derived)"                                                                                                                                                                 
DIST "POW: Distance from home to work capped maximum of 201 kilometres"                                                                                                                                 
DTYPE "Structural type of dwelling"                                                                                                                                                                     
DUR "JTW: Commuting duration"                                                                                                                                                                           
EFDECILE "Income: National economic family after-tax income decile for all persons"                                                                                                                     
EFDIMBM "Income: Disposable income for MBM of economic family for all persons"                                                                                                                          
EF_ID "Key for economic family table"
EF_RP "Economic family reference person"                                                                                                                                                                
EMPIN "Income: Employment income"                                                                                                                                                                       
ETHDER "Ethnic origin: Derived single and multiple ethnic origins"                                                                                                                                      
FCOND "Condominium fees"                                                                                                                                                                                
FOL "Language: First official language spoken"                                                                                                                                                          
FPTWK "Labour: Full-time or part-time weeks worked in 2015"                                                                                                                                             
GENSTAT "Generation status: Detailed"                                                                                                                                                                   
GTRFS "Income: Government transfers"                                                                                                                                                                    
HDGREE "Education: Highest certificate, diploma or degree"                                                                                                                                              
HH_ID "Key for household table"
HHMAINP "Person responsible for household payments"                                                                                                                                                     
HLAEN "Language: Home language (part A) – English component"                                                                                                                                            
HLAFR "Language: Home language (part A) – French component"                                                                                                                                             
HLANO "Language: Home language (part A) – First write-in component"                                                                                                                                     
HLBEN "Language: Home language (part B) – English component"                                                                                                                                            
HLBFR "Language: Home language (part B) – French component"                                                                                                                                             
HLBNO "Language: Home language (part B) – First write-in component"                                                                                                                                     
HRSWRK "Labour: Hours worked for pay or in self-employment"                                                                                                                                             
IMMSTAT "Immigration: Immigrant status"                                                                                                                                                                 
INCTAX "Income: Income taxes"                                                                                                                                                                           
KOL "Language: Knowledge of official languages"                                                                                                                                                         
LEAVE "JTW: Time leaving for work"                                                                                                                                                                      
LFTAG "Labour: Labour force status"                                                                                                                                                                     
LOCSTUD "Education: Location of study"                                                                                                                                                                  
LOC_ST_RES "Education: Location of study compared with province or territory of residence"                                                                                                              
LOLICOA "Income: Low income status based on LICO-AT"                                                                                                                                                    
LOLICOB "Income: Low income status based on LICO-BT"                                                                                                                                                    
LOLIMA "Income: Low-income status based on LIM-AT"                                                                                                                                                      
LOLIMB "Income: Low-income status based on LIM-BT"                                                                                                                                                      
LOMBM "Income: Low-income status based on MBM"                                                                                                                                                          
LSTWRK "Labour: When last worked for pay or in self-employment"                                                                                                                                         
LWAEN "Language: Language of work (part A) – English component"                                                                                                                                         
LWAFR "Language: Language of work (part A) – French component"                                                                                                                                          
LWANO "Language: Language used at work (part A) – First write-in component"                                                                                                                             
LWBEN "Language: Language of work (part B) – English component"                                                                                                                                         
LWBFR "Language: Language of work (part B) – French component"                                                                                                                                          
LWBNO "Language: Language used at work (part B) – First write-in component"                                                                                                                             
MARSTH "Marital status (de facto)"                                                                                                                                                                      
MOB1 "Mobility 1: Mobility Status – Place of residence 1 year ago (2015)"                                                                                                                               
MOB5 "Mobility 5: Mobility Status – Place of residence 5 years ago (2011)"                                                                                                                              
MODE "JTW: Main mode of commuting"                                                                                                                                                                      
MRKINC "Income: Market income"                                                                                                                                                                          
MTNEN "Language: Mother tongue – English component"                                                                                                                                                     
MTNFR "Language: Mother tongue – French component"                                                                                                                                                      
MTNNO "Language: Mother Tongue – First write-in component"                                                                                                                                              
NAICS "Labour: Industry sectors (based on the NAICS 2012)"                                                                                                                                              
NOCS "Labour: Occupation broad categories (based on the NOC 2016)"                                                                                                                                      
NOL "Language: Knowledge of non-official languages – First write-in component"                                                                                                                          
NOS "Housing suitability"                                                                                                                                                                               
OCC "JTW: Commuting vehicle occupancy"                                                                                                                                                                  
POB "Place of birth of person: Detailed"                                                                                                                                                                
POBF "Place of birth of father: Detailed"                                                                                                                                                               
POBM "Place of birth of mother: Detailed"                                                                                                                                                               
POWST "POW: Place of work status"                                                                                                                                                                       
PP_ID "Key for person table"
PR "Province or territory of current residence (2016)"                                                                                                                                                  
PR1 "Mobility 1: Province or territory of residence 1 year ago (2015)"                                                                                                                                  
PR5 "Mobility 5: Province or territory of residence 5 years ago (2011)"                                                                                                                                 
PRESMORTG "Mortgage, presence of"                                                                                                                                                                       
PRIHM "Primary household maintainer"                                                                                                                                                                    
PWPR "POW: Place of work province"                                                                                                                                                                      
REGIND "Aboriginal: Registered or Treaty Indian status"                                                                                                                                                 
REPAIR "Dwelling condition"                                                                                                                                                                             
ROOM "Rooms"                                                                                                                                                                                            
SEX "Sex"                                                                                                                                                                                               
SHELCO "Shelter cost"                                                                                                                                                                                   
SSGRAD "Education: Secondary (high) school diploma or equivalency certificate"                                                                                                                          
SUBSIDY "Subsidized housing"                                                                                                                                                                            
TENUR "Tenure"                                                                                                                                                                                          
TOTINC "Income: Total income"                                                                                                                                                                           
TOTINC_AT "Income: After-tax income"                                                                                                                                                                    
VALUE "Value (owner estimated)"                                                                                                                                                                         
VISMIN "Visible minority: Visible minority indicator"                                                                                                                                                   
WEIGHT "Individuals weighting factor"                                                                                                                                                                   
WKSWRK "Labour: weeks worked in 2015, no zero value in statistics"                                                                                                                                      
WRKACT "Labour: Work Activity in 2015"                                                                                                                                                                  
WT1 "Replicate PUMF weight"                                                                                                                                                                            
WT2 "Replicate PUMF weight"                                                                                                                                                                            
WT3 "Replicate PUMF weight"                                                                                                                                                                            
WT4 "Replicate PUMF weight"                                                                                                                                                                            
WT5 "Replicate PUMF weight"                                                                                                                                                                            
WT6 "Replicate PUMF weight"                                                                                                                                                                            
WT7 "Replicate PUMF weight"                                                                                                                                                                            
WT8 "Replicate PUMF weight"                                                                                                                                                                            
WT9 "Replicate PUMF weight"                                                                                                                                                                            
WT10 "Replicate PUMF weight"                                                                                                                                                                            
WT11 "Replicate PUMF weight"                                                                                                                                                                            
WT12 "Replicate PUMF weight"                                                                                                                                                                            
WT13 "Replicate PUMF weight"                                                                                                                                                                            
WT14 "Replicate PUMF weight"                                                                                                                                                                            
WT15 "Replicate PUMF weight"                                                                                                                                                                            
WT16 "Replicate PUMF weight"                                                                                                                                                                            
YRIMM "Immigration: Year of immigration"                                                                                                                                                                
.
VALUE LABELS
ABOID
 1 "First Nations (North American Indian)"
 2 "Métis"
 3 "Inuk (Inuit)"
 4 "Multiple Aboriginal responses"
 5 "Aboriginal responses not included elsewhere"
 6 "Non-Aboriginal identity"
 8 "Not available"
/
AGEGRP
 1 "0 to 9 years"
 2 "10 to 14 years"
 3 "15 to 19 years"
 4 "20 to 24 years"
 5 "25 to 29 years"
 6 "30 to 34 years"
 7 "35 to 39 years"
 8 "40 to 44 years"
 9 "45 to 49 years"
 10 "50 to 54 years"
 11 "55 to 64 years"
 12 "65 to 74 years"
 13 "75 years and over"
 88 "Not available"
/
AGEIMM
 1 "0 to 4 years"
 2 "5 to 9 years"
 3 "10 to 14 years"
 4 "15 to 19 years"
 5 "20 to 24 years"
 6 "25 to 29 years"
 7 "30 to 34 years"
 8 "35 to 39 years"
 9 "40 to 44 years"
 10 "45 to 49 years"
 11 "50 to 54 years"
 12 "55 to 59 years"
 13 "60 years and over"
 88 "Not available"
 99 "Not applicable"
/
ATTSCH
 1 "Did not attend school"
 2 "Attended school"
 9 "Not applicable"
/
BEDRM
 0 "No bedrooms"
 1 "1 bedroom"
 2 "2 bedrooms"
 3 "3 bedrooms"
 4 "4 bedrooms"
 5 "5 bedrooms or more"
 8 "Not available"
/
BFNMEMB
 1 "Not a member of a First Nation or Indian band"
 2 "Member of a First Nation or Indian band"
 8 "Not available"
/
BUILT
 1 "1920 or before"
 2 "1921 to 1945"
 3 "1946 to 1960"
 4 "1961 to 1970"
 5 "1971 to 1980"
 6 "1981 to 1990"
 7 "1991 to 1995"
 8 "1996 to 2000"
 9 "2001 to 2005"
 10 "2006 to 2010"
 11 "2011 to 2016"
 88 "Not available"
/
CF_RP
 1 "Census family reference person"
 2 "Other census family member"
 3 "Person not in a census family"
/
CFSTAT
 1 "Married spouse or common-law partner without children"
 2 "Married spouse or common-law partner with children"
 3 "Lone parent"
 4 "Child of a couple"
 5 "Child of a lone parent"
 6 "Person living alone"
 7 "Person living with non-relatives only"
 8 "Person not in a census family but living with other relatives"
 88 "Not available"
/
CFSTRUCT
 1 "Couple without children"
 2 "Couple with children"
 3 "Lone-parent family"
 8 "Not available"
 9 "Not applicable"
/
CIP2011
 1 "01 Education"
 2 "02 Visual and performing arts, and communications technologies"
 3 "03 Humanities"
 4 "04 Social and behavioural sciences and law"
 5 "05 Business, management and public administration"
 6 "06 Physical and life sciences and technologies"
 7 "07 Mathematics, computer and information sciences"
 8 "08 Architecture, engineering, and related technologies"
 9 "09 Agriculture, natural resources and conservation"
 10 "10 Health and related fields"
 11 "11 Personal, protective and transportation services"
 13 "No postsecondary certificate, diploma or degree"
 88 "Not available"
 99 "Not applicable"
/
CITIZEN
 1 "Canadian citizens by birth"
 2 "Canadian citizens by naturalization"
 3 "Not Canadian citizens"
 8 "Not available"
/
CITOTH
 1 "United States"
 2 "Europe"
 3 "Asia"
 4 "Other single and multiple citizenships other than Canadian"
 5 "No other country of citizenship"
 8 "Not available"
/
CMA
 462 "Montréal"
 535 "Toronto"
 825 "Calgary"
 835 "Edmonton"
 933 "Vancouver"
 999 "Other census metropolitan areas, Census Agglomerations and other geographies"
/
CONDO
 0 "Not condominium"
 1 "Condominium"
 8 "Not available"
/
COW
 1 "Employee"
 2 "Self-employed, without paid help (incorporated and unincorporated)"
 3 "Self-employed, with paid help (incorporated and unincorporated)"
 4 "Unpaid family worker"
 8 "Not available"
 9 "Not applicable"
/
DIST
 1 "Less than 5 km"
 2 "5 to 9.9 km"
 3 "10 to 14.9 km"
 4 "15 to 19.9 km"
 5 "20 to 24.9 km"
 6 "25 to 29.9 km"
 7 "Greater or equal to 30 km"
 8 "Not available"
 9 "Not applicable"
/
DTYPE
 1 "Single-detached house"
 2 "Apartment"
 3 "Other dwelling"
 8 "Not available"
/
DUR
 1 "Less than 15 minutes"
 2 "15 to 29 minutes"
 3 "30 to 44 minutes"
 4 "45 to 59 minutes"
 5 "60 minutes and over"
 8 "Not available"
 9 "Not applicable"
/
EF_RP
 1 "Economic family reference person"
 2 "Economic family member other than the reference person"
 3 "Person not in an economic family"
/
EFDECILE
 1 "In bottom decile"
 2 "In second decile"
 3 "In third decile"
 4 "In fourth decile"
 5 "In fifth decile"
 6 "In sixth decile"
 7 "In seventh decile"
 8 "In eighth decile"
 9 "In ninth decile"
 10 "In top decile"
 88 "Not available"
/
ETHDER
 1 "British Isles origins"
 2 "French origins"
 3 "North American Aboriginal origins"
 4 "Other North American origins"
 5 "European origins (excluding British Isles and French origins)"
 6 "Asian origins"
 7 "Other single origins"
 8 "Multiple origins"
 88 "Not available"
/
FOL
 1 "English"
 2 "French"
 3 "English and French"
 4 "Neither English nor French"
 8 "Not available"
/
FPTWK
 1 "Worked mainly full-time weeks in 2015"
 2 "Worked mainly part-time weeks in 2015"
 9 "Not applicable"
/
GENSTAT
 1 "First generation, respondent born outside Canada"
 2 "Second generation, respondent born in Canada, both parents born outside Canada"
 3 "Second generation, respondent born in Canada, one parent born outside Canada and one parent born in Canada"
 4 "Third generation or more, respondent born in Canada, both parents born in Canada"
 8 "Not available"
/
HDGREE
 1 "No certificate, diploma or degree"
 2 "Secondary (high) school diploma or equivalency certificate"
 3 "Trades certificate or diploma other than Certificate of Apprenticeship or Certificate of Qualification"
 4 "Certificate of Apprenticeship or Certificate of Qualification"
 5 "College, CEGEP or other non-university certificate or diploma"
 6 "University certificate or diploma below bachelor level"
 7 "Bachelor's degree"
 8 "University certificate, diploma or degree above bachelor level"
 88 "Not available"
 99 "Not applicable"
/
HHMAINP
 0 "Person is not responsible for household payments"
 1 "Person is responsible for household payments"
/
HLAEN
 0 "False - Respondent did not report English as the language spoken most often at home"
 1 "True - Respondent reported English as the language spoken most often at home"
/
HLAFR
 0 "False - Respondent did not report French as the language spoken most often at home"
 1 "True - Respondent reported French as the language spoken most often at home"
/
HLANO
 1 "No non-official language"
 2 "Chinese languages"
 3 "Spanish"
 4 "Italian"
 5 "German"
 6 "Arabic"
 7 "Punjabi (Panjabi)"
 8 "Tagalog (Pilipino, Filipino)"
 9 "Portuguese"
 10 "All other single languages"
 88 "Not available"
/
HLBEN
 0 "False - Respondent did not report English as the language spoken at home on a regular basis"
 1 "True - Respondent reported English as the language spoken at home on a regular basis"
/
HLBFR
 0 "False - Respondent did not report French as the language spoken at home on a regular basis"
 1 "True - Respondent reported French as the language spoken at home on a regular basis"
/
HLBNO
 0 "False - Respondent did not report a non-official language as the language spoken at home on a regular basis"
 1 "True - Respondent reported a non-official language as the language spoken at home on a regular basis"
/
HRSWRK
 0 "No hours of work"
 1 "1 to 9 hours of work"
 2 "10 to 19 hours of work"
 3 "20 to 29 hours of work"
 4 "30 to 37 hours of work"
 5 "38 to 40 hours of work"
 6 "41 to 49 hours of work"
 7 "50 to 59 hours of work"
 8 "60 to 69 hours of work"
 9 "70 to 79 hours of work"
 10 "80 hours or more of work"
 99 "Not applicable"
/
IMMSTAT
 1 "Non-immigrants"
 2 "Immigrants"
 3 "Non-permanent residents"
 8 "Not available"
/
KOL
 1 "English only"
 2 "French only"
 3 "English and French"
 4 "Neither English nor French"
 8 "Not available"
/
LEAVE
 1 "Between 5 and 5:59 a.m."
 2 "Between 6 and 6:59 a.m."
 3 "Between 7 and 7:59 a.m."
 4 "Between 8 and 8:59 a.m."
 5 "Between 9 and 3:59 p.m."
 6 "Between 4 p.m. and 4:59 a.m."
 9 "Not applicable"
/
LFTAG
 1 "Employed - Worked in reference week"
 2 "Employed - Absent in reference week"
 3 "Unemployed - Temporary layoff - Did not look for work"
 4 "Unemployed - Temporary layoff - Looked for full-time work"
 5 "Unemployed - Temporary layoff - Looked for part-time work"
 6 "Unemployed - New job - Did not look for work"
 7 "Unemployed - New job - Looked for full-time work"
 8 "Unemployed - New job - Looked for part-time work"
 9 "Unemployed - Looked for full-time work"
 10 "Unemployed - Looked for part-time work"
 11 "Not in the labour force - Last worked in 2016"
 12 "Not in the labour force - Last worked in 2015"
 13 "Not in the labour force - Last worked before 2015"
 14 "Not in the labour force - Never worked"
 99 "Not applicable"
/
LOC_ST_RES
 1 "Same as province or territory of residence"
 2 "Different than province or territory of residence"
 3 "Outside Canada"
 8 "Not available"
 9 "Not applicable"
/
LOCSTUD
 1 "Atlantic"
 2 "Quebec"
 3 "Ontario"
 4 "Prairies"
 5 "British Columbia"
 6 "Territories"
 7 "United States"
 8 "Other Americas"
 9 "Europe"
 10 "Eastern Asia"
 11 "Southeast and Southern Asia"
 12 "Other countries and regions"
 88 "Not available"
 99 "Not applicable"
/
LOLICOA
 1 "Not in low income"
 2 "In low income"
 8 "Not available"
 9 "Concept not applicable"
/
LOLICOB
 1 "Not in low income"
 2 "In low income"
 8 "Not available"
 9 "Concept not applicable"
/
LOLIMA
 1 "Not in low income"
 2 "In low income"
 8 "Not available"
 9 "Concept not applicable"
/
LOLIMB
 1 "Not in low income"
 2 "In low income"
 8 "Not available"
 9 "Concept not applicable"
/
LOMBM
 1 "Not in low income"
 2 "In low income"
 8 "Not available"
 9 "Concept not applicable"
/
LSTWRK
 1 "Last worked before 2015"
 2 "Last worked in 2015"
 3 "Last worked in 2016"
 4 "Never worked"
 9 "Not applicable"
/
LWAEN
 0 "False - Respondent did not report English as the language used most often at work"
 1 "True - Respondent reported English as the language used most often at work"
 9 "Not applicable"
/
LWAFR
 0 "False - Respondent did not report French as the language used most often at work"
 1 "True - Respondent reported French as the language used most often at work"
 9 "Not applicable"
/
LWANO
 0 "False - Respondent did not report a non-official language as the language used most often at work"
 1 "True - Respondent reported a non-official language as the language used most often at work"
 9 "Not applicable"
/
LWBEN
 0 "False - Respondent did not report English as the language used on a regular basis at work"
 1 "True - Respondent reported English as the language used on a regular basis at work"
 9 "Not applicable"
/
LWBFR
 0 "False - Respondent did not report French as the language used on a regular basis at work"
 1 "True - Respondent reported French as the language used on a regular basis at work"
 9 "Not applicable"
/
LWBNO
 0 "False - Respondent did not report a non-official language as the language used on a regular basis at work"
 1 "True - Respondent reported a non-official language as the language used on a regular basis at work"
 9 "Not applicable"
/
MARSTH
 1 "Never legally married (and not living common law)"
 2 "Legally married (and not separated)"
 3 "Living common law"
 4 "Separated, divorced or widowed  (and not living common law)"
 8 "Not available"
/
Mob1
 1 "Non-movers"
 2 "Non-migrants"
 3 "Different CSD, same census division"
 4 "Different CD, same province"
 5 "Interprovincial migrants"
 6 "External migrants"
 8 "Not available"
 9 "Not applicable"
/
Mob5
 1 "Non-movers"
 2 "Non-migrants"
 3 "Different CSD, same census division"
 4 "Different CD, same province"
 5 "Interprovincial migrants"
 6 "External migrants"
 9 "Not applicable"
/
MODE
 1 "Bicycle"
 2 "Car, truck, van as driver"
 3 "Motorcycle, scooter or moped"
 4 "Other method"
 5 "Car, truck, van as passenger"
 6 "Public transit"
 7 "Walked"
 9 "Not applicable"
/
MTNEn
 0 "False - Respondent did not report English as mother tongue"
 1 "True - Respondent reported English as mother tongue"
/
MTNFr
 0 "False - Respondent did not report French as mother tongue"
 1 "True - Respondent reported French as mother tongue"
/
MTNNO
 1 "No non-official language"
 2 "Chinese languages"
 3 "Spanish"
 4 "Italian"
 5 "German"
 6 "Arabic"
 7 "Punjabi (Panjabi)"
 8 "Tagalog (Pilipino, Filipino)"
 9 "Portuguese"
 10 "All other single languages"
 88 "Not available"
/
NAICS
 1 "Agriculture and other resource based industries"
 2 "Construction"
 3 "Manufacturing"
 4 "Wholesale trade"
 5 "Retail trade"
 6 "Finance and real estate"
 7 "Health care and social assistance"
 8 "Educational services"
 9 "Business services"
 10 "Public Administration"
 11 "Other services"
 88 "Not available"
 99 "Not applicable"
/
NOCS
 1 "0 Management occupations"
 2 "1 Business, finance and administration occupations"
 3 "2 Natural and applied sciences and related occupations"
 4 "3 Health occupations"
 5 "4 Occupations in education, law and social, community and government services"
 6 "5 Occupations in art, culture, recreation and sport"
 7 "6 Sales and service occupations"
 8 "7 Trades, transport and equipment operators and related occupations"
 9 "8 Natural resources, agriculture and related production occupations"
 10 "9 Occupations in manufacturing and utilities"
 88 "Not available"
 99 "Not applicable"
/
NOL
 1 "No non-official language"
 2 "Chinese languages"
 3 "Spanish"
 4 "Italian"
 5 "German"
 6 "Arabic"
 7 "Punjabi (Panjabi)"
 8 "Tagalog (Pilipino, Filipino)"
 9 "Portuguese"
 10 "All other single languages"
 11 "Respondents with multiples non-official languages"
 88 "Not available"
/
NOS
 1 "Suitable"
 2 "Not suitable"
 8 "Not available"
/
OCC
 1 "Drove alone"
 2 "Two people shared the ride to work"
 3 "Three or more people shared the ride to work"
 9 "Not applicable"
/
POB
 1 "Canada"
 2 "United States"
 3 "Europe"
 4 "Asia"
 5 "Other"
 8 "Not available"
/
POBF
 1 "Canada"
 2 "United States"
 3 "Europe"
 4 "Asia"
 5 "Other"
 8 "Not available"
/
POBM
 1 "Canada"
 2 "United States"
 3 "Europe"
 4 "Asia"
 5 "Other"
 8 "Not available"
/
POWST
 1 "Worked at home"
 2 "No fixed workplace address"
 3 "Worked outside Canada"
 4 "Worked in census subdivision (municipality) of residence"
 5 "Worked in a different census subdivision (municipality) within the census division (county) of residence"
 6 "Worked in a different census division (county)"
 7 "Worked in a different province or territory"
 8 "Not available"
 9 "Not applicable"
/
PR
 10 "Newfoundland and Labrador"
 11 "Prince Edward Island"
 12 "Nova Scotia"
 13 "New Brunswick"
 24 "Quebec"
 35 "Ontario"
 46 "Manitoba"
 47 "Saskatchewan"
 48 "Alberta"
 59 "British Columbia"
 70 "Northern Canada"
/
PR1
 10 "Newfoundland and Labrador"
 11 "Prince Edward Island"
 12 "Nova Scotia"
 13 "New Brunswick"
 24 "Quebec"
 35 "Ontario"
 46 "Manitoba"
 47 "Saskatchewan"
 48 "Alberta"
 59 "British Columbia"
 70 "Northern Canada"
 88 "Not available"
 99 "Not applicable"
/
PR5
 10 "Newfoundland and Labrador"
 11 "Prince Edward Island"
 12 "Nova Scotia"
 13 "New Brunswick"
 24 "Quebec"
 35 "Ontario"
 46 "Manitoba"
 47 "Saskatchewan"
 48 "Alberta"
 59 "British Columbia"
 70 "Northern Canada"
 99 "Not applicable"
/
PRESMORTG
 1 "Without mortgage"
 2 "With mortgage"
 8 "Not available"
 9 "Not applicable"
/
PRIHM
 0 "Person is not primary household maintainer"
 1 "Person is primary household maintainer"
/
PWPR
 10 "Newfoundland and Labrador"
 11 "Prince Edward Island"
 12 "Nova Scotia"
 13 "New Brunswick"
 24 "Quebec"
 35 "Ontario"
 46 "Manitoba"
 47 "Saskatchewan"
 48 "Alberta"
 59 "British Columbia"
 70 "Northern Canada"
 88 "Not available"
 99 "Not applicable"
/
REGIND
 1 "Not a Registered or Treaty Indian"
 2 "Registered or Treaty Indian"
 8 "Not available"
/
REPAIR
 1 "Regular maintenance needed"
 2 "Minor repairs needed"
 3 "Major repairs needed"
/
ROOM
 1 "1 room"
 2 "2 rooms"
 3 "3 rooms"
 4 "4 rooms"
 5 "5 rooms"
 6 "6 rooms"
 7 "7 rooms"
 8 "8 rooms"
 9 "9 rooms"
 10 "10 rooms"
 11 "11 rooms or more"
 88 "Not available"
/
SEX
 1 "Female"
 2 "Male"
 8 "Not available"
/
SSGRAD
 1 "No high school diploma or equivalency certificate, no postsecondary certificate, diploma or degree"
 2 "No high school diploma or equivalency certificate, with apprenticeship or trades certificate or diploma"
 3 "No high school diploma or equivalency certificate, with college, CEGEP or other non-university certificate or diploma"
 4 "With high school diploma or equivalency certificate, no postsecondary certificate, diploma or degree"
 5 "With high school diploma or equivalency certificate, with apprenticeship or trades certificate or diploma"
 6 "With high school diploma or equivalency certificate, with college, CEGEP or other non-university certificate or diploma"
 7 "With high school diploma or equivalency certificate, with university certificate or diploma below bachelor level"
 8 "With high school diploma or equivalency certificate, with bachelor's degree"
 9 "With high school diploma or equivalency certificate, with university certificate, diploma or degree above bachelor level"
 88 "Not available"
 99 "Not applicable"
/
Subsidy
 0 "Not a subsidized dwelling"
 1 "A subsidized dwelling"
 8 "Not available"
 9 "Not applicable"
/
TENUR
 1 "Owned by a member of the household"
 2 "Rented or Band housing"
 8 "Not available"
/
VISMIN
 1 "Visible minority"
 2 "Not a visible minority"
 8 "Not available"
/
WKSWRK
 0 "None - worked in 2016 only"
 1 "1 to 9 weeks of work in 2015"
 2 "10 to 19 weeks of work in 2015"
 3 "20 to 29 weeks of work in 2015"
 4 "30 to 39 weeks of work in 2015"
 5 "40 to 48 weeks of work in 2015"
 6 "49 to 52 weeks of work in 2015"
 9 "Not applicable"
/
WRKACT
 1 "Worked before 2015 or never worked"
 2 "Worked in 2016 only"
 3 "Worked 1-13 weeks full time"
 4 "Worked 1-13 weeks part time"
 5 "Worked 14-26 weeks full time"
 6 "Worked 14-26 weeks part time"
 7 "Worked 27-39 weeks full time"
 8 "Worked 27-39 weeks part time"
 9 "Worked 40-48 weeks full time"
 10 "Worked 40-48 weeks part time"
 11 "Worked 49-52 weeks full time"
 12 "Worked 49-52 weeks part time"
 99 "Not applicable"
/
YRIMM
 1 "Before 1980"
 2 "1980 to 1990"
 3 "1991 to 2000"
 4 "2001 to 2005"
 5 "2006 to 2010"
 6 "2011 to 2016"
 8 "Not available"
 9 "Not applicable"
/
.
SAVE OUTFILE='.\data_donnees_2016_hier.sav'.
