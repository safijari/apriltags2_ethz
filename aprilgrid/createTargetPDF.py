#!/usr/bin/python
# Thomas Schneider, Sept 2013
# Codes from AprilTags C++ Library (http://people.csail.mit.edu/kaess/apriltags/)

from pyx import *
import argparse
import sys

import os
import math
import numpy as np

from tagFamilies import *

class AprilTagCodes:
    def __init__(self, chosenTagFamiliy):
        try:
            self.chosenTagFamiliy = chosenTagFamiliy
            self.tagCodes = TagFamilies[chosenTagFamiliy][0]
            self.totalBits = TagFamilies[chosenTagFamiliy][1]
        except:
            print "[ERROR]: Unknown tag familiy."
            sys.exit(0)

#borderBits must be consitent with the variable "blackBorder" in the detector code in file ethz_apriltag2/src/TagFamily.cc
def generateAprilTag(canvas, position, metricSize, tagSpacing, tagID, tagFamililyData, rotation=2, symmCorners=True, borderBits=2):
    #get the tag code
    try:
        tagCode=tagFamililyData.tagCodes[tagID]
    except:
        print "[ERROR]: Requested tag ID of {0} not available in the {1} TagFamiliy".format(tagID, tagFamililyData.chosenTagFamiliy)        

    #calculate the bit size of the tag
    sqrtBits = (math.sqrt(tagFamililyData.totalBits))
    bitSquareSize = metricSize / (sqrtBits+borderBits*2)
    
    #position of tag
    xPos = position[0]
    yPos = position[1]
    
    #borders (2x bit size)
    borderSize = borderBits*bitSquareSize

    c.fill(path.rect(xPos, yPos, metricSize, borderSize),[color.rgb.black]) #bottom
    c.fill(path.rect(xPos, yPos+metricSize-borderSize, metricSize, borderSize),[color.rgb.black]) #top
    c.fill(path.rect(xPos+metricSize-borderSize, yPos, borderSize, metricSize),[color.rgb.black]) #left
    c.fill(path.rect(xPos, yPos, borderSize, metricSize),[color.rgb.black]) #right
    
    #create numpy matrix of code
    codeMatrix = np.zeros((int(sqrtBits), int(sqrtBits)))
    for i in range(0, int(sqrtBits)):
        for j in range(0, int(sqrtBits)):
            if not tagCode & (1 << int(sqrtBits)*i+j):
                codeMatrix[i,j] = 1 
                 
    #rotation
    codeMatrix = np.rot90(codeMatrix, rotation)
    
    #bits
    for i in range(0, int(sqrtBits)):
        for j in range(0, int(sqrtBits)):
            if codeMatrix[i,j]:
                c.fill(path.rect(xPos+(j+borderBits)*bitSquareSize, yPos+((borderBits-1)+sqrtBits-i)*bitSquareSize, bitSquareSize, bitSquareSize),[color.rgb.black])
                
    #add squares to make corners symmetric (decreases the effect of motion blur in the subpix refinement...)
    if symmCorners:
        metricSquareSize = tagSpacing*metricSize
        
        corners = [ 
                    [xPos-metricSquareSize, yPos-metricSquareSize ],
                    [xPos+metricSize, yPos-metricSquareSize],
                    [xPos+metricSize, yPos+metricSize],
                    [xPos-metricSquareSize, yPos+metricSize] 
                  ]
        
        for point in corners:
            c.fill(path.rect(point[0], point[1], metricSquareSize, metricSquareSize),[color.rgb.black])

