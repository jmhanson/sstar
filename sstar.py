#!/usr/bin/env python3
#
# sstar [n]
#   Draw a Siemens Star target with n spokes, default 20.
#
# https://en.wikipedia.org/wiki/Siemens_star
#
# 20210927 JMH Created, tracking changes in git.

import math
import argparse

# ------------------------------------------------------------
# Inits

# Letter: (612,792) pts
pageSize = (612, 792)
marginSize = 18

outFile = 'sstar.ps'


# ------------------------------------------------------------
# Subroutines

def write_tri(fb, triX, triY):
    """ Write PS commands for a single triangle to file buffer."""
    fb.write('newpath\n')
    fb.write('%f %f moveto\n' % (triX[0], triY[0]))
    fb.write('%f %f lineto\n' % (triX[1], triY[1]))
    fb.write('%f %f lineto\n' % (triX[2], triY[2]))            
    fb.write('closepath\n')
    fb.write('fill\n')


def xform_tri(mat, triX, triY):
    """ Apply 2x2 linear transformation defined in mat. """
    tx = [
        mat[0]*triX[0] + mat[1]*triY[0],
        mat[0]*triX[1] + mat[1]*triY[1],
        mat[0]*triX[2] + mat[1]*triY[2]
        ]
    ty = [
        mat[2]*triX[0] + mat[3]*triY[0],
        mat[2]*triX[1] + mat[3]*triY[1],
        mat[2]*triX[2] + mat[3]*triY[2]
        ]    
    return tx, ty


def main(argv=None):


    # ------------------------------------------------------------
    # Process inputs

    me = "sstar.py"
    parser = argparse.ArgumentParser(prog=me,
        description="Draw a Siemens Star target with n spokes."
        )
    parser.add_argument("n",
        nargs='?',
        type=int,
        help="Desired number of star spokes, minimum: 2, default: 20",
        default=20,
        )
    args = parser.parse_args(argv)
    assert args.n > 1, "Input n must be larger than 1"


    # ------------------------------------------------------------
    # Preliminary Calculations

    # Coordinate system
    transX = pageSize[0]/2
    transY = pageSize[1]/2
    xMax = transX - marginSize
    yMax = transY - marginSize
    dMin = min(xMax, yMax)
    scale = dMin

    # Angle spanned by a triangle (n triangles, spaced theta apart)
    theta = math.pi/args.n

    # Triangle (spoke) primitive, with the primary vertex at (0,0),
    # radial edges of length 1.0, and centerline along X. Note
    # that we don't close the path here. Apparently PS can do
    # this on its own.
    thetaH = theta/2.0
    triH = math.sin(thetaH)
    triL = math.cos(thetaH)
    triX = [0.0, triL,      triL]
    triY = [0.0, triH, -1.0*triH]

    # Incremental rotation matrix, row-major order
    thetaStep = theta*2.0
    cts = math.cos(thetaStep)
    sts = math.sin(thetaStep)
    rot = [cts, -1.0*sts, sts, cts]


    # ------------------------------------------------------------
    # Write ps file

    with open(outFile, 'w') as fb:

        # Header
        fb.write('%!PS-Adobe-2.0\n')
        fb.write('%%Creator: ' + me + '\n')
        fb.write('%%BoundingBox: 0 0 width height\n')
        fb.write('%%LanguageLevel: 2\n')
        fb.write('%%Pages: 1\n')

        # Page size
        fb.write('<< /PageSize [%s %s] >> setpagedevice\n' % pageSize)

        # Coordinate transformation
        fb.write('%s %s translate\n' % (transX, transY))
        fb.write('%f dup scale\n' % scale)

        # First triangle
        write_tri(fb, triX, triY)

        # Rotate and write remaining triangles
        for i in range(args.n-1):
            triX, triY = xform_tri(rot, triX, triY)
            write_tri(fb, triX, triY)

        fb.write('showpage\n')
        fb.write('%%EOF\n')

    print('Wrote %s' % outFile)


# This line makes the script importable without executing main()
# via import %%NAME
if __name__ == "__main__":
    raise SystemExit(main())
