





import streamlit as st
import pandas as pd
import mysql.connector



def myfun(channel_id):

    from googleapiclient.discovery import build


    api_key = 'AIzaSyA8n7PamfdehLVjYuoRCzGw0EzwVvaqZLE'
    #api_key='AIzaSyDS-OUvWtJ11LGWzvm4Oi27AM5mER47K9A'
    #api_key='AIzaSyBhd3i9HXLsoyMn1tqsfoaNlA39NWUBFuk'
    #api_key='AIzaSyCrlJj20i90l6aUoc89EkRg4DVCW0VIVfM'
    youtube = build('youtube', 'v3', developerKey=api_key)





    response = youtube.channels().list(
        id=channel_id,
        part='snippet,statistics,contentDetails'
    )

    channel_data = response.execute()



    def get_channel_videos(channel_id):
        res= youtube.channels().list(id=channel_id,part='contentDetails').execute()
        playlist_id=res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        videos =[]
        next_page_token=None
        while 1:
            res=youtube.playlistItems().list(playlistId =playlist_id,part='snippet',maxResults=50,pageToken=next_page_token).execute()
            videos += res['items']
            next_page_token = res.get('nextPageToken')

            if next_page_token is None:
                break
        return videos

    videos=get_channel_videos(channel_id)
    all_videos_id=[videos[i]['snippet']['resourceId']['videoId'] for i in range(len(videos))]

    videos_details=[]
    for i in range(len(all_videos_id)):
        result=youtube.videos().list(part='snippet,contentDetails,statistics,recordingDetails',id=all_videos_id[i]).execute()
        videos_details.append(result)

    def get_date_time(isodate):
        import datetime, pytz
        d = datetime.datetime.fromisoformat(isodate[:-1]).replace(
            tzinfo=pytz.utc)  # we need to strip 'Z' before parsing
        date_time = d.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %I:%M %p')
        return date_time

    def comments_(video_id):
        res=youtube.commentThreads().list(part='snippet,replies',videoId=video_id).execute()
        comm=[]
        next_page_token=None
        while 1:
            res=youtube.commentThreads().list(part='snippet,replies',videoId=video_id,pageToken=next_page_token).execute()
            comm += res['items']
            next_page_token = res.get('nextPageToken')
            if next_page_token is None:
                break
        return comm

    l = []
    comments_count = []
    a = None
    for i in range(len(all_videos_id)):

        try:
            a = videos_details[i]['items'][0]['statistics']['commentCount']
            a = int(a)
            if a == 0:
                l.append('No comments')
                comments_count.append(0)
                # l.append(comments_on_video(all_videos_id[i]))

            else:

                l.append(comments_(all_videos_id[i]))
                comments_count.append(int(videos_details[i]['items'][0]['statistics']['commentCount']))






        except KeyError:
            l.append('errors')
            comments_count.append(0)

    import datetime, pytz
    date_time = []
    date_time_asian = []
    for i in range(len(all_videos_id)):
        isodate = videos_details[i]['items'][0]['snippet']['publishedAt']
        d = datetime.datetime.fromisoformat(isodate[:-1]).replace(
            tzinfo=pytz.utc)  # we need to strip 'Z' before parsing
        date_time_asian.append(d.astimezone(pytz.timezone('Asia/Kolkata')).strftime('%d-%m-%Y %I:%M %p'))
        date_time.append(d.strftime('%d-%m-%Y %I:%M %p'))

    import pandas as pd
    video_duration = []
    for i in range(len(all_videos_id)):
        iso_duration = videos_details[i]['items'][0]['contentDetails']['duration']
        dt = pd.Timedelta(iso_duration)
        video_duration.append(str(dt))

    def all_comments_details_on_video():

        comments_id = []
        comments_text = []
        comments_author = []
        comments_published_time = []
        comment_details = {'list_of_comments_id': comments_id, 'list_of_comments_text': comments_text,
                           'list_of_comments_author': comments_author,
                           'list_of_comments_published_time': comments_published_time}
        total_reply = 0

        result_per_page = len(a)
        for i in range(result_per_page):
            comments_id.append(a[i]['id'])
            comments_text.append(a[i]['snippet']['topLevelComment']['snippet']['textDisplay'])
            comments_author.append(a[i]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            comments_published_time.append(get_date_time(a[i]['snippet']['topLevelComment']['snippet']['publishedAt']))
            total_reply = a[i]['snippet']['totalReplyCount']

            if total_reply > 0:
                for j in range(len(a[i]['replies']['comments'])):
                    comments_id.append(a[i]['replies']['comments'][j]['id'])
                    comments_text.append(a[i]['replies']['comments'][j]['snippet']['textDisplay'])
                    comments_author.append(a[i]['replies']['comments'][j]['snippet']['authorDisplayName'])
                    comments_published_time.append(
                        get_date_time(a[i]['replies']['comments'][j]['snippet']['publishedAt']))

            else:
                pass
        # return comments_id
        # return comments_text
        # return comments_author
        # return comments_published_time

        return comment_details




    com=[]
    for i in range(len(all_videos_id)):
        if l[i]== 'No comments':
            com.append('No comments')
        elif l[i] == 'errors':
            com.append('errors')
        else:
            a=l[i]
            com.append(all_comments_details_on_video())



    def get_comments_info(i):

        comments_infos=[]
        comments_id=[]
        for j in range(len(com[i]['list_of_comments_id'])):


            comment_info = {
                        "Comment_Id":com[i]['list_of_comments_id'][j] ,
                        "Comment_Text": com[i]['list_of_comments_text'][j],
                        "Comment_Author":com[i]['list_of_comments_author'][j],
                        "Comment_PublishedAt": com[i]['list_of_comments_published_time'][j]
                    }
            comments_id.append(com[i]['list_of_comments_id'][j])
            comments_infos.append(comment_info)



        dict_comments_info = {}
        for x, y in zip(comments_id,comments_infos):
            dict_comments_info[x] = y
        return dict_comments_info

    all_comments_list=[]
    for i in range(len(all_videos_id)):
        if l[i]== 'No comments':
            all_comments_list.append('No comments')
        elif l[i] == 'errors':
            all_comments_list.append('errors')
        else:
            a=l[i]
            all_comments_list.append(get_comments_info(i))


    data={
        'Channel_information': {
            "Channel_Name": channel_data['items'][0]['snippet']['title'],
            "Channel_Id": channel_data['items'][0]['id'],
            "Subscription_Count": channel_data['items'][0]['statistics']['subscriberCount'],
            "Channel_Views": channel_data['items'][0]['statistics']['viewCount'],
            "Channel_Description": channel_data['items'][0]['snippet']['description'],
            "Playlist_Id": "PL1234567890"}
    }

    video_detail_ = []
    for i in range(len(all_videos_id)):
        # names=all_videos_id[i]

        video_info = {"Video_Id": videos_details[i]['items'][0]['id'],
                      "Video_Name": videos_details[i]['items'][0]['snippet']['title'],
                      "Video_Description": videos_details[i]['items'][0]['snippet']['description'],
                      # "Tags":videos_details[i]['items'][0]['snippet']['tags'],

                      "PublishedAt": date_time_asian[i],
                      "View_Count": videos_details[i]['items'][0]['statistics']['viewCount'],
                      "Like_Count": videos_details[i]['items'][0]['statistics']['likeCount'],
                      # "Dislike_Count": videos_details[0]['items'][0]['statistics']['dislikeCount'],
                      "Favorite_Count": videos_details[i]['items'][0]['statistics']['favoriteCount'],
                      "Comment_Count": comments_count[i],
                      "Duration": video_duration[i],
                      "Thumbnail": videos_details[i]['items'][0]['snippet']['thumbnails']['default']['url'],
                      "Caption_Status": videos_details[i]['items'][0]['contentDetails']['caption'],
                      "Comments": all_comments_list[i]

                      }
        video_detail_.append(video_info)

    dict_videos_info = {}
    for x, y in zip(all_videos_id,video_detail_):
        dict_videos_info[x] = y



    final_data={**data,**dict_videos_info}
    return final_data


#mydata=myfun(channel_id)

st.title('Youtube Channel Data Anaylsis')


def push_mongo_sql_1(all_data):
    from pymongo import MongoClient

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["test_data"]
    collection = db['data']
    x = collection.delete_many({})

    collection.insert_one(all_data)
    # st.write('mongo channel success')

    # sql
    data_list = list(all_data)
    data = all_data

    # for i in range(1, len(data_list)):
    #    st.write(data_list[i])
    # st.write(data_list)
    # st.write(data)
    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Neha1011",
        database="mydatabase"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM Channel_3"
    mycursor.execute(sql)

    sql = "INSERT INTO Channel_3 (channel_id,channel_name,channel_type,channel_views,channel_decription,channel_status) VALUES (%s, %s,%s, %s,%s, %s)"
    val = (data['Channel_information']['Channel_Id'], data['Channel_information']['Channel_Name'], 'Education',
           data['Channel_information']['Channel_Views'], data['Channel_information']['Channel_Description'],
           'active')
    mycursor.execute(sql, val)

    mydb.commit()
    # st.write('sql channel success')

    sql = "DELETE FROM Channel_3_Videos"
    mycursor.execute(sql)

    for i in range(1, len(data_list) - 1):
        sql = "INSERT INTO Channel_3_Videos(video_id,playlist_id,video_name ,video_description ,published_date ,view_count,like_count,dislike_count,favorite_count,comment_count,duration,thumbnail,caption_status) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
        val = (data[data_list[i]]['Video_Id'], 'none', data[data_list[i]]['Video_Name'],
               data[data_list[i]]['Video_Description'], data[data_list[i]]['PublishedAt'],
               data[data_list[i]]['View_Count'], data[data_list[i]]['Like_Count'], 0,
               data[data_list[i]]['Favorite_Count'], data[data_list[i]]['Comment_Count'],
               data[data_list[i]]['Duration'], data[data_list[i]]['Thumbnail'],
               data[data_list[i]]['Caption_Status'])
        mycursor.execute(sql, val)
        mydb.commit()

    # st.write('sql Video success')

    sql = "DELETE FROM Channel_3_comments"
    mycursor.execute(sql)

    for i in range(1, len(data_list) - 1):
        if data[data_list[i]]['Comment_Count'] != 0:
            y = list(data[data_list[i]]['Comments'].values())

            for j in range(len(y)):
                sql = "INSERT INTO Channel_3_comments (comment_id,video_id,comment_text,comment_author,comment_published_date) VALUES (%s,%s,%s,%s,%s)"
                val = (y[j]['Comment_Id'], data_list[i], y[j]['Comment_Text'],
                       y[j]['Comment_Author'], y[j]['Comment_PublishedAt'])
                mycursor.execute(sql, val)
                mydb.commit()


        else:
            pass


if 'text1' not in st.session_state:
    st.session_state['text1'] = None

text_inputs1 = st.text_input('Enter 1st channel id')
if text_inputs1:
    st.session_state.text1 = text_inputs1

# st.session_state['text']
fetch1 = st.button('fetch and store data of 1st channel in MongoDB and SQL database ')

if fetch1:
    input_channel1 = st.session_state['text1']

    all_data = myfun(input_channel1)
    push_mongo_sql_1(all_data)

    # st.button('Push to mongo and sql database server ', on_click=push_mongo_sql(all_data))


def push_mongo_sql_2(all_data):
    from pymongo import MongoClient

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017")
    db = client["test_data"]
    collection = db['data']
    x = collection.delete_many({})

    collection.insert_one(all_data)
    # st.write('mongo channel success')

    # sql
    data_list = list(all_data)
    data = all_data

    # for i in range(1, len(data_list)):
    #    st.write(data_list[i])
    # st.write(data_list)
    # st.write(data)
    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Neha1011",
        database="mydatabase"
    )
    mycursor = mydb.cursor()
    sql = "DELETE FROM Channel_2"
    mycursor.execute(sql)

    sql = "INSERT INTO Channel_2 (channel_id,channel_name,channel_type,channel_views,channel_decription,channel_status) VALUES (%s, %s,%s, %s,%s, %s)"
    val = (data['Channel_information']['Channel_Id'], data['Channel_information']['Channel_Name'], 'Education',
           data['Channel_information']['Channel_Views'], data['Channel_information']['Channel_Description'],
           'active')
    mycursor.execute(sql, val)

    mydb.commit()
    # st.write('sql channel success')

    sql = "DELETE FROM Channel_2_Videos"
    mycursor.execute(sql)

    for i in range(1, len(data_list) - 1):
        sql = "INSERT INTO Channel_2_Videos(video_id,playlist_id,video_name ,video_description ,published_date ,view_count,like_count,dislike_count,favorite_count,comment_count,duration,thumbnail,caption_status) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
        val = (data[data_list[i]]['Video_Id'], 'none', data[data_list[i]]['Video_Name'],
               data[data_list[i]]['Video_Description'], data[data_list[i]]['PublishedAt'],
               data[data_list[i]]['View_Count'], data[data_list[i]]['Like_Count'], 0,
               data[data_list[i]]['Favorite_Count'], data[data_list[i]]['Comment_Count'],
               data[data_list[i]]['Duration'], data[data_list[i]]['Thumbnail'],
               data[data_list[i]]['Caption_Status'])
        mycursor.execute(sql, val)
        mydb.commit()

    # st.write('sql Video success')

    sql = "DELETE FROM  Channel_2_comments"
    mycursor.execute(sql)

    for i in range(1, len(data_list) - 1):
        if data[data_list[i]]['Comment_Count'] != 0:
            y = list(data[data_list[i]]['Comments'].values())

            for j in range(len(y)):
                sql = "INSERT INTO  Channel_2_comments(comment_id,video_id,comment_text,comment_author,comment_published_date) VALUES (%s,%s,%s,%s,%s)"
                val = (y[j]['Comment_Id'], data_list[i], y[j]['Comment_Text'],
                       y[j]['Comment_Author'], y[j]['Comment_PublishedAt'])
                mycursor.execute(sql, val)
                mydb.commit()


        else:
            pass


