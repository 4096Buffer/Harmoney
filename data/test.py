with open("userdata.csv") as f:
    x = f.read().splitlines()

fn = ''

for y in x:
    fn += y[:-1]  + '\n'

with open("months2.csv", "w") as r:
    r.write(fn)