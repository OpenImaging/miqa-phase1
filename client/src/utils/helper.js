export function cleanDatasetName(name) {
  let cleanName = name.replace(/^image/, "").replace(/.nii.gz$/, "");
  if (cleanName == "") {
    return "1";
  }
  return cleanName;
}