if 'text2' not in st.session_state:
    st.session_state['text2'] = None

text_inputs2 = st.text_input('Enter 2nd channel id')
if text_inputs2:
    st.session_state.text2 = text_inputs2

# st.session_state['text']
fetch2 = st.button('fetch and store data  of 2nd channel in MongoDB and SQL database')

if fetch2:
    input_channel2 = st.session_state['text2']

    all_data = myfun(input_channel2)
    push_mongo_sql_2(all_data)

    # st.button('Push to mongo and sql database server ', on_click=push_mongo_sql(all_data))

    # st.button('Push to mongo and sql database server ', on_click=push_mongo_sql(all_data))

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="Neha1011",
    database="mydatabase"
)
mycursor1 = mydb.cursor(buffered=True)
mycursor2 = mydb.cursor(buffered=True)

mycursor1.execute("SELECT channel_name FROM Channel_3")
mycursor2.execute("SELECT channel_name FROM Channel_2")

channel_name_1 = mycursor1.fetchall()
channel_name_2 = mycursor2.fetchall()

channel_name_1 = str((channel_name_1[-1][-1]))
channel_name_2 = str((channel_name_2[-1][-1]))

st.write('First channel name:',channel_name_1)
st.write('Second channel name:',channel_name_2)

with st.expander("Q.1 Names of all the videos for each channels"):
    mycursor1.execute("SELECT video_name FROM Channel_3_Videos")
    mycursor2.execute("SELECT video_name FROM Channel_2_Videos")

    all_videos_name_1 = mycursor1.fetchall()
    all_videos_name_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(all_videos_name_1)
    df2 = pd.DataFrame(all_videos_name_2)

    df1.columns = [channel_name_1]
    df2.columns = [channel_name_2]

    st.table(df1)
    st.table(df2)

