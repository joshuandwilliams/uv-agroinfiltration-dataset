# Shared class-balanced resampling used across the R analyses in analyses/.
# Source with: source(here::here("src", "resampling.R"))
#
# Mirrors downsample_score_classes_csv() in src/human_performance.py, which
# is used the same way from 03_human_performance.qmd (Python). The two are
# separate implementations (R and Python can't share one file), kept
# functionally equivalent: downsample every class in a chosen column to the
# smallest class's size, without replacement, so no single class can
# dominate a metric computed over the result.

#' Downsample rows so every class in `class_col` has the same count (the
#' smallest class's size), without replacement.
#'
#' @param data A data frame containing `class_col`.
#' @param class_col Name (string) of the column whose distinct values define
#'   the classes to balance (e.g. "Median_Score").
#' @param seed Random seed set immediately before sampling, for
#'   reproducibility. Pass NULL to skip seeding entirely.
#' @return A data frame with the same columns as `data`, downsampled so
#'   every class in `class_col` has an equal number of rows.
downsample_by_class <- function(data, class_col, seed = NULL) {
  if (!is.null(seed)) set.seed(seed)

  min_count <- data |>
    dplyr::count(.data[[class_col]]) |>
    dplyr::pull(n) |>
    min()

  data |>
    dplyr::group_by(.data[[class_col]]) |>
    dplyr::slice_sample(n = min_count) |>
    dplyr::ungroup()
}

#' Repeatedly class-balance `data` and apply `metric_fn` to each resample,
#' returning the resulting distribution.
#'
#' Used to correct for class imbalance (e.g. severity score 0 being far more
#' common than the others) without the reported metric depending on one
#' arbitrary random draw - repeating many times over different random draws
#' turns that single potentially-lucky-or-unlucky subsample into a
#' distribution you can report a mean, SD, and CI for. See
#' 03_human_performance.qmd for the full rationale.
#'
#' @param data A data frame containing `class_col`.
#' @param class_col Name (string) of the column whose distinct values define
#'   the classes to balance.
#' @param metric_fn A function taking one downsampled data frame and
#'   returning a single numeric value.
#' @param n_iterations Number of resampling iterations.
#' @param seed_offset Added to the iteration index (1:n_iterations) to form
#'   each iteration's seed, so independent calls (e.g. one per project in a
#'   sensitivity analysis) can use non-overlapping seed streams.
#' @return A numeric vector of length `n_iterations`.
repeated_undersampled_metric <- function(data, class_col, metric_fn, n_iterations = 1000, seed_offset = 0) {
  vapply(
    seq_len(n_iterations),
    function(i) {
      resampled <- downsample_by_class(data, class_col, seed = i + seed_offset)
      metric_fn(resampled)
    },
    numeric(1)
  )
}
