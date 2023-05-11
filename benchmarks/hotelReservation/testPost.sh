url=10.244.44.201


curl "${url}:5000/hotels?inDate=2015-04-01&outDate=2015-04-03&lat=38&lon=-122&require=nearby"
curl "${url}:5000/hotels?inDate=2015-04-01&outDate=2015-04-03&lat=38&lon=-122&require=rates"
curl "${url}:5000/hotels?inDate=2015-04-01&outDate=2015-04-03&lat=38&lon=-122&require=all"

curl "${url}:5000/recommendations?lat=38&lon=-122&require=dis&username=Cornell_1"
curl "${url}:5000/recommendations?lat=38&lon=-122&require=price&username=Cornell_1"
curl "${url}:5000/recommendations?lat=38&lon=-122&require=rate&username=Cornell_1"
curl "${url}:5000/recommendations?lat=38&lon=-122&require=overall&username=Cornell_1"

curl "${url}:5000/reservation?inDate=2015-04-01&outDate=2015-04-03&hotelId=1&username=Cornell_1&password=1111111111&number=1&customerName=Cornell_1"

