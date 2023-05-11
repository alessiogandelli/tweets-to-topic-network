graph [
  directed 1
  node [
    id 0
    label "anzio"
    bipartite 0
  ]
  node [
    id 1
    label "bonzo"
    bipartite 0
  ]
  node [
    id 2
    label "crizio"
    bipartite 0
  ]
  node [
    id 3
    label "donzo"
    bipartite 0
  ]
  node [
    id 4
    label "1"
    bipartite 1
    text "sono il tweet numero1 "
    topics NAN
    author "anzio"
  ]
  node [
    id 5
    label "2"
    bipartite 1
    text "sono il tweet numero 2"
    topics "1"
    author "bonzo"
  ]
  node [
    id 6
    label "3"
    bipartite 1
    text "sono il tweet numero 3"
    topics "1"
    author "crizio"
  ]
  node [
    id 7
    label "4"
    bipartite 1
    text "sono il tweet numero 4"
    topics "3"
    author "donzo"
  ]
  edge [
    source 0
    target 4
    weight 10
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 1
    target 5
    weight 10
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 2
    target 6
    weight 10
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 3
    target 7
    weight 10
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 5
    target 4
    weight 1
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 6
    target 4
    weight 1
    date "2016-12-31T23:53:31.000Z"
  ]
  edge [
    source 6
    target 3
  ]
  edge [
    source 7
    target 6
    weight 1
    date "2016-12-31T23:53:31.000Z"
  ]
]