with st.expander('Q.2 How many videos for each channel.'):
    mycursor1.execute("SELECT COUNT(*) FROM Channel_3_Videos")
    mycursor2.execute("SELECT COUNT(*) FROM Channel_2_Videos")

    videos_count_1 = mycursor1.fetchall()
    videos_count_2 = mycursor2.fetchall()

    a = int((videos_count_1[-1][-1]))
    b = int((videos_count_2[-1][-1]))

    chart_data = {'Channel names': [channel_name_1, channel_name_2], 'Number of videos': [a, b]}

    data = pd.DataFrame(chart_data)
    data = data.set_index('Channel names')

    st.bar_chart(data)
    st.table(chart_data)

with st.expander("Q.3 Top 10 most viewed videos on each channel"):
    mycursor1.execute("SELECT video_name,view_count FROM Channel_3_Videos ORDER BY view_count DESC LIMIT 10")
    mycursor2.execute("SELECT video_name,view_count FROM Channel_2_Videos ORDER BY view_count DESC LIMIT 10")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1.columns = ['Video Name', 'No. of views']
    df2.columns = ['Video Name', 'No. of views']

    df1 = df1.style.set_caption(channel_name_1)
    df2 = df2.style.set_caption(channel_name_2)

    st.table(df1)
    st.table(df2)

