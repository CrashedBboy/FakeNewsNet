## 4 Aspects of Data

* News dissemination cascade
* Social network
* User profile
* Text content

## 1. Global Statistics

* [x] #fake news
* [x] #fake news having propagation network (having at least one post)
* [x] #users
    - [x] #source tweet authors
    - [x] #spreader
* [x] #source tweets ( = number of cascade)
    - [x] #Quotes
    - [x] #Replies
* [x] #Retweets

## 2. Cascade Network - Structural

For propagation nwtwork of **a news article** (consists of multiple cascades)
* [x] fraction of cascade having at least 2 nodes

For propagation network of **a dissemination cascade**
* [ ] Tree depth
* [ ] #user
* [ ] #post (our prediction target)
* [ ] maximum nide out-degree
* [ ] depth of node with max-degree

## 3. Cascade Network - Temporal

For propagation nwtwork of **a news article** (consists of multiple cascades)
* [ ] average time difference between adjacent nodes
* [ ] lifespan of news
* [ ] average time difference between source tweets
* [ ] lifespan of deepest cascade

For propagation network of **a dissemination cascade**
* [ ] average time difference between adjacent node
* [ ] time difference between source tweet and its first response
* [ ] lifespan

## 4. Social Network

For social network constructed by users in each **dissemination cascade**:

* [ ] out-degree centrality
* [ ] in-degree centrality
* [ ] closeness centrality
* [ ] betweenness centrality
* [ ] graph diameter
* [ ] #node ( = #user)
* [ ] #edge

## 5. User Profile

Available attributes:
* [ ] location
* [ ] url
* [ ] protected
* [ ] followers_count
* [ ] friends_count
* [ ] listed_cout
* [ ] created_at
* [ ] favourites_count
* [ ] verified
* [ ] statuses_count
* [ ] default_profile
* [ ] default_profile_image

## 6. Text Content
* [ ] sentiment ratio (#positive / #negative)
* [ ] average sentiment score
* [ ] word frequency: word cloud , TF-IDF
* [ ] #word per sentence / article / post
* [ ] #sentence per article / post
* [ ] #hashtag, links, @mentioned per post, cascade