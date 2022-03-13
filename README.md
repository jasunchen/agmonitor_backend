# SmartGrid - Backend
- Computer Science Capstone 
- UC Santa Barbara 
- AgMonitor 

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
Acquire .env file containing appropriate keys to access API.

### Installation
- See requirements.txt for a full list of libraries.
- Use python upload.py with the relevant csv file and asset id to upload the correct data for frontend use.

### Deployment
- docker-compose -f local.yml build 
- docker-compose -f local.yml up 
- docker-compose -p project -f local.yml up -d --build 
- docker-compose -f local.yml run --rm django pytest 


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
- Data needs to be manually processed and uploaded at the moment.

### License
Apache 2.0

### APIs
Get all users' information(testing purpose):

```
GET /getAllUsers
```

Add a new user:<br />

```
POST /registerUser
```
BODY:

<img width="533" alt="image" src="https://user-images.githubusercontent.com/72473351/157151169-b745e6f1-e839-41d1-8431-82b7016fdf2d.png">


Get the user information:<br />

```
GET /getUser?email={}
```
Update the user information:<br />

```
POST /updateUser
```
BODY:

<img width="529" alt="image" src="https://user-images.githubusercontent.com/72473351/157151253-41265a67-6382-4a2e-8ad7-54f1bf37cdc7.png">

Add a new asset:<br />

```
POST /addUserAsset
```
BODY:

<img width="765" alt="image" src="https://user-images.githubusercontent.com/72473351/157151331-d4019aac-b5af-413d-a63b-55e9ceddae8c.png">


Get all assets for a user:<br />

```
GET /getAllAssets?email={}
```

Delete an asset:<br />

```
DELETE /deleteUserAsset
```
BODY

<img width="516" alt="image" src="https://user-images.githubusercontent.com/72473351/157151440-76cf4bd9-09bf-4aa2-8800-e81c09818cc8.png">

Update a new asset:<br />

```
POST /updateUserAsset
```
BODY

<img width="765" alt="image" src="https://user-images.githubusercontent.com/72473351/157151331-d4019aac-b5af-413d-a63b-55e9ceddae8c.png">


Add new asset dataset:<br />

```
POST \createAssetData
```
BODY

<img width="391" alt="image" src="https://user-images.githubusercontent.com/72473351/157151574-f19b632a-5505-49e8-9164-f0d4927f73d2.png">


Delete dataset for an asset: <br />

```
DELETE \deleteAssetData
```
BODY

<img width="536" alt="image" src="https://user-images.githubusercontent.com/72473351/157151603-f57f9acb-e9fc-4ffe-96d3-504ca407e8d2.png">

Get dataset for an asset: <br />

```
GET /getAssetData?id={}&start={}&end={}&page={}
```

Run optimization function(testing purpose): <br />

```
POST /optimization
```

BODY

<img width="530" alt="image" src="https://user-images.githubusercontent.com/72473351/157151728-7092f221-b499-46f8-9c48-b6300e8a1fb4.png">

