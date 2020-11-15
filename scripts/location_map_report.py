# coding: utf-8
#Import the necessary Python modules
import pandas as pd
import folium
from folium.plugins import TimestampedGeoJson
from shapely.geometry import Point
import os
from datetime import datetime
from branca.element import Template, MacroElement
import html
from scripts.location_map_constants import iLEAPP_KMLs, defaultShadowUrl, defaultIconUrl, colors, legend_tag, legend_title_tag, legend_div, template_part1, template_part2
import sqlite3 

from scripts.artifact_report import ArtifactHtmlReport

#Helpers
def htmlencode(string):
    return string.encode(encoding='ascii',errors='xmlcharrefreplace').decode('utf-8')

def geodfToFeatures(df, f, props):
    coords = []
    times = []
    for i,row in df[df.Description.str.contains(f)].iterrows():
        coords.append(
            [row.Point.x,row.Point.y]
        )
        times.append(datetime.strptime(row.Name,'%Y-%m-%d %H:%M:%S').isoformat())
    return {  
        'type': 'Feature',
        'geometry': {
            'type': props[f]['fType'],
            'coordinates': coords,
        },
        'properties': {
            'times': times,
            'style': {'color': props[f]['color']},
            'icon': props[f]['icon'],
            'iconstyle': {
                'iconUrl': props[f]['iconUrl'],
                'shadowUrl': props[f]['shadowUrl'],
                'iconSize': [25, 41],
                'iconAnchor': [12, 41],
                'popupAnchor': [1, -34],
                'shadowSize': [41, 41],
                'radius': 5,
            },
        },
    }


def generate_location_map(reportfolderbase,legend_title):
    KML_path = os.path.join(reportfolderbase,iLEAPP_KMLs)
    if not os.path.isdir(KML_path) or not os.listdir(KML_path):
        return

    location_path = os.path.join(reportfolderbase, 'LOCATIONS')
    os.makedirs(location_path,exist_ok=True)
    db = sqlite3.connect(os.path.join(KML_path,"_latlong.db"))
    df = pd.read_sql_query("SELECT key as Name, Activity as Description, latitude, longitude FROM data ;", db)
    df["Point"] = df.apply(lambda row: Point(float(row['longitude']),float(row['latitude']),.0), axis=1)

    #sorting is needed for correct display
    df.sort_values(by=['Name'],inplace=True)

    #Parse geo data and add to Folium Map
    data_names = df[~df.Description.str.contains('Photos')].Description.unique()
    featuresProp = {}

    for c,d in zip(colors, data_names):
        descFilter = d
        if 'ZRT' in d:
            fType =  'LineString'
            icon = 'marker'
            iconUrl = defaultIconUrl.format(c)
            shadowUrl = defaultShadowUrl
        else:
            fType =  'MultiPoint'
            icon = 'circle'
            iconUrl = ''
            shadowUrl = ''

        color = c

        featuresProp[d] = {
                'fType': fType,
                'color': c,
                'icon': icon,
                'iconUrl': iconUrl,
                'shadowUrl': defaultShadowUrl,
            }

    location_map = folium.Map([df.iloc[0].Point.y,df.iloc[0].Point.x], prefer_canvas=True, zoom_start = 6)
    bounds = (df[~df.Description.str.contains('Photos')]['longitude'].min(),
              df[~df.Description.str.contains('Photos')]['latitude'].min(),
              df[~df.Description.str.contains('Photos')]['longitude'].max(),
              df[~df.Description.str.contains('Photos')]['latitude'].max(),
             )
    location_map.fit_bounds([
            (bounds[1],bounds[0]),
            (bounds[3],bounds[2]),
        ]
    )

    tsGeo = TimestampedGeoJson({
        'type': 'FeatureCollection',
        'features': [
            geodfToFeatures(df, f, featuresProp) for f in data_names
        ]
    }, period="PT1M", duration="PT1H", loop=False, transition_time = 50, time_slider_drag_update=True, add_last_point=True, max_speed=200).add_to(location_map)


    #legend
    legend = '\n'.join([ legend_tag.format(featuresProp[f]['color'], htmlencode(f)) for f in data_names])
    template = '\n'.join([template_part1, legend_title_tag.format(htmlencode(legend_title)), legend_div.format(legend), template_part2])

    macro = MacroElement()
    macro._template = Template(template)

    location_map.get_root().add_child(macro)
    
    location_map.save(os.path.join(location_path,"Locations_Map.html"))

    report = ArtifactHtmlReport('Locations Map')
    report.start_artifact_report(location_path, 'Locations Map', 'Map plotting all locations')
    report.write_raw_html(open(os.path.join(location_path,"Locations_Map.html")).read())
    report.end_artifact_report()
