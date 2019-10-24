import discord
import math
import statistics
import random
from requests_html import HTMLSession
session = HTMLSession()


def probability(x, prob_list):
    # prob_list = [90, 70, 60, 50, 85]
    meanx = statistics.mean(prob_list)
    standard_deviation = statistics.stdev(prob_list)
    o = standard_deviation / math.sqrt(len(prob_list))
    t_test_url = 'https://people.richland.edu/james/lecture/m170/tbl-t.html'
    r = session.get(url=t_test_url)
    t = r.html.find('tr')[len(prob_list) + 1].text.split('\n')[4]

    UCL = round(meanx + (float(t) * o), 2)
    LCL = round(meanx - (float(t) * o), 2)

    percentage = 1.0 - ((int(x) - meanx) / standard_deviation)
    range_percent = round(percentage * 100, 2)
    percentage = str(round(percentage * 100, 2)) + "%"
    percentlist = []
    if range_percent >= 100 or range_percent <= 0:
        for newx in range(int(LCL), int(UCL) + 2):
            new_percentage = 1.0 - ((newx - meanx) / standard_deviation)
            new_percentage = round(new_percentage * 100, 2)
            if new_percentage < 100:  # can't have +100%
                percentlist.append(str(new_percentage) + " " + str(newx))
                maxPercent = max(percentlist)
        swap = maxPercent.split(" ")
        prob = "Maximum x with highest percentage: " + swap[1] + " (" + swap[0] + "%)"
    else:
        prob = ''
    statement = """
```
Percentage: {percentage}
Lower Confidence Level: {LCL}
Upper Confidence Level: {UCL}
{prob}
```
    """.format(percentage=percentage, LCL=LCL, UCL=UCL, prob=prob)
    return statement


def history():
    history_url = 'https://www.history.com/this-day-in-history'
    r = session.get(url=history_url)
    main_title = r.html.find('h1.m-detail-header--title')[0].text
    main_body = r.html.find('div.m-detail--body')[0].text.split('\n')[0]
    citation = r.html.find('div.m-detail--citation-meta')[3].text.split('\n')[1]
    side_quests = r.html.find('div.l-grid--item')
    main_story = [main_title, main_body, citation]
    side_stories = []
    j = 0
    for i in range(len(side_quests)):  # capturing all alternate stories
        side_stories.append(side_quests[i].text.split('\n'))
        j = j + 4

    for y in range(len(side_stories)):  # adds citation to each story
        credit = list(r.html.find('phoenix-super-link')[y].links)
        if 'this-day-in-history' in credit[0]:
            side_stories[y].append('https://www.history.com' + credit[0])
        else:
            side_stories[y].append('https://www.history.com' + credit[1])

    story_list = main_story + side_stories  # picks a story at random
    value = random.randint(0, len(story_list) - 1)
    if value == 0:
        story = """
```
{title} \n
{body} \n
{citation}
```
        """.format(title=main_title, body=main_body, citation=citation)
        return story
    else:
        if value == 1 or value == 2:
            value = random.randint(3, len(story_list) - 1)
        story = """
```
{genre} \n
{year} \n
{title} \n
{body} \n
{citation} 
```
                """.format(genre=story_list[value][0], year=story_list[value][1], title=story_list[value][2],
                           body=story_list[value][3], citation=story_list[value][4])
        return story


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

        if message.author == client.user:
            return

        if message.content.startswith('.stats'):  # need to implement > 100% prob; the print output + critical T score
            # example: .stats P(x >= 87):[90, 70, 60, 50, 85]
            x = message.content.split(" ")[3].split(')')[0]
            prob_list = message.content.strip(']').split('[')[1].strip(',').replace(',', '').split(' ')
            new_prob_list = []
            for i in range(len(prob_list)):
                new_prob_list.append(int(prob_list[i]))
            if len(new_prob_list) > 30:
                await message.channel.send('Sample size is too big')
            else:
                await message.channel.send(probability(int(x), new_prob_list))

        if message.content.startswith('.history'):
            # example: .history
            await message.channel.send(history())

        if message.content.startswith('.help'):
            # example: .help
            await message.channel.send("""
```
.help - shows help menu
.history - gives random history facts of the day
.stats - give percentage of x from list. \n         Ex: .stats P(x >= 87):[90, 70, 60, 50, 85]
```
            """)


client = MyClient()
client.run('[insert discord bot token]')
