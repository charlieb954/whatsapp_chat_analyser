import pandas as pd
import re
from datetime import datetime
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# pip install -r requirements.txt 
# run above from the command line

class WhatsAppAnalyser:
    '''Works with the .txt file export from WhatsApp (no media) to provide summary statistics in the form of graphs and tables.
    Steps to use the WhatsAppAnalyser:
    1. Export the txt file from WhatsApp and save it in your working directory.
    2. Create an instance of this class using: WhatsAppAnalyser()
    3. Enter the full name of the .txt file and hit enter
    
    The analyser will use Plotly to create various dynamic graphs including:
    Number of Messages VS Day of Week
    Number of First Contacts VS User
    Number of Messages VS Hour of Day
    
    It will also create 2 tables showing:
    Number of sent messages by user
    Total words sent by user
    Average length of message by user
    First contact count by user
    Total messages sent by day of the week'''
    
    def __init__(self):
        filename = input('please enter the filename of the txt chat export with extension: ')
        self.chat_list = self.read_file(filename)
        self.chat_list_breakdown = self.chat_breakdown(self.chat_list)
        self.message_stats = self.message_analysis(self.chat_list_breakdown)
        self.contact_dates = self.unique_contact_dates(self.chat_list_breakdown)
        self.first_contact_count = self.count_first_contact(self.chat_list_breakdown, 
                                                            self.contact_dates)
        self.hourly_chat_dict = self.hourly_chat_pattern(self.chat_list_breakdown)
        self.weekday_count = self.weekday_chat_pattern(self.chat_list_breakdown)
        self.create_plots()
        self.create_tables()
    
    def read_file(self, filename):
        '''Accomodates multiple line messages, removes encryption msg and first ever message.
        TODO, add first ever message'''
        with open(filename, 'r') as f:
            chat_list = f.read().split('\n[')[1:]
            
        return chat_list

    def chat_breakdown(self, chat):
        '''Splits each chat row to a list containing: [time/date, username, message]'''
        chat_list_breakdown = []
        
        for each in chat:
            time_date = datetime.strptime(each.split('] ')[0], '%d/%m/%Y, %H:%M:%S')
            matches = re.search(r']\s([A-z0-9\s]*)', each)
            if matches:
                user = matches.group()[2:]
            messages = each.split(': ', 1)[1]
            chat_list_breakdown.append([time_date, user, messages])
            
        return chat_list_breakdown

    def message_analysis(self, chat_breakdown_list):
        '''Count number of messages sent, total number of words and average length of 
        message for each participant'''
        participants = set(each[1] for each in chat_breakdown_list)

        result_dict = dict()
        for user in participants:
            result_dict[user] = dict()
            counter = self.message_counter(user, chat_breakdown_list)
            result_dict[user]["num_sent_messages"] = counter[0]
            result_dict[user]['total_words_sent'] = counter[1]
            result_dict[user]["average_len_message"] = round(counter[1] / counter[0], 2)
            
        return result_dict

    def message_counter(self, user, msg_list):
        '''returns 
        i = number of messages sent by user
        total_len_messages = total number of words sent over all messages'''
        i = 0
        total_len_messages = 0
        for msg_grp in msg_list:
            if msg_grp[1] == user:
                total_len_messages += len(msg_grp[2].split(' '))
                i += 1
                
        return i, total_len_messages

    def unique_contact_dates(self, chat_breakdown_list):
        '''Returns a set of unique contact dates'''
        contact_dates = set()
        for each in chat_breakdown_list:
            contact_dates.add(each[0].date())
        
        contact_dates = sorted(contact_dates)
        
        return contact_dates

    def count_first_contact(self, chat_breakdown_list, contact_dates):
        '''Counts the number of first contacts for each user'''
        chat_breakdown_list.sort(key=lambda x: x[0])

        first_contact_dict = dict()
        for each in contact_dates:
            iterator = filter(lambda date: date[0].date() == each, chat_breakdown_list)
            filtered_numbers = list(iterator)
            first_contact_dict[filtered_numbers[0][1]] = first_contact_dict.get(filtered_numbers[0][1], 0) + 1
        
        return first_contact_dict

    def hourly_chat_pattern(self, chat_breakdown_list):
        '''Work out hourly contact patterns'''
        date_time = [each[0] for each in chat_breakdown_list]
        hours = [each.hour for each in date_time]
        hours_dict = dict({i: 0 for i in range(1,25)})
        for each in hours_dict:
            hours_dict[each] = hours.count(each)
        
        return hours_dict

    def weekday_chat_pattern(self, chat_breakdown_list):
        '''Work out weekly contact patterns'''
        date_time = [each[0] for each in chat_breakdown_list]
        weekdays = [each.weekday() for each in date_time]
        weekday_map = { 0: 'Monday', 
                        1: 'Tuesday',
                        2: 'Wednesday',
                        3: 'Thursday',
                        4: 'Friday',
                        5: 'Saturday',
                        6: 'Sunday'}
        weekdays = list(map(lambda x : weekday_map[x], weekdays))
        weekday_count = dict({day:0 for day in weekday_map.values()})
        for each in weekday_count:
            weekday_count[each] = weekdays.count(each)
        
        return weekday_count

    def create_plots(self):
        '''Create graphs to show the following data:
        Number of Messages VS Day of Week
        Number of First Contacts VS User
        Number of Messages VS Hour of Day'''
        fig = make_subplots(rows=3, 
                            cols=1, 
                            subplot_titles = ['Number of First Contacts VS User',
                                              'Number of Messages VS Day of Week', 
                                              'Number of Messages VS Hour of Day'])

        fig.add_trace(go.Bar(
                    name='Msg VS Day',
                    x=list(self.first_contact_count.keys()),
                    y=list(self.first_contact_count.values())),
                    row=1, 
                    col=1)

        fig.add_trace(go.Bar(
                    name='First VS User',
                    x=list(self.weekday_count.keys()),
                    y=list(self.weekday_count.values())), 
                    row=2, 
                    col=1)

        fig.add_trace(go.Bar(
                    name='Msg VS Hour',
                    x=list(self.hourly_chat_dict.keys()),
                    y=list(self.hourly_chat_dict.values())), 
                    row=3, 
                    col=1)

        fig.update_xaxes(title_text="Name of User", 
                        row=1, 
                        col=1)
        fig.update_xaxes(title_text="Day of Week", 
                        row=2, 
                        col=1)
        fig.update_xaxes(title_text="Hour of Day (24hr)", 
                        row=3, 
                        col=1)

        fig.update_yaxes(title_text="Number of First Contacts", 
                        row=1, 
                        col=1)
        fig.update_yaxes(title_text="Number of Messages", 
                        row=2, 
                        col=1)
        fig.update_yaxes(title_text="Number of Messages", 
                        row=3, 
                        col=1)

        fig.update_traces(marker_color='rgb(158,202,225)', 
                        marker_line_color='rgb(8,48,107)',
                        marker_line_width=1.5, 
                        opacity=0.6)

        fig.update_layout(title_text="<b>WhatsApp Analysis",
                        height=1000, 
                        width=1000,
                        showlegend = False)

        return fig.show()
    
    def create_tables(self):
        '''Create Pandas DataFrames with '''
        total_msg = pd.DataFrame(data=[self.weekday_count]).T
        total_msg.reset_index(inplace=True)
        total_msg.columns = ['Day of Week', 'Total Messages Sent']
        msg_stats = pd.DataFrame(self.message_stats)
        first_contact = pd.DataFrame([self.first_contact_count])
        first_contact.index = ['first_contact_count']
        stats_and_contact = msg_stats.append(first_contact, sort=False)
        print(stats_and_contact)
        print(total_msg)


WhatsAppAnalyser()