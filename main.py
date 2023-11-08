import pandas as pd


def main(data):

    regents_df = pd.read_csv('data/1_15.csv')

    marks_df = pd.read_csv('data/1_30.csv')
    marks_cols = ['Mark','PassFailEquivalent']
    marks_df = marks_df[marks_cols]

    regents_df = regents_df.merge(
        marks_df,
        on=['Mark'],how='left'
    )

        ## Attach Counselors 
    counselors_df = pd.read_csv('data/1_49.csv')
    counselors_df = counselors_df[['StudentID','Counselor']]

    regents_df = regents_df.merge( 
        counselors_df,
        on='StudentID', how='left',
    )

    regents_df['exam_title'] = regents_df['Course'].apply(convert_exam_to_title)
    regents_df['exam_curriculum'] = regents_df['Course'].apply(convert_exam_to_curriculum)

    regents_df['exam_administration_waiver_possible'] = regents_df.apply(exam_administration_waiver_possible, axis=1)
    regents_df['exam_score_waiver_possible'] = regents_df['Mark'].apply(exam_score_waiver_possible)

    possible_waivers = []
    for (student, exam_title), exams_df in regents_df.groupby(['StudentID','exam_title']):
        if 'P' in exams_df['PassFailEquivalent'].to_list():
            pass
        else:
            possible_waiver_exam = exams_df[exams_df['exam_administration_waiver_possible'] & exams_df['exam_score_waiver_possible']]
            if len(possible_waiver_exam) > 0:
                possible_waivers.append(possible_waiver_exam)

    possible_waivers_df = pd.concat(possible_waivers)

    ## process transcript
    transcript_df = pd.read_csv('data/1_14.csv')

    transcript_df = transcript_df.merge( 
        marks_df, 
        on='Mark', how='left'
    )
    transcript_df['exam_curriculum'] = transcript_df['Course'].apply(lambda x: x[0:2])
    
    credits_earned_per_curriculum = pd.pivot_table(
        transcript_df[transcript_df['PassFailEquivalent'] == 'P'],
        index=['StudentID','exam_curriculum'],
        
        values='Credits',
        aggfunc='sum',
    ).fillna(0).reset_index()

    possible_waivers_df = possible_waivers_df.merge(
        credits_earned_per_curriculum, 
        on=['StudentID','exam_curriculum'], how='left'
    ).fillna(0)

    possible_waivers_df['credit_requirement_waiver_possible'] = possible_waivers_df.apply(credit_requirement_waiver_possible, axis=1)

    eligible_waivers_df = possible_waivers_df[
        possible_waivers_df['exam_administration_waiver_possible'] & possible_waivers_df['exam_score_waiver_possible'] & possible_waivers_df['credit_requirement_waiver_possible']  
    ]
    sort_cols = ['LastName','FirstName','exam_title','Year','Term']
    drop_dups_subset = ['StudentID','exam_title']
    eligible_waivers_df = eligible_waivers_df.sort_values(by=sort_cols)
    eligible_waivers_df = eligible_waivers_df.drop_duplicates(subset=drop_dups_subset, keep='first')

    output_cols = [
        'StudentID', 
        'LastName', 
        'FirstName', 
        'Year', 
        'Term', 
        'Course',
        'Mark', 
        'exam_title',
        'Credits',
        ]
    eligible_waivers_df = eligible_waivers_df[output_cols].sort_values(by=['exam_title'])



    output_filename = 'output/RegentsWaivers.xlsx'
    writer = pd.ExcelWriter(output_filename)

    eligible_waivers_df.to_excel(writer, index=False)

    writer.close()

    print(eligible_waivers_df)
    return True

def exam_administration_waiver_possible(exam_row):
    year = exam_row['Year']
    semester = exam_row['Term']

    if year == 2021 and semester in [2,7]:
        return True
    if year == 2022 and semester in [1,2,7]:
        return True
    else:
        return False
def exam_score_waiver_possible(mark):
    try:
        return int(mark) >= 50 and int(mark) <65
    except:
        return False

def convert_exam_to_title(course):
    exam_to_title_dict = {
             'EXRC' : 'ENG REG',
             'HXRC' : 'GLOBAL REG',
             'HXRK' : 'US HIST REG',
             'MXRC' : 'ALGEBRA REG',
             'MXRK' : 'GEOMETRY REG',
             'MXRN' : 'ALG2/TRIG REG',
             'SXRK' : 'LIVING ENV REG',
             'SXRU' : 'EARTH SCI  REG',
             'SXRX' : 'CHEMISTRY REG',
             'SXRP' : 'PHYSICS REG',
             }
    corrected_course = course[0:2] + 'R' + course[3]
    return exam_to_title_dict.get(corrected_course)

def convert_exam_to_curriculum(course):
    exam_to_title_dict = {
             'EXRC' : 'EE',
             'HXRC' : 'HG',
             'HXRK' : 'HU',
             'MXRC' : 'ME',
             'MXRK' : 'MG',
             'MXRN' : 'MR',
             'SXRK' : 'SL',
             'SXRU' : 'SE',
             'SXRX' : 'SC',
             'SXRP' : 'SP',
             }
    corrected_course = course[0:2] + 'R' + course[3]
    return exam_to_title_dict.get(corrected_course)

def credit_requirement_waiver_possible(row):
    credits = row['Credits']
    exam_curriculum = row['exam_curriculum']
    if exam_curriculum == 'EE':
        return credits >= 5
    if exam_curriculum == 'HG':
        return credits >= 4
    
    return credits >= 2

if __name__ == "__main__":
    data = {
    }
    main(data)
