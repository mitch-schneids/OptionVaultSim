from cmath import exp
from mimetypes import init
import cadCAD
import pandas as pd
import plotly.express as px
import state_updates as su
import random
from numpy import random 
from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Experiment
from cadCAD.engine import ExecutionMode, ExecutionContext
from cadCAD.engine import Executor

def generate_params():
    params = {}

    params['fee_dov'] = [random.uniform(0.05, 0.22)]
    params['fee_agg'] = [random.uniform(0.01, 0.05)]
    params['premium_rate'] = [random.uniform(0.01, 0.05)]
    
    return params

def main():
    filename = 'res/eth-usd.xlsx'
    excel = pd.read_excel(filename)
    dataset = excel.to_dict('records')
    
    strike_prices = [4400, 3700, 3700, 3200, 2800]
    
    for _ in range(100):
        params = generate_params()
        week_cnt = 0

        for i in range(0, 35, 7):
            init_dataset, expiry_dataset = dataset[i], dataset[i + 6]

            genesis_states = {
                'eth_supply': random.randint(1000, 3000),
                'init_eth_price': init_dataset['price'],
                'expiry_eth_price': expiry_dataset['price'],
                'fee_agg': 0,
                'fee_dov': 0,
                'agg_quantity': 0,
                'dov_quantity': 0,
                'treasury': 0,
                'strike_price': strike_prices[week_cnt],
                'premium': 0,
                'options_sold' : 0,
                'expired' : False
            }

            PSUBs = {
                'agg_state' : {
                    'policies' : {},
                    'variables' : {
                        's_fee_agg' : su.s_fee_agg,
                        's_deposit_agg' : su.s_deposit_agg
                    }
                },
                'dov_state0' : {
                    'policies' : {},
                    'variables' : {
                        's_deposit_dov' : su.s_deposit_dov,
                        's_options_expired' : su.s_options_expired
                    }
                },

                'dov_state1' : {
                    'policies' : {},
                    'variables' : {
                        's_options_sold' : su.s_options_sold
                    }
                },
                'dov_state2' : {
                    'policies' : {},
                    'variables' : {
                        's_premium_dov' : su.s_premium_dov,
                        's_fee_dov' : su.s_fee_dov
                    }
                }
            }


        pd.options.plotting.backend = 'plotly'

        MONTE_CARLO_RUNS = 50
        SIMULATION_TIMESTEPS = 500

        print(params)
        sim_config = config_sim(
            {
            'N': MONTE_CARLO_RUNS,
            'T': range(SIMULATION_TIMESTEPS),
            'M': params
            }
        )

        # Append configs
        exp = Experiment()
        exp.append_configs(
            initial_state = genesis_states, 
            partial_state_update_blocks = PSUBs, 
            sim_configs = sim_config

        )
        # Execution
        exec_mode = ExecutionMode()
        local_mode_ctx = ExecutionContext(context=exec_mode.local_mode)
        simulation = Executor(exec_context=local_mode_ctx, configs=exp.configs)

        raw_system_events, tensor_field, sessions = simulation.execute()

        simulation_result = pd.DataFrame(raw_system_events)

        df = simulation_result.copy()
        df = df[df.simulation == 0]
        df

        df[df.run == 1].head()
        df[df.run == 2].head()
        df[df.run == 3].head()

        px.line(df, x='timestep', y=['agg_fee', 'dov_fee', 'premium'], facet_row = 'subset', height=800, width=1000)

        week_cnt += 1

if __name__ == '__main__':
    main()
