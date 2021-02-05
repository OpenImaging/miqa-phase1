#!/usr/bin/env python3

import argparse
import itk
from numcodecs import Blosc
import zarr
from pathlib import Path
import numpy as np

def compress_encode(input_filepath,
                    output_directory,
                    multiscale=True,
                    chunk_size=64,
                    cname='zstd',
                    clevel=5,
                    shuffle=True):
    image = itk.imread(input_filepath)
    image_da = itk.xarray_from_image(image)
    dataset_name = str(Path(input_filepath))
    image_ds = image_da.to_dataset(name=dataset_name)

    store_name = output_directory
    store = zarr.DirectoryStore(store_name)

    blosc_shuffle = Blosc.SHUFFLE
    if not shuffle:
        blosc_shuffle = Blosc.NOSHUFFLE
    compressor = Blosc(cname=cname, clevel=clevel, shuffle=blosc_shuffle)

    image_ds.to_zarr(store,
                     mode='w',
                     group=f'0',
                     compute=True,
                     encoding={dataset_name: {'chunks': [chunk_size]*image.GetImageDimension(), 'compressor': compressor}})

    zarr.consolidate_metadata(store)

    if multiscale:
        # multi-resolution pyramid
        pyramid = [image_da]
        reduced = image
        while not np.all(np.array(itk.size(reduced)) < 64):
            scale = len(pyramid)
            shrink_factors = [2]*3
            for i, s in enumerate(itk.size(reduced)):
                if s < 4:
                    shrink_factors[i] = 1
            reduced = itk.bin_shrink_image_filter(reduced, shrink_factors=shrink_factors)
            reduced_da = itk.xarray_from_image(reduced).copy()
            pyramid.append(reduced_da)

        for scale in range(1, len(pyramid)):
            ds = pyramid[scale].to_dataset(name=dataset_name)
            ds.to_zarr(store,
                       mode='w',
                       group=f'{scale}',
                       compute=True,
                       encoding={dataset_name: {'chunks': [chunk_size]*3, 'compressor': compressor}})

        datasets = [ { 'path': f'{scale}/{dataset_name}' } for scale in range(len(pyramid)) ]
        with zarr.open(store) as z:
            z.attrs['multiscales'] = [{ 'version': '0.1', 'name': dataset_name, 'datasets': datasets }]

        # Re-consolidate entire dataset
        zarr.consolidate_metadata(store)
        for scale in range(0, len(pyramid)):
            store = zarr.DirectoryStore(str(Path(store_name) / f'{scale}'))
            # Also consolidate the metadata on the pyramid scales so they can be used independently
            zarr.consolidate_metadata(store)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Convert and encode a medical image file in a compressed Zarr directory store.')
    parser.add_argument('input_filepath', help='Path to input image file, e.g. a NIFTI file.')
    parser.add_argument('output_directory', help='Path to the output Zarr directory store.')

    parser.add_argument('--no-shuffle', action='store_true', help='Do not perform bit-shuffling during compression.')
    parser.add_argument('--chunk-size', default=64, type=int, help='Compression chunk size along one dimension.')
    parser.add_argument('--cname', default='zstd', help='Base compression codec.')
    parser.add_argument('--clevel', default=5, type=int, help='Compression level.')
    parser.add_argument('--no-multi-scale', action='store_true', help='Do not generate a multi-scale pyramid.')

    args = parser.parse_args()

    compress_encode(args.input_filepath,
                    args.output_directory,
                    multiscale=not args.no_multi_scale,
                    chunk_size=args.chunk_size,
                    cname=args.cname,
                    clevel=args.clevel,
                    shuffle=not args.no_shuffle)
