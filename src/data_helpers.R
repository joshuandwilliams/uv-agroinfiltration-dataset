# Shared data-loading and reshaping helpers used across the R analyses in
# analyses/. Source with: source(here::here("src", "data_helpers.R"))

#' Load the scorer name -> anonymised integer ID lookup.
#'
#' Reads the canonical key written by
#' analyses/01_generate_raw_data/02_combining_cdascorer_outputs/combine_cdascorer.qmd
#'
#' @param as_character If TRUE, return the IDs as character rather than
#'   integer (useful when the result will be used as a label rather than
#'   numerically).
#' @param path Path to the key CSV. Defaults to the canonical repo path;
#'   overridable for testing.
#' @return A named vector: names are real scorer names, values are
#'   anonymised IDs (1-10).
load_scorer_key <- function(as_character = FALSE, path = NULL) {
  if (is.null(path)) {
    path <- here::here(
      "analyses", "01_generate_raw_data", "02_combining_cdascorer_outputs", "anonymisation_key.csv"
    )
  }
  anon_key <- readr::read_csv(path, show_col_types = FALSE)
  ids <- if (as_character) as.character(anon_key$ID) else as.integer(anon_key$ID)
  setNames(ids, anon_key$Scorer_Name)
}

#' Load the project name -> anonymised label key.
#'
#' @param path Path to the key CSV. Defaults to the canonical repo path
#'   (analyses/01_generate_raw_data/01_allocation_info/project_anonymisation_key.csv);
#'   overridable for testing.
#' @return A data frame with columns Project, Anon_Label, Dual_Infiltration.
load_project_key <- function(path = NULL) {
  if (is.null(path)) {
    path <- here::here(
      "analyses", "01_generate_raw_data", "01_allocation_info", "project_anonymisation_key.csv"
    )
  }
  readr::read_csv(path, show_col_types = FALSE)
}

#' Pivot a wide 3-scorer/3-score table into one row per (CDA, scorer).
#'
#' @param data A data frame with Basename, Row, Col, Pos, Scorer1/Score1,
#'   Scorer2/Score2, Scorer3/Score3 columns (and, if `include_median_score`,
#'   a Median_Score column).
#' @param include_median_score Keep the Median_Score column in the output.
#' @param drop_missing_scores Drop rows with a missing/placeholder ("[]" or
#'   NA) score. Set to FALSE to keep them, e.g. to analyse which scores were
#'   missed.
#' @return A long data frame with one row per (CDA, scorer): Basename, Row,
#'   Col, Pos, [Median_Score], Scorer (ordered factor), Score.
long_score_table <- function(data, include_median_score = TRUE, drop_missing_scores = TRUE) {
  id_cols <- c("Basename", "Row", "Col", "Pos")
  if (include_median_score) id_cols <- c(id_cols, "Median_Score")

  long <- data |>
    dplyr::select(dplyr::all_of(id_cols), Scorer1, Score1, Scorer2, Score2, Scorer3, Score3) |>
    tidyr::pivot_longer(
      cols          = c(Scorer1, Score1, Scorer2, Score2, Scorer3, Score3),
      names_to      = c(".value", "num"),
      names_pattern = "(Scorer|Score)(\\d+)"
    ) |>
    dplyr::select(-num) |>
    dplyr::filter(!is.na(Scorer))

  if (drop_missing_scores) {
    long <- long |> dplyr::filter(!is.na(Score), Score != "[]")
  }

  long$Scorer <- factor(long$Scorer, levels = sort(as.numeric(unique(long$Scorer))))
  long
}
