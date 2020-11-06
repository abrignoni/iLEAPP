# coding: utf-8
#Import the necessary Python modules
import pandas as pd
import geopandas as gpd
import folium
from folium import IFrame
from folium.plugins import TimestampedGeoJson
import shapely
from shapely.geometry import Point
import os
import fiona
from datetime import datetime
from branca.element import Template, MacroElement
import html
from scripts.location_map_constants import iLEAPP_KMLs, defaultShadowUrl, defaultIconUrl, colors, legend_tag, legend_title_tag, legend_div, template_part1, template_part2

from scripts.artifact_report import ArtifactHtmlReport

#Helpers
def htmlencode(string):
    return string.encode(encoding='ascii',errors='xmlcharrefreplace').decode('utf-8')

def geodfToFeatures(df, f, props):
    coords = []
    times = []
    for i,row in df[df.Description.str.contains(f)].iterrows():
        coords.append(
            [row.geometry.x,row.geometry.y]
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
    location_path = os.path.join(reportfolderbase, 'LOCATIONS')
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

    #import KML files to GeoPandas
    #start with empty df
    df = gpd.GeoDataFrame()

    for filename in os.listdir(KML_path):
        if filename.endswith("kml")  and not 'Photo' in filename:
            s = gpd.read_file(os.path.join(KML_path,filename), driver='KML')
            df = df.append(s, ignore_index=True)

    #sorting is needed for correct display
    df.sort_values(by=['Name'],inplace=True)

    #Parse KML data and add to Folium Map
    data_names = df.Description.str.extract(r'.{30} - (.*)')[0].unique()

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

    location_map = folium.Map([df.iloc[0].geometry.y,df.iloc[0].geometry.x], prefer_canvas=True, zoom_start = 6)
    location_map.fit_bounds([
            (df.geometry.total_bounds[1],df.geometry.total_bounds[0]),
            (df.geometry.total_bounds[3],df.geometry.total_bounds[2]),
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
