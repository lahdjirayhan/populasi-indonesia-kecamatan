# Indonesian Population per District, based on 2010 Population Census

... because I can't get my hands on the *detailed* results of more recent censuses.


**Important Note**

If you use this data in a publication, Statistics Indonesia (BPS) requires you to cite, or otherwise give acknowledgement, that your data is sourced from BPS.

If you cite me -- or mention that I convert from PDF to CSV -- I'll be glad, though I don't know how exactly.

## Table of Contents

1. The PDF file is the original source material (book) from which I extract the data. The PDF file contains tabulated population count data, which I extracted using a tool called Camelot.

2. The Python files are the scripts I used to extract and tidy the data.

3. The CSV files are the outputs from the Python files. They contain the population data in CSV format, which can be loaded and read using Excel.

   - `ID-population-kec-by-book.csv` has all the rows for district, region, and province aggregates are mixed together. This is exactly as found in the book. You can use this if you want to find something and you need it to be exactly as found in the book.
   - `ID-population-kec-tidy.csv` is the tidier format. The format is one row for one district. **I would recommend you to use this.**
   - `warnings-row-with-newline.csv` is there just for debugging purposes and does not contain any meaningful population data.

## Workflow

Environment used to perform this work:
- Windows 7
- Python 3.8.5
- `pandas` 1.3.4
- `camelot-py` 0.10.1

The following is the steps that I do to obtain the data:

1. Make sure the dependencies are installed.

2. Have the PDF file and the Python scripts in one folder.

3. Read the data from the PDF by invoking (in the folder):
    ```sh
    python reading_data.py
    ```

    This step will create `ID-population-kec-by-book.csv` and `warnings-row-with-newline.csv`.
4. Tidy the data into more convenient format by invoking:
    ```sh
    python transforming_data_tidy.py
    ```

    This step will create `ID-population-by-kec-tidy.csv`.

## Credits and Acknowledgements

This work is available thanks to:

- [Statistics Indonesia](https://bps.go.id) (Badan Pusat Statistik), the Indonesian official statistics bureau that carried out the census and published the data.
- [Camelot](https://github.com/camelot-dev/camelot), the Python library used to pull the data from PDF format.

Also:

- [Original link from where I downloaded the PDF file](https://media.neliti.com/media/publications/50099-ID-hasil-olah-cepat-penduduk-indonesia-menurut-provinsi-kabkota-dan-kecamatan-sp201.pdf). I cannot make absolute guarantee that this file is original, but I think it's fine.
