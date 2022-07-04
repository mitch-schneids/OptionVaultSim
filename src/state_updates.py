import math
import random

def s_fee_agg(params, substep, state_history, previous_state, policy_input):
    value = previous_state['eth_supply'] * previous_state['init_eth_price']
    fee = value * params['fee_agg']

    return 'fee_agg', fee

def s_deposit_agg(params, substep, state_history, previous_state, policy_input):
    value = previous_state['eth_supply'] * previous_state['init_eth_price']
    fee = value * params['fee_agg']

    agg_quantity = fee /  previous_state['init_eth_price']

    return 'agg_quantity', agg_quantity


def s_deposit_dov(params, substep, state_history, previous_state, policy_input):
    dov_quantity = previous_state['eth_supply'] - previous_state['agg_quantity']

    return ('dov_quantity', dov_quantity)

def s_premium_dov(params, substep, state_history, previous_state, policy_input):
    premium = previous_state['init_eth_price'] * previous_state['options_sold'] * params['premium']

    return 'premium', premium

def s_fee_dov(params, substep, state_history, previous_state, policy_input):
    fee_dov = previous_state['options_sold'] * previous_state['expiry_eth_price'] * params['fee_dov']

    return 'fee_dov', fee_dov if not previous_state['options_expired'] else 0

def s_options_sold(params, substep, state_history, previous_state, policy_input):
    options_sold = math.floot(previous_state['dov_quantity'] * 0.90)

    return 'options_sold', options_sold

# calc if options finished ITM or OTM
def s_options_expired(params, substep, state_history, previous_state, policy_input):
    return 'expired', True if previous_state['expiry_eth_price'] >= previous_state['strike_price'] else False
