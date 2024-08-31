library(GGally)
library(plotly)

# Load the data
data <- read.csv("results_down_trend.csv")
head(data)

# 3D scatter plot of the data
fig <- plot_ly(data, x = ~TP, y = ~SL, z = ~Balance, 
               type = 'scatter3d', mode = 'markers',
               marker = list(size = 5, color = 'blue'))

fig <- fig %>% layout(
  scene = list(
    xaxis = list(title = 'TP'),
    yaxis = list(title = 'SL'),
    zaxis = list(title = 'Balance')
  ),
  title = '3D Plot of TP, SL, and Balance'
)

fig
ggpairs(data)

# Function to plot the fitted model and data
plot_fitted_model <- function(model, test_data = NULL, include_original_data = FALSE) {
  # Extract coefficients and model data
  coefficients <- coef(model)
  data <- model$model
  
  # Create a grid of TP and SL values
  TP_seq <- seq(min(data$TP), max(data$TP), length.out = 50)
  SL_seq <- seq(min(data$SL), max(data$SL), length.out = 50)
  grid <- expand.grid(TP = TP_seq, SL = SL_seq)
  
  # Predict Balance values for the grid
  predicted_values <- predict(model, newdata = grid)
  grid$Balance <- predicted_values
  
  # Create the interactive 3D scatter plot
  fig <- plot_ly()
  
  # Optionally include original data points
  if (include_original_data) {
    fig <- fig %>% add_trace(data = data, x = ~TP, y = ~SL, z = ~Balance, 
                             type = 'scatter3d', mode = 'markers',
                             marker = list(size = 5, color = 'blue'),
                             name = 'Data Points')
  }
  
  # Add the fitted plane
  fig <- fig %>% add_trace(x = grid$TP, y = grid$SL, z = grid$Balance,
                           type = 'mesh3d', opacity = 0.5, color = 'yellow',
                           name = 'Fitted Plane')
  
  # If test data is provided, plot it and calculate R^2 and adjusted R^2
  if (!is.null(test_data)) {
    if (all(c("TP", "SL", "Balance") %in% colnames(test_data))) {
      test_pred <- predict(model, newdata = test_data)
      
      # Calculate R^2 and adjusted R^2 for the test data
      ss_total <- sum((test_data$Balance - mean(test_data$Balance))^2)
      ss_residual <- sum((test_data$Balance - test_pred)^2)
      r_squared <- 1 - (ss_residual / ss_total)
      adj_r_squared <- 1 - (1 - r_squared) * (nrow(test_data) - 1) / (nrow(test_data) - length(coefficients) - 1)
      
      cat("R^2 for test data: ", r_squared, "\n")
      cat("Adjusted R^2 for test data: ", adj_r_squared, "\n")
      
      fig <- fig %>% add_trace(data = test_data, x = ~TP, y = ~SL, z = ~Balance,
                               type = 'scatter3d', mode = 'markers',
                               marker = list(size = 5, color = 'red'),
                               name = 'Test Data Points')
    } else {
      stop("Test data must contain columns: TP, SL, Balance")
    }
  }
  
  # Customize the layout
  fig <- fig %>% layout(
    scene = list(
      xaxis = list(title = 'TP'),
      yaxis = list(title = 'SL'),
      zaxis = list(title = 'Balance')
    ),
    title = '3D Plot of TP, SL, and Balance with Fitted Plane'
  )
  
  # Display the plot
  fig
}

# Split the data into training and testing sets
set.seed(4)
train <- sample(1:nrow(data), nrow(data) * 0.8) 
data_train <- data[train,]
data_test <- data[-train,]

# Linear regression models with increasing polynomial terms
g <- lm(Balance ~ TP + SL, data = data_train)
summary(g)
plot_fitted_model(g, data_test)

g_2 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2), data = data_train)
summary(g_2)
plot_fitted_model(g_2, data_test)

g_3 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3), data = data_train)
summary(g_3)
plot_fitted_model(g_3, data_test)

g_3_sin <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + sin(0.24*TP) + sin(0.24*SL) + cos(0.24*TP) + cos(0.24*SL), data = data_train)
summary(g_3_sin)
plot_fitted_model(g_3_sin, data_test)

