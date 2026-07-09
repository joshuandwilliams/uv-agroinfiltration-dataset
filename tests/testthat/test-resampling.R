source(here::here("src", "resampling.R"))

test_that("downsample_by_class balances every class to the smallest class's size", {
  data <- data.frame(
    Median_Score = c(rep(0, 10), rep(1, 3), rep(2, 5)),
    id = 1:18
  )

  result <- downsample_by_class(data, "Median_Score", seed = 1)

  counts <- table(result$Median_Score)
  expect_true(all(counts == 3))
  expect_equal(nrow(result), 9)
})

test_that("downsample_by_class is reproducible with the same seed", {
  data <- data.frame(Median_Score = c(rep(0, 20), rep(1, 5)), id = 1:25)

  first <- downsample_by_class(data, "Median_Score", seed = 42)
  second <- downsample_by_class(data, "Median_Score", seed = 42)

  expect_equal(first$id, second$id)
})

test_that("downsample_by_class gives different draws for different seeds", {
  # Class sizes must differ so the smaller class's size (10) actually
  # subsets the larger class (20) - equal-sized classes would sample every
  # row regardless of seed, just in a different order.
  data <- data.frame(Median_Score = c(rep(0, 20), rep(1, 10)), id = 1:30)

  first <- downsample_by_class(data, "Median_Score", seed = 1)
  second <- downsample_by_class(data, "Median_Score", seed = 2)

  expect_false(identical(sort(first$id), sort(second$id)))
})

test_that("downsample_by_class preserves other columns", {
  data <- data.frame(
    Median_Score = c(0, 0, 1, 1),
    Score = c(0, 1, 1, 2)
  )

  result <- downsample_by_class(data, "Median_Score", seed = 1)

  expect_true("Score" %in% names(result))
  expect_equal(nrow(result), 4)
})

test_that("repeated_undersampled_metric returns one value per iteration", {
  data <- data.frame(
    Median_Score = c(rep(0, 20), rep(1, 20), rep(2, 20)),
    Exact_Match = sample(c(TRUE, FALSE), 60, replace = TRUE)
  )

  result <- repeated_undersampled_metric(
    data, "Median_Score",
    metric_fn = function(d) mean(d$Exact_Match) * 100,
    n_iterations = 10
  )

  expect_length(result, 10)
  expect_true(is.numeric(result))
})

test_that("repeated_undersampled_metric is reproducible for the same seed_offset", {
  data <- data.frame(
    Median_Score = c(rep(0, 20), rep(1, 20)),
    Exact_Match = c(rep(TRUE, 15), rep(FALSE, 5), rep(TRUE, 10), rep(FALSE, 10))
  )
  metric_fn <- function(d) mean(d$Exact_Match) * 100

  first <- repeated_undersampled_metric(data, "Median_Score", metric_fn, n_iterations = 5)
  second <- repeated_undersampled_metric(data, "Median_Score", metric_fn, n_iterations = 5)

  expect_equal(first, second)
})

test_that("repeated_undersampled_metric's seed_offset shifts the draw sequence", {
  # Class sizes must differ (see downsample_by_class test above) so the draw
  # is actually a genuine subset rather than every row in shuffled order.
  data <- data.frame(
    Median_Score = c(rep(0, 20), rep(1, 10)),
    Exact_Match = c(rep(TRUE, 15), rep(FALSE, 5), rep(TRUE, 5), rep(FALSE, 5))
  )
  metric_fn <- function(d) mean(d$Exact_Match) * 100

  base <- repeated_undersampled_metric(data, "Median_Score", metric_fn, n_iterations = 5, seed_offset = 0)
  shifted <- repeated_undersampled_metric(data, "Median_Score", metric_fn, n_iterations = 5, seed_offset = 100)

  expect_false(identical(base, shifted))
})
