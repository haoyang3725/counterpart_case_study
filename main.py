from rater_example import rater

json_input = {
	"Asset Size": 1200000, 
	"Limit": 5000000, 
	"Retention": 1000000, 
	"Industry": "Hazard Group 2"
}

result = rater.execute(json_input)
print(result)