with st.expander("Q.4 How many comments were made on each video for every channel"):
    mycursor1.execute("SELECT video_name,comment_count FROM Channel_3_Videos")
    mycursor2.execute("SELECT video_name,comment_count FROM Channel_2_Videos")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1.columns = ['Video Name', 'No. of comments']
    df2.columns = ['Video Name', 'No. of comments']

    df1 = df1.style.set_caption(channel_name_1)
    df2 = df2.style.set_caption(channel_name_2)

    st.table(df1)
    st.table(df2)

with st.expander("Q.5 Videos which have the highest number of likes for each channel"):
    mycursor1.execute(
        "SELECT video_name,like_count FROM Channel_3_Videos WHERE  like_count= (SELECT MAX(like_count) FROM Channel_3_Videos)")
    mycursor2.execute(
        "SELECT video_name,like_count FROM Channel_2_Videos WHERE  like_count= (SELECT MAX(like_count) FROM Channel_2_Videos)")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1['Channel name'] = channel_name_1
    df2['Channel name'] = channel_name_2

    df = [df1, df2]
    df_res = pd.concat(df)
    df_res.columns = ['Video Name', 'No. of likes', 'Channel_name']

    st.table(df_res)

with st.expander("Q.6  Total number of likes and dislikes were made on each video."):
    mycursor1.execute("SELECT video_name,like_count,dislike_count FROM Channel_3_Videos")
    mycursor2.execute("SELECT video_name,like_count,dislike_count FROM Channel_2_Videos")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1.columns = ['Video Name', 'like count', 'dislike count']
    df2.columns = ['Video Name', 'like count', 'dislike count']

    df1 = df1.style.set_caption(channel_name_1)
    df2 = df2.style.set_caption(channel_name_2)

    st.table(df1)
    st.table(df2)

