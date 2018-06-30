nCr_tool.py
================

Transforms all pairwise comparisons of any sized set of 
choice candidates into ordinal preference structures. This script outputs the vertices
of any sized permutahedron and notes the number of transitive and intransitive
structures, by reproducing the projection matrix found 
[here](https://lsa.umich.edu/psych/junz/Publication/2004%20Zhang%20JMP%20Permutahedron.pdf).
Simply run the script in your interactive shell or notebook interface and use the function
Zonotope() to calculate the projected vertices. Set argument 'sums' to True if you would
like to list all vector projections in your output, regardless of redundancy, for a manual check.
