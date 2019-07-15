export default {
  cjv: {
    display: "CJV",
    fullname: "Coefficient of Joint Variation",
    description:
      "Higher values are related to the presence of heavy head motion and large INU artifacts. So, <b>lower values are preferred.</b>"
  },
  cnr: {
    display: "CNR",
    fullname: "Contrast-to-Noise Ratio",
    description:
      "An extension of the SNR calculation to evaluate how separated the tissue distributions of GM and WM are. <b>Higher values indicate better quality.</b>"
  },
  efc: {
    display: "EFC",
    fullname: "Entropy-Focus Criterion",
    description:
      "Uses the Shannon entropy of voxel intensities as an indication of ghosting and blurring induced by head motion. <b>Lower values are better</b>."
  },
  fber: {
    display: "FBER",
    fullname: "Foreground-Background Energy Ratio",
    description:
      "Calculated as the mean energy of image values within the head relative the mean energy of image values in the air mask. Consequently, <b>higher values are better</b>."
  },
  fwhm: {
    display: "FWHM",
    fullname: "Full-Width Half-Maximum",
    description:
      "An estimation of the blurriness of the image using AFNI’s 3dFWHMx. <b>Smaller is better</b>. It is calculated for x-axis, y-axis, z-axis, and average value."
  },
  icvs: {
    display: "ICV",
    fullname: "Intra-Cranial Volume",
    description:
      "Estimation of the icv of each tissue calculated on the FSL FAST’s segmentation. <b>Normative values fall around 20%, 45% and 35% for cerebrospinal fluid (CSF), White Matter (WM), and Grey Matter (GM), respectively</b>. Thus, it provides 3 values."
  },
  inu: {
    display: "INU",
    fullname: "Intensity Non-Uniformity",
    description:
      "MRIQC measures the location and spread of the bias field extracted estimated by the inu correction. The <b>smaller spreads located around 1.0 are better</b>. It provides the median and range for INU, thus 2 values."
  },
  qi: {
    display: "QI",
    fullname: "Quality Index",
    description:
      "1: measures the amount of artifactual intensities in the air surrounding the head above the nasio-cerebellar axis. <br /> 2: a calculation of the goodness-of-fit of a chi-square distribution on the air mask. <b>The smaller the better</b> for both numbers."
  },
  rpve: {
    display: "rPVE",
    fullname: "Residual Partial Volume Effect",
    description:
      "A tissue-wise sum of partial volumes that fall in the range [5%-95%] of the total volume of a pixel. <b>Smaller residual partial volume effects (rPVEs) are better</b>. It provides the score for cerebro-spinal fluid(CSF), white matter(WM), grey matter(GM)."
  },
  size: {
    display: "size",
    fullname: "",
    description: ""
  },
  snr: {
    display: "SNR",
    fullname: "Signal-to-Noise Ratio",
    description:
      "SNR is reported using air background as noise reference for cerebro-spinal fluid(CSF), white matter(WM), grey matter(GM), and total. Also, a simplified calculation using the within tissue variance is also provided for CSF, WM, GM, and total image. <b>Higher the SNR, the better</b> the image quality."
  },
  snrd: {
    display: "SNRd",
    fullname: "Signal-to-Noise Ratio-dietrich",
    description:
      "SNR is reported using air background as noise reference for cerebro-spinal fluid(CSF), white matter(WM), grey matter(GM), and total. Also, a simplified calculation using the within tissue variance is also provided for CSF, WM, GM, and total image using SNR-dietrich. <b>Higher the SNR, the better</b> the image quality."
  },
  spacing: {
    display: "spacing",
    fullname: "",
    description: ""
  },
  summary_bg: {
    display: "SSTATS background",
    fullname: "Summary Statistics Background",
    description:
      "Several summary statistics (mean, standard deviation, percentiles 5% and 95%, and kurtosis) are computed within the following regions of interest: background, CSF, WM, and GM. There are 8 scores for each region, thus 32 values are reported."
  },
  summary_csf: {
    display: "SSTATS CSF",
    fullname: "Summary Statistics CSF",
    description:
      "Several summary statistics (mean, standard deviation, percentiles 5% and 95%, and kurtosis) are computed within the following regions of interest: background, CSF, WM, and GM. There are 8 scores for each region, thus 32 values are reported."
  },
  summary_gm: {
    display: "SSTATS GM",
    fullname: "Summary Statistics GM",
    description:
      "Several summary statistics (mean, standard deviation, percentiles 5% and 95%, and kurtosis) are computed within the following regions of interest: background, CSF, WM, and GM. There are 8 scores for each region, thus 32 values are reported."
  },
  summary_wm: {
    display: "SSTATS WM",
    fullname: "Summary Statistics WM",
    description:
      "Several summary statistics (mean, standard deviation, percentiles 5% and 95%, and kurtosis) are computed within the following regions of interest: background, CSF, WM, and GM. There are 8 scores for each region, thus 32 values are reported."
  },
  tpm_overlap: {
    display: "TPMs",
    fullname: "Tissue Probability Maps",
    description:
      "Overlap of tissue probability maps estimated from the image and the corresponding maps from the ICBM nonlinear-asymmetric 2009c template. TPM is calculated for CSF, WM, and GM."
  },
  wm2max: {
    display: "WM2MAX",
    fullname: "White Matter to Maximum Intensity Ratio",
    description:
      "The white-matter to maximum intensity ratio is the median intensity within the WM mask over the 95% percentile of the full intensity distribution, that captures the existence of long tails due to hyper-intensity of the carotid vessels and fat. <b>Values should be around the interval [0.6, 0.8].</b>"
  }
};
