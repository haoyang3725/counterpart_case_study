import pandas as pd
import numpy as np
import os

def execute(json_input):
	_validate_input(json_input)

	asset_size = json_input['Asset Size']
	limit = json_input['Limit']
	retention = json_input['Retention']
	industry = json_input['Industry']

	asset_sizes, base_rates, limits, limit_factors, industry_factor_dict = _get_data()

	base_rate = _get_base_rate(asset_size, asset_sizes, base_rates)
	retention_factor = _get_limit_retention_factor(retention, limits, limit_factors)
	limit_factor = _get_limit_retention_factor(limit + retention, limits, limit_factors)
	industry_factor = _get_industry_factor(industry, industry_factor_dict)
	
	return int(base_rate * (limit_factor - retention_factor) * industry_factor * 1.7)

def _validate_input(json_input):
	required_keys = ['Asset Size', 'Limit', 'Retention', 'Industry']
	valid_industries = ['Hazard Group 1', 'Hazard Group 2', 'Hazard Group 3']

	for key in required_keys:
		if key not in json_input:
			raise ValueError(f'Missing required field: {key}')

	asset_size = json_input['Asset Size']
	limit = json_input['Limit']
	retention = json_input['Retention']
	industry = json_input['Industry']

	if not isinstance(asset_size, int) or asset_size < 1 or asset_size > 250000000:
		raise ValueError('Asset Size must be an integer between 1 and 250,000,000')
	if not isinstance(limit, int) or limit <= 0:
		raise ValueError("Limit must be an integer greater than 0")
	if not isinstance(retention, int) or retention < 0:
		raise ValueError("Retention must be an integer greater than or equal to 0")
	if (limit + retention) >= 10000000:
		raise ValueError("Total policy limit exceeds the maximum allowed capacity of 10,000,000")
	if industry not in valid_industries:
		raise ValueError(f"Industry must be one of {valid_industries}")


def _get_data():
	current_dir = os.path.dirname(os.path.abspath(__file__))

	asset_size_df = pd.read_csv(current_dir + '/asset_size.csv')
	asset_sizes = np.array(asset_size_df['asset_size'])
	base_rates = np.array(asset_size_df['base_rate'])

	limit_retention_factor_df = pd.read_csv(current_dir + '/limit_retention_factor.csv')
	limits = np.array(limit_retention_factor_df['limit'])
	limit_factors = np.array(limit_retention_factor_df['factor'])

	industry_factor_df = pd.read_csv(current_dir + '/industry_factor.csv')
	industry_factor_dict = industry_factor_df.set_index('industry')['factor'].to_dict()

	return asset_sizes, base_rates, limits, limit_factors, industry_factor_dict

# based on the preset asset_sizes and their respective base_rates
# linearly interpolate the base rate for asset sizes in between discreet values
def _get_base_rate(asset_size, asset_sizes, base_rates):
	if asset_size == asset_sizes[-1]:
		return base_rates[-1]

	low_idx = len(asset_sizes[asset_sizes <= asset_size]) - 1
	high_idx = low_idx + 1

	asset_size_low = asset_sizes[low_idx]
	asset_size_high = asset_sizes[high_idx]
	base_rate_low = base_rates[low_idx]
	base_rate_high = base_rates[high_idx]

	# linear interpolation
	base_rate = base_rate_low + (asset_size - asset_size_low) / (asset_size_high - asset_size_low) * (base_rate_high - base_rate_low)
	
	return base_rate

# based on the preset limit and their respective limit retention factors
# linearly interpolate the factor for limits in between discreet values
def _get_limit_retention_factor(limit, limits, limit_factors):
	if limit == limits[-1]:
		return limit_factors[-1]

	low_idx = len(limits[limits <= limit]) - 1
	high_idx = low_idx + 1

	limit_low = limits[low_idx]
	limit_high = limits[high_idx]
	factor_low = limit_factors[low_idx]
	factor_high = limit_factors[high_idx]

	# linear interpolation
	factor = factor_low + (limit - limit_low) / (limit_high - limit_low) * (factor_high - factor_low)

	return factor

def _get_industry_factor(group, industry_factor_dict):
	return industry_factor_dict[group]