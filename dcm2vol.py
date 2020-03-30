#!/usr/bin/env python
from functools import reduce
import sys

import numpy as np
import pydicom

def normalize(a, axis=-1, order=2):
  l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
  l2[l2 == 0] = 1
  return a / np.expand_dims(l2, axis)

def getSpatialOrder(instance):
  x = normalize([float(i) for i in instance.ImageOrientationPatient[:3]])
  y = normalize([float(i) for i in instance.ImageOrientationPatient[3:]])
  z = np.cross(x, y)
  imagePositionPatient = [float(i) for i in instance.ImagePositionPatient]
  return np.dot(z, imagePositionPatient)

def autoWindowing(instances, paddingValue, rescaleSlope, rescaleIntercept):
  min = 0
  max = 0
  count = 0

  pixelSet = set()
  histogram = {}
  for instance in instances:
    for lines in instance.pixel_array:
      for pixel in lines:
        if pixel == paddingValue: continue
        histogram[pixel] = histogram.get(pixel, 0) + 1
        count += 1
        if min > pixel: min = pixel
        if max < pixel: max = pixel
        pixelSet.add(pixel)

  pixelArray = sorted(list(pixelSet))
  removed = 0
  whichEnd = 0
  while ((count - removed) / count) > 0.40:
    pixel = pixelArray.pop(0) if whichEnd % 2 else pixelArray.pop()
    whichEnd += 1
    removed += histogram.get(pixel)
    pixelSet.remove(pixel)

  remainingPixelArray = sorted(list(pixelSet))
  windowWidth = (remainingPixelArray[-1] * rescaleSlope + rescaleIntercept
    - remainingPixelArray[0] * rescaleSlope + rescaleIntercept)
  windowCenter = (remainingPixelArray[0] * rescaleSlope + rescaleIntercept) + windowWidth / 2

  from collections import namedtuple
  Windowing = namedtuple('Windowing', 'WindowWidth WindowCenter')
  return Windowing(int(windowWidth), int(windowCenter))

def main(argv):
  dcmfiles = [item for item in argv if pydicom.misc.is_dicom(item)]
  datasets = [pydicom.dcmread(file) for file in dcmfiles]
  seriess = {}
  for ds in datasets:
    if ds.SeriesInstanceUID not in seriess:
      seriess[ds.SeriesInstanceUID] = []
    seriess[ds.SeriesInstanceUID].append(ds)
  # Just take the first series and split it
  series = list(seriess.values())[0]
  series.sort(key=getSpatialOrder)
  paddingValue = series[0].PaddingValue if 'PaddingValue' in series[0] else 0
  windowing = (
    series[0] if 'WindowCenter' in series[0] and 'WindowWidth' in series[0]
    else autoWindowing(series, paddingValue, series[0].RescaleSlope, series[0].RescaleIntercept))
  header_fields = [
    series[0].Rows,
    series[0].Columns,
    series[0].BitsAllocated,
    series[0].PhotometricInterpretation,
    series[0].PixelRepresentation,
    paddingValue,
    series[0].RescaleSlope,
    series[0].RescaleIntercept,
    windowing.WindowCenter,
    windowing.WindowWidth,
    ' '.join([str(float(i)) for i in series[0].ImageOrientationPatient]),
    ' '.join([str(float(i)) for i in series[0].ImagePositionPatient]),
    ' '.join([str(float(i)) for i in series[0].PixelSpacing]),
    series[0].SliceThickness,
    reduce(lambda acc, value: acc + len(ds.pixel_array.tobytes()), series, 0),
  ]
  sys.stdout.write(' '.join([str(f) for f in header_fields]))
  sys.stdout.write('\n')
  sys.stdout.flush()
  for instance in series:
    sys.stdout.buffer.write(instance.pixel_array.tobytes())

if __name__ == '__main__':
  main(sys.argv)
