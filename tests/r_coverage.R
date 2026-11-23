# Run the testthat tests and measure coverage of the R code in src/.
# src/ holds sourced scripts, not a package, so covr::file_coverage() is used.
# Writes cobertura.xml for Codecov and stops if any test fails.
library(testthat)

src <- list.files("src", "[.]R$", full.names = TRUE)
tests <- list.files("tests/testthat", "^test-.*[.]R$", full.names = TRUE)

results <- lapply(tests, test_file, reporter = "summary", stop_on_failure = TRUE)

cov <- covr::file_coverage(src, tests)
print(cov)
covr::to_cobertura(cov, "cobertura.xml")
