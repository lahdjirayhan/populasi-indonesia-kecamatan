import camelot
import pandas as pd

FILENAME = "50099-ID-hasil-olah-cepat-penduduk-indonesia-menurut-provinsi-kabkota-dan-kecamatan-sp201.pdf"

TOP = '635'
BOTTOM = '50'
LEFT = '45'
RIGHT = '440'
TABLE_AREA = f'{LEFT},{TOP},{BOTTOM},{RIGHT}'

COLUMNS_LOCATION = [95, 255,315,390]
COLUMNS = ','.join([str(x) for x in COLUMNS_LOCATION])

PAGES='38-214'

tables = camelot.read_pdf(FILENAME, flavor='stream', pages=PAGES, columns=[COLUMNS], edge_tol=5, row_tol=10)

def separate_header_information(DF):
    ROW_CONCATENATED = DF.apply(
        lambda series: series.str.replace(r' ', '', regex=True).str.cat(),
        axis=1
    )

    try:
        NUMERIC_HEADER_INDEX = ROW_CONCATENATED.index[ROW_CONCATENATED == '(1)(2)(3)(4)(5)'].item()
    except ValueError:
        raise AssertionError('No numeric header like this "(1)(2)(3)(4)(5)" is found for this dataframe.')

    return (
        DF.iloc[(NUMERIC_HEADER_INDEX + 1):, :].copy().reset_index(drop=True),
        DF.iloc[:(NUMERIC_HEADER_INDEX + 1), :].copy().reset_index(drop=True)
    )

def separate_footer_information(DF):
    BOTTOM_ROW_INGESTED = DF.iloc[-1, :].str.cat()
    assert "Penduduk Indonesia" in BOTTOM_ROW_INGESTED, "BOTTOM ROW INGESTED is not as expected"

    return (
        DF.iloc[:-1, :].copy().reset_index(drop=True),
        DF.iloc[(-1):, :].copy().reset_index(drop=True)
    )


def get_humanpage_from_footer(FOOTER):
    digit_chars = [char for char in FOOTER.iloc[0].str.cat() if char.isdigit()]
    humanpage = int(''.join(digit_chars))
    return humanpage

def remove_empty_rows(DF):
    empty_rows = (
        DF.apply(lambda series: series.isin([' ', ''])).sum(axis = 1) == 5
    )

    RESULT = DF[~empty_rows].copy()
    return RESULT

def clean_watermark(DF):
    watermark_characters = r'[htps:/w.bpsgoid]'
    RESULT = DF.apply(lambda series: series.str.replace(watermark_characters, '', regex=True)).copy()

    return RESULT

def clean_infixed_newlines(DF):
    # NOTE: Infixed newlines can originate from 1) watermark and 2) Camelot being unable to decide a row
    cell_contains_newline = DF.apply(lambda series: series.str.contains('\n'))

    row_newline_count = cell_contains_newline.sum(axis=1)

    # Here we shall warn about multiple newlined cells
    rows_with_newline = DF[row_newline_count > 0].copy()
    rows_with_newline['n_cells_with_newline'] = row_newline_count

    RESULT = DF.apply(lambda series: series.str.replace(r'\n', '', regex=True))
    return RESULT, rows_with_newline

def rectify_types(DF):
    RESULT = DF.copy()

    # Total column
    total = DF[4]
    total = total.str.replace(' ', '', regex=False)
    total = total.astype(int)

    # Female (perempuan) column
    female = DF[3]
    female = female.str.replace(' ', '', regex=False)
    female = female.astype(int)

    # Male (laki-laki) column
    # NOTE: Many of this cell are corrupted thanks to watermark
    male = DF[2]
    male = male.str.replace(' ', '', regex=False)

    # Recover by total - female
    missing_male = male == ''
    male[missing_male] = (total - female)[missing_male]

    male = male.astype(int)

    # Region name column
    name = DF[1]
    assert(name != '').all()

    # Code column
    code = DF[0]
    code = code.astype(int)

    # Put everything together
    RESULT[0] = code
    RESULT[1] = name
    RESULT[2] = male
    RESULT[3] = female
    RESULT[4] = total

    return RESULT


def preliminary_check(DF):
    # Ensure dataframe size
    NROW = len(DF)
    NCOL = len(DF.columns)

    assert NCOL == 5, "Number of columns is not exactly 5"

    # Separate the main table from header
    DF, HEADER = separate_header_information(DF)

    # Separate the main table from footer
    DF, FOOTER = separate_footer_information(DF)

    return DF, HEADER, FOOTER


def process_data(DF):
    # Clean watermark
    DF = clean_watermark(DF)

    # Remove newlines that get stuck inside them somehow
    DF, WARNINGS = clean_infixed_newlines(DF)

    # Remove empty rows
    DF = remove_empty_rows(DF)

    # Change population count data from string into integer
    DF = rectify_types(DF)

    return DF, WARNINGS


TABLES = []
NEWLINE_ROWS = []
MSG = ""

for i, table in enumerate(tables):
    DF = table.df
    MSG = f"{i}: Page {table.page} "

    # PRELIMINARY CHECK
    # =================
    try:
        DF, HEADER, FOOTER = preliminary_check(DF)

        # Get human-readable page for report
        HUMAN_PAGE = get_humanpage_from_footer(FOOTER)
        MSG += f"(humanpage {HUMAN_PAGE}) passed preliminary checks. "
    except AssertionError:
        MSG += f"failed preliminary checks, SKIP. "
        print(MSG)
        continue

    # Get only the data
    DF

    # PROCESSING DATA
    # ===============
    try:
        DF, WARNINGS = process_data(DF)
    except AssertionError:
        MSG += f"Encountered error in data processing, SKIP. "
        print(MSG)
        continue

    # FINAL REPORT AND APPEND
    # =======================

    MSG += f"SUCCESS, shape {DF.shape}"
    print(MSG)

    TABLES.append(DF)
    NEWLINE_ROWS.append(WARNINGS)


FINAL = pd.concat(TABLES, ignore_index=True)
COLUMN_NAMES = ['CODE', 'NAME', 'MALE_POPULATION', 'FEMALE_POPULATION', 'TOTAL_POPULATION']
FINAL.columns = COLUMN_NAMES


FINAL_WARNINGS = pd.concat(NEWLINE_ROWS, ignore_index=True)

assert not FINAL.isna().sum().any(), 'Extracted data contains missing values'
assert not (FINAL == '').sum().any(), 'Extracted data contains empty cells'

FINAL.to_csv('ID-population-kec-by-book.csv', index=False)
FINAL_WARNINGS.to_csv('warnings-row-with-newline.csv', index=False)


# **Things to consider**
#
# 1. Table footer (page number)
# 2. Table header (column title, possibly table name)
# 3. Catch rows that denote PROVINCE AGGREGATE: ends in xx00 where xx is province code, see page 11 in the same book
# 4. Catch rows that denote KABUPATEN AGGREGATE: four-digit xxyy where xx is province code and yy is kabupaten order/code
#
# 5. Other than 3 and 4 is KECAMATAN
#
# 6. Remove the watermark `https://www.bps.go.id` that pollutes the middle page:
#     - watermark in lowercase, data in uppercase
#
# 7. Watch out or remove (debug?) multiple kecamatan in one row separated by `\n`
#
# 8. Reconstruct column LAKI-LAKI by TOTAL - PEREMPUAN
#     - the watermark corrupts the middle column esp LAKI-LAKI, resulted in blank cells
#
# 9. Watch out or debug kecamatan names (case-by-case basis so far)
