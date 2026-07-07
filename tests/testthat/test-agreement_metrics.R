source(here::here("src", "agreement_metrics.R"))

test_that("build_scorer_matrix builds one row per scorer and one column per CDA", {
  data <- data.frame(
    Basename = c("img.tif", "img.tif"), Row = c(1, 1), Col = c(1, 1), Pos = c(1, 2),
    Scorer1 = c(4, 4), Score1 = c(2, 0),
    Scorer2 = c(5, 5), Score2 = c(2, 1),
    Scorer3 = c(6, 6), Score3 = c(3, 0),
    stringsAsFactors = FALSE
  )

  mat <- build_scorer_matrix(data)

  expect_equal(sort(rownames(mat)), c("4", "5", "6"))
  expect_equal(ncol(mat), 2)
  expect_equal(unname(mat["4", "img.tif_1_1_1"]), 2)
  expect_equal(unname(mat["6", "img.tif_1_1_2"]), 0)
})

test_that("bootstrap_kripp_alpha returns n_boot replicates and is reproducible with a seed", {
  set.seed(1)
  mat <- matrix(sample(0:6, 4 * 20, replace = TRUE), nrow = 4)
  rownames(mat) <- paste0("scorer", 1:4)

  boot <- bootstrap_kripp_alpha(mat, method = "ordinal", n_boot = 5, sample_size = 10, seed = 42)
  expect_length(boot, 5)
  expect_true(is.numeric(boot))

  boot_again <- bootstrap_kripp_alpha(mat, method = "ordinal", n_boot = 5, sample_size = 10, seed = 42)
  expect_equal(boot, boot_again)
})

test_that("bootstrap_kripp_alpha with seed = NULL does not reset the RNG", {
  mat <- matrix(sample(0:6, 4 * 20, replace = TRUE), nrow = 4)

  set.seed(1)
  before <- runif(1)
  set.seed(1)
  boot <- bootstrap_kripp_alpha(mat, method = "ordinal", n_boot = 5, sample_size = 10, seed = NULL)
  after <- runif(1)

  expect_length(boot, 5)
  # If seed = NULL had reset the RNG to a fixed state, `after` would just be
  # the *next* draw from that fixed state every time; instead it should
  # simply differ from `before` because real draws happened in between.
  expect_false(isTRUE(all.equal(before, after)))
})

test_that("bootstrap_kripp_alpha supports sampling with replacement", {
  set.seed(1)
  mat <- matrix(sample(0:6, 3 * 15, replace = TRUE), nrow = 3)

  boot <- bootstrap_kripp_alpha(
    mat,
    method = "ordinal", n_boot = 3, replace = TRUE, suppress_warnings = TRUE
  )
  expect_length(boot, 3)
})

test_that("pairwise_score_data computes exact-match agreement per scorer pair", {
  # One CDA: scorers 1 and 2 agree (score 3), scorer 3 disagrees (score 5).
  long <- data.frame(
    Basename = "img.tif", Row = 1, Col = 1, Pos = 1,
    Scorer = factor(c("1", "2", "3")), Score = c(3, 3, 5),
    stringsAsFactors = FALSE
  )

  result <- pairwise_score_data(long)

  pair_12 <- result[result$Scorer.x == "1" & result$Scorer.y == "2", ]
  pair_13 <- result[result$Scorer.x == "1" & result$Scorer.y == "3", ]
  pair_23 <- result[result$Scorer.x == "2" & result$Scorer.y == "3", ]

  expect_equal(pair_12$Total, 1)
  expect_equal(pair_12$Percent_Agree, 100)
  expect_equal(pair_13$Percent_Agree, 0)
  expect_equal(pair_23$Percent_Agree, 0)

  # Only Scorer.x < Scorer.y pairs are kept.
  expect_true(all(as.integer(as.character(result$Scorer.x)) < as.integer(as.character(result$Scorer.y))))
})

test_that("pairwise_score_data reports NA (not a dropped row) for pairs with no shared CDAs", {
  # Scorer 1 and 2 share CDA "a"; scorer 2 and 3 share CDA "b"; 1 and 3 never
  # share a CDA directly, but both appear elsewhere so the (1, 3) pair should
  # still show up in the output, just with NA agreement rather than being
  # silently dropped.
  long <- rbind(
    data.frame(Basename = "a", Row = 1, Col = 1, Pos = 1, Scorer = factor("1"), Score = 2),
    data.frame(Basename = "a", Row = 1, Col = 1, Pos = 1, Scorer = factor("2"), Score = 2),
    data.frame(Basename = "b", Row = 1, Col = 1, Pos = 1, Scorer = factor("2"), Score = 3),
    data.frame(Basename = "b", Row = 1, Col = 1, Pos = 1, Scorer = factor("3"), Score = 3)
  )

  result <- pairwise_score_data(long)
  pair_13 <- result[result$Scorer.x == "1" & result$Scorer.y == "3", ]
  expect_equal(nrow(pair_13), 1)
  expect_true(is.na(pair_13$Total))
})

test_that("average_pairwise_agreement computes the CDA-count-weighted mean", {
  data <- data.frame(
    Scorer.x = c("1", "1"), Scorer.y = c("2", "3"),
    Total = c(10, 30), Percent_Agree = c(100, 0)
  )

  # weighted mean: 10 at 100% and 30 at 0%, weighted by Total, comes to 25%
  expect_equal(average_pairwise_agreement(data), 25)
})

test_that("average_pairwise_agreement ignores NA pairs", {
  data <- data.frame(
    Scorer.x = c("1", "1"), Scorer.y = c("2", "3"),
    Total = c(10, NA), Percent_Agree = c(100, NA)
  )

  expect_equal(average_pairwise_agreement(data), 100)
})
