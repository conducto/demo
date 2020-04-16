library(argparser, quietly=TRUE)
library(jsonlite, quietly=TRUE)

pp <- arg_parser("Summarize Monte Carlo results")
pp <- add_argument(pp, "dir", help="path to results in temp-data")

argv <- parse_args(pp)
print(argv)

# Use `conducto-temp-data list` command line tool to get all the file
cmd = sprintf("conducto-temp-data list --prefix=%s", argv$dir)
files = fromJSON(system(cmd, intern=TRUE))

names(files) <- gsub(".*/", "", files)
datas = lapply(files, function(f) {
    # Call `conducto-temp-data gets` to get an individual dataset. `gets` prints
    # the data exactly as is, and the data is JSON-encoded, so call fromJSON to
    # extract the data. If the data instead were CSV, we would do:
    #   read.csv(...)
    cmd = sprintf("conducto-temp-data gets --name=%s", f)
    fromJSON(system(cmd, intern=TRUE))
})

# Print the results
round(data.frame(mean=sapply(datas, mean), stdev=sapply(datas, sd)))