with st.expander("Q.7  Total number of views for each channel"):
    mycursor1.execute("SELECT channel_views FROM Channel_3")
    mycursor2.execute("SELECT channel_views FROM Channel_2")

    channel_views_1 = mycursor1.fetchall()
    channel_views_2 = mycursor2.fetchall()

    a = int((channel_views_1[-1][-1]))
    b = int((channel_views_2[-1][-1]))

    chart_data = {'Channel names': [channel_name_1, channel_name_2], 'channel views': [a, b]}

    st.table(chart_data)

with st.expander("Q.8  Videos  published in the year 2022 for channel"):
    mycursor1.execute("SELECT video_name,published_date FROM Channel_3_Videos")
    mycursor2.execute("SELECT video_name,published_date  FROM Channel_2_Videos")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1.columns = ['Video Name', 'publish date']
    df2.columns = ['Video Name', 'publish date']

    df1['year'] = df1['publish date'].str[6:10]
    df2['year'] = df2['publish date'].str[6:10]

    df1 = df1[df1['year'] == '2022']
    df2 = df2[df2['year'] == '2022']

    df1 = df1.style.set_caption(channel_name_1)
    df2 = df2.style.set_caption(channel_name_2)

    st.table(df1)
    st.table(df2)

with st.expander("Q.9  Average duration of videos for each channel"):
    mycursor1.execute("SELECT duration FROM Channel_3_Videos")
    mycursor2.execute("SELECT duration FROM Channel_2_Videos")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1.columns = ['duration']
    df2.columns = ['duration']

    df1['time'] = pd.to_numeric(df1['duration'].str[0:-13]) * 24 * 3600 + pd.to_numeric(
        df1['duration'].str[-8:-6]) * 3600 + pd.to_numeric(df1['duration'].str[-5:-3]) * 60 + pd.to_numeric(
        df1['duration'].str[-2:]) * 1
    df2['time'] = pd.to_numeric(df2['duration'].str[0:-13]) * 24 * 3600 + pd.to_numeric(
        df2['duration'].str[-8:-6]) * 3600 + pd.to_numeric(df2['duration'].str[-5:-3]) * 60 + pd.to_numeric(
        df2['duration'].str[-2:]) * 1

    a = df1['time'].mean(axis=0)
    b = df2['time'].mean(axis=0)

    a = a / 60
    b = b / 60

    d = {'Channel names': [channel_name_1, channel_name_2], 'avg duration(minutes)': [a, b]}
    df = pd.DataFrame(d)
    st.table(d)

with st.expander("Q.10 Videos which have the highest number of comments for each channel names"):
    mycursor1.execute(
        "SELECT video_name,comment_count FROM Channel_3_Videos WHERE  comment_count= (SELECT MAX(comment_count) FROM Channel_3_Videos)")
    mycursor2.execute(
        "SELECT video_name,comment_count FROM Channel_2_Videos WHERE  comment_count= (SELECT MAX(comment_count) FROM Channel_2_Videos)")

    res_1 = mycursor1.fetchall()
    res_2 = mycursor2.fetchall()

    df1 = pd.DataFrame(res_1)
    df2 = pd.DataFrame(res_2)

    df1['Channel name'] = channel_name_1
    df2['Channel name'] = channel_name_2

    df = [df1, df2]
    df_res = pd.concat(df)
    df_res.columns = ['Video Name', 'No. of comments', 'Channel_name']

    st.table(df_res)
