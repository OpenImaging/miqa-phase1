# Introduction

This document describes the data import JSON format as well as how to use it
to import arbitrary data into the MIQA application.

# JSON format

The project contains a trivial sample dataset, located in the `sample_data`
directory.  The `sample.json` file in that directory is a descriptor file
that describes the organization of the sample dataset in sufficient detail
for MIQA to be able to import it.  By looking at the layout of the `sample_data`
directory structure while examining the `sample.json` file, you should get a
good idea of the meaning of the various keys in the descriptor file.  However,
there is also a schema for the data import description format located in
`server/miqa_server/schema/data_import.py`, and the schema specifies the
allowed syntax.  The schema is also used to validate the json file before it
can be used to import a dataset into the MIQA application.

Data to be imported into MIQA can be thought of as existing in a session.  A
session is composed of one or more experiments, and each experiment is made up
of one or more scans.  A scan is either a 3D image file, or may have a time
component as well (e.g. FMRI).  In either case, the heavy data associated with
a scan is usually one or more nifti files (`.nii.gz`).

## Specifying the root of the data to import

The first thing to note about the data import format is that it contains a
top level key `data_root`, which should point to a root location on the file
system underneath which all the experiments and scans are housed.  Usually
the json description file lives there as well, but that is not required.

## Specifying location of scans

The next thing to notice is that the `scans` key is a list corresponding to
individual scans, and that each scan has a `path` which should be the
relative path under `data_root` where the images for that scan live.  By
setting `path` to the empty string, you're telling MIQA that all the scans
live together in the `data_root` directory.

## Describing images within a scan

Within a scan, there are two methods for describing the images that make up
that scan: `images` and `imagePattern`.  Using `imagePattern` is more
efficient when MIQA is importing the data for the first time, but has some
constraints which prevent you from using it in some cases.  `images` is a
little less efficient, but works in all cases.

### Specifying images with `imagePattern`

If the nifti files within a scan are named in such a way that sorting them
alphabetically results in the properly ordered sequence of images, and if you
can write a simple regular expression to find them all, then you should use
`imagePattern`.

For example, if you have 12 images named as follows:

```
image01.nii.gz
image02.nii.gz
image03.nii.gz
image04.nii.gz
image05.nii.gz
image06.nii.gz
image07.nii.gz
image08.nii.gz
image09.nii.gz
image10.nii.gz
image11.nii.gz
```

Then your `scan` item in the JSON descriptor can specify:

```
    "imagePattern": "nii\\.gz"
```

Which means that any file in the `path` directory that has "nii.gz" somewhere
in the filename belongs to the scan.  The `imagePattern` key gives you the full
power of regular expressions, in case a more complicated expression is required
to pick out the images associated with a particular scan.

Note that in the example filenames above, there is proper left zero padding in
the image numbers so that if the filenames are sorted alphabetically, they'll
come out in the order shown above, which is likely the right order for a time
sequence of images.  Note also that without that left zero padding, `image10.nii.gz`
and `image11.nii.gz` would come right after `image1.nii.gz` and right before
`image2.nii.gz`.

Consider the case where those same images are named another way, however:


```
one.nii.gz
two.nii.gz
three.nii.gz
four.nii.gz
five.nii.gz
six.nii.gz
seven.nii.gz
eight.nii.gz
nine.nii.gz
ten.nii.gz
eleven.nii.gz
```

In a situation like the one above, even though the same `imagePattern` could be
used to pick out the images associated with the scan, alphabetically sorting the
files by name would not result in the proper ordering of the images.  In this
situation, you should use `images` instead of `imagePattern` to describe the
images which make up the scan.

### Specifying images with `images`

In cases like the one described above, when you cannot pick out the images
associated with a scan from within a directory using a pattern match, or when
the image order would be incorrect using alphabetical sorting, you can simply
provided a list of filenames using the `images` key:

```
    "images": [
        "one.nii.gz",
        "two.nii.gz",
        "three.nii.gz",
        "four.nii.gz"
    ]
```

This lets you specify unambiguously the images you want from the directory as
well as the order in which they belong.

## Associating sites and experiments

The JSON format also allows you to provide lists of `sites` and `experiments`,
each instance of which is identified by an `id` field.  Then scans can refer
to those sites or experiments using `site_id` and `experiment_id` keys.

## Specifying arbitrary data

If you have arbitrary data in the form of key/value pairs you want to associate
with a scan, those can be specified using the  `user_fields` key within the
`scan`.  For example:

```
    "user_fields": {
        "MQy:VRX": "0.94",
        "MQy:VRY": "0.94",
        "MQy:VRZ": "1.2",
        "MQy:ROWS": "256"
    }
```

These values will be picked up by the import process and added as individual
metadata items to the folder containing the scan images.
