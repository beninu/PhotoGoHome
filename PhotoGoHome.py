#!/usr/bin/env python
# coding: utf-8
#
# beninu@gmail.com

USAGE=u'''
python %prog [options] source_dir destination_dir



# 该脚本用来整理数码相机输出的图片和视频文件
# 目前只对Canon相机做过测试，具体来说是
#   Canon PowerShot S2 IS
# 和
#   Canon PowerShot A620
# 通过图片和视频的EXIF信息生成新的文件名  
# 并放年月结构的目录中, 如下
# `-- 2011
#     |-- 02
#     |   |-- 2011-02-27.Canon PowerShot S2 IS.MVI_1707027.AVI
#     |   `-- 2011-02-27.Canon PowerShot S2 IS.MVI_1707027.THM
#     `-- 09
#          `-- 2011-09-30.Canon PowerShot S2 IS.IMG_1848456.JPG
#
# 遇到不认识的格式，或者解析失败，跳过，不动源文件

'''
import os
import re
import sys
import datetime
import pyexiv2

def checkDir(filename):
  """ 检查filename中的path部分是否都存在，没有话创建dir

  """
  filedir = os.path.dirname(filename)
  if not os.path.isdir(filedir):
    print "[INFO]checkDir:mkdir -p %s"%filedir
    if not dryrun:
      os.makedirs(filedir)
  
def exifInfo(img_file):
  """ 提取一个image文件的信息
      日期.机型.img_file
      比如
      ./IMG_6632.JPG
      2010-10-06.Canon PowerShot S2 IS.IMG_6632.JPG
  """
  if debug:
    print "[DEBUG]exifInfo: img_file=%s"%img_file
  if pyexiv2.version_info[1] >= 2: # XXX need to check
    metadata = pyexiv2.ImageMetadata(img_file)
    metadata.read()
    model = metadata['Exif.Image.Model'].value
    riqi = metadata['Exif.Image.DateTime'].value
    try:
      filenumber = metadata['Exif.Canon.FileNumber'].value
    except KeyError as e:
      filenumber = riqi.strftime("%H%M%S")
      print "[DEBUG]exifInfo: cannot find Exif.Canon.FileNumber for img_file=%s, using time for filenumber=%s"%(img_file,filenumber)
  else:
    metadata = pyexiv2.Image(img_file)
    metadata.readMetadata()
    model = metadata['Exif.Image.Model']
    riqi = metadata['Exif.Image.DateTime']
    try:
      filenumber = metadata['Exif.Canon.FileNumber']
    except KeyError as e:
      filenumber = riqi.strftime("%H%M%S")
      print "[DEBUG]exifInfo: cannot find Exif.Canon.FileNumber for img_file=%s, using time for filenumber=%s"%(img_file,filenumber)

  if debug:
    print "[DEBUG]exifInfo: model=%s, riqi=%s, filenumber=%s"%(model, riqi, filenumber)
  return (model, riqi, filenumber)

def getFilePath(subdir, old_filename, file_type, dest_root): 
  """ 通过源文件的exif信息，生成新的文件名和路径
      比如
  """
  old_filepath = os.path.join(subdir,old_filename)
  model, riqi, filenumber = exifInfo(old_filepath)

  pic_root = dest_root
  year = str(riqi.year)
  month = "%02d"%(riqi.month)
  if file_type in ("JPG", 'jpg'):
    new_filename = "%s.%s.IMG_%s.JPG"%(riqi.strftime("%Y-%m-%d"), model, filenumber)
    new_filepath = os.path.join(pic_root, year, month, new_filename)
    old_filepath_avi = None
    new_filepath_avi = None
  elif file_type == 'CR2':
    new_filename = "%s.%s.IMG_%s.CR2"%(riqi.strftime("%Y-%m-%d"), model, filenumber)
    new_filepath = os.path.join(pic_root, year, month, new_filename)
    old_filepath_avi = None
    new_filepath_avi = None
  elif file_type == 'THM':
    old_filepath_avi = old_filepath[:-4]+".AVI"
    new_filename = "%s.%s.MVI_%s.THM"%(riqi.strftime("%Y-%m-%d"), model, filenumber)
    new_filename_avi = "%s.%s.MVI_%s.AVI"%(riqi.strftime("%Y-%m-%d"), model, filenumber)
    new_filepath = os.path.join(pic_root, year, month, new_filename)
    new_filepath_avi = os.path.join(pic_root, year, month, new_filename_avi)

  return old_filepath, new_filepath, old_filepath_avi, new_filepath_avi

