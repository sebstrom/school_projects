# Kolla på API

library(pxweb)
min_data <- interactive_pxweb()

######## STORE AS JSON FILE ########

# Download data 
# PXWEB query 
pxweb_query_list <- 
  list("Region"=c("00"),
       "Drivmedel"=c("100","110","120","130","140","150","160","190"),
       "ContentsCode"=c("TK1001AA"),
       "Tid"=c("2024M02","2024M01","2023M12","2023M11","2023M10","2023M09","2023M08","2023M07","2023M06","2023M05","2023M04","2023M03"))

px_data <- 
  pxweb_get(url = "https://api.scb.se/OV0104/v1/doris/sv/ssd/TK/TK1001/TK1001A/PersBilarDrivMedel",
            query = pxweb_query_list)

# Convert to data.frame 
px_data_frame <- as.data.frame(px_data, column.name.type = "text", variable.value.type = "text")

# Get pxweb data comments 
px_data_comments <- pxweb_data_comments(px_data)
px_data_comments_df <- as.data.frame(px_data_comments)

# Cite the data as 
pxweb_cite(px_data)

str(px_data_frame)

print(px_data_frame)

summary(px_data)

names(px_data_frame)

head(px_data_frame)

# Beräkna totala summan
total_sum <- sum(px_data_frame$"Nyregistrerade personbilar", na.rm = TRUE)
total_sum

#total_sum = 300844
total_sum/12
# total_sum/12 = 25070.33


###############
# Ska skapa en regressions modell på datan som samlats in 
# vad behöver man tänka på? Steg för steg?
# 1. Tvätta datan
# 2. Ladda in datan 
# 3. EDA
# 4. Skapa model och utforska variablarna 
# 5. utvärdera, kolla fel osv
# 6. Repeat

# Ladda in libraries
install.packages("leaps")
install.packages("stringr")
install.packages("caret")
install.packages("car")
install.packages("glmnet")
install.packages("MASS")
install.packages("Metrics")
library(leaps)
library(dplyr)
library(stringr)
library(caret)
library(car)
library(glmnet)
library(MASS)  
library(Metrics)

# Ladda in bildatan
file_path <- "C:/Users/sebbe/Desktop/Skolsaker/R/Datasets/bil_data_ren.csv"
bil_data <- read.csv(file_path, sep = ";", header = TRUE, fileEncoding = "latin1", stringsAsFactors = FALSE)

head(bil_data)
dim(bil_data)
summary(bil_data)

# Ta bort alla NA rader
bil <- na.omit(bil_data)

# miltal är chr ändra den till numerisk (tack Tova för fina kodsnutten)

bil$Miltal <- gsub("[^0-9]", "", bil$Miltal)
bil$Miltal <- as.numeric(bil$Miltal)

head(bil)

# Ta bort bilmodeller med mindre än 30 observationer
bil_count <- bil %>% 
  group_by(Märke) %>%
  summarise(count = n())

filtered_bil <- bil_count %>%
  filter(count >= 30)

final_bil <- bil %>% 
  filter(Märke %in% filtered_bil$Märke)

# log på pris för att få det mer normalfördelat
bil$Pris_log <- log(bil$Pris)


# One-hot encoding på våra kategoriska variabler
?dummyVars
encode <- c("Biltyp", "Drivning", "Bränsle", "Märke", "Växellåda")

#fullRank = TRUE för att inte hamna i dummy trap
encoded_df <- dummyVars("~.", data = bil[, encode], fullRank = TRUE) %>%
  predict(bil[, encode])

# Kombinera allt till ny df 
df <- cbind(encoded_df, bil[, -which(names(bil) %in% encode)])
colnames(df) <- c(colnames(encoded_df), colnames(bil[, -which(names(bil) %in% encode)]))

# lite EDA
head(df)
dim(df)
summary(df)

corr <- cor(df)
head(df)
print(corr)

# histogram före och efter log på pris 

