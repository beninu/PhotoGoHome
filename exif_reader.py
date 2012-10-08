#!/usr/bin/env python
# coding=utf-8
#
# Author : wengcj@rd.netease.com
# Created: 2011 Oct 24 Mon 03:37:40 PM CST
import sys
import pyexiv2

def exiv_read(img_filepath):
  img = pyexiv2.Image(img_filepath)
  img.readMetadata()
  for k in img.exifKeys():
    print "%s=%s"%(k, img[k])
  print img['Exif.Image.DateTime'].hour
  print img['Exif.Image.DateTime'].minute
  print img['Exif.Image.DateTime'].second
def exiv_read2(img_filepath):
  metadata = pyexiv2.ImageMetadata(img_filepath)
  metadata.read()
  for k in metadata.exif_keys:
    print "%s=%s"%(k, metadata[k].raw_value)
    print "%s=%s"%(k, metadata[k].value)

def main():
  img_filepath=sys.argv[1]
  if pyexiv2.version_info[1] >=2:
    exiv_read2(img_filepath)
  else:
    exiv_read(img_filepath)

if __name__=="__main__":
  main()

