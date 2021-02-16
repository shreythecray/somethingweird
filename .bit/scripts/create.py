import re
import ast

weeks = []
responses = []
stepContent = {}
steps = {}

name = "# (.*)"
content = "(?<=\*)[^*]+(?=\*)"
with open(".bit/course-details.md", "r") as file:
  file = file.read()
  course_name = re.findall(name, file)[0]
  course_descr = re.findall(content, file)[0]

with open(".bit/.info", "r") as myfile:
  readList = ast.literal_eval(myfile.read())
  print(readList)
  responses = readList["responses"]
  weeks = readList["weeks"]

with open(".bit/.config", "r") as myfile:
  stepContent = ast.literal_eval(myfile.read())

for i in range(1,int(max(weeks))+1):
  count = 0
  for file in responses:
    if int(file[0]) == i:
        count += 1
  steps[i] = count

def createStep(week, title, descr, event, response, files):
  content = "    - title: 'Week %s: %s'\n      description: %s\n      event: %s\n      link: '{{ repoUrl }}/issues'\n      actions:\n        - type: respond\n          with: %s\n          files: %s\n" % (week, title, descr, event, response, files)
  return content

def writeyml():
  print("Creating the config.yml file...")
  final = ""
  content = "title: %s\ndescription: >-\n    %s\ntemplate:\n    name: %s\n    repo: %s\nbefore:\n    - type: createIssue\n      title: Week 1\n      body: %s" % (course_name, course_descr, "learninglab-template", "your-learninglab-template", responses[0])
  count = 0
  for i in range(int(max(weeks))):
    for y in range(steps[i+1]):
      if y == steps[i+1]-1:
        response = "feedback.md"
      else:
        response = responses[count+1]
      final += createStep(i+1, stepContent[responses[count]][0], stepContent[responses[count]][1], "pull_request.closed", response, stepContent[responses[count]][2])

      if y == steps[i+1]-1 and i == int(max(weeks)) - 1:
        final += "    - title: 'Week %s: Feedback'\n      description: Provide your feedback for Week %s!\n      event: issue_comment.created\n      link: '{{ repoUrl }}/issues'\n      actions:\n        - type: respond\n          with: %s\n        - type: closeIssue\n" % (i+1, i+1, str(i+1)+"-complete.md")
      elif y == steps[i+1]-1:
        final += "    - title: 'Week %s: Feedback'\n      description: Provide your feedback for Week %s!\n      event: issue_comment.created\n      link: '{{ repoUrl }}/issues'\n      actions:\n        - type: respond\n          with: %s\n        - type: createIssue\n          title: Week %s\n          body: %s\n        - type: closeIssue\n" % (i+1, i+1, str(i+1)+"-complete.md", i+2, responses[count+1])
      count += 1
  
  configyml = content + "\nsteps:\n" + final
  return configyml

try:
  with open(".bit/responses/feedback.md", "w+") as myfile:
    print("Creating response files...")
    myfile.write("## Providing Feedback\n\nWhat was confusing about this week? If you could change or add something to this week, what would you do? Your feedback is valued and appreciated!")

  for i in range(1,int(max(weeks))+1):
    with open(".bit/responses/" + str(i) + "-complete.md", "w+") as response:
      if i == int(max(weeks)):
        response.write("That's it for Week %s! Great job on finishing the course!" % str(i))
      else:
        response.write("That's it for Week %s, move on to Week %s in your new issue!" % (str(i), str(i + 1)))

  with open(".bit/config.yml", "w+") as file:
    file.write(writeyml())
except:
  raise Exception("[ERROR] Was not able to create response and/or config.yml files. Refer to errors in previous steps for guidance.")