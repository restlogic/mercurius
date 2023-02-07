def lcs(S,T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])

    return lcs_set

def infer_common_key_name(creating_response_keys, sub_request_key):

    # 'lcs' stands for Longest Common Substring

    lcs_sorted = sorted(
        map(
            lambda x: {'l': len(next(iter(lcs(sub_request_key, x)))), 'key': x},
            creating_response_keys
            ), 
            key=lambda x: x['l'],
            reverse=True
        )

    most_likely_key = lcs_sorted[0]['key']

    return most_likely_key

