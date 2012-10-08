#!/usr/bin/env python
# coding=utf-8
#
# Author : beninu@gmail.com
#
# Created: 2012 Oct 08 Mon 09:36:04 AM CST

import  unittest
class PhotoGoHomeTestCase(unittest.TestCase):
  def setUp(self):
    pass
  def tearDown(self):
    pass
  def testGoHome(self):
    import os
    ret = os.system('cp -r test_data src_dir') 
    self.assertEqual(ret, 0)

    ret = os.system('python ../PhotoGoHome.py src_dir dest_dir')
    self.assertEqual(ret, 0)

    self.assertTrue(os.path.exists('./dest_dir/2011/02/2011-02-27.Canon PowerShot S2 IS.MVI_1707027.AVI'))
    self.assertTrue(os.path.exists('./dest_dir/2011/02/2011-02-27.Canon PowerShot S2 IS.MVI_1707027.THM'))
    self.assertTrue(os.path.exists('./dest_dir/2011/09/2011-09-30.Canon PowerShot S2 IS.IMG_1848456.JPG'))
    self.assertTrue(os.path.exists('./dest_dir/2012/09/2012-09-24.Canon EOS 60D.IMG_134350.JPG'))
    self.assertTrue(os.path.exists('./dest_dir/2012/09/2012-09-24.Canon EOS 60D.IMG_134350.CR2'))

    ret = os.system('rm -rf src_dir dest_dir')
    self.assertEqual(ret, 0)

def main():
  #unittest.main()
  suite = unittest.TestLoader().loadTestsFromTestCase(PhotoGoHomeTestCase)
  unittest.TextTestRunner(verbosity=2).run(suite)


if __name__=="__main__":
  main()

