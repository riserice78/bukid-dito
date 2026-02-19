from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent

from typing import List
from pathlib import Path
from bukid.models.models import VegetableScheduleOutput
import json
import streamlit as st
from crewai.tasks.task_output import TaskOutput
from langchain_anthropic import ChatAnthropic

from crewai_tools import FileReadTool
claude = ChatAnthropic(model="claude-sonnet-4-5")   #claude-sonnet-4-20250514



@CrewBase
class Bukid():
    """Bukid crew"""

    @before_kickoff
    def before_kickoff_function(self, inputs):
        print(f"Before kickoff function with inputs: {inputs}")
        return inputs # You can return the inputs or modify them as needed

    @after_kickoff
    def after_kickoff_function(self, result):
        print(f"After kickoff function with result")
        return result # You can return the result or modify it as needed

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def plant_finder(self) -> Agent:
        #file_read_test = FileReadTool(file_path='./src/bukid/sample_response/plant_finder.txt')
        return Agent(
            config=self.agents_config['plant_finder'], # type: ignore[index]
            verbose=True,
            llm=claude
            #tools=[file_read_test]    #SerperDevTool()
        )

    @agent
    def plant_researcher(self) -> Agent:
        #file_read_test = FileReadTool(file_path='./src/bukid/sample_response/plant_researcher.txt')
        return Agent(
            config=self.agents_config['plant_researcher'], # type: ignore[index]
            verbose=True,
            llm=claude
            #tools=[file_read_test]
        )
    
    
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task

    @task
    def plant_finder_task(self) -> Task:
        print(f"In plant_finder_task")
        return Task(
            config=self.tasks_config['plant_finder_task'], # type: ignore[index],
            callback=lambda output: print("TASK 2 plant_finder_task COMPLETED") 
        )

    @task
    def plant_researcher_task(self) -> Task:
        print(f"In plant_researcher_task")
        return Task(
            config=self.tasks_config['plant_researcher_task'], # type: ignore[index],
            output_pydantic=VegetableScheduleOutput
            #callback=lambda output: print("TASK 4 plant_researcher_task COMPLETED") 
        )


    @crew
    def research_crew(self) -> Crew:
        return Crew(
            agents=[self.plant_finder()],
            tasks=[self.plant_finder_task()], 
            process=Process.sequential,
            verbose=False
        )

    # ── Schedule-only crew ───────────────────────────────────
    @crew
    def schedule_crew(self) -> Crew:
        return Crew(
            agents=[self.plant_researcher()], #self.reporter()
            tasks=[self.plant_researcher_task()], # self.reporter_task()
            process=Process.sequential,
            verbose=False
        )


def run_research(crew_inputs: dict) -> str:
    inputs = {
        "location": crew_inputs["location"],
        "previous_year": crew_inputs["previous_year"],
        "language": crew_inputs["language"],
        "planting_medium": crew_inputs["planting_medium"]
    }
    result = Bukid().research_crew().kickoff(inputs)
    return result.raw


def run_schedule(crew_inputs: dict, vegetables: str) -> str:
    print(f"In run_schedule: {crew_inputs}")
    inputs = {
        "location": crew_inputs["location"],        # 👈 use dict access
        "vegetables": vegetables,
        "language": crew_inputs["language"],
        "planting_medium": crew_inputs["planting_medium"]
    }
    result = Bukid().schedule_crew().kickoff(inputs=inputs)
    return result.pydantic