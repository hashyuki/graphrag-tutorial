# GraphRAG

## ゼロから始める GraphRAG

> [!WARNING]  
> このレポジトリは README の手順を全て行ったあとの完成系です。  
> clone した場合は graphrag のインストールのみで手順 7.を実行できます。

1.  python の実行環境整備

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    <details>
    <summary>この段階のディレクトリ構造</summary>

    ```bash
    .
    └── .venv
    ```

    </details>

2.  graphrag のインストール

    ```bash
    pip install graphrag
    ```

3.  rag 対象のデータ作成

    ```bash
    mkdir -p ./ragtest/input
    vim ./ragtest/input/sample.txt
    ```

    <details>
    <summary><code>sample.txt</code>の中身</summary>

    ChatGPT で適当に作成

    ```sample.txt
    ある遠い国に、緑豊かな山々と透き通る湖に囲まれた小さな村がありました。この村の人々は、農業や漁業を生業とし、平和で幸せな生活を送っていました。しかし、この村には長い間隠された秘密がありました。それは、湖の底に眠る古代の竜がいつか目覚め、村を滅ぼすという予言でした。

    村の人々はこの予言を恐れ、代々伝えられてきたお守りを持ち歩き、竜を鎮めるための儀式を毎年行っていました。しかし、多くの人々はこの予言をただの伝説として捉え、日常生活を楽しんでいました。

    ある日、若い農夫のリオは湖の近くで珍しい青い石を見つけました。その石は不思議な輝きを放っており、リオはそれをお守りとして持ち帰りました。彼の妹であるリナは、その石が古代の竜に関連しているかもしれないと感じました。リナは村の長老であるエルドに相談しに行きました。

    エルドは石を見て驚きました。彼は古い文献を引っ張り出し、その石が「ドラゴンの涙」と呼ばれるものだと説明しました。この石は、古代の竜が深い悲しみを感じたときに流した涙が結晶化したものであり、竜の魂と繋がっていると言われていました。エルドは、石を村の外に持ち出し、封印するようにリオとリナに言いました。

    リオとリナはエルドの指示に従い、石を村から遠く離れた場所に持ち出しました。しかし、彼らが石を封印しようとしたその瞬間、湖が突然荒れ狂い、巨大な竜が水面から姿を現しました。村の人々は驚きと恐怖で逃げ惑いました。竜は怒りの咆哮を上げ、村を破壊しようとしました。

    リオとリナは竜を止めるために必死になりましたが、彼らの力ではどうにもなりませんでした。そのとき、リナは石を使って竜に話しかけることを思いつきました。彼女は石を握りしめ、竜の心に語りかけました。「私たちはあなたを傷つけるつもりはありません。ただ、この村を守りたいのです。」

    すると、竜は一瞬静かになり、リナの言葉に耳を傾けました。竜は彼女の純粋な心を感じ取り、自らの怒りを鎮めました。竜は彼女に、自分がこの湖に封印された理由を話し始めました。古代の時代、竜は人間たちによって利用され、酷い仕打ちを受けていました。最終的に竜は暴走し、破壊の神と化してしまいました。それを恐れた古代の賢者たちは竜を封印し、その存在を忘れ去ることにしました。

    リナは竜に対して深い同情を感じ、彼を解放するために何ができるかを尋ねました。竜は彼女に、彼の封印を解くためには、彼がかつて破壊した場所を修復し、その土地に新しい命を吹き込む必要があると説明しました。リナとリオは竜の言葉を信じ、村の人々に協力を求めました。

    村の人々は最初は躊躇していましたが、リオとリナの熱意と竜の真実を知ると、皆で協力して破壊された土地を再生させることを決意しました。村は総出で新しい畑を作り、木を植え、湖をきれいにしました。時間が経つにつれて、自然は再び豊かさを取り戻し、竜の封印は徐々に解かれていきました。

    竜は再び自由を得た後、村の人々に感謝の意を示しました。彼は彼らに、いつか困難な時が訪れたら再び助けに来ることを約束し、静かに湖の中に戻っていきました。リオとリナ、そして村の人々は、竜との出会いを通じて自然と調和して生きることの大切さを学びました。

    それ以来、村は「竜の祝福を受けた村」として知られるようになり、人々は竜を敬いながら平和に暮らしました。竜はその後も湖の底で静かに眠り続け、村の人々を見守り続けました。そして、リオとリナの子孫たちはその物語を次世代に伝え続け、竜との絆を大切にしていきました。

    こうして、遠い国の小さな村は、伝説と共に豊かな歴史を刻んでいったのです。
    ```

    </details>

    <details>
    <summary>この段階のディレクトリ構造</summary>

    ```bash
    .
    ├── .venv
    └── ragtest
        └── input
            └── sample.txt
    ```

    </details>

