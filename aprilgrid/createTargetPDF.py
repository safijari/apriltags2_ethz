#!/usr/bin/python
# Codes from AprilTags C++ Library (http://people.csail.mit.edu/kaess/apriltags/)
import jonky as jk
import math
import numpy as np
from aprilgrid.tagFamilies import TagFamilies
from argh import dispatch_command
import os


class AprilTagCodes(object):
    def __init__(self, chosenTagFamily):
        self.chosenTagFamily = chosenTagFamily
        self.tagCodes = TagFamilies[chosenTagFamily][0]
        self.totalBits = TagFamilies[chosenTagFamily][1]


chosenTagFamily = "t36h11"
tagFamilyData = AprilTagCodes(chosenTagFamily)


def generateAprilTag(
    xPos,
    yPos,
    tagSize,
    tagSpacing,
    tagID,
    tagFamilyData,
    rotation=2,
    symmCorners=True,
    borderBits=2,
):
    # get the tag code
    metricSize = tagSize
    try:
        tagCode = tagFamilyData.tagCodes[tagID]
    except Exception:
        print(
            "[ERROR]: Requested tag ID of {0} not available in the {1} TagFamiliy".format(
                tagID, tagFamilyData.chosenTagFamily
            )
        )

    # calculate the bit size of the tag
    sqrtBits = math.sqrt(tagFamilyData.totalBits)
    bitSquareSize = metricSize / (sqrtBits + borderBits * 2)

    # borders (2x bit size)
    borderSize = borderBits * bitSquareSize

    out = jk.Group()
    sw = 0
    out.nodes.append(
        jk.Rectangle(stroke_width=sw, width=metricSize, height=borderSize, fill_color="black").set_pose(x=xPos, y=yPos)
    )
    out.nodes.append(
        jk.Rectangle(stroke_width=sw, width=metricSize, height=borderSize, fill_color="black").set_pose(
            x=xPos, y=yPos + metricSize - borderSize
        )
    )
    out.nodes.append(
        jk.Rectangle(stroke_width=sw, width=borderSize, height=metricSize, fill_color="black").set_pose(
            x=xPos + metricSize - borderSize, y=yPos
        )
    )
    out.nodes.append(
        jk.Rectangle(stroke_width=sw, width=borderSize, height=metricSize, fill_color="black").set_pose(x=xPos, y=yPos)
    )

    # create numpy matrix of code
    codeMatrix = np.zeros((int(sqrtBits), int(sqrtBits)))
    for i in range(0, int(sqrtBits)):
        for j in range(0, int(sqrtBits)):
            if not tagCode & (1 << int(sqrtBits) * i + j):
                codeMatrix[i, j] = 1

    # rotation
    codeMatrix = np.rot90(codeMatrix, rotation)

    # bits
    for i in range(0, int(sqrtBits)):
        for j in range(0, int(sqrtBits)):
            if codeMatrix[codeMatrix.shape[0] - i - 1, j]:
                out.nodes.append(
                    jk.Rectangle(
                        width=bitSquareSize,
                        height=bitSquareSize,
                        fill_color="black",
                        stroke_width=0,
                    ).set_pose(
                        xPos + (j + borderBits) * bitSquareSize,
                        yPos + ((borderBits - 1) + sqrtBits - i) * bitSquareSize,
                    )
                )
                # c.fill(path.rect(xPos+(j+borderBits)*bitSquareSize, yPos+((borderBits-1)+sqrtBits-i)*bitSquareSize, bitSquareSize, bitSquareSize),[color.rgb.black])

    # add squares to make corners symmetric (decreases the effect of motion blur in the subpix refinement...)
    if symmCorners:
        metricSquareSize = tagSpacing * metricSize
        corners = [
            [xPos - metricSquareSize, yPos - metricSquareSize],
            [xPos + metricSize, yPos - metricSquareSize],
            [xPos + metricSize, yPos + metricSize],
            [xPos - metricSquareSize, yPos + metricSize],
        ]

        for point in corners:
            out.nodes.append(
                jk.Rectangle(
                    metricSquareSize,
                    metricSquareSize,
                    fill_color="black",
                    stroke_width=0,
                ).set_pose(point[0], point[1])
            )

    return out


def generateAprilBoard(n_cols, n_rows, tagSize, tagSpacing=0.25, tagFamilily="t36h11", shift=0, dpi=300):

    if tagSpacing < 0 or tagSpacing > 1.0:
        raise Exception("[ERROR]: Invalid tagSpacing specified.  [0-1.0] of tagSize")

    # convert to cm
    # tagSize = tagSize*100.0
    tagSizeM = tagSize
    tagSize = tagSize * dpi * 39.3701

    canvas_w = (n_cols + 1) * tagSize + (n_cols + 1) * (tagSize * tagSpacing)
    canvas_h = (n_rows + 1) * tagSize + (n_rows + 1) * (tagSize * tagSpacing)

    canvas = jk.Group([jk.Rectangle(width=canvas_w, height=canvas_h, stroke_width=(tagSize * 0.01))])

    # get the tag familiy data
    tagFamililyData = AprilTagCodes(tagFamilily)

    # create one tag
    numTags = n_cols * n_rows

    out = jk.Group()
    canvas.nodes.append(out.set_pose(x=tagSize / 2 * 0, y=tagSize / 2 * 0))

    # draw tags
    for y in range(0, n_rows):
        for x in range(0, n_cols):
            tid = n_cols * y + x + shift
            pos = (
                x * (1 + tagSpacing) * tagSize + tagSize * (0.5 + tagSpacing),
                (n_rows - y) * (1 + tagSpacing) * tagSize - tagSize / 2,
            )
            out.nodes.append(
                generateAprilTag(x, y, tagSize, tagSpacing, tid, tagFamililyData, rotation=2).set_pose(*pos)
            )

    # draw axis
    pos = (-1.5 * tagSpacing * tagSize, -1.5 * tagSpacing * tagSize)
    canvas.nodes.append(
        jk.PangoText(
            f"{n_cols}x{n_rows} tags, size={tagSizeM*100}cm, spacing={tagSizeM*100*tagSpacing}cm, shift={shift}"
        ).set_pose(tagSize / 2, canvas_h - tagSize / 2)
    )
    return canvas, canvas_w, canvas_h


def main(columns=1, rows=1, size=0.02, spacing_fraction=25, shift=0):
    board, w, h = generateAprilBoard(columns, rows, size, spacing_fraction / 100.0, shift=shift)
    fname = f"board_{columns}x{rows}_{size}m_{spacing_fraction}pct_{shift}.pdf"
    canvas = jk.CanvasPS(w, h, fname, [board])
    canvas.draw()
    os.system(f"evince {fname}")
    pass


if __name__ == "__main__":
    dispatch_command(main)
