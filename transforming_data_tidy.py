import pandas as pd

BOOK_OUTPUT_DF = pd.read_csv("ID-population-kec-by-book.csv")
BOOK_OUTPUT_DF['CODE'] = BOOK_OUTPUT_DF['CODE'].astype(str)

DISTRICT = BOOK_OUTPUT_DF[BOOK_OUTPUT_DF['CODE'].str.len() > 4].copy()

FOUR_DIGIT_CODE = BOOK_OUTPUT_DF[BOOK_OUTPUT_DF['CODE'].str.len() == 4].copy()

PROVINCE = FOUR_DIGIT_CODE[FOUR_DIGIT_CODE['CODE'].str.endswith('00')].copy()[['CODE', 'NAME']]
PROVINCE.columns = ['PROVINCIAL_CODE', 'PROVINCE']

REGIONS = FOUR_DIGIT_CODE[~FOUR_DIGIT_CODE['CODE'].str.endswith('00')].copy()[['CODE', 'NAME']]
REGIONS.columns = ['REGIONAL_CODE', 'REGION']

DISTRICT['PROVINCIAL_CODE'] = BOOK_OUTPUT_DF['CODE'].apply(lambda x: x[0:2] + '00')
DISTRICT['REGIONAL_CODE'] = BOOK_OUTPUT_DF['CODE'].apply(lambda x: x[0:4])

TIDY_DATA = DISTRICT.merge(
    REGIONS,
    on = 'REGIONAL_CODE'
).merge(
    PROVINCE,
    on = 'PROVINCIAL_CODE'
)

COLUMN_ARRANGEMENT = ['PROVINCIAL_CODE', 'PROVINCE',
                      'REGIONAL_CODE', 'REGION',
                      'CODE', 'NAME',
                      'MALE_POPULATION', 'FEMALE_POPULATION', 'TOTAL_POPULATION']

RENAME_DICT = {'CODE': 'DISTRICT_CODE',
               'NAME': 'DISTRICT'}

TIDY_DATA = TIDY_DATA[COLUMN_ARRANGEMENT].rename(columns = RENAME_DICT)

TIDY_DATA.to_csv('ID-population-kec-tidy.csv', index=False)
