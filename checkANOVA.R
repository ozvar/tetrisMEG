# load libraries
library(stats)
library(ez)


# load data
df <- read.csv('/groups/Projects/P1454/behavioural_data/analysis_df.csv')
df$state <- as.factor(df$state)

# run
ezANOVA(
  data=df,
  within=.(state, scout),
  wid=.(SID),
  dv=.(RMS_alpha)
)