#tagSpaceing in % of tagSize
def generateAprilBoard(canvas, n_cols, n_rows, tagSize, tagSpacing=0.25, tagFamilily="t36h11"):
    
    if(tagSpacing<0 or tagSpacing>1.0):
        print "[ERROR]: Invalid tagSpacing specified.  [0-1.0] of tagSize"
        sys.exit(0)
        
    #convert to cm
    tagSize = tagSize*100.0
       
    #get the tag familiy data
    tagFamililyData = AprilTagCodes(tagFamilily)
    
    #create one tag
    numTags = n_cols*n_rows

    #draw tags
    for y in range(0,n_rows):
        for x in range(0,n_cols):
            id = n_cols * y + x
            pos = ( x*(1+tagSpacing)*tagSize, y*(1+tagSpacing)*tagSize)
            generateAprilTag(canvas, pos, tagSize, tagSpacing, id, tagFamililyData, rotation=2)
            #c.text(pos[0]+0.45*tagSize, pos[1]-0.7*tagSize*tagSpacing, "{0}".format(id))
    
    #draw axis
    pos = ( -1.5*tagSpacing*tagSize, -1.5*tagSpacing*tagSize)
    c.stroke(path.line(pos[0], pos[1], pos[0]+tagSize*0.3, pos[1]),
             [color.rgb.red,
              deco.earrow([deco.stroked([color.rgb.red, style.linejoin.round]),
              deco.filled([color.rgb.red])], size=tagSize*0.10)])
    c.text(pos[0]+tagSize*0.3, pos[1], "x")
    
    c.stroke(path.line(pos[0], pos[1], pos[0], pos[1]+tagSize*0.3),
             [color.rgb.green,
              deco.earrow([deco.stroked([color.rgb.green, style.linejoin.round]),
              deco.filled([color.rgb.green])], size=tagSize*0.10)])
    c.text(pos[0], pos[1]+tagSize*0.3, "y")

    #text
    caption = "{0}x{1} tags, size={2}cm and spacing={3}cm".format(n_cols,n_rows,tagSize,tagSpacing*tagSize)
    c.text(pos[0]+0.6*tagSize, pos[0], caption)


def generateCheckerboard(canvas, n_cols, n_rows, size_cols, size_rows):
    #convert to cm
    size_cols = size_cols*100.0
    size_rows = size_rows*100.0
    
    #message
    print "Generating a checkerboard with {0}x{1} corners and a box size of {2}x{3} cm".format(n_cols,n_rows,size_cols,size_rows)
    
    #draw boxes
    for x in range(0,n_cols+1):
        for y in range(0,n_rows+1):
            up_left_x = x*size_cols
            up_left_y = y*size_rows
            if (x+y+1)%2 != 0:
                c.fill(path.rect(up_left_x, up_left_y, size_cols, size_rows),[color.rgb.black])
    
    #print caption
    caption = "{0}x{1}@{2}x{3}cm".format(n_cols,n_rows,size_cols,size_rows)
    
    # text.preamble(r"\DeclareFixedFont{\LittleFont}{T1}{ptm}{b}{it}{0.75in}") #
    c.text(1.05*size_cols, 0.04*size_rows, caption)


if __name__ == "__main__":
    
    #setup the argument list
    parser = argparse.ArgumentParser(description='Generate a PDF with a calibration pattern.')
    parser.add_argument('output', nargs="?", default="target", help='Generator output file')
    
    parser.add_argument('--type', dest='gridType', default='apriltag', help='The grid pattern type. (\'apriltag\' or \'checkerboard\') (default: %(default)s)')
    
    parser.add_argument('--nx', type=int, default=6, dest='n_cols', help='The number of tags in x direction (default: %(default)s)\n')
    parser.add_argument('--ny', type=int, default=7, dest='n_rows', help='The number of tags in y direction (default: %(default)s)')
    
    parser.add_argument('--tsize', type=float, default=0.02, dest='tsize', help='The size of one tag [m] (default: %(default)s)')
    parser.add_argument('--tspace', type=float, default=0.25, dest='tagspacing', help='The space between the tags in fraction of the edge size [0..1] (default: %(default)s)')
    parser.add_argument('--tfam', default='t36h11', dest='tagfamiliy', help='Familiy of April tags {0} (default: %(default)s)'.format(TagFamilies.keys())) 
    
    parser.add_argument('--csx', type=float, default=0.03, dest='chessSzX', help='The size of one chessboard square in x direction [m] (default: %(default)s)')
    parser.add_argument('--csy', type=float, default=0.03, dest='chessSzY', help='The size of one chessboard square in y direction [m] (default: %(default)s)')
    
    parser.add_argument('--eps', action='store_true', dest='do_eps', help='Also output an EPS file', required=False)

    #Parser the argument list
    try:
        parsed = parser.parse_args()
    except:
        sys.exit(0)
 
    #open a new canvas
    c = canvas.canvas()
    
    #draw the board
    if parsed.gridType == "apriltag":
        generateAprilBoard(canvas, parsed.n_cols, parsed.n_rows, parsed.tsize, parsed.tagspacing, parsed.tagfamiliy)
    elif parsed.gridType == "checkerboard":
        generateCheckerboard(c, parsed.n_cols, parsed.n_rows, parsed.chessSzX, parsed.chessSzY)
    else:
        print "[ERROR]: Unknown grid pattern"
        sys.exit(0)
            
    #write to file
    c.writePDFfile(parsed.output)
    
    if parsed.do_eps:
        c.writeEPSfile(parsed.output)
    
    os.system("evince " + parsed.output + ".pdf &")
        
    

    
