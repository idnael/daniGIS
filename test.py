#!/usr/bin/python3
# coding: utf-8

# 202007 Daniel

import codecs, math, shapefile, re, sys, glob, subprocess, os, shutil, random

reader = shapefile.Reader("test.shp")

for field in reader.fields[1:]:
    print(field)
    