par(mfrow = c(2, 2))
hist(df$Pris, main = "Before", xlab = "Price", ylab = "Frequency", col = "skyblue", border = "black",breaks = 25)
hist(df$Pris_log, main = "After", xlab = "log Price", ylab = "Frequency", col = "skyblue", border = "black",breaks = 25)

# Splitta datan i train test val 

spec = c(train = .6, test = .2, validate = .2)

set.seed(42)

g = sample(cut(
  seq(nrow(df)), 
  nrow(df)*cumsum(c(0,spec)),
  labels = names(spec)
))

res = split(df, g)

# Kolla så min split fungerade 
sapply(res, nrow)/nrow(df)
addmargins(prop.table(table(g)))

# Nya variabler för train val test 
# ta bort outlier 
train_data <- res$train
val_data <- res$validate
test_data <- res$test


# Skapa 3 modeller och utvärdera och jämför. En där jag väljer variabler själv, en Full och en Best

############## 1 Logic metoden, 
# uppvisar mycket heteroskadicitet sak så gör LOG på pris
# logic <- lm(Pris ~ Modellår + Miltal + HK + Motorstorlek, data = train_data)
logic <- lm(Pris_log ~ Modellår + Miltal + HK + Motorstorlek, data = train_data)
summary(logic)

par(mfrow = c(2, 2))
plot(logic)

vif(logic)

# Beräkna cooks avstånd då vi har några outliers jag vill ha bort över avstånd 0,04
#cooks_dist <- cooks.distance(logic)
#outlier_index <- which(cooks_dist > 0.04)

# Ta bort outliers och skapa ny datafram called train_datan
# train_datan <- train_data[-outlier_index, ]

#logic <- lm(Pris_log ~ Modellår + Miltal + HK + Motorstorlek, data = train_datan)
# summary(logic)

# par(mfrow = c(2, 2))
# plot(logic)
# vif(logic)

############  2 Full
# Log så remove pris från df 
# full <- lm(Pris ~ ., data = train_data)
full <- lm(Pris_log ~ .- Pris, data = train_data)


summary(full)

alias(full)
vif(full)

par(mfrow = c(2, 2))
plot(full)
str(full)

#3 Best
############# 3 Best
?regsubsets

# best <- regsubsets(Pris ~ .,data = train_data, really.big = TRUE)
best <- regsubsets(Pris_log ~ .- Pris, data = train_data, really.big = TRUE)

summary(best)
best_summary = summary(best)
summary(best_summary)

names(best_summary)
best_summary$adjr2

par(mfrow = c(1, 1))
plot(best_summary$adjr2)

coef(best, 3)
plot(best, scale = "adjr2")

par(mfrow = c(2, 2))
plot(best)

# Skapa ny modell från best 
best_predictors <- names(which(best_summary$which[which.max(best_summary$adjr2), ] == 1))

# Lägg till "Pris" i listan över bästa prediktorer
best_predictors <- c("Pris_log", best_predictors)

# Välj kolumnerna som finns både i train_data och best_predictors
selected_columns <- intersect(names(train_data), best_predictors)

# Passa en linjär regression med endast de bästa prediktorerna
# best_model <- lm(Pris ~ ., data = train_data[, selected_columns])
best_model <- lm(Pris_log ~ ., data = train_data[, selected_columns])

summary(best_model)
b_summary = summary(best_model)
par(mfrow = c(1, 1))
plot(b_summary$adjr2)

coef(best_model, 3)
plot(best_model, scale = "adjr2")

par(mfrow = c(2, 2))
plot(best_model)

# Beräkna VIF för den bästa modellen
vif_value <- car::vif(best_model)
print(vif_value)

# VIF resultat
# Miltal Modellår       HK 
# 1.049186 1.053241 1.004528

# efter jag tagit bort outlier.. Sämre resultat efter jag tagit bort outliers, gör om igen med outliers i min modell
#print(vif_value)
#Modellår Motorstorlek         Pris 
#2.758531     1.594165     2.791296 


#########  Utvärdera modellerna på validation datan och jämföra 

