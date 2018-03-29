from peewee import *
import pandas as pd
import xlrd
import numpy
import requests
from bokeh.plotting import figure, output_file, show, curdoc
from bokeh.models import ColumnDataSource, HoverTool

db = SqliteDatabase("overdose_deaths.db")
#url = "http://eric.clst.org/assets/wiki/uploads/Stuff/gz_2010_us_040_00_20m.json"
output_file("bar_chart.html")

# Establishes database connection
if __name__ == '__main__':
    db.connect()
    print("We connected!")

# This statement uses a built in pandas method to read my excel file, changes the column names, and creates a database table
try:
    df_from_xlsx = pd.read_excel("VSRR_Provisional_Drug_Overdose_Death_Counts.xlsx")
    df_from_xlsx.columns = df_from_xlsx.columns.str.strip()
    df_from_xlsx.columns = [c.lower().replace(' ', '_') for c in df_from_xlsx.columns]
    df_from_xlsx.to_sql("vssr_counts", db, flavor=None, schema=None, if_exists='fail', index=True, index_label=None, chunksize=None, dtype=None)
except ValueError:
    pass

# This chunk of code pulls a dataframe from a SQL Query
df_from_db = pd.read_sql("SELECT * FROM vssr_counts WHERE \"year\" = \"2016\" AND \"month\" = \"December\"", db, index_col=None, coerce_float=True, params=None, parse_dates=None, chunksize=None)

# This chunk of code creates an sorted, iterable list of state codes
states = df_from_db.state.unique().tolist()
states.sort()

# This chunk iterates over the list of state codes, selects both "Total Deaths" and "Number of Overdose Deaths", then calculates a percentage
# and appends that to top_data[] for use in my bar chart.
top_data=[]

for state in states:
    num_overdose_deaths = df_from_db.loc[(df_from_db['state'] == state) & (df_from_db['indicator'] == "Number of Drug Overdose Deaths")].get("data_value")
    num_overall_deaths = df_from_db.loc[(df_from_db['state'] == state) & (df_from_db['indicator'] == "Number of Deaths")].get("data_value")
    percent_of_deaths = ((float(num_overdose_deaths)/float(num_overall_deaths))*100)
    top_data.append(percent_of_deaths)

# Setting up the plot and showing the plot
p = figure(x_range=states, plot_height=500, plot_width=1200, title="Perecntage of Total Death Count related to Drug Overdose by State for 2016",
           toolbar_location=None, tools="")
p.vbar(x=states, top=top_data, width=0.9)
p.xgrid.grid_line_color = None
p.y_range.start = 0
show(p)

# r = requests.get(url)
# states_geojson_data = r.json()
#
#
# def extract_single_county_patch(raw_geojson):
#     manual_x = []
#     manual_y = []
#
#     for coord in raw_geojson[0]:
#         manual_x.append(coord[0])
#         manual_y.append(coord[1])
#
#     return (manual_x, manual_y)
#
# def manually_build_patches(raw_geojson):
#     manual_xs = []
#     manual_ys = []
#     names = []
#
#     for feature in raw_geojson['features']:
#         names.append(feature['properties']['NAME'])
#         manual_x, manual_y = extract_single_county_patch(feature['geometry']['coordinates'])
#         manual_xs.append(manual_x)
#         manual_ys.append(manual_y)
#         names.append
#
#     return (manual_xs, manual_ys, names)
#
#
# def build_state_map(data_to_align, mapped_data_name):
#
#     # build the lists of data in the correct orders for our ColumnData
#     manual_x, manual_y, county_names = manually_build_patches(states_geojson_data)
#
#     # biulds a sale_value array aligned in the correct order to match the geo data counties
#     #mapped_data = build_sale_val_array(data_to_align, county_names, mapped_data_name)
#
#     # source dictionary to pass to ColumnDataSource
#     manual_data_for_map = {
#         'xs': manual_x,
#         'ys': manual_y,
#         'county_name': county_names,
#         mapped_data_name: mapped_data
#     }
#
#     return manual_data_for_map
#
#
# coulmn_source = ColumnDataSource(build_state_map())
#
# state_map = figure(title="VSSR Provisional Drug Overdose Data by State")
# state_map.patches('xs', 'ys',
#                               fill_color=None,
#                               fill_alpha=0.7, line_color='grey',
#                               line_width=0.5,
#                               source=coulmn_source,
#                               name='counties'
#                              )
#
# show(state_map)