g_4 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4), data = data_train)
summary(g_4)
plot_fitted_model(g_4, data_test)

# Calculating max of the Balance
# Extract coefficients from the model
coefficients <- coef(g_4)
print(coefficients)

# Define the polynomial function with the actual names from the model
poly_function <- function(params, coefs) {
  TP <- params[1]
  SL <- params[2]
  
  intercept <- ifelse("(Intercept)" %in% names(coefs), coefs["(Intercept)"], 0)
  TP_coef <- ifelse("TP" %in% names(coefs), coefs["TP"], 0)
  SL_coef <- ifelse("SL" %in% names(coefs), coefs["SL"], 0)
  TP2_coef <- ifelse("I(TP^2)" %in% names(coefs), coefs["I(TP^2)"], 0)
  SL2_coef <- ifelse("I(SL^2)" %in% names(coefs), coefs["I(SL^2)"], 0)
  TP3_coef <- ifelse("I(TP^3)" %in% names(coefs), coefs["I(TP^3)"], 0)
  SL3_coef <- ifelse("I(SL^3)" %in% names(coefs), coefs["I(SL^3)"], 0)
  TP4_coef <- ifelse("I(TP^4)" %in% names(coefs), coefs["I(TP^4)"], 0)
  SL4_coef <- ifelse("I(SL^4)" %in% names(coefs), coefs["I(SL^4)"], 0)
  
  intercept + TP_coef * TP + SL_coef * SL + 
    TP2_coef * TP^2 + SL2_coef * SL^2 + 
    TP3_coef * TP^3 + SL3_coef * SL^3 + 
    TP4_coef * TP^4 + SL4_coef * SL^4
}

# Define the negative polynomial function for minimization
neg_poly_function <- function(params) {
  -poly_function(params, coefficients)
}

# Initial guess for the parameters (TP and SL)
initial_guess <- c(TP = 10, SL = 10)

# Use optim to find the maximum by minimizing the negative polynomial function
result <- optim(par = initial_guess, fn = neg_poly_function, method = "L-BFGS-B")

# The maximum point and the maximum value
max_point <- result$par
max_value <- -result$value

cat("Maximum at TP:", max_point[1], "SL:", max_point[2], "\n")
cat("Maximum value:", max_value, "\n")

# Testing models with higher-order polynomial terms
g_5 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4) + I(TP^5) + I(SL^5), data = data)
summary(g_5)
plot_fitted_model(g_5)

g_6 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4) + I(TP^5) + I(SL^5) + I(TP^6) + I(SL^6), data = data)
summary(g_6)
plot_fitted_model(g_6)

# Perform the same analysis on uptrend data
data <- read.csv("results_up_trend.csv")
head(data)

set.seed(4)
train <- sample(1:nrow(data), nrow(data) * 0.8)
data_train <- data[train,]
data_test <- data[-train,]

g <- lm(Balance ~ TP + SL, data = data_train)
summary(g)
plot_fitted_model(g, data_test)

g_2 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2), data = data_train)
summary(g_2)
plot_fitted_model(g_2, data_test)

g_3 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3), data = data_train)
summary(g_3)
plot_fitted_model(g_3, data_test)

g_4 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4), data = data)
summary(g_4)
plot_fitted_model(g_4)

g_5 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4) + I(TP^5) + I(SL^5), data = data)
summary(g_5)
plot_fitted_model(g_5)

g_6 <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4) + I(TP^5) + I(SL^5) + I(TP^6) + I(SL^6), data = data)
summary(g_6)
plot_fitted_model(g_6)

# Calculating max of the Balance for combined models
data <- read.csv("results_down_trend.csv")
set.seed(4)
train <- sample(1:nrow(data), nrow(data) * 0.8)
data_train <- data[train,]
data_test <- data[-train,]
g_down <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3) + I(TP^4) + I(SL^4), data = data)
summary(g_down)
plot_fitted_model(g_down, data_test)
coefficients_d <- coef(g_down)