def getFileType(f):
  file_type = f.split('.')[-1]
  if debug:
    print "[DEBUG]getFileType: file=%s, file_type=%s"%(f, file_type)
  return file_type

def move2YearMonth(subdir, f, dest_root):
  """根据f的exif信息，把文件改名为Year-Month-Day.Camera_Model.img_filenumber.jpg
      并移动到pic_root/Year/Month中
  """
  file_type = getFileType(f)

  if file_type not in ("JPG", "jpg", "THM", "CR2"):
    print "[WARNING]unknonw file_type=%s"%file_type
    return

  try:
    old_filepath, new_filepath, old_filepath_avi, new_filepath_avi = getFilePath(subdir, f, file_type, dest_root)
  except RuntimeError as e:
    print "[ERROR]move2YearMonth: getFilePath exception: %s, file=%s, I do nothing"%(e.value, os.path.join(subdir, f))
    return

  checkDir(new_filepath)
  if os.path.isfile(new_filepath):
    print "[WARNING]move2YearMonth:duplicated file %s and %s, I do nothing"%(old_filepath, new_filepath)
    return

  cmd = 'mv "%s" "%s"'%(old_filepath, new_filepath)
  print "[INFO]move2YearMonth:%s"%cmd
  if not dryrun:
    os.system(cmd)
  
  if file_type in ('JPG', 'jpg', 'CR2'): # JPG文件只移动本身，THM文件需要移动相应的AVI文件
    return

  cmd = 'mv "%s" "%s"'%(old_filepath_avi, new_filepath_avi)
  print "[INFO]move2YearMonth:%s"%cmd
  if not dryrun:
    os.system(cmd)


def walkDir(root_dir, file_pat, call_back, arg):
  """ 遍历root_dir下的所有文件f
      对文件名符合file_pat的文件进行call_back(root, f, arg)的操作
      其中，root是从root_dir开始的相对路径，含root_dir，f是文件名
      arg是call_back需要的其他参数
  """
  total = 0
  matched= 0
  pat = re.compile(file_pat)
  for (root, subdirs, files) in os.walk(root_dir):
    if debug:
      print "[DEBUG]walkDir:root(=%s) subdirs(=%s)"%(root, subdirs)
    for f in files:
      total += 1
      m = pat.match(f)
      if m:
        matched += 1
        print "[INFO]walkDir: process %s"%(os.path.join(root, f))
        call_back(root, f, arg)
      else:
        pass
  if debug:
    print "[DEBUG]total(=%d) files scand and %d files matched"%(total, matched)

def initLog(logfile, debug=False):
  import logging
  logger = logging.getLogger()
  if not logfile:
    handler = logging.FileHandler(logfile)
  else:
    handler = logging.StreamHandler()
  formatter = logging.Formatter('%(asctime)s %(levename)7s %(funcName)16s: %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  if debug:
    logger.setLevel(logging.DEBUG)
  else:
    logger.setLevel(logging.INFO)

  return logger

def initOptionParser(usage):
  import optparse
  parser = optparse.OptionParser(usage)
  parser.add_option('', '--debug', dest='debug', 
                    default=False, action='store_true',
                    help='print debug logg info, DEFAULT=False')

  parser.add_option('', '--dryrun', dest='dryrun',
                    default=False, action='store_true',
                    help='run the scripts and print status and do nothing real, DEFAULT=False')
                
  #parser.add_option('-s', '--src_dir', type='str',
  #                  help='photoes source dir')
  
  #parser.add_option('-d', '--dest_dir', type='str',
  #                  help='destination dir')

  return parser


  
if __name__ == "__main__":
  global dryrun
  global log
  options = initOptionParser(USAGE)
  opts, args = options.parse_args(sys.argv[1:])
  if len(args) != 2:
    options.print_help()
    #options.error('need source dir and destination dir')
    sys.exit(-1)

  dryrun = opts.dryrun
  debug = opts.debug
  print "[INFO]dryrun=%s, debug=%s"%(dryrun, debug)  
  root_dir, pic_root = args
  walkDir(root_dir, ".*\.(JPG|jpg|THM|CR2)", move2YearMonth, pic_root)
