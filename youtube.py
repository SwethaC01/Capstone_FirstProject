# Import the Packages
import streamlit as st
import time
from streamlit_option_menu import option_menu
from googleapiclient.discovery import build
import isodate
import mysql.connector
import pandas as pd

# Youtube API Information

api_service_name = "youtube"
api_version = "v3"
api_key="AIzaSyC_cL7uS5_cPyYn5Mbe-Djir7HBNU5jpPI"
youtube = build(api_service_name, api_version,developerKey=api_key)

# Connect to the MySQL Database

mydb = mysql.connector.connect(host="localhost",user="root",password="",database='youtube_db')
mycursor = mydb.cursor(buffered=True)

mycursor.execute('create database IF NOT EXISTS youtube_db')

# Create table for Channel details
mycursor.execute('create table IF NOT EXISTS youtube_db.channel_table(channel_Id VARCHAR(255)PRIMARY KEY,channel_Name VARCHAR(255),channel_Type VARCHAR(255),channel_playlistId VARCHAR(255),channel_Description TEXT,channel_Status VARCHAR(255),channel_ViewCount INT,channel_Subcount INT,channel_VideoCount INT)')

# Create table for Video details
mycursor.execute('CREATE TABLE IF NOT EXISTS youtube_db.video_table(Video_Id VARCHAR(255)PRIMARY KEY,channel_Id VARCHAR(255),FOREIGN KEY(channel_Id)REFERENCES channel_table(channel_Id),video_name VARCHAR(255),video_description TEXT,video_published_date DATETIME,video_viewcount INT,video_likecount INT,video_favoritecount INT,video_commentcount INT,duration VARCHAR(255),video_thumbnails VARCHAR(255),video_caption_status VARCHAR(255));')

# Create table for Comments details
mycursor.execute("""CREATE TABLE IF NOT EXISTS youtube_db.comment_table (Videos_id VARCHAR(255),
FOREIGN KEY(Videos_id) REFERENCES video_table(Video_Id),
Comment_Id VARCHAR(255)PRIMARY KEY,
Comment_Text TEXT,
Comment_Author VARCHAR(255),
Comment_PublishedAt DATETIME)""")

# Get Channel Details

def channel_details(channel_id):
                        request = youtube.channels().list(part="snippet,contentDetails,statistics,status",id=channel_id)

                        response = request.execute()

                        data={"channel_Id":response['items'][0]['id'],
                                "channel_Name":response['items'][0]['snippet']['title'],
                                "channel_Type":response['items'][0]['kind'],
                                "channel_playlistId":response['items'][0]['contentDetails']['relatedPlaylists']['uploads'],
                                "channel_Description":response['items'][0]['snippet']['description'],
                                "channel_Status":response['items'][0]['status']['privacyStatus'],
                                "channel_ViewCount":response['items'][0]['statistics'].get('viewCount'),
                                "channel_Subcount":response['items'][0]['statistics']['subscriberCount'],
                                "channel_VideoCount":response['items'][0]['statistics']['videoCount']
                        }
                        return data

# Get Video ids

def get_videos_id(channel_id):
                
                response = youtube.channels().list(part="contentDetails",id=channel_id).execute()

                c_playlistId=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                vid_ids=[]

                next_Token=None

                while True:
                        responsev= youtube.playlistItems().list(part="snippet",playlistId=c_playlistId,maxResults=50,pageToken=next_Token).execute()
                        for v in range(len(responsev['items'])):
                                vid_ids.append(responsev['items'][v]['snippet']['resourceId']['videoId'])
                                next_Token=responsev.get('nextPageToken')
                        if next_Token is None:
                                break

                return vid_ids

# Converting duration to seconds

def duration_to_seconds(video_duration):
                
                duration = isodate.parse_duration(video_duration)
                hours = duration.days * 24 + duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60
                seconds = duration.seconds % 60
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return total_seconds

#Get Video details

def get_video_details(vid_ids):
                
                vid_data=[]

                for video_id in vid_ids:
                        request = youtube.videos().list(
                                part="snippet,contentDetails,statistics",id=video_id)
                        responses = request.execute()

                        for item in responses['items']:
                                video_duration=duration_to_seconds(item['contentDetails'].get('duration'))
                                video_info = {
                                "Video_Id":item['id'],
                                "Channel_Id":item['snippet']['channelId'],
                                "video_name":item['snippet']['title'],
                                "video_description": item['snippet'].get('description'),
                                "video_published_date":item['snippet']['publishedAt'],
                                "video_viewcount":item['statistics'].get('viewCount',0),
                                "video_likecount":item['statistics'].get('likeCount',0),
                                "video_favoritecount":item['statistics']['favoriteCount'],
                                "video_commentcount":item['statistics'].get('commentCount',0),
                                "duration":video_duration,
                                "video_thumbnails": item['snippet']['thumbnails']['default']['url'],
                                "video_caption_status": item['contentDetails']['caption']}      
                                vid_data.append(video_info)

                return vid_data


