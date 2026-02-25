DSCI-441 Project Milestone 0
Used Car Price Prediction System
Spring 2026
Statistical and Machine Learning
1. Project Overview
Project Title
Used Car Price Prediction System
Project Abstract
This project develops an intelligent pricing tool that predicts used car market values using regression analysis techniques learned in DSCI-441. By analyzing vehicle attributes including brand, model year, mileage, condition, fuel type, and transmission, the system provides accurate price estimates to help buyers make informed purchasing decisions and sellers set competitive prices.
Project Goals:
•	Implement and compare multiple regression models (OLS, Ridge, Lasso)
•	Perform comprehensive feature engineering and multicollinearity analysis
•	Achieve R² > 0.80 on test set using proper train-test split methodology
•	Create interactive StreamLit web application for real-time price prediction
•	Visualize feature importance and residual analysis for model validation
This project directly applies supervised learning regression methods from DSCI-441 lectures while delivering a practical consumer tool for transparent car pricing in the secondary automobile market.
2. Dataset Information
Craigslist Used Cars Dataset
A comprehensive collection of over 400,000 used vehicle listings scraped from Craigslist across the United States, providing rich features for regression analysis.
Download Links:
•	Primary: https://www.kaggle.com/datasets/austinreese/craigslist-carstrucks-data
•	Alternative: https://www.kaggle.com/datasets/mbaabuharun/craigslist-vehicles
Dataset Details:
Total Records	426,880 vehicle listings
Target Variable	Price (USD)
Key Features	Year, manufacturer, model, condition, odometer, fuel, transmission, drive, type, paint color, state
Data Format	CSV (will preprocess and clean)
License	Public domain (free for academic use)

3. Methodology
Regression Techniques
This project will implement and compare the following regression models covered in DSCI-441:
•	Ordinary Least Squares (OLS): Baseline model using normal equations (X
•	Ridge Regression: L2 regularization to handle multicollinearity
•	Lasso Regression: L1 regularization for automatic feature selection
Feature Engineering
•	Handle missing values and outliers
•	Encode categorical variables (manufacturer, fuel type, transmission)
•	Create derived features (vehicle age, price per mile)
•	Normalize/standardize numerical features
Model Evaluation
•	80/20 train-test split with random seed for reproducibility
•	Metrics: R², RMSE, MAE
•	Residual analysis to validate model assumptions
•	Cross-validation for hyperparameter tuning
4. Expected Outcomes
Technical Deliverables
•	Regression models achieving R² > 0.80 on test set
•	Feature importance analysis and correlation heatmaps
•	Interactive StreamLit web application with intuitive UI
•	Comprehensive Jupyter notebooks documenting analysis
•	Complete GitHub repository with documentation
Success Metrics
Metric	Target
Model Accuracy (R²)	> 0.80 on test set
Prediction Error (RMSE)	< $3,000
GitHub Commits	Minimum 10 (distributed)
Code Documentation	Complete with README

--- End of Document ---