val_pred_logic <- predict(logic, newdata = val_data)
val_pred_full <- predict(full, newdata = val_data)
val_pred_best_model <- predict(best_model, newdata = val_data)

results <- data.frame(
  Model = c("Logic", "Full", "Best"),
  RMSE_val_data = c(rmse(val_data$Pris_log, val_pred_logic),
                    rmse(val_data$Pris_log, val_pred_full),
                    rmse(val_data$Pris_log, val_pred_best_model)),
  Adj_R_squared = c(summary(logic)$adj.r.squared,
                    summary(full)$adj.r.squared,
                    summary(best_model)$adj.r.squared),
  BIC = c(BIC(logic), BIC(full), BIC(best_model))
)

results


# exponera vår log variabel så den blir normal igen
val_pred_logic_exp <- exp(val_pred_logic)
val_pred_full_exp <- exp(val_pred_full)
val_pred_best_model_exp <- exp(val_pred_best_model)

# Skapa en ny data.frame för att hålla resultaten med riktiga priser
results_exp <- data.frame(
  Model = c("Logic", "Full", "Best"),
  RMSE_val_data = c(rmse(exp(val_data$Pris_log), val_pred_logic_exp),
                    rmse(exp(val_data$Pris_log), val_pred_full_exp),
                    rmse(exp(val_data$Pris_log), val_pred_best_model_exp)),
  Adj_R_squared = c(summary(logic)$adj.r.squared,
                    summary(full)$adj.r.squared,
                    summary(best_model)$adj.r.squared),
  BIC = c(BIC(logic), BIC(full), BIC(best_model))
)

results_exp


#########  Utvärdera vår valda modell (logic) på testdatan
final_model <- predict(logic, newdata = test_data)
rmse(exp(test_data$Pris_log), exp(final_model))

predicted_prices <- exp(predictions)
true_prices <- exp(test_data$Pris_log)

# Scatterplot för predicted vs true prices
plot(x = predicted_prices, y = true_prices,
     xlab = "Predicted Prices", ylab = "True Prices",
     main = "Scatterplot of Predicted vs True Prices",
     col = "black", pch = 20, cex = 0.7)  # Anpassa färger och symboler

# Lägg till linje för perfekt förutsägelse
abline(a = 0, b = 1, col = "red", lwd = 2)

# Lägg till rutnät
grid()

# Lägg till en legend
legend("topleft", legend = "Perfect Prediction Line", col = "red", lty = 1, lwd = 2, cex = 0.8)
options(scipen = 999) 


par(mfrow = c(2, 2))
plot(final_model)

summary(final_model)

confint(logic)

conf_int <- confint(logic)

### Skapa ki och pi 
confidence_intervals <- predict(logic, newdata = test_data, interval = "confidence", level = 0.95)
prediction_intervals <- predict(logic, newdata = test_data, interval = "prediction", level = 0.95)

confidence_intervals
prediction_intervals

ci_exp <- exp(confidence_intervals)
pi_exp <- exp(prediction_intervals)

ci_exp
pi_exp

##### Skapa medel ki och pi 
# Beräkna medelvärdet av alla observationer för att få ett konfidens/prediktionsintervall
mean_value_ci <- mean(ci_exp)
n_ci <- nrow(test_data)

# Beräkna standardfelet för ki
se_mean_ci <- sd(ci_exp) / sqrt(n_ci)

# Beräkna medelvärdet för pi
mean_value_pi <- mean(pi_exp)

# observationer för pi och medelfel
n_pi <- nrow(test_data)
se_mean_pi <- sd(pi_exp) / sqrt(n_pi)

# Beräkna z-värdet
z_value <- qnorm(0.975)  

# Beräkna ki och pi för medelvärdet
ci_mean <- c(mean_value_ci - z_value * se_mean_ci, mean_value_ci, mean_value_ci + z_value * se_mean_ci)
pi_mean <- c(mean_value_pi - z_value * se_mean_pi, mean_value_pi, mean_value_pi + z_value * se_mean_pi)

ci_mean
pi_mean

