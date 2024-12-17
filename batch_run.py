#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bank_reserves.agents import Bank, Person
import itertools
from mesa import Model
from mesa.batchrunner import BatchRunner
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns

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

###############################################################################

"""
This version of the model has a BatchRunner at the bottom. This
is for collecting data on parameter sweeps. It is not meant to
be run with run.py, since run.py starts up a server for visualization, which
isn't necessary for the BatchRunner. To run a parameter sweep, call
batch_run.py in the command line.

The BatchRunner is set up to collect step by step data of the model. It does
this by collecting the DataCollector object in a model_reporter (i.e. the
DataCollector is collecting itself every step).

The end result of the batch run will be a csv file created in the same
directory from which Python was run. The csv file will contain the data from
every step of every run.
"""


# Start of DataCollector functions
def get_num_rich_agents(model):
    rich_agents = [a for a in model.schedule.agents if a.savings > model.rich_threshold]
    return len(rich_agents)

def get_num_poor_agents(model):
    poor_agents = [a for a in model.schedule.agents if a.loans > 10]
    return len(poor_agents)

def get_num_mid_agents(model):
    mid_agents = [a for a in model.schedule.agents if a.loans < 10 and a.savings < model.rich_threshold]
    return len(mid_agents)

def get_total_savings(model):
    agent_savings = [a.savings for a in model.schedule.agents]
    return np.sum(agent_savings)

def get_total_wallets(model):
    agent_wallets = [a.wallet for a in model.schedule.agents]
    return np.sum(agent_wallets)

def get_total_money(model):
    wallet_money = get_total_wallets(model)
    savings_money = get_total_savings(model)
    return wallet_money + savings_money

def get_total_loans(model):
    agent_loans = [a.loans for a in model.schedule.agents]
    return np.sum(agent_loans)

def track_params(model):
    return (model.init_people, model.rich_threshold, model.reserve_percent)

def track_run(model):
    return model.uid

class BankReservesModel(Model):
    id_gen = itertools.count(1)

    grid_h = 20
    grid_w = 20

    def __init__(self, height=grid_h, width=grid_w, init_people=2, rich_threshold=10, reserve_percent=50):
        self.uid = next(self.id_gen)
        self.height = height
        self.width = width
        self.init_people = init_people
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.width, self.height, torus=True)
        self.rich_threshold = rich_threshold
        self.reserve_percent = reserve_percent

        self.datacollector = DataCollector(
            model_reporters={
                "Step": lambda m: m.schedule.time,
                "Rich": get_num_rich_agents,
                "Poor": get_num_poor_agents,
                "Middle Class": get_num_mid_agents,
                "Savings": get_total_savings,
                "Wallets": get_total_wallets,
                "Money": get_total_money,
                "Loans": get_total_loans,
                "Model Params": track_params,
                "Run": track_run
            },
            agent_reporters={"Wealth": lambda x: x.wealth}
        )

        self.bank = Bank(1, self, self.reserve_percent)

        for i in range(self.init_people):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            p = Person(i, (x, y), self, True, self.bank, self.rich_threshold)
            self.grid.place_agent(p, (x, y))
            self.schedule.add(p)

        self.running = True

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def run_model(self):
        for i in range(self.run_time):
            self.step()

br_params = {"init_people": [25, 100, 150, 200],
             "rich_threshold": [5, 10, 15, 20],
             "reserve_percent": [0, 50, 100]}

# Visualization Functions
def visualize_data(step_data):
    plt.figure(figsize=(10, 6))
    plt.plot(step_data["Step"], step_data["Savings"], label="Total Savings", linewidth=1, alpha=0.7)
    plt.plot(step_data["Step"], step_data["Loans"], label="Total Loans", linewidth=1, alpha=0.7)
    plt.xlabel("Step")
    plt.ylabel("Amount")
    plt.title("Total Savings and Loans Over Time")
    plt.legend()
    plt.grid()
    plt.savefig("Savings_Loans_Over_Time.png", dpi=300)
    plt.close()

    step_data["Bank Reserves"] = step_data["Savings"] * 0.2
    plt.figure(figsize=(10, 6))
    plt.plot(step_data["Step"], step_data["Savings"], label="Deposits", linewidth=1, alpha=0.7)
    plt.plot(step_data["Step"], step_data["Bank Reserves"], label="Bank Reserves", linewidth=1, alpha=0.7)
    plt.plot(step_data["Step"], step_data["Loans"], label="Loans", linewidth=1, alpha=0.7)
    plt.xlabel("Step")
    plt.ylabel("Amount")
    plt.title("Bank Deposits, Reserves, and Loans Over Time")
    plt.legend()
    plt.grid()
    plt.savefig("Bank_Reserves_Loans.png", dpi=300)
    plt.close()

if __name__ == '__main__':
    br = BatchRunner(
        BankReservesModel,
        br_params,
        iterations=1,
        max_steps=1000,
        model_reporters={"Data Collector": lambda m: m.datacollector}
    )

    br.run_all()
    br_df = br.get_model_vars_dataframe()

    step_data_frames = []
    for i in range(len(br_df["Data Collector"])):
        if isinstance(br_df["Data Collector"][i], DataCollector):
            i_run_data = br_df["Data Collector"][i].get_model_vars_dataframe()
            i_run_data["Run"] = i + 1
            step_data_frames.append(i_run_data)

    br_step_data = pd.concat(step_data_frames, ignore_index=True)

    if "Step" not in br_step_data.columns:
        raise ValueError("Step column is missing from the data.")

    br_step_data.to_csv("BankReservesModel_Step_Data.csv", index=False)
    visualize_data(br_step_data)

