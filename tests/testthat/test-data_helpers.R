source(here::here("src", "data_helpers.R"))

test_that("long_score_table pivots wide scores to one row per scorer", {
  data <- data.frame(
    Basename = "img.tif", Row = 1, Col = 1, Pos = 1, Median_Score = 2,
    Scorer1 = 4, Score1 = 2, Scorer2 = 5, Score2 = 2, Scorer3 = 6, Score3 = 3,
    stringsAsFactors = FALSE
  )

  long <- long_score_table(data)

  expect_equal(nrow(long), 3)
  expect_setequal(as.character(long$Scorer), c("4", "5", "6"))
  expect_equal(long$Score[long$Scorer == "4"], 2)
  expect_equal(long$Score[long$Scorer == "6"], 3)
  expect_true(is.factor(long$Scorer))
  expect_equal(levels(long$Scorer), c("4", "5", "6"))
})

test_that("long_score_table can include or drop the Median_Score column", {
  data <- data.frame(
    Basename = "img.tif", Row = 1, Col = 1, Pos = 1, Median_Score = 2,
    Scorer1 = 4, Score1 = 2, Scorer2 = 5, Score2 = 2, Scorer3 = 6, Score3 = 3,
    stringsAsFactors = FALSE
  )

  expect_true("Median_Score" %in% names(long_score_table(data, include_median_score = TRUE)))
  expect_false("Median_Score" %in% names(long_score_table(data, include_median_score = FALSE)))
})

test_that("long_score_table drops missing/placeholder scores by default", {
  data <- data.frame(
    Basename = "img.tif", Row = 1, Col = 1, Pos = 1, Median_Score = 2,
    Scorer1 = 4, Score1 = "2", Scorer2 = 5, Score2 = "[]", Scorer3 = 6, Score3 = NA,
    stringsAsFactors = FALSE
  )

  dropped <- long_score_table(data)
  expect_equal(nrow(dropped), 1)
  expect_equal(as.character(dropped$Scorer), "4")

  kept <- long_score_table(data, drop_missing_scores = FALSE)
  expect_equal(nrow(kept), 3)
})

test_that("long_score_table drops rows with a missing scorer entirely", {
  data <- data.frame(
    Basename = "img.tif", Row = 1, Col = 1, Pos = 1, Median_Score = 2,
    Scorer1 = 4, Score1 = 2, Scorer2 = NA, Score2 = NA, Scorer3 = 6, Score3 = 3,
    stringsAsFactors = FALSE
  )

  long <- long_score_table(data, drop_missing_scores = FALSE)
  expect_equal(nrow(long), 2)
  expect_setequal(as.character(long$Scorer), c("4", "6"))
})

test_that("load_scorer_key builds a name -> ID lookup from a key CSV", {
  tmp <- withr::local_tempfile(fileext = ".csv")
  readr::write_csv(data.frame(ID = c(1, 2, 3), Scorer_Name = c("Alice", "Bob", "Carol")), tmp)

  key <- load_scorer_key(path = tmp)
  expect_equal(unname(key["Alice"]), 1L)
  expect_equal(unname(key["Bob"]), 2L)
  expect_true(is.integer(key))

  key_chr <- load_scorer_key(path = tmp, as_character = TRUE)
  expect_equal(unname(key_chr["Carol"]), "3")
  expect_true(is.character(key_chr))
})

test_that("load_project_key reads the project key CSV as-is", {
  tmp <- withr::local_tempfile(fileext = ".csv")
  readr::write_csv(
    data.frame(Project = "example_project", Anon_Label = "Project A", Dual_Infiltration = 0),
    tmp
  )

  key <- load_project_key(path = tmp)
  expect_equal(nrow(key), 1)
  expect_equal(key$Anon_Label, "Project A")
  expect_equal(key$Dual_Infiltration, 0)
})
