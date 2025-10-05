import csv

with open(r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST6\duplicate_words6.csv", "r", encoding="utf-8") as infile, \
        open(r"C:\Users\User\Downloads\ETS2023\ETS2023_TEST6\duplicate_words61.csv", "w", newline='', encoding="utf-8") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)

    for row in reader:
        # Đảm bảo có 4 cột, thêm "" nếu thiếu
        while len(row) < 4:
            row.append("")
        writer.writerow(row)