4.  workspace の初期化

    ```bash
    OPENAI_API_KEY="<your openai api key>"

    python -m graphrag.index --init --root ./ragtest
    ```

    > [!NOTE]  
    > この時`ragtest/.env`の`GRAPHRAG_API_KEY`に OPENAI_API_KEY が入っていることを確認する。  
    > 入っていない場合は手動で入れる。

    <details>
    <summary>この段階のディレクトリ構造</summary>

    ```
    .
    ├── .venv
    └── ragtest
        ├── input
        │   └── sample.txt
        ├── output
        │   └── 20240731-220508
        │       └── reports
        │           └── indexing-engine.log
        ├── prompts
        │   ├── claim_extraction.txt
        │   ├── community_report.txt
        │   ├── entity_extraction.txt
        │   └── summarize_descriptions.txt
        ├── .env
        └── settings.yaml
    ```

    </details>

5.  （OPTIONAL）`setting.yaml`の編集

    今回は以下のような変更を加えた

    ```diff
        type: openai_chat # or azure_openai_chat
    -   model: gpt-4-turbo-preview
    +   model: gpt-4o-mini
        model_supports_json: true # recommended if this is available for your model.
        :
        :
      chunks:
    -   size: 1200
    -   overlap: 100
    +   size: 512
    +   overlap: 128
        group_by_columns: [id] # by default, we don't allow chunks to cross documents
    ```

