def write_to_excel(df, output_excel):
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "AWS Services Billing"

    ws.append(["Service", "Cost ($)", "% Contribution"])

    for index, row in df.iterrows():
        ws.append([row['Service'], round(row['Cost'], 2), round(row['% Contribution'], 2)])

    wb.save(output_excel)
