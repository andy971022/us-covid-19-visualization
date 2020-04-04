import pandas as pd
import pandasql as ps
import json
from folium import Map, LayerControl, Choropleth
import numpy
import os
from PIL import Image
import glob
import subprocess

def plot_map(date, df):
	maximum = df[df["date"] == date]["cases"].max()
	m = Map(location = [37,-98],
	    zoom_start = 4)
	Choropleth(geo_data = GEOJSON_PATH + GEOJSON_FILE,
	            name = 'choropleth',
	            data = df[df["date"] == date],
	            columns = ['state','cases'],
	            key_on = 'feature.properties.name',
	            fill_opacity = 0.7,
	            line_opacity = 0.2,
	            line_color = 'red',
	            fill_color = 'YlOrRd',
	            bins = [0,2,4,6,9,12],
	          ).add_to(m)
	LayerControl().add_to(m)
	return m

if __name__ == '__main__':
	GEOJSON_PATH = "./GeoJson/"
	CSV_DIRECTORY = "./CSV_Files/"
	FILE_NAME = "us-counties.csv"
	GEOJSON_FILE = "us-states.json"
	df = pd.read_csv(f"{CSV_DIRECTORY}{FILE_NAME}")

	print(df.columns)

	q1 = """
	select distinct date, state, sum(cases) as cases from df group by date, state
	"""
	cases_df = ps.sqldf(q1, locals())

	cases_df["cases"] = cases_df["cases"].apply(lambda x : numpy.log(x))
	print(cases_df.columns)

	## us geojson : https://github.com/PublicaMundi/MappingAPI/blob/master/data/geojson/us-states.json
	
	gj = json.load(open(f"{GEOJSON_PATH}{GEOJSON_FILE}"))


	for date in cases_df[cases_df['date'] > '2020-03-01'].date.unique():
		maps = plot_map(f"{date}", cases_df)
		maps.save(f"./Maps/{date}.html")

	for file in os.listdir(f"./Maps/"):
	    command = f"cutycapt --url=file://{os.getcwd()}/Maps/{file} --out=./images/{file.split('.')[0]}.png --delay=1000"
	    subprocess.run(command.split(" "))


	# pip install pillow==6.2.2

	files = sorted(glob.glob('./images/*.png'))
	images = list(map(lambda file: Image.open(file), files))
	images[0].save('us_covid-19_visualization_cases.gif', save_all=True, append_images=images[1:], duration=20, loop=0)
