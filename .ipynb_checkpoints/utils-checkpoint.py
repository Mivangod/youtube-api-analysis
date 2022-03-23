###Define functions
def get_channel_stats(youtube, channel_ids):
    """
    Function to get channel statistics
    
    Parameters:
    --------
    youtube: build object of YouTube API
    channel_ids: Channel IDs that are given by each channel
    
    Returns:
    --------
    dataframe with all of the channel statistics
    """
    all_data=[]
    
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=','.join(channel_ids)
    )
    response = request.execute()

    #loop through items
    for i in range(len(response['items'])):
        data = dict(channelName = response['items'][i]['snippet']['title'],
                subscribers= response['items'][i]['statistics']['subscriberCount'],
                views = response['items'][i]['statistics']['viewCount'],
                totalVideos = response['items'][i]['statistics']['videoCount'],
                playlistId = response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                   )
        
    
        all_data.append(data)
    
    return(pd.DataFrame(all_data))


def get_video_ids(youtube, playlist_id):
    """
    Function to get the video ids
    
    Parameters:
    ----------
    youtube: build object of YouTube API
    playlist_id: the IDs that each of the videos produce
    
    Returns:
    -------
    dataframe of each specific video ID
    
    """
    video_ids = []
    
    request = youtube.playlistItems().list(
                part='snippet, contentDetails',
                playlistId = playlist_id,
                maxResults = 50
    )
    response = request.execute()
    
    
    
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()
    
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
        
    return video_ids


#Get Video Info
def get_video_details(youtube, video_ids):
    """
    Function to grab all video details
    
    Parameters:
    ----------
    youtube : build object of YouTube API
    video_ids : past function to get each specific video ID for specidications
    
    
    """
    
    all_video_info=[]
    
    for i in range(0, len(video_ids),50):
        request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=','.join(video_ids[i:i+50])
        )
        response = request.execute()
        
        for video in response['items']:
            stat_keep = {'snippet':['channelTitle','title','description','tags','publishedAt'],
                         'statistics':['viewCount','likeCount','favoriteCount','commentCount'],
                         'contentDetails':['duration','definition','captions']
                        }
            video_info = {}
            video_info['video_id'] = video['id']
            
            for k in stat_keep.keys():
                for v in stat_keep[k]:
                    try:
                        video_info[v]=video[k][v]
                    except:
                        video_info[v]=None
                        
            all_video_info.append(video_info)
            
    return pd.DataFrame(all_video_info)
                            
    
    
    #Get Comments
def get_comments_in_video(youtube, video_ids):
    """
    Function to grab all available comments
    
    Parameters:
    ----------
    youtube : build object of YouTube API
        video_ids : past function to get each specific video ID for specidications
    
    
    """
    
    all_comments=[]
    
    for video_id in video_ids:
        try:
            
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id
            )
            response = request.execute()

            comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items'][0:10]]
            comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

            all_comments.append(comments_in_video_info)

        except:
            #When comments are disabled
            print('could not get comment for video '+ video_id)
            
    return pd.DataFrame(all_comments)