6.  index の作成

    ```bash
    python -m graphrag.index --root ./ragtest
    ```

    <details>
    <summary>出力</summary>

    ```
    🚀 Reading settings from ragtest/settings.yaml
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    🚀 create_base_text_units
                                    id  ... n_tokens
    0  ee71298ece5a63e8b7c090e56ebb7fc4  ...      512
    1  f9fcd5f66a1822340e74c982831397d0  ...      512
    2  bdb5dc10d04545e18822999dd984e569  ...      512
    3  4d07cb7b889dc3477821f70571af3a36  ...      501
    4  58e70d7ad09e03e070998b0a30ea382e  ...      117

    [5 rows x 5 columns]
    🚀 create_base_extracted_entities
                                            entity_graph
    0  <graphml xmlns="http://graphml.graphdrawing.or...
    🚀 create_summarized_entities
                                            entity_graph
    0  <graphml xmlns="http://graphml.graphdrawing.or...
    🚀 create_base_entity_graph
    level                                    clustered_graph
    0      0  <graphml xmlns="http://graphml.graphdrawing.or...
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    🚀 create_final_entities
                                    id  ...                              description_embedding
    0   b45241d70f0e43fca764df95b2b81f77  ...  [0.02316942811012268, 0.024793269112706184, -0...
    1   4119fd06010c494caa07f439b333f4c5  ...  [0.06715891510248184, 0.004567499738186598, -0...
    2   d3835bf3dda84ead99deadbeac5d0d7d  ...  [0.05989678204059601, -0.0033195731230080128, ...
    3   077d2820ae1845bcbb1803379a3d1eae  ...  [0.033260777592659, 0.03621453419327736, 0.026...
    4   3671ea0dd4e84c1a9b02c5ab2c8f4bac  ...  [0.02856464311480522, 0.03173849359154701, 0.0...
    5   19a7f254a5d64566ab5cc15472df02de  ...  [0.04524395242333412, 0.0011291108094155788, -...
    6   e7ffaee9d31d4d3c96e04f911d0a8f9e  ...  [0.05900789424777031, 0.037175919860601425, 0....
    7   f7e11b0e297a44a896dc67928368f600  ...  [0.058140140026807785, 0.004840914160013199, -...
    8   1fd3fa8bb5a2408790042ab9573779ee  ...  [0.02418745495378971, 0.026932936161756516, -0...
    9   27f9fbe6ad8c4a8b9acee0d3596ed57c  ...  [0.0088186739012599, 0.007403782568871975, 0.0...
    10  e1fd0e904a53409aada44442f23a51cb  ...  [0.037841152399778366, 0.03634297102689743, 0....
    11  de988724cfdf45cebfba3b13c43ceede  ...  [0.02729884162545204, 0.022319013252854347, -0...
    12  96aad7cb4b7d40e9b7e13b94a67af206  ...  [0.04774624481797218, 0.011277662590146065, 0....
    13  c9632a35146940c2a86167c7726d35e9  ...  [0.03143661469221115, 0.03712940216064453, 0.0...
    14  9646481f66ce4fd2b08c2eddda42fc82  ...  [0.057556137442588806, 0.02506774663925171, 0....
    15  d91a266f766b4737a06b0fda588ba40b  ...  [0.026913965120911598, 0.021225426346063614, 0...
    16  bc0e3f075a4c4ebbb7c7b152b65a5625  ...  [0.036188289523124695, 0.01746024377644062, -0...
    17  254770028d7a4fa9877da4ba0ad5ad21  ...  [0.034683842211961746, -0.0016732353251427412,...
    18  4a67211867e5464ba45126315a122a8a  ...  [0.02455723285675049, 0.011785458773374557, 0....
    19  04dbbb2283b845baaeac0eaf0c34c9da  ...  [0.01961551234126091, 0.024331865832209587, 0....
    20  1943f245ee4243bdbfbd2fd619ae824a  ...  [0.04918732866644859, 0.0025027054361999035, -...
    21  273daeec8cad41e6b3e450447db58ee7  ...  [0.02605934627354145, 0.0056322128511965275, -...
    22  e69dc259edb944ea9ea41264b9fcfe59  ...  [0.0762547180056572, 0.022520506754517555, 0.0...
    23  e2f5735c7d714423a2c4f61ca2644626  ...  [0.07805293053388596, 0.02422463893890381, 0.0...
    24  deece7e64b2a4628850d4bb6e394a9c3  ...  [0.04740399867296219, 0.04178982973098755, 0.0...
    25  e657b5121ff8456b9a610cfaead8e0cb  ...  [0.0363662987947464, 0.034985776990652084, 0.0...
    26  bf4e255cdac94ccc83a56435a5e4b075  ...  [0.05069461092352867, -0.013929769396781921, -...
    27  3b040bcc19f14e04880ae52881a89c1c  ...  [0.11038185656070709, 0.07458128780126572, 0.0...
    28  3d6b216c14354332b1bf1927ba168986  ...  [0.03483894094824791, 0.03588946908712387, -0....
    29  1c109cfdc370463eb6d537e5b7b382fb  ...  [0.053373657166957855, 0.02771691419184208, -0...
    30  3d0dcbc8971b415ea18065edc4d8c8ef  ...  [0.050201136618852615, 0.02363327145576477, -0...
    31  68105770b523412388424d984e711917  ...  [0.05895720049738884, 0.014720208011567593, -0...
    32  85c79fd84f5e4f918471c386852204c5  ...  [0.06239404156804085, -0.02401130087673664, -0...

    [33 rows x 8 columns]
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/datashaper/engine/verbs/convert.py:72:
    FutureWarning: errors='ignore' is deprecated and will raise in a future version. Use to_datetime without passing
    `errors` and catch exceptions explicitly instead
    datetime_column = pd.to_datetime(column, errors="ignore")
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/datashaper/engine/verbs/convert.py:72:
    UserWarning: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To
    ensure parsing is consistent and as-expected, please specify a format.
    datetime_column = pd.to_datetime(column, errors="ignore")
    🚀 create_final_nodes
        level        title       type  ...                 top_level_node_id  x  y
    0       0          "村"      "GEO"  ...  b45241d70f0e43fca764df95b2b81f77  0  0
    1       0         "リオ"   "PERSON"  ...  4119fd06010c494caa07f439b333f4c5  0  0
    2       0         "リナ"   "PERSON"  ...  d3835bf3dda84ead99deadbeac5d0d7d  0  0
    3       0        "エルド"   "PERSON"  ...  077d2820ae1845bcbb1803379a3d1eae  0  0
    4       0     "ドラゴンの涙"    "EVENT"  ...  3671ea0dd4e84c1a9b02c5ab2c8f4bac  0  0
    5       0       "古代の竜"     "MYTH"  ...  19a7f254a5d64566ab5cc15472df02de  0  0
    6       0         "村人"   "PERSON"  ...  e7ffaee9d31d4d3c96e04f911d0a8f9e  0  0
    7       0         "予言"    "EVENT"  ...  f7e11b0e297a44a896dc67928368f600  0  0
    8       0        "青い石"             ...  1fd3fa8bb5a2408790042ab9573779ee  0  0
    9       0          "湖"      "GEO"  ...  27f9fbe6ad8c4a8b9acee0d3596ed57c  0  0
    10      0       "ドラゴン"             ...  e1fd0e904a53409aada44442f23a51cb  0  0
    11      0        "竜の魂"      "GEO"  ...  de988724cfdf45cebfba3b13c43ceede  0  0
    12      0     "エルドの文献"      "GEO"  ...  96aad7cb4b7d40e9b7e13b94a67af206  0  0
    13      0       "竜の怒り"      "GEO"  ...  c9632a35146940c2a86167c7726d35e9  0  0
    14      0       "村の守り"      "GEO"  ...  9646481f66ce4fd2b08c2eddda42fc82  0  0
    15      0      "リナの計画"      "GEO"  ...  d91a266f766b4737a06b0fda588ba40b  0  0
    16      0       "湖の神秘"      "GEO"  ...  bc0e3f075a4c4ebbb7c7b152b65a5625  0  0
    17      0          "竜"   "PERSON"  ...  254770028d7a4fa9877da4ba0ad5ad21  0  0
    18      0      "古代の時代"    "EVENT"  ...  4a67211867e5464ba45126315a122a8a  0  0
    19      0         "封印"    "EVENT"  ...  04dbbb2283b845baaeac0eaf0c34c9da  0  0
    20      0      "リナの言葉"    "EVENT"  ...  1943f245ee4243bdbfbd2fd619ae824a  0  0
    21      0        "竜の心"  "CONCEPT"  ...  273daeec8cad41e6b3e450447db58ee7  0  0
    22      0         "協力"    "EVENT"  ...  e69dc259edb944ea9ea41264b9fcfe59  0  0
    23      0       "村の決意"  "CONCEPT"  ...  e2f5735c7d714423a2c4f61ca2644626  0  0
    24      0      "古代の遺跡"      "GEO"  ...  deece7e64b2a4628850d4bb6e394a9c3  0  0
    25      0      "リナの使命"  "CONCEPT"  ...  e657b5121ff8456b9a610cfaead8e0cb  0  0
    26      0  "竜の祝福を受けた村"      "GEO"  ...  bf4e255cdac94ccc83a56435a5e4b075  0  0
    27      0      "自然の再生"    "EVENT"  ...  3b040bcc19f14e04880ae52881a89c1c  0  0
    28      0      "リナの子孫"             ...  3d6b216c14354332b1bf1927ba168986  0  0
    29      0          "絆"  "CONCEPT"  ...  1c109cfdc370463eb6d537e5b7b382fb  0  0
    30      0        "次世代"  "CONCEPT"  ...  3d0dcbc8971b415ea18065edc4d8c8ef  0  0
    31      0         "歴史"  "CONCEPT"  ...  68105770b523412388424d984e711917  0  0
    32      0     "コミュニティ"  "CONCEPT"  ...  85c79fd84f5e4f918471c386852204c5  0  0

    [33 rows x 14 columns]
    /Users/«username/{{}}/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    /Users/«username»/{{}}/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    🚀 create_final_communities
    id  ...                                      text_unit_ids
    0  1  ...  [4d07cb7b889dc3477821f70571af3a36,58e70d7ad09e...
    1  2  ...  [4d07cb7b889dc3477821f70571af3a36,58e70d7ad09e...
    2  0  ...  [ee71298ece5a63e8b7c090e56ebb7fc4,f9fcd5f66a18...
    3  3  ...  [4d07cb7b889dc3477821f70571af3a36,58e70d7ad09e...

    [4 rows x 6 columns]
    🚀 join_text_units_to_entity_ids
                        text_unit_ids  ...                                id
    0  4d07cb7b889dc3477821f70571af3a36  ...  4d07cb7b889dc3477821f70571af3a36
    1  58e70d7ad09e03e070998b0a30ea382e  ...  58e70d7ad09e03e070998b0a30ea382e
    2  bdb5dc10d04545e18822999dd984e569  ...  bdb5dc10d04545e18822999dd984e569
    3  ee71298ece5a63e8b7c090e56ebb7fc4  ...  ee71298ece5a63e8b7c090e56ebb7fc4
    4  f9fcd5f66a1822340e74c982831397d0  ...  f9fcd5f66a1822340e74c982831397d0

    [5 rows x 3 columns]
    /Users/«username»/{{}}/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/numpy/core/fromnumeric.py:59: FutureWarning:
    'DataFrame.swapaxes' is deprecated and will be removed in a future version. Please use 'DataFrame.transpose'
    instead.
    return bound(*args, **kwds)
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/datashaper/engine/verbs/convert.py:65:
    FutureWarning: errors='ignore' is deprecated and will raise in a future version. Use to_numeric without passing
    `errors` and catch exceptions explicitly instead
    column_numeric = cast(pd.Series, pd.to_numeric(column, errors="ignore"))
    🚀 create_final_relationships
    source       target  weight  ... source_degree target_degree rank
    0     "村"     "ドラゴンの涙"     1.0  ...            10             2   12
    1     "村"         "村人"     2.0  ...            10             2   12
    2     "村"         "予言"     2.0  ...            10             1   11
    3     "村"         "リオ"     4.0  ...            10             6   16
    4     "村"       "ドラゴン"     1.0  ...            10             3   13
    5     "村"          "湖"     1.0  ...            10             2   12
    6     "村"         "リナ"     2.0  ...            10             7   17
    7     "村"          "竜"     2.0  ...            10             5   15
    8     "村"      "自然の再生"     1.0  ...            10             2   12
    9     "村"  "竜の祝福を受けた村"     1.0  ...            10             1   11
    10   "リオ"         "リナ"     4.0  ...             6             7   13
    11   "リオ"        "青い石"     2.0  ...             6             1    7
    12   "リオ"         "村人"     2.0  ...             6             2    8
    13   "リオ"          "竜"     1.0  ...             6             5   11
    14   "リオ"      "リナの子孫"     1.0  ...             6             2    8
    15   "リナ"        "エルド"     1.0  ...             7             2    9
    16   "リナ"       "古代の竜"     2.0  ...             7             1    8
    17   "リナ"       "ドラゴン"     1.0  ...             7             3   10
    18   "リナ"          "竜"     2.0  ...             7             5   12
    19   "リナ"      "リナの子孫"     1.0  ...             7             2    9
    20  "エルド"     "ドラゴンの涙"     2.0  ...             2             2    4
    21    "湖"       "ドラゴン"     1.0  ...             2             3    5
    22    "竜"      "古代の時代"     1.0  ...             5             1    6
    23    "竜"      "自然の再生"     1.0  ...             5             2    7

    [24 rows x 10 columns]
    🚀 join_text_units_to_relationship_ids
                                    id                                   relationship_ids
    0  ee71298ece5a63e8b7c090e56ebb7fc4  [eae4259b19a741ab9f9f6af18c4a0470, 3138f39f2bc...
    1  4d07cb7b889dc3477821f70571af3a36  [3138f39f2bcd43a69e0697cd3b05bc4d, dde131ab575...
    2  58e70d7ad09e03e070998b0a30ea382e  [de9e343f2e334d88a8ac7f8813a915e5, 17ed1d92075...
    3  bdb5dc10d04545e18822999dd984e569  [de9e343f2e334d88a8ac7f8813a915e5, b462b94ce47...
    4  f9fcd5f66a1822340e74c982831397d0  [de9e343f2e334d88a8ac7f8813a915e5, e2bf2601155...
    🚀 create_final_community_reports
    community  ...                                    id
    0         0  ...  650cdbe0-827e-4e27-b92f-162dcb14b09f
    1         1  ...  a1c39282-74d4-47dd-95e9-beb164823365
    2         2  ...  954be0b6-aec0-4f14-9fae-8f44b4579369
    3         3  ...  2ce313c8-cc17-4c5d-879d-4b863d23ce22

    [4 rows x 10 columns]
    🚀 create_final_text_units
                                    id  ...                                   relationship_ids
    0  ee71298ece5a63e8b7c090e56ebb7fc4  ...  [eae4259b19a741ab9f9f6af18c4a0470, 3138f39f2bc...
    1  f9fcd5f66a1822340e74c982831397d0  ...  [de9e343f2e334d88a8ac7f8813a915e5, e2bf2601155...
    2  bdb5dc10d04545e18822999dd984e569  ...  [de9e343f2e334d88a8ac7f8813a915e5, b462b94ce47...
    3  4d07cb7b889dc3477821f70571af3a36  ...  [3138f39f2bcd43a69e0697cd3b05bc4d, dde131ab575...
    4  58e70d7ad09e03e070998b0a30ea382e  ...  [de9e343f2e334d88a8ac7f8813a915e5, 17ed1d92075...

    [5 rows x 6 columns]
    /Users/«user»/«repos_dir»/.venv/lib/python3.10/site-packages/datashaper/engine/verbs/convert.py:72:
    FutureWarning: errors='ignore' is deprecated and will raise in a future version. Use to_datetime without passing
    `errors` and catch exceptions explicitly instead
    datetime_column = pd.to_datetime(column, errors="ignore")
    🚀 create_base_documents
                                    id  ...       title
    0  5e34c15c05424bd267864e8b474d5a73  ...  sample.txt

    [1 rows x 4 columns]
    🚀 create_final_documents
                                    id  ...       title
    0  5e34c15c05424bd267864e8b474d5a73  ...  sample.txt

    [1 rows x 4 columns]
    ⠦ GraphRAG Indexer
    ├── Loading Input (text) - 1 files loaded (0 filtered) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:00
    ├── create_base_text_units
    ├── create_base_extracted_entities
    ├── create_summarized_entities
    ├── create_base_entity_graph
    ├── create_final_entities
    ├── create_final_nodes
    ├── create_final_communities
    ├── join_text_units_to_entity_ids
    ├── create_final_relationships
    ├── join_text_units_to_relationship_ids
    ├── create_final_community_reports
    ├── create_final_text_units
    ├── create_base_documents
    └── create_final_documents
    🚀 All workflows completed successfully.
    ```

    </details>

    <details>
    <summary>この段階のディレクトリ構造</summary>

    ```bash
    .
    ├── .venv
    └── ragtest
        ├── cache
        │   ├── community_reporting
        │   │   ├── create_community_report-chat-v2-b83a0e9718b23f9a6cf70d1920f9aba8
        │   │   ├── create_community_report-chat-v2-b9acc96502a6b0edc5fbebc5bcdd7a63
        │   │   ├── create_community_report-chat-v2-e3eaf82c7e3c14ab2e4bc2e9883f2138
        │   │   └── create_community_report-chat-v2-fcb48589127e8a51ad5e7594357eb3b7
        │   ├── entity_extraction
        │   │   ├── chat-185f9691c56ffcfd876f3edbcca5298f
        │   │   ├── chat-3d8033b3616521278f72688d9387b875
        │   │   ├── chat-493922962812bbc08bf2f13c511dd8d6
        │   │   ├── chat-f2db94e9b1120728f9b4c370f2c7ba14
        │   │   ├── chat-f82f7a7416acfa0ca4deee9233129c2d
        │   │   └── extract-continuation-0-chat-v2-d4f5822c71d472b217a53c22ef9e547c
        │   ├── summarize_descriptions
        │   │   ├── summarize-chat-v2-016f104468ec4072fddb7111a42c11b2
        │   │   ├── summarize-chat-v2-0e652bbfd32e2ff4e4ce9ddbe5d89e7d
        │   │   ├── summarize-chat-v2-155d18b7053793a63384938af560786b
        │   │   ├── summarize-chat-v2-1713c328d1164fe3183d2615abb23b05
        │   │   ├── summarize-chat-v2-1d2b3a1e61a3b69724597e6cb9c47162
        │   │   ├── summarize-chat-v2-31b6c2fb59e7fdec3aadfa00a92f8faa
        │   │   ├── summarize-chat-v2-3de4156d02b8fc85512b28d628d444d7
        │   │   ├── summarize-chat-v2-5731e510e96a57bea86e9676b01d0537
        │   │   ├── summarize-chat-v2-57d5e032c8978ddf12f0509888cf9a4f
        │   │   ├── summarize-chat-v2-af32eff4e8993dbf695a29663b200a47
        │   │   ├── summarize-chat-v2-bbaba745d17c30436518616a22809ea0
        │   │   ├── summarize-chat-v2-d066c4b9c99bb8cce0d3f1b80950edd1
        │   │   ├── summarize-chat-v2-e85340694b99fd2929df26cfd3c1b840
        │   │   └── summarize-chat-v2-e995d2f46dce34a9e8e9a4bbfd54497a
        │   └── text_embedding
        │       ├── embedding-4d38973970183c344748fd455e55d4cb
        │       ├── embedding-be41f447fe9f533254a15e52c63948a2
        │       └── embedding-e6e8029f70514157253be0b882940a11
        ├── input
        │   └── sample.txt
        ├── output
        │   ├── 20240731-220508
        │   │   └── reports
        │   │       └── indexing-engine.log
        │   └── 20240731-223410
        │       ├── artifacts
        │       │   ├── create_base_documents.parquet
        │       │   ├── create_base_entity_graph.parquet
        │       │   ├── create_base_extracted_entities.parquet
        │       │   ├── create_base_text_units.parquet
        │       │   ├── create_final_communities.parquet
        │       │   ├── create_final_community_reports.parquet
        │       │   ├── create_final_documents.parquet
        │       │   ├── create_final_entities.parquet
        │       │   ├── create_final_nodes.parquet
        │       │   ├── create_final_relationships.parquet
        │       │   ├── create_final_text_units.parquet
        │       │   ├── create_summarized_entities.parquet
        │       │   ├── join_text_units_to_entity_ids.parquet
        │       │   ├── join_text_units_to_relationship_ids.parquet
        │       │   └── stats.json
        │       └── reports
        │           ├── indexing-engine.log
        │           └── logs.json
        ├── prompts
        │   ├── claim_extraction.txt
        │   ├── community_report.txt
        │   ├── entity_extraction.txt
        │   └── summarize_descriptions.txt
        ├── .env
        └── settings.yaml
    ```

    </details>