data <- read.csv("results_up_trend.csv")
set.seed(4)
train <- sample(1:nrow(data), nrow(data) * 0.8)
data_train <- data[train,]
data_test <- data[-train,]
g_up <- lm(Balance ~ TP + SL + I(TP^2) + I(SL^2) + I(TP^3) + I(SL^3), data = data_train)
summary(g_up)
plot_fitted_model(g_up, data_test)
coefficients_u <- coef(g_up)

# Define the polynomial function with the actual names from the model
poly_function <- function(params, coefs) {
  TP <- params[1]
  SL <- params[2]
  
  intercept <- ifelse("(Intercept)" %in% names(coefs), coefs["(Intercept)"], 0)
  TP_coef <- ifelse("TP" %in% names(coefs), coefs["TP"], 0)
  SL_coef <- ifelse("SL" %in% names(coefs), coefs["SL"], 0)
  TP2_coef <- ifelse("I(TP^2)" %in% names(coefs), coefs["I(TP^2)"], 0)
  SL2_coef <- ifelse("I(SL^2)" %in% names(coefs), coefs["I(SL^2)"], 0)
  TP3_coef <- ifelse("I(TP^3)" %in% names(coefs), coefs["I(TP^3)"], 0)
  SL3_coef <- ifelse("I(SL^3)" %in% names(coefs), coefs["I(SL^3)"], 0)
  TP4_coef <- ifelse("I(TP^4)" %in% names(coefs), coefs["I(TP^4)"], 0)
  SL4_coef <- ifelse("I(SL^4)" %in% names(coefs), coefs["I(SL^4)"], 0)
  
  intercept + TP_coef * TP + SL_coef * SL + 
    TP2_coef * TP^2 + SL2_coef * SL^2 + 
    TP3_coef * TP^3 + SL3_coef * SL^3 + 
    TP4_coef * TP^4 + SL4_coef * SL^4
}

# Define the negative polynomial function for minimization
neg_poly_function <- function(params) {
  -weights[1]*poly_function(params, coefficients_d) - weights[2]*poly_function(params, coefficients_u)
}

# Initial guess for the parameters (TP and SL)
initial_guess <- c(TP = 10, SL = 10)
weights <- c(0.50, 0.50)

# Use optim to find the maximum by minimizing the negative polynomial function
result <- optim(par = initial_guess, fn = neg_poly_function, method = "L-BFGS-B")

# The maximum point and the maximum value
max_point <- result$par
max_value <- -result$value

cat("Maximum at TP:", max_point[1], "SL:", max_point[2], "\n")
cat("Maximum value:", max_value, "\n")

# Define the coefficient arrays
coefficients1 <- coefficients_d
coefficients2 <- coefficients_u

# Sum of the polynomial functions
sum_poly_function <- function(params) {
  poly_function(params, coefficients1) + poly_function(params, coefficients2)
}

# Define a grid of TP and SL values
TP_seq <- seq(0, 30, length.out = 100)
SL_seq <- seq(0, 30, length.out = 100)
grid <- expand.grid(TP = TP_seq, SL = SL_seq)

grid$Balance <- apply(grid, 1, function(row) sum_poly_function(row))

single_point_TP <- 6.380509
single_point_SL <- 16.37428
single_point_Balance <- sum_poly_function(c(single_point_TP, single_point_SL))

# Create the 3D plot
fig <- plot_ly(x = ~grid$TP, y = ~grid$SL, z = ~grid$Balance, 
               type = 'mesh3d', opacity = 0.5, color = 'lightblue',
               name = 'Sum of Polynomial Functions')

# Add the single point
fig <- fig %>% add_trace(x = ~single_point_TP, y = ~single_point_SL, z = ~single_point_Balance,
                         type = 'scatter3d', mode = 'markers',
                         marker = list(size = 5, color = 'red'),
                         name = 'Single Point')

# Customize the layout
fig <- fig %>% layout(
  scene = list(
    xaxis = list(title = 'TP'),
    yaxis = list(title = 'SL'),
    zaxis = list(title = 'Balance')
  ),
  title = '3D Plot of the Sum of Two Polynomial Functions with Single Point'
)

# Display the plot
fig

