# Experiment: Random-Tagprop Distance-Networks

Hello.

```arg1 arg2 arg3

x = 5
y = x*2

mmd.emit(y)
```

Hello, *hi*, howdy.

Testing $f(x)=y$ math mode.

$$
    x = 1\\
    y = 2
$$

$$
\sum_{i=0}^n i^2 = \frac{(n^2+n)(2n+1)}{6}
$$

$$
\begin{aligned} 2x - 4 &= 6 \\ 2x &= 10 \\ x &= 5 \end{aligned}
$$

$$
\begin{align*} 2x - 4 &= 6 \\ 2x &= 10 \\ x &= 5 \end{align*}
$$

$$
a < b > c
$$

```
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

x = np.array([1,2,3])
y = x*x
sns.relplot(x = x, y = y)

mmd.emit(plt.gcf())
```

This should do the same thing:

```plot
x = np.array([1,2,3])
y = x*x
sns.relplot(x = x, y = y)
```

Multiple plots:

```
import matplotlib.pyplot as plt

sns.relplot(x = x, y = y)
p1 = plt.gcf()
mmd.emit(p1)

sns.relplot(x = y, y = x)
p2 = plt.gcf()
mmd.emit(p2)

mmd.emit('This is some text. Hi!')
```

It should also be OK to have no output:

```
import sys
sys.stderr.write("This won't go to the file!\n")
```

$$
\begin{aligned} 2x - 4 &= 6 \\ 2x &= 10 \\ x &= 5 \end{aligned}
$$

$$
\begin{align*} 2x - 4 &= 6 \\ 2x &= 10 \\ x &= 5 \end{align*}
$$

$$
a < b > c
$$

Fallback renderer calls repr:

```
import pandas as pd

table = pd.DataFrame(dict(a = [1,2,3], b = [4,5,6]))
mmd.emit(table)
```
