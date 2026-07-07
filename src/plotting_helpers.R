# Shared plotting helpers used across the R analyses in analyses/.
# Source with: source(here::here("src", "plotting_helpers.R"))

#' Severity palette: pale yellow (0 = no cell death) to deep red (6 = strong
#' cell death). Sequential YlOrRd, colourblind-safe.
sev_pal <- setNames(RColorBrewer::brewer.pal(7, "YlOrRd"), as.character(0:6))

#' Construct the output path for a saved analysis plot.
#'
#' @param analysis_dir Name of the analysis folder under `analyses/`, e.g.
#'   "05_inter_rater_agreement".
#' @param dir Subfolder within that analysis folder, e.g. "supp_plots" or
#'   "thesis_plots".
#' @param filename Plot filename, e.g. "score_counts.png".
#' @return The full path `analyses/<analysis_dir>/<dir>/<filename>`.
plot_output_path <- function(analysis_dir, dir, filename) {
  here::here("analyses", analysis_dir, dir, filename)
}

#' Build a save_plot() function bound to one analysis's output folder.
#'
#' @param analysis_dir Name of the analysis folder under `analyses/`, e.g.
#'   "05_inter_rater_agreement".
#' @return A function `save_plot(p, filename, width, height, dir =
#'   "supp_plots")` that saves ggplot `p` to
#'   `analyses/<analysis_dir>/<dir>/<filename>`.
make_save_plot <- function(analysis_dir) {
  function(p, filename, width, height, dir = "supp_plots") {
    ggplot2::ggsave(
      plot_output_path(analysis_dir, dir, filename),
      plot = p, width = width, height = height, units = "in", dpi = 300
    )
  }
}
