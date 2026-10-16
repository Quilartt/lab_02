d = {}

if 'new_key' in d:
    d['new_key'] += 1
else:
    d['new_key'] = 1

print(d.get('old'))