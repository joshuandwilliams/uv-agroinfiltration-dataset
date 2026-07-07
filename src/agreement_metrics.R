# Shared inter-rater agreement calculations used across the R analyses in
# analyses/. Source with: source(here::here("src", "agreement_metrics.R"))

#' Build a scorer x CDA matrix from a wide 3-scorer/3-score table.
#'
#' Suitable as input to irr::kripp.alpha().
#'
#' @param score_data A data frame with Basename, Row, Col, Pos, and
#'   Scorer1/Score1, Scorer2/Score2, Scorer3/Score3 columns.
#' @return A matrix with one row per scorer (rownames = scorer ID) and one
#'   column per CDA.
build_scorer_matrix <- function(score_data) {
  long <- score_data |>
    dplyr::select(Basename, Row, Col, Pos, Scorer1, Score1, Scorer2, Score2, Scorer3, Score3) |>
    tidyr::pivot_longer(
      cols          = c(Scorer1, Score1, Scorer2, Score2, Scorer3, Score3),
      names_to      = c(".value", "num"),
      names_pattern = "(Scorer|Score)(\\d+)"
    ) |>
    dplyr::select(-num) |>
    dplyr::filter(!is.na(Scorer), !is.na(Score)) |>
    dplyr::mutate(
      CDA_ID = paste(Basename, Row, Col, Pos, sep = "_"),
      Scorer = as.integer(Scorer)
    )

  long |>
    dplyr::select(Scorer, CDA_ID, Score) |>
    tidyr::pivot_wider(names_from = CDA_ID, values_from = Score) |>
    tibble::column_to_rownames("Scorer") |>
    as.matrix()
}

#' Bootstrap Krippendorff's alpha over repeated column resamples of a scorer matrix.
#'
#' @param matrix A scorer x item matrix, as built by build_scorer_matrix().
#' @param method Distance metric passed to irr::kripp.alpha() (e.g.
#'   "ordinal", "interval").
#' @param n_boot Number of bootstrap replicates.
#' @param sample_size Number of columns to draw per replicate. Defaults to
#'   `ncol(matrix)` (a full-size resample); pass a smaller number for a
#'   fixed-size subsample.
#' @param replace Sample columns with replacement (TRUE, a classic bootstrap
#'   resample) or without (FALSE, a fixed-size subsample without repeats).
#' @param seed Random seed set immediately before resampling, for
#'   reproducibility. Pass NULL to skip seeding entirely and use the RNG
#'   state as-is - e.g. when the caller has already seeded once and is
#'   iterating this function over several groups, and wants the draws to
#'   continue advancing the RNG stream across groups rather than resetting
#'   for each one.
#' @param suppress_warnings Suppress kripp.alpha()'s warnings (e.g. from
#'   degenerate resamples).
#' @return A numeric vector of length `n_boot`, the alpha value from each
#'   replicate.
bootstrap_kripp_alpha <- function(matrix, method, n_boot = 1000, sample_size = ncol(matrix),
                                  replace = FALSE, seed = 42, suppress_warnings = FALSE) {
  if (!is.null(seed)) set.seed(seed)
  draw_once <- function() {
    idx <- sample(ncol(matrix), sample_size, replace = replace)
    irr::kripp.alpha(matrix[, idx], method = method)$value
  }
  if (suppress_warnings) {
    replicate(n_boot, suppressWarnings(draw_once()))
  } else {
    replicate(n_boot, draw_once())
  }
}

#' Compute pairwise scorer-vs-scorer agreement from a long score table.
#'
#' For every CDA, compares every pair of scorers who scored it and tallies
#' exact-match agreement, symmetrised so (A, B) and (B, A) both appear.
#'
#' @param score_data_long A long score table (see long_score_table()) with
#'   Basename, Row, Col, Pos, Scorer, Score columns.
#' @return A data frame with one row per (Scorer.x, Scorer.y) pair where
#'   Scorer.x < Scorer.y, columns Total (shared CDA count), Agree (exact
#'   matches), and Percent_Agree. Pairs with no shared CDAs get NA rather
#'   than being dropped. Scorer.y is an ordered factor.
pairwise_score_data <- function(score_data_long) {
  data <- score_data_long |>
    dplyr::mutate(Score = as.numeric(Score)) |>
    dplyr::group_by(Basename, Row, Col, Pos) |>
    dplyr::mutate(id = dplyr::row_number()) |>
    dplyr::ungroup()

  pairwise_comparisons <- data |>
    dplyr::full_join(data, by = c("Basename", "Row", "Col", "Pos"), relationship = "many-to-many") |>
    dplyr::filter(id.x < id.y) |>
    dplyr::select(Scorer.x, Score.x, Scorer.y, Score.y) |>
    dplyr::group_by(Scorer.x, Score.x, Scorer.y, Score.y) |>
    dplyr::summarise(Count = dplyr::n(), .groups = "drop")

  filtered_data <- pairwise_comparisons |>
    dplyr::filter(!is.na(Score.x) & !is.na(Score.y))

  filtered_copy <- filtered_data
  names(filtered_copy)[names(filtered_copy) %in% c("Scorer.x", "Scorer.y")] <- c("Scorer.y", "Scorer.x")
  filtered_data <- rbind(filtered_data, filtered_copy)

  agreement_data <- filtered_data |>
    dplyr::group_by(Scorer.x, Scorer.y) |>
    dplyr::summarise(
      Total = sum(Count),
      Agree = sum(Count * (Score.x == Score.y)),
      Percent_Agree = (Agree / Total) * 100,
      .groups = "drop"
    ) |>
    dplyr::filter(as.integer(Scorer.x) < as.integer(Scorer.y))

  all_combinations <- expand.grid(
    Scorer.x = unique(agreement_data$Scorer.x),
    Scorer.y = unique(agreement_data$Scorer.y)
  )

  merged_df <- all_combinations |>
    dplyr::left_join(agreement_data, by = c("Scorer.x", "Scorer.y")) |>
    dplyr::mutate(dplyr::across(c(Total, Agree, Percent_Agree), ~ ifelse(is.na(.), NA, .))) |>
    dplyr::filter(as.integer(Scorer.x) < as.integer(Scorer.y))

  merged_df$Scorer.y <- factor(merged_df$Scorer.y, levels = sort(unique(merged_df$Scorer.y)))
  merged_df
}

#' Weighted average pairwise agreement across scorer pairs.
#'
#' @param data Output of pairwise_score_data(): must have Total and
#'   Percent_Agree columns.
#' @return A single number: the agreement percentage across all shared
#'   CDAs, weighted by how many CDAs each pair shares.
average_pairwise_agreement <- function(data) {
  valid_data <- data[!is.na(data$Total) & !is.na(data$Percent_Agree), ]
  sum(valid_data$Percent_Agree * valid_data$Total) / sum(valid_data$Total)
}
