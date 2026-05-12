from all_buildup import BATCH
from analysis import ANALYSE

files = [r'main_2019-09-19.csv',
        r'main_2019-10-04.csv',
        r'main_2019-11-15.csv',
        r'main_2020-12-22.csv',
        r'main_2021-09-03.csv',
        r'main_2021-09-09.csv',
        r'main_2021-09-10.csv',
        r'main_2021-09-21.csv',
        r'main_2021-10-11.csv',
        r'main_2022-04-12.csv',
        r'main_2025-07-03.csv',
        r'main_2025-07-04.csv',
        r'main_2025-07-07.csv',
        r'main_2025-07-08.csv',
        r'main_2025-10-23.csv',
        r'main_2025-10-28.csv',
        r'main_2025-11-06.csv',
        r'main_2025-11-21.csv',
        r'main_2025-12-01.csv',
        r'main_2025-12-05.csv']  # new is the trial with more recent dial and ratio calibration
# files = [r'main_2021-08-27_a.csv', r'main_2025-07-08.csv'] # select subset
batch = BATCH(files, 'run_lists')
summary_files = batch.execute()  # both executes the buildups and gives the list of summary files
anal = ANALYSE(summary_files)
anal.all_sumry()  # loads the data
anal.corrected_dict()  # applies constraint of the mean of AH11 set #1
anal.corrected_to_std_con()
anal.plot(['AH11A1', 'AH11B1', 'AH11C1', 'AH11D1', 'AH11A2', 'AH11B2', 'AH11C2', 'AH11D2'], 'AH11 set')
anal.plot(['ES14', 'ES13', 'ES16', 'GR10', 'GR100', 'GR1000A', 'GR1000B', 'ES13ES16'], 'GR and S ball set')
out_block = anal.out_block()  # prepares csv-friendly lists
anal.file_block('analysis.csv', out_block)  # writes to csv file
anal.store_dicts()
