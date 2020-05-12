# whatsapp_analyser

Works with the .txt file export from WhatsApp (no media) to provide summary statistics in the form of graphs and tables.
Steps to use the WhatsAppAnalyser:
1. Export the txt file from WhatsApp and save it inyour working directory.
2. Create an instance of this class using:WhatsAppAnalyser()
3. Enter the full name of the .txt file and hit enter

The analyser will use Plotly to create variousdynamic graphs including:
Number of Messages VS Day of Week
Number of First Contacts VS User
Number of Messages VS Hour of Day

It will also create 2 tables showing:
Number of sent messages by user
Total words sent by user
Average length of message by user
First contact count by user
Total messages sent by day of the week