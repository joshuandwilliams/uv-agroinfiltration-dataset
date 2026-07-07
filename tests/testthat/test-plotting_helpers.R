source(here::here("src", "plotting_helpers.R"))

test_that("plot_output_path builds the expected analyses/<dir>/<subdir>/<file> path", {
  expect_equal(
    plot_output_path("05_inter_rater_agreement", "supp_plots", "score_counts.png"),
    here::here("analyses", "05_inter_rater_agreement", "supp_plots", "score_counts.png")
  )
  expect_equal(
    plot_output_path("02_score_distributions", "thesis_plots", "cdaexamples.png"),
    here::here("analyses", "02_score_distributions", "thesis_plots", "cdaexamples.png")
  )
})

test_that("make_save_plot returns a function bound to its analysis_dir with a supp_plots default", {
  save_plot <- make_save_plot("05_inter_rater_agreement")

  expect_true(is.function(save_plot))
  expect_equal(formals(save_plot)$dir, "supp_plots")
})

test_that("sev_pal has one colour per score class 0-6", {
  expect_equal(names(sev_pal), as.character(0:6))
  expect_length(sev_pal, 7)
})
