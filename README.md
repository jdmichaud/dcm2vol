# dcm2vol

From a list of dicom files, generates a volume file.

## Usage

```bash
pip install -f requirements.txt
python3 dcm2vol /path/to/dicom/*
```

This will load all the DICOM files provided, split in series and then split
the first series into volume and dump the first volume to standard output.

## Volume format

The volume file start with a one line text header from which data separated by one or more space.
The token are as follows:
* Columns
* Rows
* BitsAllocated
* PhotometricInterpretation
* PixelRepresentation
* PaddingValue
* RescaleSlope
* RescaleIntercept
* WindowCenter
* WindowWidth
* ImageOrientationPatient x0
* ImageOrientationPatient x1
* ImageOrientationPatient x2
* ImageOrientationPatient y0
* ImageOrientationPatient y1
* ImageOrientationPatient y2
* ImagePositionPatient 0
* ImagePositionPatient 1
* ImagePositionPatient 2
* PixelSpacing y
* PixelSpacing x
* Number of bytes the volume contains (number of voxels also depends on BitsAllocated)
* New line character

Then the volume data is stored in binary. The number of bytes is provided as the last token of the
header, right before the new line character.
