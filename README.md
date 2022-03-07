# SmartGrid - Backend
Computer Science Capstone
UC Santa Barbara 
AgMonitor

## Summary
### Motivation
- Power shutoffs are frequent, impacting millions of customers yearly.
- SOLAR+STORAGE systems provide a cost-effective way to weather power shutoffs.
- Used efficiently, SOLAR+STORAGE can reduce greenhouse emissions to fight climate change.
- Current microgrid auto-management tools are based on human-engineered heuristics, which lack the flexibility to provide personalized recommendations.

### Research Questions
- What should the battery threshold be?
- How should you schedule flexible loads?

### Solution
- Interpretable AI-optimized personal energy management recommendations.
- Historical microgrid usage visualization.

## Setup
### System Overview
Our system is comprised of the following technologies:
- Django
- Postgresql
- Twilio
- Enphase
- Forecast.solar
- Weatherbit.io

### Prerequisites
None.

### Installation
See requirements.txt for a full list of libraries.

### Deployment
docker-compose -f local.yml build
docker-compose -f local.yml up
docker-compose -p project -f local.yml up -d --build
docker-compose -f local.yml run --rm django pytest


## Specs
### Functionality
1. As a potential customer, I can find a brief digest about the software to understand the product.
2. As a new user, I can sign up for a new account at the homepage.
3. As a customer user, I can log in and log out on the website to ensure my personal data is secure.
4. As an internal developer, I can upload a CSV file of data so I can use the data for optimization.
5. As a user, I can download a CSV file of data (after data-cleaning).
6. As an internal engineer, I can transform customer data to provide data processing for convenience.
7. As a customer user, I can see my energy data usage summary on the home page after I logged in.
8. As a data scientist, I can look into and edit my raw data for my energy usage to correct errors.
9. As a customer user, I can explore my energy data for a better understanding of my energy usage.
10. As an internal engineer, I can find an algorithm to help users optimize their microgrid effectively.
11. As a developer, I can provide improvements to customers’ energy usage from their historical data.
12. As a customer user, I can opt into receiving notifications for energy optimization recs.
13. As a customer user, I can configure different assets to correctly align consumption/usage data.
14. As a customer user, I can see the percent of power each asset consumed/generated.
15. As a customer user, I can add constraints to the optimizations to prevent not applicable recs.
16. As a customer user, I can configure my profile page.
17. As an internal developer, I can integrate Tesla Powerwall data into our existing database.
18. As a customer user, I can compare Tesla Powerwall data and the optimization differences.
19. As a user, I can add/delete assets on the dashboard so I can control assets I want to optimize.
20. As a user, I can link my variable assets so its charging/discharging is automatically controlled.

### Known Issues
TODO

### License
Apache 2.0

### APIs

add a new user:<br />
```
/editUser
```
![image](https://user-images.githubusercontent.com/72473351/146705763-9a13d613-c915-4350-87dd-1a6bc2e62733.png)

add a new asset:<br />
```
/addUserAsset
```
![image](https://user-images.githubusercontent.com/72473351/146705912-9d0e36b7-8b68-40db-b97f-5560cef8381f.png)

get all assets for a user:<br />
```
/getUserAsset
```
![image](https://user-images.githubusercontent.com/72473351/146705973-32fe5f23-3f99-42c2-8507-28bc51fb4c86.png)

delete a new asset:<br />
```
/deleteUserAsset
```
![image](https://user-images.githubusercontent.com/72473351/146706105-aca87817-cfcc-4a74-82b2-abc65da5a617.png)

update a new asset:<br />
```
/updateUserAsset
```
![image](https://user-images.githubusercontent.com/72473351/146706591-040dd90c-5b8f-4e36-801e-aacefaaa78fb.png)

add new asset dataset:<br />
```
\createAssetData
```
![image](https://user-images.githubusercontent.com/72473351/146706426-ed4306ad-dd3b-47a3-923b-f790eafa753d.png)

delete dataset for an asset: <br />
```
\deleteAssetData
```
![image](https://user-images.githubusercontent.com/72473351/146706445-22ae8f3f-f5c0-42d0-b039-7261a3d75dc9.png)

get dataset for an asset: <br />
```
/getAssetData
```
![image](https://user-images.githubusercontent.com/72473351/146706490-cda27dc5-fcfe-4504-aee5-488203ae23aa.png)

