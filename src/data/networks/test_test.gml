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
    label "f"
    bipartite 0
  ]
  node [
    id 3
    label "c"
    bipartite 0
  ]
  node [
    id 4
    label "d"
    bipartite 0
  ]
  node [
    id 5
    label "e"
    bipartite 0
  ]
  node [
    id 6
    label "tweet1"
    bipartite 1
    text "tweet1"
    topics 1
    author "a"
    is_retweet "original"
  ]
  node [
    id 7
    label "tweet2"
    bipartite 1
    text "tweet2"
    topics 1
    author "a"
    is_retweet "original"
  ]
  node [
    id 8
    label "tweet3"
    bipartite 1
    text "tweet3"
    topics 1
    author "b"
    is_retweet "retweet"
  ]
  node [
    id 9
    label "tweet4"
    bipartite 1
    text "tweet4"
    topics 1
    author "b"
    is_retweet "original"
  ]
  node [
    id 10
    label "tweet5"
    bipartite 1
    text "tweet5"
    topics 1
    author "f"
    is_retweet "retweet"
  ]
  node [
    id 11
    label "tweet6"
    bipartite 1
    text "tweet6"
    topics 1
    author "c"
    is_retweet "retweet"
  ]
  node [
    id 12
    label "tweet7"
    bipartite 1
    text "tweet7"
    topics 1
    author "d"
    is_retweet "retweet"
  ]
  node [
    id 13
    label "tweet8"
    bipartite 1
    text "tweet8"
    topics 1
    author "e"
    is_retweet "retweet"
  ]
  node [
    id 14
    label "tweet9"
    bipartite 1
    text "tweet9"
    topics 1
    author "f"
    is_retweet "retweet"
  ]
  edge [
    source 0
    target 6
    weight 10
    date "2022-01-01"
  ]
  edge [
    source 0
    target 7
    weight 10
    date "2022-01-02"
  ]
  edge [
    source 1
    target 8
    weight 10
    date "2022-01-03"
  ]
  edge [
    source 1
    target 9
    weight 10
    date "2022-01-04"
  ]
  edge [
    source 2
    target 10
    weight 10
    date "2022-01-05"
  ]
  edge [
    source 2
    target 14
    weight 10
    date "2022-01-09"
  ]
  edge [
    source 3
    target 11
    weight 10
    date "2022-01-06"
  ]
  edge [
    source 4
    target 12
    weight 10
    date "2022-01-07"
  ]
  edge [
    source 5
    target 13
    weight 10
    date "2022-01-08"
  ]
  edge [
    source 8
    target 7
    weight 1
    date "2022-01-02"
  ]
  edge [
    source 10
    target 8
    weight 1
    date "2022-01-03"
  ]
  edge [
    source 11
    target 7
    weight 1
    date "2022-01-02"
  ]
  edge [
    source 12
    target 7
    weight 1
    date "2022-01-02"
  ]
  edge [
    source 13
    target 7
    weight 1
    date "2022-01-02"
  ]
  edge [
    source 14
    target 13
    weight 1
    date "2022-01-08"
  ]
]
