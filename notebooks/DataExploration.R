fname="Building_Violations_sample_50000.csv"
df = read.csv(fname)
dim(df)
names(df)

#---Basic R Plotting
#---BARS
freq  = table(df$INSPECTION.CATEGORY)
barplot(freq)
#---stacked bar
freq  = table(df$INSPECTION.STATUS, df$INSPECTION.CATEGORY)
freq
barplot(freq, legend = rownames(freq), col=seq(1:length(levels(df$INSPECTION.STATUS))))
barplot(freq, legend = rownames(freq), col=seq(1:length(levels(df$INSPECTION.STATUS))), beside=TRUE)

slices = table(df$INSPECTION.STATUS)
pie(slices, labels = levels(df$INSPECTION.STATUS))

#---SCATTERS
plot(df$LATITUDE, df$LONGITUDE)
plot(df$LATITUDE, df$LONGITUDE, col=factor(df$INSPECTION.STATUS))

plot(df$LATITUDE, df$LONGITUDE, col=factor(df$INSPECTION.STATUS), xlab="Latitude", ylab="Longitude", main="A scatter map!")
legend("bottomleft", pch=1,col=seq(1:length(levels(df$INSPECTION.STATUS))),levels(df$INSPECTION.STATUS))

#---LINES
sm = df[sample(nrow(df), 1000),]
sm = sm[order(sm$VIOLATION.DATE),]
plot(sm$VIOLATION.DATE, sm$SSA, type="l")
lines(sm$VIOLATION.DATE, sm$SSA)

#######################
#---Grammar of Graphics Plotting
#---http://zevross.com/blog/2014/08/04/beautiful-plotting-in-r-a-ggplot2-cheatsheet-3/

library(ggplot2)
#---aesthetics - x, y, color, size, shape
#---geometry - bar, area, text, point, line
#---statistical transforms - smooth, log
#---scales - discrete, continuous
#---facets

#---BARS
bplot <- ggplot(df, aes(x = INSPECTION.CATEGORY)) + geom_histogram()
bplot
bplot <- ggplot(df, aes(x = INSPECTION.CATEGORY)) + geom_bar(stat="bin")
bplot
#---stacked bar
bplot <- ggplot(df, aes(x = INSPECTION.CATEGORY, fill=INSPECTION.STATUS)) + geom_bar(stat="bin", color="black") + ylim(0,40000)
bplot
#---set theme to format everything from axis labels to grid lines to legends http://docs.ggplot2.org/0.9.2.1/theme.html
bplot <- ggplot(df, aes(x = INSPECTION.CATEGORY, fill=INSPECTION.STATUS)) + geom_bar(stat="bin", position=position_dodge(), color="black") + ylim(0,40000) + theme(axis.text = element_text(size = 8), panel.grid.major = element_line(colour = "grey40"), panel.grid.minor = element_blank())
bplot

#---horizontal bars
bplot + coord_flip() 

#---SCATTERS
splot <- ggplot(df, aes(x = LONGITUDE, y = LATITUDE )) + geom_point()
splot
splot <- ggplot(df, aes(x = LONGITUDE, y = LATITUDE, color=INSPECTION.STATUS)) + geom_point()
splot
splot + geom_smooth(method = 'lm')
#--contours
splot + stat_density2d()

splot + ggtitle("A fake map!") + scale_x_continuous(name = "Longitude", limits = range(df$LONGITUDE, na.rm=T))  + scale_y_continuous("Latitude", limits = range(df$LATITUDE, na.rm=T))

#--hexbins
bins = ggplot(df, aes(x =LONGITUDE, y = LATITUDE , fill=INSPECTION.STATUS))  + stat_binhex (bins=20, aes (alpha = ..count..))
bins
bins + facet_grid (~ INSPECTION.STATUS)
splot + facet_grid (INSPECTION.CATEGORY ~ INSPECTION.STATUS)

#---LINES
sm = df[1:10000,]
sm = sm[order(sm$VIOLATION.DATE),]
lplot <- ggplot(sm, aes(x=VIOLATION.DATE, y=SSA)) + geom_point(size=1.5, fill="white") + geom_line(size=0.5)
lplot
lplot + facet_grid (~ INSPECTION.STATUS)

#---MAPS
library(ggmap)
map.center <- geocode("Chicago, IL")
map <- get_map(c(lon=map.center$lon, lat=map.center$lat), source="google", zoom=11)
mapPoints <- ggmap(map) + geom_point(data=df, aes(LONGITUDE, LATITUDE, size=SSA, col=INSPECTION.STATUS, alpha = 0.5))
mapPoints
mapPoints + facet_wrap (~ INSPECTION.STATUS, ncol=2)

#--contours
ggmap(map) + stat_density2d(aes(x = LONGITUDE, y = LATITUDE, fill = ..level.. , alpha = ..level..),size = 2, bins = 8, data = df, geom = 'polygon')

