import pytest
from rater_example import rater

asset_sizes, base_rates, limits, limit_factors, industry_factor_dict = rater._get_data()

# testing the main execute function is calculating the correct premium based on the input 
@pytest.mark.parametrize('asset_size, limit, retention, industry, expected_premium', [
	(1200000, 5000000, 1000000, 'Hazard Group 2', 6311),
	(50000000, 23000, 0, 'Hazard Group 1', 7839),
	(60000, 400000, 5000, 'Hazard Group 3', 4069),
])
def test_execute_valid_input(asset_size, limit, retention, industry, expected_premium):
	json_input = {
		'Asset Size': asset_size,
		'Limit': limit,
		'Retention': retention,
		'Industry': industry
	}
	result = rater.execute(json_input)
	
	assert result == pytest.approx(expected_premium, abs = 1)

# testing miss keys raise the correct error and message 
def test_validate_input_missing_key():
	json_input = {}
	with pytest.raises(ValueError, match = 'Missing required field'):
		rater._validate_input(json_input)

# testing the validation of asset_size that it raises the correct error and message for invalid inputs
@pytest.mark.parametrize('invalid_asset_size', [
	'not an integer',
	12.50,
	0,
	-1000,
	2500000001,
	None
])
def test_validate_asset_size(invalid_asset_size):
	json_input = json_input = {
		'Asset Size': invalid_asset_size,
		'Limit': 1000000,
		'Retention': 0,
		'Industry': 'Hazard Group 1'
	}

	with pytest.raises(ValueError, match = 'Asset Size must be an integer between 1 and 250,000,000'):
		rater.execute(json_input)

# testing the validation of limit that it raises the correct error and message for invalid inputs
@pytest.mark.parametrize('invalid_limit', [
	'not an integer',
	12.50,
	0,
	-1000,
	None
])
def test_validate_limit(invalid_limit):
	json_input = json_input = {
		'Asset Size': 1000000,
		'Limit': invalid_limit,
		'Retention': 0,
		'Industry': 'Hazard Group 1'
	}

	with pytest.raises(ValueError, match = 'Limit must be an integer greater than 0'):
		rater.execute(json_input)

# testing the validation of retention that it raises the correct error and message for invalid inputs
@pytest.mark.parametrize('invalid_retention', [
	'not an integer',
	12.50,
	-1000,
	None
])
def test_validate_retention(invalid_retention):
	json_input = json_input = {
		'Asset Size': 1000000,
		'Limit': 1000000,
		'Retention': invalid_retention,
		'Industry': 'Hazard Group 1'
	}

	with pytest.raises(ValueError, match = 'Retention must be an integer greater than or equal to 0'):
		rater.execute(json_input)

# testing the validation of combined policy limit >10M that it raises the correct error and message
@pytest.mark.parametrize('limit, retention', [
	(5000000, 5000001),
	(10000000, 1),
	(1, 10000000)
])
def test_validate_limit_plus_retention_less_than_10M(limit, retention):
	json_input = json_input = {
		'Asset Size': 1000000,
		'Limit': limit,
		'Retention': retention,
		'Industry': 'Hazard Group 1'
	}

	with pytest.raises(ValueError, match = 'Total policy limit exceeds the maximum allowed capacity of 10,000,000'):
		rater.execute(json_input)

# testing the validation of industry that it raises the correct error and message for invalid inputs
@pytest.mark.parametrize('invalid_industry', [
	12,
	12.000,
	'not an industry',
	'hazard group 1',
	'HAZARD GROUP 1',
	'Hazard Group 4'
])
def test_validate_industries(invalid_industry):
	json_input = json_input = {
		'Asset Size': 1000000,
		'Limit': 1000000,
		'Retention': 1000000,
		'Industry': invalid_industry
	}

	with pytest.raises(ValueError, match = 'Industry must be one of'):
		rater.execute(json_input)

# testing the get_base_rate function is returning the correct base rate for given asset size input
@pytest.mark.parametrize('input_asset_size, expected_base_rate',[
	(1, 1065),
	(500000, 1442),
	(1000000, 1819),
	(2500000, 3619),
	(5000000, 3966),
	(7500000, 4129),
	(10000000, 4291),
	(90000000, 7080),
	(250000000, 8380),
	(1200000, 2059)
])
def test_get_base_rate(input_asset_size, expected_base_rate):
	result = rater._get_base_rate(input_asset_size, asset_sizes, base_rates)

	assert result == pytest.approx(expected_base_rate, abs = 1)

# testing the get_limit_retention_factor function is returning the correct factor for given limit/retention input
@pytest.mark.parametrize('input_limit, expected_factor', [
	(0, -0.76),
	(100, -0.744),
	(100000, 0.35),
	(333333, 0.654),
	(1000000, 1),
	(5000000, 1.986),
	(8000000, 2.331),
	(9500000, 2.463),
	(10000000, 2.503),
])
def test_get_limit_retention_factor(input_limit, expected_factor):
	result = rater._get_limit_retention_factor(input_limit, limits, limit_factors)

	assert result == pytest.approx(expected_factor, abs = 0.001)

# testing the get_industry_factor function is returning the correct factor for given industry input
@pytest.mark.parametrize('industry, expected_factor', [
	('Hazard Group 1', 1),
	('Hazard Group 2', 1.62),
	('Hazard Group 3', 1.944),
])
def test_get_industry_factor(industry, expected_factor):
	result = rater._get_industry_factor(industry, industry_factor_dict)

	assert result == expected_factor






