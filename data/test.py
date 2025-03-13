with open("user-data.csv") as f:
    x = f.read().splitlines()

fn = ''

for y in x:
    s = y.split(',')
    n = ''
    for p in s:
        n += p+','
    
    n = n[:-1]

    fn += n + '\n'

with open("user-data", "w") as r:
    r.write(fn)