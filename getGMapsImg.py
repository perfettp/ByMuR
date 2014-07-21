#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
from math import pi, sin, cos, tan, sqrt, pow, log, exp, atan
import StringIO
import sys
import urllib
import matplotlib.pyplot as plt


def utm2lola(x, y, z):
  '''Conversion from UTM to Latitude and Longitude'''

  # WGS84
  a = 6378137             # Equatorial radius
  b = 6356752.3142        # Polar radius
  k0 = 0.9996             # Scale along lon0
  deg2rad = pi/180.0      # degree to radiants
  rad2deg = 180.0/pi      # radiants to degree

  e = sqrt(1-pow(b,2)/pow(a,2))  # Earth's eccentricity 
  e2 = pow(e,2)/(1-pow(e,2))
  e4 = pow(e2,2) 

  e1 = (1-pow(1-pow(e,2),0.5))/(1+pow(1-e2,0.5))
  
  # central meridian from zone number
  lon0D = (int(z[:-1])-1)*6 - 180 + 3 
  lon0 = lon0D * deg2rad
  # conventional easting offset
  x = x-500000
  # offset for southern hemisphere
  if (z[-1] == "S"):
    y = y-10000000.0
  
  M = y/k0   # the Meridional Arc
  mu = M/(a*(1-pow(e,2)/4-3*pow(e,4)/64-5*pow(e,6)/256))
  
  j1 = (3*e1/2-27*pow(e1,3)/32)
  j2 = (21*pow(e1,2)/16-55*pow(e1,4)/32)
  j3 = (151*pow(e1,3)/96)
  j4 = (1097*pow(e1,4)/512)
  
  fp = mu+j1*sin(2*mu)+j2*sin(4*mu)+j3*sin(6*mu)+j4*sin(8*mu) 
  
  c1 = e2*pow(cos(fp),2)
  t1 = pow(tan(fp),2)
  r1 = a*(1-pow(e,2))/pow(1-pow(e,2)*pow(sin(fp),2),1.5)
  n1 = a/pow(1-pow(e,2)*pow(sin(fp),2),0.5)
  d = x/(n1*k0)
  
  q1 = n1*tan(fp)/r1
  q2 = pow(d,2)/2
  q3 = (5+3*t1+10*c1-4*pow(c1,2)-9*e2)*pow(d,4)/24
  q4 = (61+90*t1 + 298*c1 + 45*pow(t1,2) - 3*pow(c1,2) - 252*e2)*pow(d,6)/720
  q5 = d
  q6 = (1+2*t1+c1)*pow(d,3)/6
  q7 = (5-2*c1+28*t1-3*pow(c1,2)+8*e2+24*pow(t1,2))*pow(d,5)/120
  
  lon = lon0+(q5-q6+q7)/cos(fp)
  lat = fp-q1*(q2-q3+q4)

  lonD = lon*rad2deg
  latD = lat*rad2deg
  return (lonD, latD)


def latlontopixels(lat, lon, zoom):
  """
  
  """
  x = (lon * origin_shift) / 180.0
  y = log(tan((90 + lat) * pi/360.0))/(pi/180.0)
  y = (y * origin_shift) /180.0
  res = initial_resolution / (2**zoom)
  px = (x + origin_shift) / res
  py = (y + origin_shift) / res
  return px, py
     

def pixelstolatlon(px, py, zoom):
  """
  """
  res = initial_resolution / (2**zoom)
  x = px * res - origin_shift
  y = py * res - origin_shift
  lat = (y / origin_shift) * 180.0
  lat = 180 / pi * (2*atan(exp(lat*pi/180.0)) - pi/2.0)
  lon = (x / origin_shift) * 180.0
  return lat, lon


def calcNxNy(lat_min, lat_max, lon_min, lon_max):
  """
  Calculation of the number nx*ny of images that will be downloaded from gmaps.
  The number is limited by a threshold to avoid too many images (and a final
  image too big in size). Moreover the present Google Maps policy is 25000 
  free maps for application for day (superstronzi). Here it is set a maximum of 
  3x3=9 free maps to describe the selected region.
  """

  global zoom
  
  threshold = 3  

  xmin, ymin = latlontopixels(lat_min, lon_min, zoom)
  xmax, ymax = latlontopixels(lat_max, lon_max, zoom)
  
  # calculate total pixel dimensions of final image
  dlon = (xmax - xmin)
  dlat = (ymax - ymin)
  nx = int(dlon/size)+1
  ny = int(dlat/size)+1
  #print nx, ny, zoom

  while (nx > threshold or ny > threshold):
    zoom = zoom - 1
    #if zoom < 0:
      #zoom = 0
    xmin, xmax, ymin, ymax, nx, ny, dlon, dlat = calcNxNy(lat_min, lat_max, lon_min, lon_max)

  return xmin, xmax, ymin, ymax, nx, ny, dlon, dlat
  

def getUrlGMaps(lon_min_utm, lat_min_utm, lon_max_utm, lat_max_utm,  
                utm_zone, savepath):

  """
  Create and save the final image as sum of all nx*ny images downloaded from 
  google maps. Images are downloaded with urllib, which connect to the 
  corresponding url of each single image. The images are glued and saved 
  by using the Python Image Library.      
  """  

  lon_min, lat_min = utm2lola(lon_min_utm, lat_min_utm, utm_zone)
  lon_max, lat_max = utm2lola(lon_max_utm, lat_max_utm, utm_zone)

  xmin, xmax, ymin, ymax, nx, ny, dlon, dlat = calcNxNy(lat_min, lat_max, 
                                                        lon_min, lon_max)

  dx = int(dlon/nx)
  dy = int(dlat/ny)

  img = Image.new("RGB", (int(dlon), int(dlat)))

  for i in range(nx):
    for j in range(ny):
      x = xmin + 0.5*dx + (i*dx)
      y = ymax - 0.5*dy - (j*dy)
      lat, lon = pixelstolatlon(x, y, zoom)
      #print i, j, lat, lon 
      position = ','.join((str(lat), str(lon)))
      
      urlparams = urllib.urlencode({'center': position,
                                    'zoom': str(zoom),
                                    'size': '%dx%d' % (dx, dy),
                                    'maptype': maptype,
                                    'sensor': 'false',
                                    'scale': scale})
      url = 'http://maps.google.com/maps/api/staticmap?' + urlparams
      #print url
      f = urllib.urlopen(url)
      imgtmp = Image.open(StringIO.StringIO(f.read()))
      img.paste(imgtmp, (int(i*dx), int(j*dy)))
      #f = urllib.urlretrieve(url, imgname + "." + imgfmt)
  
  img.save(savepath)
  return savepath


# global parameters
earth_radius = 6378137
equator_circumference = 2*pi*earth_radius
initial_resolution = equator_circumference/256.0
origin_shift = equator_circumference/2.0

# google maps parameters
scale = 1               # 1 or 2 - 2 double the size
size = 640              # max 640
zoom = 18               # 0-21
maptype = 'satellite'   # satellite, terrain, roadmap, hybrid


