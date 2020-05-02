library(argparser, quietly=TRUE)
library(jsonlite, quietly=TRUE)

pp <- arg_parser("Summarize Monte Carlo results")
pp <- add_argument(pp, "dir", help="path to results in conducto-data-pipeline")

argv <- parse_args(pp)
print(argv)

# Use `conducto-data-pipeline list` command to get all the files.
cmd = sprintf("conducto-data-pipeline list --prefix=%s", argv$dir)
files = fromJSON(system(cmd, intern=TRUE))

names(files) <- gsub(".*/", "", files)
datas = lapply(files, function(f) {
    # Call `conducto-data-pipeline gets` to get an individual dataset.
    # Since the  data is JSON-encoded, call fromJSON() to extract
    # the data. Other data formats are ok too. For CSV data, do:
    #   read.csv(system(cmd, intern=TRUE))
    cmd = sprintf("conducto-data-pipeline gets --name=%s", f)
    fromJSON(system(cmd, intern=TRUE))
})

# Print the results
round(data.frame(mean=sapply(datas, mean), stdev=sapply(datas, sd)))
