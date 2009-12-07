#!/usr/bin/env python

from ctypes import c_int
from ctypes_opencv import *
from sys import argv, exit

image = None
frame = None

class PointTracker:
    def __init__(self):
        self.capture = None
        self.image = None
        self.frame = None
        self.points = []
        self.oldpoints = []
        
        self.window_name = "Paul Tracker"
        
        self.sizeX = 640

        self.capture = cvCaptureFromCAM(0)
        cvNamedWindow( self.window_name, 1 )
        
        self.loop()
        
    def loop(self):
        while True:
            self.frame = cvQueryFrame( self.capture )
            if not self.frame:
                break
        
            if not self.image:
                # allocate all the buffers
                self.image = cvCreateImage( cvGetSize(self.frame), 8, 3 )
                self.image.origin = self.frame.origin
                hsv = cvCreateImage( cvGetSize(self.frame), 8, 3 )
                hue = cvCreateImage( cvGetSize(self.frame), 8, 1 )
                mask = cvCreateImage( cvGetSize(self.frame), 8, 1 )
                backproject = cvCreateImage( cvGetSize(self.frame), 8, 1 )
                
                self.gray = cvCreateImage (cvGetSize (self.frame), 8, 1)
                self.prev_gray = cvCreateImage (cvGetSize (self.frame), 8, 1)
                self.pyramid = cvCreateImage (cvGetSize (self.frame), 8, 1)
                self.prev_pyramid = cvCreateImage (cvGetSize (self.frame), 8, 1)

            cvCopy(self.frame, self.image)
            
            self.gray = self.getGrayscaleImage(self.image)
                        
            #Running goodfeaturestotrack ontop of points tracked last frame creates visually pleasing noise.
            self.checkInput(self.image)
            
            if len(self.points) > 0:
                newpoints, status = cvCalcOpticalFlowPyrLK (
                    self.prev_gray, self.gray, self.prev_pyramid, self.pyramid,
                    [pt['pt'] for pt in self.points], None, None, 
                    cvSize (10, 10), 3,
                    None, None,
                    cvTermCriteria (CV_TERMCRIT_ITER|CV_TERMCRIT_EPS,
                                       20, 0.03), 0)
        
                self.oldpoints = self.points
                self.points = [{'pt' : pt, 'tracking': self.updateTracking(self.points[idx],pt)  } for idx, pt in enumerate(newpoints)]

                for the_point in self.points:

                    cvCircle (self.image, cvPointFrom32f(the_point['pt']),
                                 3, self.colorForPoint(the_point), #cvScalar (0, 255, 0, 0),
                                 -1, 8, 0)

            cvShowImage( self.window_name, self.image )
            
            self.prev_gray, self.gray = self.gray, self.prev_gray
            self.prev_pyramid, self.pyramid = self.pyramid, self.prev_pyramid
            
    def updateTracking(self,old_pt,new_pt):
        if old_pt['tracking'] is not None:
            direction = old_pt['tracking']['dir']
            current_amount = old_pt['tracking']['cnt']
            current_frame = old_pt['tracking']['cur']
            max_frame = old_pt['tracking']['max']
            
            if current_frame < max_frame:
            
                diffX = new_pt.x - old_pt['pt'].x
            
                current_amount = current_amount + diffX
#                print "diffX: %s" % diffX
                return {'dir' : direction, 'cnt' : current_amount, 'cur' : current_frame+1, 'max' : max_frame}
            else:
                return old_pt['tracking']
        else:
            return None

    def colorForPoint(self,pt):
#        print pt['tracking']
        if pt['tracking'] is None:
            return cvScalar(0,255,0,0)
        elif pt['tracking']['cur'] < pt['tracking']['max']:
            print "cur: %s max:%s diff:%s" % (pt['tracking']['cur'],pt['tracking']['max'],pt['tracking']['max']-pt['tracking']['cur'])
            return cvScalar(255,0,0,0)

        percentCount = 255.0 * pt['tracking']['cnt']*100.0
        
        if pt['tracking']['dir'] == "left":
            return cvScalar(0,0,int(255.0 * pt['tracking']['cnt']*100.0/self.sizeX),0)
        elif pt['tracking']['dir'] == "right":
            return cvScalar(0,0,abs(int(255.0 * pt['tracking']['cnt']*100.0/self.sizeX)),0)
        
        return cvScalar(128,128,128,128)

    def checkInput(self,cv_image):
        c = '%c' % (cvWaitKey(10) & 255)
        if c == 'f':
            grayscale_img = self.gray
            self.points = [{'pt' : pt, 
                'tracking' : None
            } for pt in cvGoodFeaturesToTrack(grayscale_img, None, None, None, 500, 0.01, 10)]

    #        cvFindCornerSubPix (
    #            grayscale_img,
    #            self.points,
    #            cvSize (10, 10), cvSize (-1, -1),
    #            cvTermCriteria (CV_TERMCRIT_ITER | CV_TERMCRIT_EPS,
    #                               20, 0.03))
        elif c == 'r':
            print "r!"
            self.points = [ self.updateTrackingDict(pt,{'dir' : 'right', 'cur' : 0, 'max' : 30, 'cnt' : 0}) for pt in self.points]
        elif c == 'l':
            print "l!"
            self.points = [ self.updateTrackingDict(pt,{'dir' : 'left', 'cur' : 0, 'max' : 30, 'cnt' : 0}) for pt in self.points]

    def updateTrackingDict(self,pt, new_tracking):
        pt.update(tracking=new_tracking)
        return pt

    #http://stackoverflow.com/questions/1807528/python-opencv-converting-images-taken-from-capture
    def getGrayscaleImage(self,img):
        img_size = cvSize(640,480)
    
        newFrameImage32F = cvCreateImage(img_size, IPL_DEPTH_32F, 3)
        cvConvertScale(img,newFrameImage32F)

        newFrameImageGS_32F = cvCreateImage (img_size, IPL_DEPTH_32F, 1)
        cvCvtColor(newFrameImage32F,newFrameImageGS_32F,CV_RGB2GRAY)

        newFrameImageGS = cvCreateImage (img_size, IPL_DEPTH_8U, 1)
        cvConvertScale(newFrameImageGS_32F,newFrameImageGS)
    
        return newFrameImageGS

PointTracker()