# Get Comment Details

def get_comment_details(v_comment):
        comment_data=[]
        try:
                for v_id in v_comment:
                        request= youtube.commentThreads().list(part="snippet",maxResults=100,videoId=v_id)
                        c_response = request.execute()
                        for comment in c_response['items']:
                                comment_information = {"Video_Id":comment['snippet']['topLevelComment']['snippet']['videoId'],
                                "Comment_Id": comment['snippet']['topLevelComment']['id'],
                                "Comment_Text": comment['snippet']['topLevelComment']['snippet']['textDisplay'],
                                "Comment_Author": comment['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                "Comment_PublishedAt": comment['snippet']['topLevelComment']['snippet']['publishedAt']}
                                comment_data.append(comment_information)
        except:
                pass

        return comment_data

#Streamlit UI

with st.sidebar:
        selected = option_menu(None,["HOME","FETCH DATA","VIEW"], 
                                icons=["house-door-fill","tools","card-text"],
                                default_index=0,
                                orientation="vertical",
                                styles={"nav-link": {"font-size": "30px", "text-align": "centre", "margin": "0px", 
                                        "--hover-color": "#C80101"},
                                        "icon": {"font-size": "30px"},
                                        "container" : {"max-width": "6000px"},
                                        "nav-link-selected": {"background-color": "#C80101"}})


if selected == 'HOME':
        st.title(':red[YOUTUBE DATA HARVESTING]')
        st.image('YouTube-1-1000x600.jpg')

        st.title(':red[OVERVIEW]')
        st.write("Youtube Data harvesting is to collect the data from the Youtube API and store it in a SQL database. It enables users to search for channel details and join tables to view data in the Streamlit app.")

        st.title(':red[TECHNOLOGIES]')
        st.write("The project utilizes various technologies including YouTube API for data retrieval, Python Scripting to fetch the particular data through documents, Streamlit for creating the user interface, Pandas for data manipulation, MySQL for database management, and API integration for connecting to external services.")

# Fetch Data from Database and calling the function

def main():

        if selected=='FETCH DATA':

                channel_id = st.text_input("Enter your channel id here:")

                if st.button("Click Me"):

                        if not channel_id:

                                st.warning("Enter valid channel id here")
                        else:

                                channels = channel_details(channel_id)

                                channel_df=pd.DataFrame(channels,index=[0])

                                channel_insert=[tuple(row)for row in channel_df.values]

                                channel_sql="insert into youtube_db.channel_table(channel_Id,channel_Name,channel_Type,channel_playlistId,channel_Description,channel_Status,channel_ViewCount,channel_Subcount,channel_VideoCount)values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                                mycursor.executemany(channel_sql,channel_insert)

                                mydb.commit()

                                st.write(channel_df)

                                # # Fetch video IDs
                                playlists = get_videos_id(channel_id)

                                # Fetch video details
                                video_details = get_video_details(playlists)

                                video_df = pd.DataFrame(video_details)

                                videos_insert = [tuple(row) for row in video_df.values]

                                video_sql ='INSERT INTO youtube_db.video_table(`Video_Id`,`channel_Id`,`video_name`,`video_description`,`video_published_date`,`video_viewcount`,`video_likecount`,`video_favoritecount`, `video_commentcount`,`duration`,`video_thumbnails`, `video_caption_status`)VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                                mycursor.executemany(video_sql, videos_insert)

                                mydb.commit()
                                
                                # Fetch Comments details
                                comments=get_comment_details(playlists)

                                commments_df=pd.DataFrame(comments)

                                comments_insert = [tuple(row) for row in commments_df.values]

                                comment_sql ="INSERT INTO youtube_db.comment_table(`Videos_id`, `Comment_Id`, `Comment_Text`, `Comment_Author`, `Comment_PublishedAt`)VALUES(%s, %s, %s, %s, %s)"

                                mycursor.executemany(comment_sql, comments_insert)

                                mydb.commit()

                                with st.spinner('Wait for it...'):
                                        time.sleep(5)
                        
                                st.success('Data was migrated and fetched successfully', icon="✅")

if __name__ == "__main__":
        main()

if selected=='VIEW':

        st.write("## :WHITE[QUESTIONS FOR STREAMLIT]")

        mycursor.execute("use youtube_db")

        Question = st.selectbox('Choose any one of the Questions',('---Select any Question----',
        '1.What are the names of all the videos and their corresponding channels?',
        '2.Which channels have the most number of videos, and how many videos do they have?',
        '3.What are the top 10 most viewed videos and their respective channels?',
        '4.How many comments were made on each video, and what are their corresponding video names?',
        '5.Which videos have the highest number of likes, and what are their corresponding channel names?',
        '6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
        '7.What is the total number of views for each channel, and what are their corresponding channel names?',
        '8.What are the names of all the channels that have published videos in the year 2022?',
        '9.What is the average duration of all videos in each channel, and what are their corresponding channel names?',
        '10.Which videos have the highest number of comments, and what are their corresponding channel names?'))
        
        if Question=='1.What are the names of all the videos and their corresponding channels?':
                mycursor.execute("""SELECT channel_Name as ChannelName, video_name as VideoName FROM channel_table JOIN video_table ON channel_table.channel_Id=video_table.channel_Id;""")
                q1=mycursor.fetchall()
                df=pd.DataFrame(q1,columns=["VideoName","ChannelName"])
                st.write(df)

        elif Question=='2.Which channels have the most number of videos, and how many videos do they have?':
                mycursor.execute("""SELECT channel_Name as ChannelName,channel_VideoCount as VideoCount FROM channel_table ORDER BY VideoCount DESC""")
                q2=mycursor.fetchall()
                df2=pd.DataFrame(q2,columns=["VideoCount","ChannelName"])
                st.write(df2)

        elif Question=='3.What are the top 10 most viewed videos and their respective channels?':
                mycursor.execute("""SELECT channel.channel_Name AS ChannelName,MAX(video.video_viewcount) AS VideoViewCount FROM video_table AS video JOIN channel_table AS channel ON video.Channel_Id = channel.channel_Id GROUP BY channel.channel_Name ORDER BY MAX(video.video_viewcount) DESC LIMIT 10;""")
                q3=mycursor.fetchall() 
                df3=pd.DataFrame(q3,columns=["VideoViewCount","ChannelName"])
                st.write(df3)

        elif Question=='4.How many comments were made on each video, and what are their corresponding video names?':
                mycursor.execute("""SELECT video_commentcount AS CommentCount,video_name as VideoName FROM video_table ORDER BY CommentCount desc""")
                q4=mycursor.fetchall()
                df4=pd.DataFrame(q4,columns=["CommentCount","VideoName"])
                st.write(df4)

        elif Question=='5.Which videos have the highest number of likes, and what are their corresponding channel names?':
                mycursor.execute("""SELECT channel_Name AS ChannelName, MAX(video_likecount) AS VideoLikeCount 
                FROM video_table INNER JOIN channel_table ON channel_table.channel_Id = video_table.channel_Id GROUP BY channel_table.channel_Name ORDER BY VideoLikeCount DESC;""")
                q5=mycursor.fetchall()
                df5=pd.DataFrame(q5,columns=["VideoLikeCount","ChannelName"])
                st.write(df5)

        elif Question=='6.What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
                mycursor.execute("""SELECT video_name as VideoNames, video_likecount AS TotalLikes FROM video_table ORDER BY TotalLikes DESC;""")
                q6=mycursor.fetchall()
                df6=pd.DataFrame(q6,columns=["VideoNames","TotalLikes"])
                st.write(df6)

        elif Question=='7.What is the total number of views for each channel, and what are their corresponding channel names?':
                mycursor.execute("""SELECT channel_Name as ChannelNames, channel_ViewCount AS Total_Views FROM channel_table ORDER BY Total_Views DESC;""")
                q7=mycursor.fetchall()
                df7=pd.DataFrame(q7,columns=["ChannelName","Total_Views"])
                st.write(df7)  

        elif Question=='8.What are the names of all the channels that have published videos in the year 2022?':
                mycursor.execute("""SELECT channel_table.channel_Name AS ChannelName,video_table.video_published_date AS VideoPublishDate 
                FROM video_table JOIN channel_table ON channel_table.channel_Id = video_table.channel_Id WHERE YEAR(video_table.video_published_date) = 2022""")
                q8=mycursor.fetchall()
                df8=pd.DataFrame(q8,columns=["ChannelName","VideoPublishDate"])
                st.write(df8)

        elif Question=='9.What is the average duration of all videos in each channel, and what are their corresponding channel names?':
                mycursor.execute("""SELECT channel_Name AS ChannelName, AVG(video_table.duration) AS VideoDurationSeconds FROM video_table JOIN channel_table ON channel_table.channel_Id = video_table.channel_Id GROUP BY channel_Name""")
                q9=mycursor.fetchall()
                df9=pd.DataFrame(q9,columns=["ChannelName","VideoDurationSeconds"])
                st.write(df9)

        elif Question=='10.Which videos have the highest number of comments, and what are their corresponding channel names?':
                mycursor.execute("SELECT channel_table.channel_Name AS ChannelName, MAX(video_table.video_commentcount)AS VideoCommentCount FROM channel_table JOIN video_table ON channel_table.channel_Id = video_table.channel_Id GROUP BY channel_Name ORDER BY VideoCommentCount DESC")
                q10=mycursor.fetchall()  
                df10=pd.DataFrame(q10,columns=["ChannelName","VideoCommentCount"])
                st.write(df10)