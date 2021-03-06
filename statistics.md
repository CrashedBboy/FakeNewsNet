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
* [x] Tree depth
* [x] #user
* [x] #post (our prediction target)
* [x] maximum node out-degree

## 3. Cascade Network - Temporal

For propagation network of **a dissemination cascade**
* [x] average time difference between adjacent node
* [x] time difference between source tweet and its first response
* [x] lifespan
* [x] post time distribution

## 4. Social Network

For social network constructed by users in each **dissemination cascade**:

* [x] out-degree centrality
* [x] in-degree centrality
* [x] closeness centrality
* [x] betweenness centrality
* [x] #node ( = #user)
* [x] #edge

## 5. User Profile

Available attributes:
* location
* url
* protected
* followers_count
* friends_count
* listed_cout
* created_at
* favourites_count
* verified
* statuses_count
* default_profile
* default_profile_image

## 6. Text Content
* [ ] sentiment ratio (#positive / #negative)
* [ ] average sentiment score
* [x] word frequency: word cloud , TF-IDF
* [x] #word per article / cascade (article + post)
* [x] #hashtag, links, @mentioned, media per cascade