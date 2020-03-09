# Making Notes Useful: Experiments with OneNote

Machine learning is now widely used to discover insights and relationships from user data. Applications can identify the required language, extract key phrases and entities, retrieve a positive or negative sentiment associated with the text and automatically organize data (by time, topics, content etc.). The focus of this project is to explore how machine learning can be applied to user notes to capture insights.

1. Create skeleton to retrieve required details from OneNote API.
2. Draw insights from the collected raw API data

Currently only (1) has been implemented. The code can be found here.

The note-taking application used for this project is OneNote and a significant portion of the content related to project management tasks such as flagging open questions, tracking action items, summarizing meeting minutes etc. This project tries to automate the more trivial tasks like predicting next activity or sub-activity in the workflow, track open items etc. and use data points from previous notes items to inform (and ideally automate) future steps in the workflow. More simply, the application should be able to tell you your work items everyday (or a timescale or your choice). While there are several popular project management tools available (some of which may even include this feature in some sense), this effort is centered around the analysis of note content from an ML and NLP perspective to gain useful insights and not so much from a project management perspective.

## Context discovery
Context discovery in notes is currently difficult, time-consuming, and often frustrating due to the effort it takes to reveal useful or pertinent information from our notes. Today's note-taking apps are designed as digital storage buckets that require diligent organization to find information easily. Additionally, the inputs to the task of information discovery are vague. Here are some considerations:
1. What is the unit of analysis for gathering context ? At the paragraph/list level or note-block level ?
2. What is the input to output mapping ? many to one or many to many ?
3. Note taking is inherently subjective. There is a lot of variability in writing style and drawing conclusions

## Experiments
We will create a baseline skeleton code base and interface to retrieve user notes, which can then be fed to downstream machine learning and natural language processing algorithms for insights. Once completed, the next step is to develop a methodology to predict the next logical step for each task sub-activity in the workflow.

**Assumptions**
* Contiguous text blocks (paragraphs, lists) belong to same sub-activity
* Notes contains labels (TODO, action item, team name etc.) for context
* Current API only picks from last ~7 days

### Approach outline
1. Track activities in a day at section level
2. Track activities at page level and use page titles as labels
3. Create sub-activity flows using content in each contiguous text block
4. Experiment with clustering algorithm to identify closely associated sub-activities
5. Align macro understanding (similarity, topic analysis etc.) with micro understanding (terms, phrases, sentences etc.)
6. Create chronology/logical flow from identified sub-activities
7. Predict next step in the logical flow

### Version 0
Simple tasks such as:
1. Reaching out to contact
2. Setting up meetings
3. Adding to running list of open questions etc.
Note: Depending on the gaps in data, the effort may also need integration with Outlook API for aggregation of mailbox information (mails, meetings, tasks etc.) to help inform current activity, sub-activity and next steps

## References
1. https://medium.com/@mylesmcginley/ai-meets-your-notebook-8c2228e0d701
2. https://teamworkiq.com/assign-tasks-from-meeting-minutes/
3. https://www.wrike.com/blog/action-items-with-meeting-notes-template/
4. https://www.searchtechnologies.com/blog/natural-language-processing-techniques
5. https://asana.com/guide/resources/info-sheets/everyday-workflows
6. https://docs.microsoft.com/en-us/graph/integrate-with-onenote
7. https://portal.azure.com/?quickstart=true#blade/Microsoft_Azure_Resources/QuickstartCenterBlade
