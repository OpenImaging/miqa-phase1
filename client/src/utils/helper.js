export function cleanDatasetName(name) {
  return name.replace(/^image/, "").replace(/.nii.gz$/, "");
}
