#!/usr/bin/env python3

import argparse
import itk
from numcodecs import Blosc
import zarr

def compress_encode(input_filepath,
                    output_directory,
                    chunk_size=64,
                    cname='zstd',
                    clevel=5,
                    shuffle=True):
    image = itk.imread(input_filepath)
    image_da = itk.xarray_from_image(image)
    dataset_name = input_filepath
    image_ds = image_da.to_dataset(name=dataset_name)

    store_name = output_directory
    store = zarr.DirectoryStore(store_name)

    blosc_shuffle = Blosc.SHUFFLE
    if not shuffle:
        blosc_shuffle = Blosc.NOSHUFFLE
    compressor = Blosc(cname=cname, clevel=clevel, shuffle=blosc_shuffle)

    image_ds.to_zarr(store,
                     mode='w',
                     compute=True,
                     encoding={dataset_name: {'chunks': [chunk_size]*image.GetImageDimension(), 'compressor': compressor}})

    zarr.consolidate_metadata(store)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Convert and encode a medical image file in a compressed Zarr directory store.')
    parser.add_argument('input_filepath', help='Path to input image file, e.g. a NIFTI file.')
    parser.add_argument('output_directory', help='Path to the output Zarr directory store.')

    parser.add_argument('--no-shuffle', action='store_true', help='Do not perform bit-shuffling during compression.')
    parser.add_argument('--chunk-size', default=64, type=int, help='Compression chunk size along one dimension.')
    parser.add_argument('--cname', default='zstd', help='Base compression codec.')
    parser.add_argument('--clevel', default=5, type=int, help='Compression level.')

    args = parser.parse_args()

    compress_encode(args.input_filepath,
                    args.output_directory,
                    chunk_size=args.chunk_size,
                    cname=args.cname,
                    clevel=args.clevel,
                    shuffle=not args.no_shuffle)
