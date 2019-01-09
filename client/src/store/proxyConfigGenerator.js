export default url => {
  return {
    options: {
      recycleViews: true
    },
    sources: [
      {
        id: "3",
        group: "Sources",
        name: "TrivialProducer",
        props: {
          name: "nifti.nii.gz",
          type: "vtkImageData",
          dataset: {
            name: "nifti.nii.gz",
            url: url
          }
        }
      }
    ],
    views: [],
    representations: [],
    fields: {}
  };
};
