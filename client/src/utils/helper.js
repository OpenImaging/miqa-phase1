export function cleanDatasetName(name) {
  return name.replace(/.nii.gz$/, "");
}
