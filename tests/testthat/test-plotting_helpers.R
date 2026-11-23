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

test_that("make_save_plot saves into the analysis's plot folder", {
  root <- withr::local_tempdir()
  dir.create(file.path(root, "analyses", "99_example", "supp_plots"), recursive = TRUE)
  local_mocked_bindings(here = function(...) file.path(root, ...), .package = "here")

  save_plot <- make_save_plot("99_example")
  p <- ggplot2::ggplot(data.frame(x = 1:3, y = 1:3), ggplot2::aes(x, y)) +
    ggplot2::geom_point()
  save_plot(p, "example.png", width = 2, height = 2)

  expect_true(file.exists(file.path(root, "analyses", "99_example", "supp_plots", "example.png")))
})
