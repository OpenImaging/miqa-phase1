import vtkXMLPolyDataReader from 'vtk.js/Sources/IO/XML/XMLPolyDataReader';
import vtkXMLImageDataReader from 'vtk.js/Sources/IO/XML/XMLImageDataReader';
import vtkSTLReader from 'vtk.js/Sources/IO/Geometry/STLReader';
import vtkOBJReader from 'vtk.js/Sources/IO/Misc/OBJReader';
import vtkPDBReader from 'vtk.js/Sources/IO/Misc/PDBReader';
import vtkJSONReader from 'vtk.js/Sources/IO/Misc/JSONReader';
import vtkSkyboxReader from 'vtk.js/Sources/IO/Misc/SkyboxReader';


import vtkITKImageReader from 'vtk.js/Sources/IO/Misc/ITKImageReader';

import extensionToImageIO from 'itk/extensionToImageIO';
import readImageArrayBuffer from 'itk/readImageArrayBuffer';


// import vtkGlanceStateReader from 'paraview-glance/src/io/GlanceStateReader';
// import vtkGlanceZipObjReader from 'paraview-glance/src/io/GlanceZipObjReader';
import ReaderFactory from './ReaderFactory';
import vtkITKDicomImageReader from './ITKDicomImageReader';

// ----------------------------------------------------------------------------
// Register default readers
// ----------------------------------------------------------------------------

// enable loading of *.glance files
// ReaderFactory.registerReader({
//   extension: 'glance',
//   name: 'Glance State Reader',
//   vtkReader: vtkGlanceStateReader,
//   binary: true,
// });

// enable loading of *.obz files (zip of (obj/mtl/jpg))
// ReaderFactory.registerReader({
//   extension: 'obz',
//   name: 'OBJ bundle',
//   vtkReader: vtkGlanceZipObjReader,
//   binary: true,
// });

ReaderFactory.registerReader({
  extension: 'vtp',
  name: 'Polydata Reader',
  vtkReader: vtkXMLPolyDataReader,
  binary: true,
});

ReaderFactory.registerReader({
  extension: 'vti',
  name: 'ImageData Reader',
  vtkReader: vtkXMLImageDataReader,
  binary: true,
});

ReaderFactory.registerReader({
  extension: 'stl',
  name: 'STL Binary Reader',
  vtkReader: vtkSTLReader,
  binary: true,
});

ReaderFactory.registerReader({
  extension: 'obj',
  name: 'OBJ Reader',
  vtkReader: vtkOBJReader,
  binary: false,
});

ReaderFactory.registerReader({
  extension: 'pdb',
  name: 'PDB Reader',
  vtkReader: vtkPDBReader,
  binary: false,
  sourceType: 'vtkMolecule',
});

ReaderFactory.registerReader({
  extension: 'glyph',
  name: 'Glyph Data Reader',
  vtkReader: vtkJSONReader,
  binary: false,
  sourceType: 'Glyph',
});

ReaderFactory.registerReader({
  extension: 'skybox',
  name: 'Skybox Data Reader',
  vtkReader: vtkSkyboxReader,
  binary: true,
  sourceType: 'Skybox',
});



vtkITKImageReader.setReadImageArrayBufferFromITK(readImageArrayBuffer);

const extensions = Array.from(
  new Set(Object.keys(extensionToImageIO).map((ext) => ext.toLowerCase()))
);

extensions.filter((e) => e !== 'dcm').forEach((extension) =>
  ReaderFactory.registerReader({
    extension,
    name: `${extension.toUpperCase()} Reader`,
    vtkReader: vtkITKImageReader,
    binary: true,
    fileNameMethod: 'setFileName',
  })
);

ReaderFactory.registerReader({
  extension: 'dcm',
  name: 'DICOM File Series Reader',
  vtkReader: vtkITKDicomImageReader,
  fileNameMethod: 'setFileName',
  fileSeriesMethod: 'readFileSeries',
});
