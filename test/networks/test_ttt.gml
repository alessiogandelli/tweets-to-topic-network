graph [
  directed 1
  node [
    id 0
    label "a"
    bipartite 0
  ]
  node [
    id 1
    label "b"
    bipartite 0
  ]
  node [
    id 2
    label "c"
    bipartite 0
  ]
  node [
    id 3
    label "d"
    bipartite 0
  ]
  node [
    id 4
    label "t1"
    bipartite 1
    text "tweet1"
    topics 1
    author "a"
    is_retweet "original"
  ]
  node [
    id 5
    label "t2"
    bipartite 1
    text "tweet2"
    topics 1
    author "b"
    is_retweet "retweet"
  ]
  node [
    id 6
    label "t3"
    bipartite 1
    text "tweet3"
    topics 1
    author "c"
    is_retweet "retweet"
  ]
  node [
    id 7
    label "t4"
    bipartite 1
    text "tweet4"
    topics 1
    author "c"
    is_retweet "original"
  ]
  node [
    id 8
    label "t5"
    bipartite 1
    text "tweet5"
    topics 2
    author "a"
    is_retweet "retweet"
  ]
  node [
    id 9
    label "t6"
    bipartite 1
    text "tweet6"
    topics 2
    author "d"
    is_retweet "retweet"
  ]
  node [
    id 10
    label "t7"
    bipartite 1
    text "tweet7"
    topics 2
    author "d"
    is_retweet "original"
  ]
  edge [
    source 0
    target 4
    weight 10
    date "2022-01-01"
  ]
  edge [
    source 0
    target 8
    weight 10
    date "2022-01-05"
  ]
  edge [
    source 1
    target 5
    weight 10
    date "2022-01-02"
  ]
  edge [
    source 2
    target 6
    weight 10
    date "2022-01-03"
  ]
  edge [
    source 2
    target 7
    weight 10
    date "2022-01-04"
  ]
  edge [
    source 3
    target 9
    weight 10
    date "2022-01-06"
  ]
  edge [
    source 3
    target 10
    weight 10
    date "2022-01-07"
  ]
  edge [
    source 4
    target 1
  ]
  edge [
    source 5
    target 4
    weight 1
    date "2022-01-01"
  ]
  edge [
    source 6
    target 5
    weight 1
    date "2022-01-02"
  ]
  edge [
    source 8
    target 10
    weight 1
    date "2022-01-07"
  ]
  edge [
    source 9
    target 10
    weight 1
    date "2022-01-07"
  ]
]
