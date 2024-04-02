import pprint as pp

def search_by_difficulty(client,index_name : str, query : str, num_results = 1):
    
    difficulty_query = {
        'size': num_results,
        "_source": ["recipeName","totalTimeMinutes","difficultyLevel"],
        'query' : {
            'multi_match' : {
                'query': query,
                'fields': ['difficultyLevel']
            }
        }
    }
    
    response = client.search(
        body=difficulty_query,
        index=index_name
    )
    
    print('\nSearch results:')
    pp.pprint(response)
    
def search_by_course(client,index_name : str, query : str, num_results = 1):
    
    difficulty_query = {
        'size': num_results,
        "_source": ["recipeName","totalTimeMinutes","courses"],
        'query' : {
            'multi_match' : {
                'query': query,
                'fields': ['courses']
            }
        }
    }
    
    response = client.search(
        body=difficulty_query,
        index=index_name
    )
    
    print('\nSearch results:')
    pp.pprint(response)
    
def search_by_total_time(client, index_name: str, max_time: int, num_results=10):
    total_time_query = {
        'size': num_results,
        "_source": ["recipeName", "totalTimeMinutes", "difficultyLevel"],
        'query': {
            'range': {
                'totalTimeMinutes': {'lte': max_time}
            }
        }
    }

    response = client.search(
        body=total_time_query,
        index=index_name
    )

    print('\nSearch results:')
    pp.pprint(response)