UCSB agmonitor
=========

Deploy command
---------------

docker-compose -f local.yml build

docker-compose -f local.yml up

docker-compose -f local.yml run --rm django pytest


APIs
--------

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




