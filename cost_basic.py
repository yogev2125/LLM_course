import anthropic
import json
import time
import re
import numpy as np
import matplotlib.pyplot as plt

f = open('task_2_plan_optimality.json')
data = json.load(f)
client = anthropic.Anthropic(api_key=api_key)
answer_reg = r"(\((\w*-?\w*\s*)+\))"
break_point =[]
corr_count=np.zeros(20)
def get_message(problem: str):
  return client.messages.create(
      model="claude-3-5-sonnet-20240620",
      max_tokens=1000,
      temperature=0,
      system="write the best plan you can using only (action object) or (action ob1 ob2).",
      messages= [
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": problem
                  }
              ]
          }
      ]
  ) 
def format_answer(response : str):
  answer_reg = r"(\((\w*-?\w*\s*)+\))+"
  response_array = re.findall(answer_reg,  response)
  answer =""
  # print(response)
  for index,i in enumerate(response_array):
    if index >-1 and i[0] != "(action object)" and i[0] != "(action ob1 ob2)":
      answer +=i[0]
  return answer.replace("putdown","put-down").replace("pickup","pick-up")

def compare_prefix(answer:str, correct:str):
  print("started compare_prefix")
  cor_array = re.findall(answer_reg,answer)
  answer_array = re.findall(answer_reg,correct)
  size = len(answer_array)
  for i,action in enumerate(cor_array):
    if i>=size or (i<size and action[0] != answer_array[i][0]):
      break
    if i>=len(break_point):
      break_point.append(1)
    else:
      break_point[i]+=1
  for i,action in enumerate(answer_array):
    corr_count[i] +=1
  print("ended compare_prefix")

      
    

remove = len(" My plan is as follows:\n\n[PLAN]")
# suffix = ". describe initial state and return the plan using *only* the notation (action object) or (action ob1 ob2) [new state], use every new state as new initial state.\n\
#   \nthen say if the plan is logicly correctMy plan is as follows:\n\n[PLAN]"
suffix = "describe initial state and return the plan using *only* the notation (action object) or (action ob1 ob2).\n\
  :\n\n[PLAN]"

init_regex = r"As initial (\w+\,*\s*)+(\w)+\."
goal_regex = r"My goal is\s(\w+\s)+(\w*)"


success = 0
match_list = []
data_size = len(data["instances"])

for i,instance in enumerate(data["instances"]):
  if i == 200: break
  print(f"test number: {i}/{data_size}")
  problem = str(instance["query"])[:-remove] + suffix
  goal = re.search(goal_regex, problem).group()
  message = get_message(problem).content[0].text
  correct = str(instance["ground_truth_plan"]).replace("\n","")
  response = format_answer(message)
  # print(problem)
  
  print("\n",goal)
  print("\n",response,"\n",correct,"\n\n")
  succ = True
  for j,c in enumerate(correct):
    if len(correct) > len(response) or response[j]!=c:
      succ = False
      break
  if succ:
    match_list.append(i)
    print("success!!!!")
    success +=1
  print(success/len(data["instances"]))
  print(match_list)
  compare_prefix(response,correct)
print(break_point)

plt.plot(np.arange(1,len(break_point)+1),break_point,label = "LM's correct actions") 
plt.plot(np.arange(1,len(break_point)+1),corr_count[:len(break_point)],label = "corrects answers length") 
plt.legend()
plt.grid()

plt.show()