7.  質問

    **global 質問**

    ```bash
    python -m graphrag.query \
    --root ./ragtest \
    --method global \
    "主人公の交友関係を説明して"
    ```

    回答

    > ## 主人公の交友関係
    >
    > 主人公であるリナとリオは、村の中で特別な絆を持つ存在であり、彼らの関係は村の人々に対する影響力を強化しています。彼らは共に村人を導き、課題に取り組む姿勢を示しており、この協力的なアプローチは村のコミュニティイニシアティブを促進する要因となっています [Data: Reports (2, 1, 3, 0, +more)]。
    >
    > リナは、自然との調和や文化遺産の重要性を強調する重要なリーダーとして描かれています。一方で、リオは村人が自分の考えを表現し、経験を共有することを促す協力の触媒として機能しています。このように、彼らの役割は村の文化的な伝承を支える重要な要素となっています [Data: Reports (2, 1, 3, 0, +more)]。
    >
    > さらに、村人たちは強いコミュニティ意識と文化的アイデンティティを維持しており、これは彼らの生存と繁栄にとって重要です。特に、ドラゴンやそれに関連する古代の予言がもたらす課題に直面する中で、この文化的な結束は彼らの力となっています [Data: Reports (1, 3, 0, +more)]。
    >
    > ## 結論
    >
    > リナとリオの交友関係は、村の人々にとっての指導力と文化的なつながりを強化する重要な要素です。彼らの協力的な姿勢と文化的な価値観は

    **local 質問**

    ```bash
    python -m graphrag.query \
    --root ./ragtest \
    --method local \
    "主人公の交友関係を説明して"
    ```

    回答

    > ## 主人公の交友関係
    >
    > 主人公であるリナとリオは、村の中心的な存在であり、彼らの交友関係は村の人々との深い結びつきを反映しています。リナは村のリーダーとして、村人たちとの強い絆を築いており、特に村の歴史や文化を守るために積極的に活動しています。彼女は村の長老たちと交流し、彼らの知恵を学ぶことで、村の伝統を次世代に伝える役割を果たしています。このようなリナの姿勢は、村人たちにとっての信頼の源となっており、彼女のリーダーシップは村のアイデンティティを強化しています [Data: Entities (2); Relationships (6, 10, 19)]。
    >
    > 一方、リオは村の若い農夫として、村人たちとの協力を促進する重要な役割を担っています。彼は村人たちに対して、自然との調和を重視し、文化的な物語や方言を次世代に伝えることの重要性を強調しています。リオは村の人々を団結させ、共通の目的に向かって行動するように導く存在です。彼の優しさと情熱は、村人たちにインスピレーションを与え、彼らの共同体意識を高めています [Data: Entities (1); Relationships (3, 12, 14)]。
    >
    > ## リナとリオの関係
    >
    > リナとリオは、血縁関係にある兄妹であり、彼らの絆は村の発展において重要な役割を果たしています。彼らは共に村の文化を守り、村人たちを導くために協力しています。特に、青い石に関する議論を通じて、彼らは村の歴史や伝説を深く理解し、村人たちにその重要性を伝えています。このような共同作業は、彼らの関係を強化し、村全体の結束を促進しています [Data: Relationships (10)]。
    >
    > ## 村人とのつながり
    >
    > リナとリオは、村人たちとの関係を大切にし、彼らの意見や経験を尊重しています。リナは村人たちと積極的にコミュニケーションを取り、彼らの声を聞くことで、村の問題に対処するための具体的な行動を起こしています。また、リオは村人たちに対して、彼らの真の自己を追求するように促し、共同体の一体感を高める役割を果たしています。このように、リナとリオは村人たちとの強い結びつきを通じて、村の未来を築くために努力しています [Data: Relationships (8, 19)]。
    >
    > リナとリオの交友関係は、村の文化や伝統を守るための重要な要素であり、彼らのリーダーシップは村人たちにとっての希望の象徴となっています。彼らの努力は、村のアイデンティティを強化し、持続可能な未来を築くための基盤を提供しています。

## まとめ

Langchain などを利用した GraphRAG だと、langchain の破壊的な変更で動作しなくなったり、Neo4j のセットアップや retriever の自作など利用のハードルが高かった。

一方で microsoft の graphrag を使うと、このパッケージのみで graphrag を完結させることができ、細かな設定にこだわらなければ、コマンド実行だけで実装できた。

さらに、細かい調整をしたい場合も、`settings.yaml`や`prompts/`を編集するだけで反映できるので、プロダクトに GraphRAG を導入するだけなら、下手に自作するよりはこれを使う方が良さそう。

今回は CLI からの実行だったが全てを python コードとしても記述することができるので([参考](https://microsoft.github.io/graphrag/posts/query/notebooks/overview/))、出力の加工や API の実装など柔軟に利用できそう。
