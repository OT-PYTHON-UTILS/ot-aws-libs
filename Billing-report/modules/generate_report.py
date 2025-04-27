import pandas as pd

def process_cost_data(cost_data):
    service_data = cost_data['ResultsByTime'][0]['Groups']

    rows = []
    for service in service_data:
        service_name = service['Keys'][0]
        amount = float(service['Metrics']['UnblendedCost']['Amount'])
        rows.append((service_name, amount))

    df = pd.DataFrame(rows, columns=['Service', 'Cost'])
    df['% Contribution'] = (df['Cost'] / df['Cost'].sum()) * 100
    return df
