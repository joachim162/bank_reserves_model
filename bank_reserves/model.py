#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bank_reserves.agents import Bank, Person
from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np
import random

"""
The following code was adapted from the Bank Reserves model included in Netlogo
Model information can be found at: http://ccl.northwestern.edu/netlogo/models/BankReserves
Accessed on: November 2, 2017
Author of NetLogo code:
    Wilensky, U. (1998). NetLogo Bank Reserves model.
    http://ccl.northwestern.edu/netlogo/models/BankReserves.
    Center for Connected Learning and Computer-Based Modeling,
    Northwestern University, Evanston, IL.
"""

"""
If you want to perform a parameter sweep, call batch_run.py instead of run.py.
For details see batch_run.py in the same directory as run.py.
"""


# Start of DataCollector functions
def get_num_rich_agents(model):
    # list of rich agents
    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    # return number of rich agents
    return len(rich_agents)


def get_num_poor_agents(model):
    # list of poor agents
    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    # return number of poor agents
    return len(poor_agents)


def get_num_mid_agents(model):
    # list of middle class agents
    mid_agents = [a for a in model.schedule.agents if
                  a.loans < 10 and a.savings < model.rich_threshold]
    # return number of middle class agents
    return len(mid_agents)


def get_total_savings(model):
    # list of amounts of all agents' savings
    agent_savings = [a.savings for a in model.schedule.agents]
    # return the sum of agents' savings
    return np.sum(agent_savings)


def get_total_wallets(model):
    # list of amounts of all agents' wallets
    agent_wallets = [a.wallet for a in model.schedule.agents]
    # return the sum of all agents' wallets
    return np.sum(agent_wallets)


def get_total_money(model):
    # sum of all agents' wallets
    wallet_money = get_total_wallets(model)
    # sum of all agents' savings
    savings_money = get_total_savings(model)
    # return sum of agents' wallets and savings for total money
    return wallet_money + savings_money


def get_total_loans(model):
    # list of amounts of all agents' loans
    agent_loans = [a.loans for a in model.schedule.agents]
    # return sum of all agents' loans
    return np.sum(agent_loans)


class BankReservesModel(Model):

    # grid height
    grid_h = 20
    # grid width
    grid_w = 20

    """init parameters "init_people", "rich_threshold", and "reserve_percent"
       are all UserSettableParameters"""
    def __init__(self, height=grid_h, width=grid_w, init_people=2, rich_threshold=10,
                 reserve_percent=50, run_time=1000):
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        # rich_threshold is the amount of savings a person needs to be considered "rich"
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent
        self.run_time = run_time  # Store run_time as an attribute
        
        # see datacollector functions above
        self.datacollector = DataCollector(model_reporters={
                                           "Rich": get_num_rich_agents,
                                           "Poor": get_num_poor_agents,
                                           "Middle Class": get_num_mid_agents,
                                           "Savings": get_total_savings,
                                           "Wallets": get_total_wallets,
                                           "Money": get_total_money,
                                           "Loans": get_total_loans},
                                           agent_reporters={
                                           "Wealth": lambda x: x.wealth})

        # create a single bank for the model
        self.bank = Bank(1, self, self.reserve_percent)

        # create people for the model according to number of people set by user
        for i in range(self.init_people):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            self.grid.place_agent(p, (x, y))
            self.schedule.add(p)

        # Explicitly set running to True
        self.running = True
        self.current_step = 0

    def step(self):
        # Only step if the model is still running
        if self.running:
            # collect data
            self.datacollector.collect(self)
            # tell all the agents in the model to run their step function
            self.schedule.step()
            self.current_step += 1

            # Optional: stop the model after a certain number of steps
            if self.current_step >= self.run_time:
                self.running = False

            # if the step count is in the list then create a data file of model state
            if self.current_step in [100, 500, 1000]:
                model_data = self.datacollector.get_model_vars_dataframe()
                model_data.to_csv(f"BankReservesModel_Step_Data_Single_Run{self.current_step}.csv")

    def run_model(self, run_time=1000):
        """
        Run the model for a specified number of steps.
        
        Args:
            run_time (int): Number of steps to run the model. Defaults to 1000.
        """
        for i in range(run_time):
            print(f'Stepping {i}')
            self.step()
